from threading import Thread

from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse

from utils.download import download
from utils import get_logger
from scraper import scraper, is_valid
import time

from crawler.recorder import Recorder


class Worker(Thread):
    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        self.robots_txt_dict = dict()
        super().__init__(daemon=True)
        
    def can_fetch(self, url):
        parsed = urlparse(url)

        if parsed.netloc in self.robots_txt_dict:
            return self.robots_txt_dict[parsed.netloc].can_fetch('*', url)
        
        rp = RobotFileParser()
        rp.set_url('{}://{}/robots.txt'.format(parsed.scheme, parsed.netloc))
        rp.read()
        self.robots_txt_dict[parsed.netloc] = rp

        return rp.can_fetch('*', url)


    def run(self):
        
        # this is where we are gonna call the function to get the robot.txt
        record = Recorder()
        while True:
            tbd_url = self.frontier.get_tbd_url()

            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.")
                break

            if not self.can_fetch(tbd_url):
                continue

            resp = download(tbd_url, self.config, self.logger)
            self.logger.info(
                f"Downloaded {tbd_url}, status <{resp.status}>, "
                f"using cache {self.config.cache_server}.")

            scraped_urls = scraper(tbd_url, resp)

            # adding data to recorder
            record.add_url(tbd_url)

            if not (resp.raw_response is None and is_valid(tbd_url)):
                record.add_words(resp.raw_response.content, tbd_url)

            record.save()

            for scraped_url in scraped_urls:
                self.frontier.add_url(scraped_url)
            self.frontier.mark_url_complete(tbd_url)
            time.sleep(self.config.time_delay)
        
        record.finish_crawl_report()
