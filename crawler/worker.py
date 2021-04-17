from threading import Thread

from utils.download import download
from utils import get_logger
from scraper import scraper
import time

# added these imports
import crawler
from urllib.parse import urlparse, urldefrag


class Worker(Thread):
    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        super().__init__(daemon=True)
        
    # called in __init__.py 
    def run(self):
        while True:
            tbd_url = self.frontier.get_tbd_url() # gets the next URL to be downloaded from the frontier

            # this will add to the global set in __init__ which keeps track of all visited URLs
            no_fragment = urldefrag(tbd_url)
            crawler.unique_URLs.add(no_fragment)
            
            if not tbd_url: # if there are no more URLS then we are done!
                self.logger.info("Frontier is empty. Stopping Crawler.")
                break
            # else we download the URL that was popped off of the frontier
            resp = download(tbd_url, self.config, self.logger)
            self.logger.info(
                f"Downloaded {tbd_url}, status <{resp.status}>, "
                f"using cache {self.config.cache_server}.")
            scraped_urls = scraper(tbd_url, resp) # call to the scraper
            for scraped_url in scraped_urls:
                self.frontier.add_url(scraped_url)
            self.frontier.mark_url_complete(tbd_url)
            time.sleep(self.config.time_delay)
