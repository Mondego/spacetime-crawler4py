from threading import Thread

from inspect import getsource
from utils.download import download
from utils import get_logger
import scraper
import time
import nltk 
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

class Worker(Thread):
    def __init__(self, worker_id, config, frontier, word_dict, checkSum_hashes):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        self.word_dict = word_dict
        self.stop_words = set(stopwords.words('english'))
        self.sum_hashes = checkSum_hashes
        # basic check for requests in scraper
        assert {getsource(scraper).find(req) for req in {"from requests import", "import requests"}} == {-1}, "Do not use requests in scraper.py"
        assert {getsource(scraper).find(req) for req in {"from urllib.request import", "import urllib.request"}} == {-1}, "Do not use urllib.request in scraper.py"
        super().__init__(daemon=True)
        
    def parse_text(self, tbd_url, resp) -> None:
        string = ""
        soup = BeautifulSoup(html_content, 'html.parser') # bts content into a varaible that we can further parse 
        headers_types = ['title', 'h1','h2,''h3', 'h4', 'h5','h6','p']
        # para = soup.find_all('p')

        # headers = soup.find_all(headers_types)
        for headers in headers_types:
            plain_text = soup.find_all(headers)
            for text in plain_text:
                string += text.get_text() + ' ' # concatenate all the words together into one big string 
            
        words = [word for word in word_tokenize(string.lower())  # parse only alphnumeric chars 
                if (word.isalpha() or word.isdigit()) and word not in self.stop_words] # ignore stops words in self.stop_words 

        checkSum = scraper.checkSum_Hash(words) # get a tuple for check sum 

        if checkSum not in self.sum_hashes:
            for word in words:
                if word not in self.stop_words:
                    if word in self.word_dict: #not already in dict, and not a stop word
                        self.word_dict[word] +=1 
                    else:
                        self.word_dict[word] = 1
            self.sum_hashes[checkSum] = tbd_url 
            # add that sum to keep track if we hit a duplicate this also helps keep track of unqiue urls (non duplicate urls) 

    def run(self):
        while True:
            tbd_url = self.frontier.get_tbd_url()
            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.")
                if self.worker_id == 0: # only one worker can print to output.txt
                    file_path = 'freq_words.txt'
                        # Open the file in write mode
                    with open(file_path, 'w') as file:
                            # Loop through the dictionary and write key-value pairs
                        for key, value in sorted(self.word_dict.items(), key=lambda x: x[1], reverse= True):
                            file.write(f"{key}: {value}\n")
                print(len(self.sum_hashes)) # get a count of number of unqiue urls
                break
            resp = download(tbd_url, self.config, self.logger)
            self.logger.info(
                f"Downloaded {tbd_url}, status <{resp.status}>, "
                f"using cache {self.config.cache_server}.")
            self.parse_text(tbd_url, resp) # parse the text and add it to our dict, and add a checksum hash to the url dict too 
            scraped_urls = scraper.scraper(tbd_url, resp)
            for scraped_url in scraped_urls:
                self.frontier.add_url(scraped_url)
            self.frontier.mark_url_complete(tbd_url) # <- simhash / checksum of the tbh_url should be passed into the mark_complete, so that we can write it into our txt file / dict 
            time.sleep(self.config.time_delay)
