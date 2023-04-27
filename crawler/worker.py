from threading import Thread
from urllib.parse import urlparse    # to get host part of URL --> hash into numbers --> modulo by 4 to get which thread gets the url
import hashlib

from inspect import getsource
from utils.download import download
from utils import get_logger
import scraper
import time


class Worker(Thread):
    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.worker_id = worker_id
        self.config = config
        self.frontier = frontier
        # basic check for requests in scraper
        assert {getsource(scraper).find(req) for req in {"from requests import", "import requests"}} == {-1}, "Do not use requests in scraper.py"
        assert {getsource(scraper).find(req) for req in {"from urllib.request import", "import urllib.request"}} == {-1}, "Do not use urllib.request in scraper.py"
        super().__init__(daemon=True)
        
    def run(self):                       # each of the 4 threads runs the below code:
        while True:
            with self.frontier.lock:     # lock frontier when getting url from frontier (releases lock at end of block-- by indentation, so by line 29)
                tbd_url = self.frontier.get_tbd_url()
                if not tbd_url:
                    self.logger.info("Frontier is empty. Stopping Crawler.")
                    break

            # find out which worker thread to assign this url to
            parsed_url = urlparse(tbd_url)        # parse url, get host below
            parsed_host = parsed_url.netloc
            hashed_url = int(hashlib.sha256(parsed_host.encode('utf-8')).hexdigest(), 16)   # hash host url into number
            which_thread = hashed_url % 4         # gives 0-3

            # only run if you are the thread that has matching id
            if which_thread == self.worker_id:
                resp = download(tbd_url, self.config, self.logger)
                self.logger.info(
                    f"Downloaded {tbd_url}, status <{resp.status}>, "
                    f"using cache {self.config.cache_server}.")
                
                url_fingerprint = scraper.extract_text_fingerprint(tbd_url, resp)
                with self.frontier.lock:
                    self.frontier.add_fingerprint(url_fingerprint, tbd_url)                  # ?????

                scraped_urls = scraper.scraper(tbd_url, resp)
                with self.frontier.lock:
                    for scraped_url in scraped_urls:
                        self.frontier.add_url(scraped_url)
                    self.frontier.mark_url_complete(tbd_url)
                time.sleep(self.config.time_delay)            # time delay only affects this thread? Not sure
