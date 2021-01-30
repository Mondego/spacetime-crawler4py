import re
import shelve
from collections import defaultdict
from urllib.request import urlopen
from bs4 import BeautifulSoup

from urllib.parse import urlparse

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    links = []
    if 599 >=resp.status >= 200 and resp.raw_response != None:
        bsObj = BeautifulSoup(resp.raw_response, 'html.parser')
        try:
            with shelve.open('store_url') as db:
                un_url = url.split("#")[0]
                # get text on the url and write into db
                text = re.findall(r'^\w+$', resp.raw_response.strip().lower())
                if un_url not in db:
                    db[un_url] = text

                t1 = bsObj.find_all('a')
                for t2 in t1:
                    if(t2.get('href') != None and t2.get('href') not in links):
                        links.append(t2)

        finally:
            db.close()
    return links


def containHugeNum(path):
    return not re.match('^\d+$', path)

def is_valid(url):
    seeds = ['.+\.cs.uci.edu/.*',
             '.+\.ics.uci.edu/.*',
             '.+\.informatics.uci.edu/.*',
             '.+\.stat.uci.edu/.*',
             'today.uci.edu/department/information_computer_sciences/.*']
    seeds = [re.compile(i)for i in seeds]
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        if len(parsed.path.split('/')) > 20:
            return False
        if not any([i.match(i) for i in seeds]):
            return False
        the_path = parsed.path.split('/')
        path_dict = defaultdict(int)

        for i in the_path:
            if containHugeNum(i.lower()):
                return False
            path_dict[i] +=1
            if path_dict[i] >=4:
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
        raise