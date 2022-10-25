import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from urllib.parse import urljoin
from urllib.parse import urldefrag

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    if resp.status != 200:
        print("Error in getting url, code:", resp.status)
        return list()

    ret = list()
    soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
    links =  soup.findAll("a")
    for link in links:
        href = link.get('href')
        href = urldefrag(href)[0] # assume we want to remove fragments
        href = urljoin(url, href) #join for relative URLS
        parse = urlparse(href)
        if is_valid(href) == True:
            #print("Valid url:",href, "domain:", parse.hostname, "protocol:", parse.scheme)
            #ret.append(link_url)
            print(end="")
        else:
            print("Invalid url:",href, "domain:", parse.hostname, "protocol:", parse.scheme)

    
      
    return ret

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        # https://docs.python.org/3/library/urllib.parse.html
        # scheme://netloc/path;parameters?query#fragment
        parsed = urlparse(url)
        if isBadDomain(parsed.hostname):
            return False
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

def isBadDomain(domain):
    domains = ["www.ics.uci.edu", "www.cs.uci.edu", "www.informatics.uci.edu" ,"www.stat.uci.edu"]
    if domain in domains:
        return False
    #print("Wrong domain:", domain)
    return True