from threading import Thread, Timer

from inspect import getsource
from utils.download import download
from utils import get_logger
import scraper
import time

def release_politeness_lock(semaphore):
    semaphore.release()

class Worker(Thread):
    
    def __init__(self, worker_id, config, frontier, pages, max_word_count_global, high_freq_words_global, semaphore):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        self.multithreaded_politer = semaphore
        self.pages = pages
        self.max_word_count_global = max_word_count_global
        self.high_freq_words_global = high_freq_words_global
        # basic check for requests in scraper
        assert {getsource(scraper).find(req) for req in {"from requests import", "import requests"}} == {-1}, "Do not use requests in scraper.py"
        assert {getsource(scraper).find(req) for req in {"from urllib.request import", "import urllib.request"}} == {-1}, "Do not use urllib.request in scraper.py"
        super().__init__(daemon=True)
        
    def run(self):
        while True:
            tbd_url = self.frontier.get_tbd_url()
            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.")
                break
            # Acquire the politeness lock before doing any download from internet
            self.multithreaded_politer.acquire()
            
            resp = download(tbd_url, self.config, self.logger)

            # Set timer to be released after the politeness is done
            t = Timer(self.config.time_delay, release_politeness_lock, [self.multithreaded_politer])
            t.start()

            self.logger.info(
                f"Downloaded {tbd_url}, status <{resp.status}>, "
                f"using cache {self.config.cache_server}.")
            scraped_urls = scraper.scraper(tbd_url, resp, self.pages, self.max_word_count_global,
                                    self.high_freq_words_global)
            for scraped_url in scraped_urls:
                self.frontier.add_url(scraped_url)
            self.frontier.mark_url_complete(tbd_url)
            time.sleep(self.config.time_delay)
