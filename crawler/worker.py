from threading import Thread

from inspect import getsource
from utils.download import download
from utils import get_logger
import scraper
import time
from threading import Lock


# changes only add generate report stuff after frontier is empty
class Worker(Thread):
    domainCrawlTimer = {}
    workerLock = Lock()
    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        # basic check for requests in scraper
        assert {getsource(scraper).find(req) for req in {"from requests import", "import requests"}} == {-1}, "Do not use requests from scraper.py"
        super().__init__(daemon=True)
        
    

    

    def run(self):
        while True:
            tbd_url = self.frontier.get_tbd_url()
            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.")
                scraper.generate_report()
                break
            
            urlDomain = scraper.extract_domain(tbd_url)
            # print(Worker.domainCrawlTimer)
            while True:
                Worker.workerLock.acquire()
                if (urlDomain not in Worker.domainCrawlTimer):
                    Worker.domainCrawlTimer[urlDomain] = time.time()
                    Worker.workerLock.release()
                else:
                    timeDelta = time.time()-Worker.domainCrawlTimer[urlDomain]
                    
                    if  timeDelta < self.config.time_delay:
                        Worker.workerLock.release()
                        time.sleep(self.config.time_delay-timeDelta+.1)
                    else:
                        Worker.domainCrawlTimer[urlDomain] = time.time()
                        Worker.workerLock.release()
                        break
                

            resp = download(tbd_url, self.config, self.logger)


            self.logger.info(
                f"Downloaded {tbd_url}, status <{resp.status}>, "
                f"using cache {self.config.cache_server}.")
            scraped_urls = scraper.scraper(tbd_url, resp)
            for scraped_url in scraped_urls:
                self.frontier.add_url(scraped_url)
            self.frontier.mark_url_complete(tbd_url)
            #time.sleep(self.config.time_delay)
