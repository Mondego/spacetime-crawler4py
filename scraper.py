import re
from urllib.parse import urlparse
import utils.response
from bs4 import BeautifulSoup
from urllib.parse import urldefrag
from simhash import Simhash, SimhashIndex
import requests
from utils.response import Response
import cbor


class Scrape():

    def __init__(self,config):
        self.config = config
        self.host, self.port = config.cache_server
        self.robots = {}
        self.simhashes = SimhashIndex([])
        self.link = 1

    def scraper(self,url:str, resp: utils.response.Response) -> list:
        links = self.extract_next_links(url,resp)
        return links


    def extract_next_links(self,url, resp) -> list:
        
        blackList = ['[document]', 'noscript', 'header', 'html', 'meta', 'head', 'input', 'script', 'style', 'b', 'button']

        links = set() # make it a set so it checks duplicates after removing the fragment
        if (200 <= resp.status <= 599)  and resp.status != 204:
            soup = BeautifulSoup(resp.raw_response.content, "lxml")

            if resp.status == 200 and soup.prettify() == '':  # avoid dead URLs that return a 200 status but no data
                return []
            
            output = " "

            text = soup.find_all(text=True)

            for t in text:
                if t.parent.name not in blackList:
                    output += '{} '.format(t)

            simh = Simhash(output)

            if len(self.simhashes.get_near_dups(simh)) != 0:
                return []
            else:
                for link in soup.findAll('a'):
                   if self.is_valid(link.get('href')):
                        # remove the fragment here
                       unfragmented = urldefrag(link.get('href'))
                       links.add(unfragmented.url)
            self.simhashes.add(self.link,simh)
            self.link += 1
            return list(links)
        return list(links)
        
    def is_valid(self,url):
        try:
            parsed = urlparse(url)
            if parsed.scheme not in set(["http", "https"]):
                return False

            not_crawling_patterns = (r".*\.(css|js|bmp|gif|jpe?g|ico"
                                     r"|png|tiff?|mid|mp2|mp3|mp4"
                                     r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
                                     r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
                                     r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
                                     r"|epub|dll|cnf|tgz|sha1"
                                     r"|thmx|mso|arff|rtf|jar|csv"
                                     r"|rm|smil|wmv|swf|wma|zip|rar|gz)$")

            not_crawling_path_patterns = (r".*/?(css|js|bmp|gif|jpe?g|ico"
                                     r"|png|tiff?|mid|mp2|mp3|mp4"
                                     r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
                                     r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
                                     r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
                                     r"|epub|dll|cnf|tgz|sha1"
                                     r"|thmx|mso|arff|rtf|jar|csv"
                                     r"|rm|smil|wmv|swf|wma|zip|rar|gz).*$")

            if(re.match(not_crawling_patterns, parsed.path.lower()) or re.match(not_crawling_path_patterns, parsed.path.lower())):  # check if the path has the patterns
                # ex: https://www.informatics.uci.edu/files/pdf/InformaticsBrochure-March2018
                    return False

            if(re.match(not_crawling_patterns, parsed.query.lower())):  # also need to check if the query has the patterns
                # ex: http://sli.ics.uci.edu/Classes/2011W-178?action=download&upname=HW2.pdfcle
                return False

            if(re.match(
                r".*\.ics\.uci\.edu\/?.*|.*\.cs\.uci\.edu\/?.*|.*\.informatics\.uci\.edu\/?.*|.*\.stat\.uci\.edu\/?.*"
                + r"|today\.uci\.edu\/department\/information_computer_sciences\/?.*$"
                ,parsed.netloc.lower() )):
                if (len(parsed.geturl()) <= 200):  # any links bigger than 200 will be discarded
                    #code from utils.download
                    print(f"{parsed.scheme}{parsed.netloc}")
                    resp = requests.get(
                            f"http://{self.host}:{self.port}/",
                            params=[("q", f"{parsed.scheme}{parsed.netloc}"), ("u", f"{self.config.user_agent}")])
                    if resp:
                        print(Response(cbor.loads(resp.content)))
                        #print(x.raw_response.content.decode())
                    else:
                        print("Failure")
                    
                    return True
                        
                return False


        except TypeError:
            print ("TypeError for ", parsed)
            raise
