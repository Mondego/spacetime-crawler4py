import re, shelve, urllib
from collections import defaultdict
from bs4 import BeautifulSoup
from urllib.parse import urlparse


allowed_url = ['.+\.cs.uci.edu/.*', '.+\.ics.uci.edu/.*', '.+\.informatics.uci.edu/.*', '.+\.stat.uci.edu/.*', 'today.uci.edu/department/information_computer_sciences/.*']
allowed_url = [re.compile(x) for x in allowed_url]

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]


def extract_next_links(url, resp):
    links = []
    if 200 <= resp.status <= 599 and resp.raw_response != None:
        bsObj = BeautifulSoup(resp.raw_response.content, 'html.parser')
        try:
            url_list = shelve.open('urlText.db')
            un_url = url.split("#")[0]
            # get text on the url and write into db
            text = re.findall(r'^\w+$', bsObj.get_text().strip().lower())
            if un_url not in url_list:
                url_list[un_url] = text

            t1 = bsObj.find_all('a')
            for t2 in t1:
                if(t2.get('href') != None and t2.get('href') not in url_list):
                    links.append(t2)

        finally:
            url_list.close()
        
    return links


def containHugeNum(path):
    return re.match('^\d+$', path)
def containDummyWord(path):
    if path.find("comment") != -1 or path.find("respond") != -1 or path.find("reply") != -1:
        return True

def is_valid(url):
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        elif len(parsed.path.split('/')) > 20:
            return False
        elif containHugeNum(url):
            return False
        elif containDummyWord(url):
            return False
        else:
            if not any([i.match(url) for i in allowed_url]):
                return False
            
        The_path = parsed.path.split("/")
        pass_dict = defaultdict(int)
        
        for i in The_path:
            pass_dict[i] += 1
            
            if pass_dict[i] > 3:
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