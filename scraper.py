import re
from urllib.parse import urldefrag, urlparse
from bs4 import BeautifulSoup as BS
from report import Report
from utils.response import Response


def scraper(url, resp, report: Report):
    links = extract_next_links(url, resp)

    # count the total number of words in this page and save the total if it's
    # higher than the previous max
    report.count_total_page_words(url, resp)

    # count the frequency of each word in every page and add it to a dictionary
    # for reporting the 50 most common words in the entire set of pages
    report.count_each_page_word(url, resp)

    # Count the number of unique pages
    # A unique page is defined by removing # and all subsequent characters from a link
    report.count_unique_page(url, resp)

    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp: Response):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    url_list = []
    if 200 <= resp.status <= 206:
        html = BS(resp.raw_response.content, 'html.parser')
        anchors = html.find_all('a')               # get all <a> tags
        for href in anchors:
            found_url = href.get('href')          # get the actual link
            useless = check_useless(found_url)
            if found_url != url and not useless:
                url_list.append(found_url)
            # remove_useless_pages(url_list)
        return url_list
    return list()


def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        #or parsed.hostname not in set(["www.ics.uci.edu","www.cs.uci.edu/","www.informatics.uci.edu/", "www.stat.uci.edu/" ])
        #looks throught to make sure the domain is one of the ones we are supposed to be in. Will also filter out comment sections so that they are not valid urls to look at. 
        if parsed.scheme not in set(["http", "https"]) or not re.search('ics.uci.edu|cs.uci.edu|informatics.uci.edu|stat.uci.edu', parsed.netloc) or re.match('comment|respond', parsed.fragment):
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

# useless pages - 
# 1) page with query
# 2) 
def check_useless(url):
    if '?' in str(url): 
        return True
