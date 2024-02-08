#Test
import re
from urllib.parse import urlparse

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    urlStr = urlparse(url).geturl
    reExp = ""
    allLinks = re.match(reExp, resp.raw_response.content)
    for l in allLinks:
        if not (is_valid(l)):
            allLinks.remove(l)
    

    re.match(".ics.uci.edu/")

    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page! 
    # we will use the beautifulSoup to get the html content
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    return list()

def helper(url):
    if (".ics.uci.edu/" in urlparse(url).geturl) or (".cs.uci.edu/" in urlparse(url).geturl) or (".informatics.uci.edu/" in urlparse(url).geturl)  or (".stat.uci.edu/" in urlparse(url).geturl):
        return True
    else:
        return False

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
#         *.ics.uci.edu/*
# *.cs.uci.edu/*
# *.informatics.uci.edu/*
# *.stat.uci.edu/*
        if parsed.scheme not in set(["http", "https"]) or not(helper(url)) :
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
