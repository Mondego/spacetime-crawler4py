from utils import get_logger
from crawler.frontier import Frontier
from crawler.worker import Worker

# this set it going to store all of the URLs we visit without the fragment section
unique_URLs = set() # will be unique to each crawler

class Crawler(object):
    def __init__(self, config, restart, frontier_factory=Frontier, worker_factory=Worker):
        self.config = config
        self.logger = get_logger("CRAWLER")
        self.frontier = frontier_factory(config, restart)
        self.workers = list()
        self.worker_factory = worker_factory

    def start_async(self):
        self.workers = [
            self.worker_factory(worker_id, self.config, self.frontier)
            for worker_id in range(self.config.threads_count)] # if we only have one thread, we will only see one worker
        for worker in self.workers:
            worker.start() # if thread is only 1 then there will only be one worker

    def start(self):
        self.start_async()
        self.join()

    def join(self):
        for worker in self.workers:
            worker.join()
