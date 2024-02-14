from threading import Thread

from urllib.parse import urlparse
from inspect import getsource
from utils.download import download
from utils import get_logger
import scraper
import time
import nltk 
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from bs4 import BeautifulSoup

class Worker(Thread):
    def __init__(self, worker_id, config, frontier, word_dict, checkSum_hashes, UniqueUrls, JustICS):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        self.word_dict = word_dict
        self.stop_words = set(stopwords.words('english'))
        self.sum_hashes = checkSum_hashes
        self.worker_id = worker_id
        self.most_content = ("", 0) # this will be held in order to keep track of url with biggest content block

        self.UniqueUrls = UniqueUrls # dict that will hold all ics/stat/info/cs sub domains
        self.JustICS = JustICS # dict that will keep track of a subdomain in ics, and how many links it has 
        # basic check for requests in scraper
        assert {getsource(scraper).find(req) for req in {"from requests import", "import requests"}} == {-1}, "Do not use requests in scraper.py"
        assert {getsource(scraper).find(req) for req in {"from urllib.request import", "import urllib.request"}} == {-1}, "Do not use urllib.request in scraper.py"
        super().__init__(daemon=True)
        


    def get_subdomain(self, tbd_url, urls):
        # urls is the list of urls extracted from tbd

        parsed_tbd = urlparse(tbd_url)
        parsed_tbd_sub = parsed_tbd.netloc.split('.') # get the netloc 
        if parsed_tbd_sub[1] == "ics": # we only want ics domains 
            unqies = set()
            for url in urls:
                if url not in self.UniqueUrls: #this is to avoid duplicates / over counting 
                    unqies.add(url) 

            if parsed_tbd_sub[0] not in self.JustICS: # if this specific subdmaoin is not in ics
                
                self.JustICS[parsed_tbd_sub[0]] = (parsed_tbd.scheme + '://' + parsed_tbd.netloc, len(unqies))
                # key : subdomain, val : (url, num unqiue urls)
            else:
                url, unqie_links = self.JustICS[parsed_tbd_sub[0]] # get the tuple 
                unqie_links += len(unqies) # add the extra links we got from that sub domain 
                self.JustICS[parsed_tbd_sub[0]] = (url, unqie_links) # update our tuple 
        


    def parse_text(self, tbd_url, resp) -> None:
        string = ""

        soup = BeautifulSoup(resp.raw_response.content, 'html.parser') # bts content into a varaible that we can further parse 
        headers_types = ['title', 'h1','h2,''h3', 'h4', 'h5','h6','p']
        # para = soup.find_all('p')

        # headers = soup.find_all(headers_types)
        for headers in headers_types:
            plain_text = soup.find_all(headers)
            for text in plain_text:
                string += text.get_text() + ' ' # concatenate all the words together into one big string 
            
        words = [word for word in word_tokenize(string.lower())  # parse only alphnumeric chars, lowercase  
                if (word.isalpha() or word.isdigit()) and word not in self.stop_words] # ignore stops words in self.stop_words 

        if (len(words) > self.most_content[1]): # if this url content is larger than current url content
            self.most_content = (tbd_url, len(words)) # change to this new

        checkSum = scraper.checkSum_Hash(words) # get a tuple for check sum 

        if checkSum not in self.sum_hashes or checkSum == (): # some html pages might not have a valid hash, so we just ignore it 
            for word in words:
                if word in self.word_dict: #not already in dict
                    self.word_dict[word] +=1 
                else:
                    self.word_dict[word] = 1
            self.sum_hashes.add(checkSum) #add that checkSum into our set
            self.UniqueUrls.add(tbd_url)   # count and add to our ics thingy 

            # add that sum to keep track if we hit a duplicate this also helps keep track of unqiue urls (non duplicate urls) 

    def run(self):
        while True:
            
            tbd_url = self.frontier.get_tbd_url()
            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.")
                if self.worker_id == 0: # only one worker can print to freq_words.txt
                    file_path = 'freq_words.txt'
                    file_path2 = 'justics.txt'
                    file_path3 = "unquie_links.txt"
                    # print the number of unqiue urls 
                    print(f"Unqiue links: {len(self.UniqueUrls)}")
                    
                    # print the url with most words 
                    print(f"largest site: {self.most_content}")
                    
                    with open(file_path, 'w') as file:
                            # write words in largest to smallest order 
                        for key, value in sorted(self.word_dict.items(), key=lambda x: x[1], reverse= True):
                            file.write(f"{key}: {value}\n")

                    with open(file_path2, 'w') as file:
                            # write ics domains alpha betically
                        for key, value in sorted(self.JustICS.items(), key=lambda x: x[0]):
                            file.write(f"{key}: {value}\n")

                    with open(file_path3, 'w') as file:
                            # write ics domains alpha betically
                        for item in self.UniqueUrls:
                            file.write(f"{item} \n")
                break
            resp = download(tbd_url, self.config, self.logger)
            self.logger.info(
                f"Downloaded {tbd_url}, status <{resp.status}>, "
                f"using cache {self.config.cache_server}.")

            if resp.status == 200: # confirm status real quick
                self.parse_text(tbd_url, resp) # parse the text and add it to our dict, and add a checksum hash to the url dict too 
            scraped_urls = scraper.scraper(tbd_url, resp)

            self.get_subdomain(tbd_url, scraped_urls) # check the sub domain of ics 
            # check the url if its of ics type, we take the scraped urls (uci.edu type and sort it into a fucniton )
            for scraped_url in scraped_urls:
                self.frontier.add_url(scraped_url)

            self.UniqueUrls.add(tbd_url)   # count and add to our ics thingy 

            self.frontier.mark_url_complete(tbd_url) 
            time.sleep(self.config.time_delay)
