import re
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

def scraper(url, resp):
    # do something with resp
    is_valid(url)
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    # do something with resp
    reqs = requests.get(url)
    soup = BeautifulSoup(reqs.text, 'html.parser')

    urls = []
    for link in soup.find_all('a'):
        # print(link.get('href'))
        urls.append(link.get('href'))
    return urls

def is_valid(url):
    # change to check for base urls
    # come back later: fix parsed.netloc
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False

        # something.ics.uci.edu
        if re.match(r'today.uci.edu', parsed.netloc) and re.match(r'/department/information_computer_sciences/*', parsed.path):
            print("parsed:",parsed)
        if not (re.search(".ics.uci.edu", parsed.netloc) or 
           re.match(r'today.uci.edu/department/information_computer_sciences/*', parsed.netloc)):
            return False
           # re.search(".cs.uci.edu", parsed.netloc) or 
           # re.search(".informatics.uci.edu", parsed.netloc) or 
           # re.search(".stat.uci.edu", parsed.netloc) or 
        
            #return False
        # print("parsed:", parsed)
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
        raise