from utils import get_logger
from utils.statistics import write_statistics
from crawler.frontier import Frontier
from crawler.worker import Worker
from threading import Semaphore

class Crawler(object):
    def __init__(self, config, restart, pages, max_word_count_global, high_freq_words_global, frontier_factory=Frontier, worker_factory=Worker):
        self.config = config
        self.logger = get_logger("CRAWLER")
        self.multithreaded_politer = Semaphore()
        self.frontier = frontier_factory(config, restart)
        self.workers = list()
        self.worker_factory = worker_factory
        self.pages = pages
        self.max_word_count_global = max_word_count_global
        self.high_freq_words_global = high_freq_words_global

    def start_async(self):
        self.workers = [
            self.worker_factory(worker_id, self.config, self.frontier, self.pages, self.max_word_count_global,
            self.high_freq_words_global, self.multithreaded_politer)
            for worker_id in range(self.config.threads_count)]
        for worker in self.workers:
            worker.start()

    def start(self):
        self.start_async()
        self.join()

    def join(self):
        for worker in self.workers:
            worker.join()
        write_statistics(self.pages, self.max_word_count_global, self.high_freq_words_global)
