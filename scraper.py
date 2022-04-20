import re
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from crawler.frontier import *
import configparser
from utils.config import *

# from Queue import Queue
from utils.response import Response

def scraper(url: str, resp: Response) -> list:
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url: str, resp: Response):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content

    # 1. need to take care of web traps
    #   -i.e runs infinite (calendars)
    #       -Web server responds with ever changing URLs and content. dynamic pages
    #   -avoid pages with low information value. have to set value ourselves. explain in interview
    #   -duplicates
    #   -Some webadmins can create traps to penalize impolite crawlers
    #   -dynamic pages
    #   -data noise
    #       Web pages have content not directly related to the page
    #           –Ads, templates, etc
    #           –Noise negatively impacts information retrieval
    # 2. check for politeness. how many times visited per time unit
    # 3. Does it exist in Prof. Lopes' Web cache server logs?
    # 4. Did you crawl ALL domains and paths mentioned in the spec?
    #                    !!!!   AND   !!!! 
    #      Did it crawl ONLY the domains and paths mentioned in the spec?

    # q = Queue(maxsize = 0)
    # q.put(resp.url)
    # while(!q.empty()):    

        
            
    return list()

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        # raise

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read("config.ini")
    c = Config(config)
    frontier = Frontier(c, False)
    frontier.add_url("https://www.ics.uci.edu")
    print("Frontier size:", len(frontier.to_be_downloaded))
    print(frontier.to_be_downloaded)