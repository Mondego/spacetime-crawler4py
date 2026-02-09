from threading import Thread

from inspect import getsource
from utils.download import download
from utils import get_logger
import scraper
import time

#Reference for politeness implementation: https://dev.to/h0tb0x/webcrawling-is-just-a-brute-force-algorithm-2meg, https://www.packtpub.com/en-us/product/python-web-scraping-9781782164364/chapter/1-introduction-to-web-scraping-1/section/crawling-your-first-website-ch01lvl1sec05, https://realpython.com/python-thread-lock/    
class Worker(Thread):
    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier

        # basic check for requests in scraper
        assert {getsource(scraper).find(req) for req in {"from requests import", "import requests"}} == {-1}, "Do not use requests in scraper.py"
        assert {getsource(scraper).find(req) for req in {"from urllib.request import", "import urllib.request"}} == {-1}, "Do not use urllib.request in scraper.py"
        
        # We set daemon to True so that the worker threads will automatically exit when the main thread exits. This is important for clean shutdown of the crawler.
        super().__init__(daemon=True)
        
    def run(self):
        while True:
            tbd_url = self.frontier.get_tbd_url()
            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.")
                break

            resp = download(tbd_url, self.config, self.logger)
            if not resp:
                self.logger.info(f"Failed to download {tbd_url} using cache {self.config.cache_server}.")
                self.frontier.mark_url_complete(tbd_url) # mark as complete to avoid retrying indefinitely
                self.frontier.close_if_done()
                continue

            self.logger.info(
                f"Downloaded {tbd_url}, status <{resp.status}>, "
                f"using cache {self.config.cache_server}.")
            scraped_urls = scraper.scraper(tbd_url, resp) # return list of URLs to add back to frontier
            for scraped_url in scraped_urls:
                self.frontier.add_url(scraped_url)

            self.frontier.mark_url_complete(tbd_url)
            self.frontier.close_if_done()