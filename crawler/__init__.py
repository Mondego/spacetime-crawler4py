from utils import get_logger
from utils.robotstxt_sitemap import get_sitemap_urls
from crawler.frontier import Frontier
from crawler.worker import Worker

class Crawler(object):
    def __init__(self, config, restart, frontier_factory=Frontier, worker_factory=Worker):
        self.config = config
        self.logger = get_logger("CRAWLER")
        self.frontier = frontier_factory(config, restart)
        self._add_sitemap_urls()
        self.workers = list()
        self.worker_factory = worker_factory

    def start_async(self):
        self.workers = [
            self.worker_factory(worker_id, self.config, self.frontier)
            for worker_id in range(self.config.threads_count)]
        for worker in self.workers:
            worker.start()

    def start(self):
        self.start_async()
        self.join()

    def join(self):
        for worker in self.workers:
            worker.join()
    
    def _add_sitemap_urls(self) -> None:
        urls_to_add = get_sitemap_urls(self.config.seed_urls, self.config, self.logger)
        for url in urls_to_add:
            self.frontier.add_url(url)