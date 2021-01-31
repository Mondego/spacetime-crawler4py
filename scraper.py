import re, shelve, urllib
from urllib.parse import urlparse
from urllib.request import urlopen
from utils.response import Response
from bs4 import BeautifulSoup
from collections import defaultdict

# global variable for regular expression
allowed_url = ['.+\.cs.uci.edu/.*', '.+\.ics.uci.edu/.*', '.+\.informatics.uci.edu/.*', '.+\.stat.uci.edu/.*', 'today.uci.edu/department/information_computer_sciences/.*']
allowed_url = [re.compile(x) for x in allowed_url]

def scraper(url: str, resp: Response) -> list:
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]


def extract_next_links(url, resp):
    links = []
    # get links from resp
    if 200 <= resp.status <= 599 and resp.raw_response != None:
        soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
        # Store text and url to shelve
        try:
            url_list = shelve.open('urlText.db')
            un_url = url.split('#')[0]

            all_word = re.sub(r'[^A-Z^a-z^0-9^ ]', '', soup.get_text().strip().lower())

            if un_url not in url_list:
                url_list[un_url] = all_word

            for link in soup.findAll('a'):
                if link.get('href') is not None:
                    if link.get('href') not in url_list:
                        links.append(link.get('href'))  
                    
        finally:
            url_list.close()

    return links

def is_valid(url):
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        elif len(parsed.path.split('/')) > 20:
            return False
        else:
            if not any([i.match(url) for i in allowed_url]):
                return False
            
        The_path = parsed.path.split("/")
        pass_dict = defaultdict(int)
        
        for i in The_path:
            if "pdf" in i or "img" in i or re.match('[0-9]+', i) or re.match('[0-9]+-[0-9]+-[0-9]+',i):
                return False
            pass_dict[i] += 1
            
            if pass_dict[i] > 4:
                return False
            
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz|ppsx)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise
