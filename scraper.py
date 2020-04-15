import re
from urllib.parse import urlparse
import urllib.request
from bs4 import BeautifulSoup

    #For tokenizing 
dec_values = set()
dec_values.update(range(48,57+1))
dec_values.update(range(65,90+1))
dec_values.update(range(97,122+1))

#Pages found
unique_pages = set()

    #Longest page in terms of words
longest_page = dict()

    #Common words
common_words = dict()

    #Subdomains of ics.uci.edu
subdomains = 0

    #All results ?
all_results = dict()

def tokenize(html):
    tokens = []
    for line in html:
        line = str(line)
        for word in re.split("[\s;,\-\n.?']",line):
            if len(word) > 1:
                word = word.lower()
                val = checkalnum(word)
                if val:
                    tokens.append(word)
    return tokens


def checkalnum(word):
    for i in range(len(word)):
        if ord(word[i]) not in dec_values:
            return False
    return True

def scraper(url, resp):
    links = extract_next_links(url, resp)
    if is_valid(url):
        tokens = tokenize(resp)
        all_results[url] = tokens
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    #res = urllib.request.urlopen(url)
    #html = res.read()
    soup = BeautifulSoup(resp,features='lxml')
    links = soup.find_all('a',attrs={'href': re.compile("^https://|^http://")})
    return links

def is_valid(url):
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
        raise


