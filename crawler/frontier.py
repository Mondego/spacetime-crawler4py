import os
import shelve

from threading import Lock, Condition
import time 
import heapq
from collections import deque
from urllib.parse import urlparse

from utils import get_logger, get_urlhash, normalize
from scraper import is_valid

POLITENESS_DELAY = 0.5    # 500 ms per requirements

#Reference for politeness implementation: https://dev.to/h0tb0x/webcrawling-is-just-a-brute-force-algorithm-2meg, https://www.packtpub.com/en-us/product/python-web-scraping-9781782164364/chapter/1-introduction-to-web-scraping-1/section/crawling-your-first-website-ch01lvl1sec05, https://realpython.com/python-thread-lock/    
# General architecture ideas: https://deepwiki.com/unclecode/crawl4ai/6.2-rate-limiting-and-domain-management
class Frontier(object):
    def __init__(self, config, restart):
        self.logger = get_logger("FRONTIER")
        self.config = config

        # Thread-safe queue for URLs to be downloaded, and set for deduplication.
        self.lock = Lock() # lock for synchronizing access to the frontier
        self.condition = Condition(self.lock) # used to allow threads to sleep till condition/notify other threads
        self.per_domain= {} # stores domain as key, then deque of its URLS
        self.next_allowed = {} # maps domain to its next earliest fetch time
        self.ready_heap = [] # min-heap to grab the next earliest domain access
        self.inflight = 0 # tracks how many urls currently worked on, for clean shut down

        self.closed = False 

        # Config for shelve batch saves
        # sync()'s slow performance: https://runebook.dev/en/docs/python/library/shelve/shelve.Shelf.sync
        self._dirty_writes = 0
        self.SYNC_EVERY = 200
        self._last_sync = time.monotonic()
        self.SYNC_INTERVAL = 5.0   # secs

        #Persistent storage for discovered URLs and their completion status. Keyed by URL hash.
        if not os.path.exists(self.config.save_file) and not restart:
            # Save file does not exist, but request to load save.
            self.logger.info(
                f"Did not find save file {self.config.save_file}, "
                f"starting from seed.")
        elif os.path.exists(self.config.save_file) and restart:
            # Save file does exists, but request to start from seed.
            self.logger.info(
                f"Found save file {self.config.save_file}, deleting it.")
            os.remove(self.config.save_file)

        # Load existing save file, or create one if it does not exist.
        self.save = shelve.open(self.config.save_file)

        # If restart, seed the frontier with the seed urls. Otherwise, populate the frontier with the urls in the save file that are not marked as completed.
        if restart:
            for url in self.config.seed_urls:
                self.add_url(url) # if restarting, add each seed to the frontier
        else:
            # Set the frontier state with contents of save file.
            self._parse_save_file()
            if not self.save: # If the save is empty, fall back to seeding
                for url in self.config.seed_urls:
                    self.add_url(url)


    def _domain(self, url: str) -> str:
        """grabs the domain from the url"""
        return (urlparse(url).netloc or "").lower()


    def _parse_save_file(self):
        ''' This function can be overridden for alternate saving techniques. '''
        total_count = len(self.save) # how many URLs hav been discovered 
        tbd_count = 0 # how many are still pending 

        for url, completed in self.save.values():
            if not completed and is_valid(url):
                self._schedule_existing(url) # add to todolist
                tbd_count += 1

        self.logger.info(
            f"Found {tbd_count} urls to be downloaded from {total_count} "
            f"total urls discovered.")


    def get_tbd_url(self):
        with self.condition:
            while True:
                if self.closed: 
                    return None

                if not self.ready_heap:
                    if self.inflight == 0:  # if no job in line, just close
                        self.closed = True
                        return None
                    self.condition.wait()  # no domain, wait for population
                    continue

                ready_time, domain = self.ready_heap[0] # grab the earliest domain
                now = time.monotonic() # current time

                if ready_time > now:  # worker wait until next domain crawl
                    self.condition.wait(timeout=ready_time - now)
                    continue

                heapq.heappop(self.ready_heap)
                url_queue = self.per_domain.get(domain)

                if not url_queue: # no urls in domain
                    continue
                
                url = url_queue.popleft()

                self.inflight += 1

                next_time = now + POLITENESS_DELAY
                self.next_allowed[domain] = next_time

                if url_queue: # can crawl the domain now, rescheduling next domain crawl
                    heapq.heappush(self.ready_heap, (next_time, domain))

                else: # no more urls, cleaning up
                    self.per_domain.pop(domain, None)
                
                return url


    def add_url(self, url):
        # --- Clean up phase ---
        url = normalize(url) # normalize so same page doesn't appear in multiple forms

        if not is_valid(url): # cut invalid urls out (early)
            return

        urlhash = get_urlhash(url) # compute hash key for 

        domain = self._domain(url)
        if not domain:
            return
        # ----------------------

        with self.condition: # lock
            if urlhash not in self.save:
                self.save[urlhash] = (url, False) # store hash key as not completed yet
                self._maybe_sync() # sync in batches
                url_queue = self.per_domain.setdefault(domain, deque())  # return if domain exists, if not create new deque

                was_empty = (len(url_queue) == 0)
                url_queue.append(url)

                if was_empty:
                    ready_time = self.next_allowed.get(domain, 0.0) # if domain exist, return time, if not, set to 0
                    heapq.heappush(self.ready_heap, (ready_time, domain))

                self.condition.notify()
    

    def mark_url_complete(self, url):
        urlhash = get_urlhash(url)

        with self.condition: 
            if urlhash not in self.save:
                # This should not happen.
                self.logger.error(
                    f"Completed url {url}, but have not seen it before.")
                return

            self.save[urlhash] = (url, True) # update status to completed
            self.inflight = max(0, self.inflight - 1) # updates inflight as processing urls decrease by 1
            self._maybe_sync()
            self.condition.notify() # wakes ]up a worker that is sleeping/waiting


    def _schedule_existing(self, url: str):
        """Only used for scheduling urls in shelve"""
        url = normalize(url)
        if not is_valid(url):
            return

        domain = self._domain(url)
        if not domain:
            return

        url_queue = self.per_domain.setdefault(domain, deque())
        was_empty = (len(url_queue) == 0)
        url_queue.append(url)

        if was_empty:
            ready_time = self.next_allowed.get(domain, 0.0)
            heapq.heappush(self.ready_heap, (ready_time, domain))


    def close_if_done(self):
        """closes the program when all processes empty"""
        with self.condition:
            if not self.ready_heap and self.inflight == 0:
                self.closed = True
                self.condition.notify_all() # wakes everyone up and stops


    def close(self):
        with self.condition:
            self.closed = True
            self.condition.notify_all()  # wakes all workers up and exit

        # flush to disk
        try:
            self.save.sync()
        finally:
            self.save.close()


    def _maybe_sync(self):
        """Helper for syncing/flushing to shelve in batches for performance"""
        now = time.monotonic()
        self._dirty_writes += 1
        if (self._dirty_writes >= self.SYNC_EVERY) or (now - self._last_sync) >= self.SYNC_INTERVAL:
            self.save.sync()
            self._dirty_writes = 0
            self._last_sync = now