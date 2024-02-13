from utils import get_logger
from crawler.frontier import Frontier
from crawler.worker import Worker

class Crawler(object):
    def __init__(self, config, restart, frontier_factory=Frontier, worker_factory=Worker):
        self.config = config
        self.logger = get_logger("CRAWLER")
        self.frontier = frontier_factory(config, restart)
        self.word_dict = dict() # pass a dictionary to keep track of all words, is referenced by all workers 
        self.workers = list()
        self.worker_factory = worker_factory
        self.checkSum_hashes = set()
        self.UniqueUrls = set()
        self.JustICS = dict()
            # this keeps track of all domains and their sub domains, sets will grow under these domains 

    def start_async(self):
        self.workers = [
            self.worker_factory(worker_id, self.config, self.frontier, self.word_dict, self.checkSum_hashes, self.UniqueUrls, self.JustICS)
            for worker_id in range(self.config.threads_count)]
        for worker in self.workers:
            worker.start()

    def start(self):
        self.start_async()
        self.join()

    def join(self):
        for worker in self.workers:
            worker.join()
