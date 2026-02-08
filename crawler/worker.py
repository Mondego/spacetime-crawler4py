from threading import Thread
import hashlib
from urllib.parse import urlparse, urlunparse
from inspect import getsource
from utils.download import download
from utils.url_pattern_detection import get_url_pattern_hash
from utils import get_logger
import scraper
import time
from collections import defaultdict
import tldextract
import json

class Worker(Thread):
    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        self.seen_urls = set()
        self.seen_url_patterns = defaultdict(int)
        self.subdomains_count = defaultdict(int)
        self.counts_stats_file = "count_stats.txt"
        self.MAX_URL_PATTERN_HITS = 500
        self.MAX_SUBDOMAIN_HITS = 10000
        # basic check for requests in scraper
        assert {getsource(scraper).find(req) for req in {"from requests import", "import requests"}} == {-1}, "Do not use requests in scraper.py"
        assert {getsource(scraper).find(req) for req in {"from urllib.request import", "import urllib.request"}} == {-1}, "Do not use urllib.request in scraper.py"
        super().__init__(daemon=True)
    def write_stats(self):
        data = {
            "num_urls": len(self.seen_urls),
            "subdomain_count": dict(self.subdomains_count)
        }
        with open(self.counts_stats_file, "w") as f:
            json.dump(data, f, indent=4) 
    def run(self):
        while True:
            tbd_url = self.frontier.get_tbd_url()
            try:
                if not tbd_url:
                    self.logger.info("Frontier is empty. Stopping Crawler.")
                    break
                resp = download(tbd_url, self.config, self.logger)
                self.logger.info(
                    f"Downloaded {tbd_url}, status <{resp.status}>, "
                    f"using cache {self.config.cache_server}.")
                scraped_urls = scraper.scraper(tbd_url, resp)
                for scraped_url in scraped_urls:
                    parsed_url = urlparse(scraped_url)._replace(scheme='',fragment="")
                    url_str =  urlunparse(parsed_url)
                    hashed_url = hashlib.sha256(url_str.encode('utf-8')).hexdigest()
                    hashed_url_pattern = get_url_pattern_hash(scraped_url)
                    

                    if hashed_url in self.seen_urls:
                        print(f"Hashed url already seen...skipping")
                        continue

                    if self.seen_url_patterns[hashed_url_pattern] >= self.MAX_URL_PATTERN_HITS:
                        print(f"Hashed url pattern reaached its limit:", hashed_url_pattern)
                        continue
                    
                    curr_subdomain = tldextract.extract(parsed_url.hostname).subdomain
                    if self.subdomains_count[curr_subdomain] >= self.MAX_SUBDOMAIN_HITS:
                        print(f"Subdomain has reaached its limit:", subdomain)
                        continue
                    
                    self.subdomains_count[curr_subdomain] += 1
                
                    depth = len([segment for segment in parsed_url.path.split('/') if segment])
                    if depth >= 6:
                        print(f"URL depth is 6 or more...skipping")
                        continue
                    self.seen_url_patterns[hashed_url_pattern] += 1

                    self.seen_urls.add(hashed_url)
                    if len(self.seen_urls) % 10 == 0:
                        self.write_stats()
                    self.frontier.add_url(scraped_url)
                self.frontier.mark_url_complete(tbd_url)
                time.sleep(self.config.time_delay)
            except Exception:
                continue
