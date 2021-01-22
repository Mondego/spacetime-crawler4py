import re
from bs4 import BeautifulSoup as bs4
from urllib.parse import urlparse

def scraper(url, resp):
    _print_page_links(resp)
    # _print_page_text(resp)
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    return list()

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

def _get_soup(resp):
    page_text = resp.raw_response.text
    soup = bs4(page_text, 'html.parser')
    return soup

def _print_page_links(resp):
    soup = _get_soup(resp)

    for link in soup.find_all('a'):
        print(link.get('href'))


def _print_page_text(resp):
    soup = _get_soup(resp)

    for p_elem in soup.find_all('p'):
        print(p_elem.get_text())
