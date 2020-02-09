import re
from urllib.parse import urlparse
import utils.response
from bs4 import BeautifulSoup
from urllib.parse import urldefrag


def scraper(url:str, resp: utils.response.Response) -> list:
    links = extract_next_links(url,resp)
    return links
     

def extract_next_links(url, resp) -> list:
    links = set() # make it a set so it checks duplicates after removing the fragment
    if (200 <= resp.status <= 599)  and resp.status != 204:
        soup = BeautifulSoup(resp.raw_response.content, "lxml")
        
        if resp.status == 200 and soup.prettify() == '':  # avoid dead URLs that return a 200 status but no data
            pass
        else:
            for link in soup.findAll('a'):
               if is_valid(link.get('href')):
                    
                    # remove the fragment here
                   unfragmented = urldefrag(link.get('href'))
                   links.add(unfragmented.url)
    return list(links)
    
def is_valid(url):
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False

        if( re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())): # need to check if other parts have these toos
                return False

        # print(parsed.netloc.lower())
        if(re.match(
            r".*\.ics\.uci\.edu\/?.*|.*\.cs\.uci\.edu\/?.*|.*\.informatics\.uci\.edu\/?.*|.*\.stat\.uci\.edu\/?.*"
            + r"|today\.uci\.edu\/department\/information_computer_sciences\/?.*$"
            ,parsed.netloc.lower() )):
            if (len(parsed.geturl()) <= 200):  # any links bigger than 200 will be discarded
                return True

        return False

    except TypeError:
        print ("TypeError for ", parsed)
        raise
