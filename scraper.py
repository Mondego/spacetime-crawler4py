import re
from urllib.parse import urlparse
from urllib.parse import urljoin
from bs4 import BeautifulSoup

Blacklist = set()
Visited = set()

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
    nextLinks = set()
    global Blacklist
    global Visited

    #temporary
    #if resp.status != 200:
    #    print(resp.error)
    
    # If status is bad or link already visited add it to a blacklist to avoid
    if(resp.status != 200 or url in Blacklist or url in Visited):
        Blacklist.add(url)
        return ()

    soup = BeautifulSoup(resp.raw_response.content, "html.parser")
    for link in soup.find_all('a'):
        href = link.attrs.get('href')

        # If link is relative make it absolute
        if bool(urlparse(url).netloc):
            href = urljoin(url, href)
        
        # Stop duplicates of same link by splitting 
        # (ex #ref40, #ref45 etc of same link)
        # not sure if including '?' is necessary, neef further testing
        href = href.split('#')[0]
        href = href.split('?')[0]

        if is_valid(href):
            nextLinks.add(href)

    # Add current url to list of visited urls so we don't end up visiting already visited links
    parsed = urlparse(url)
    Visited.add(parsed.scheme + '://' + parsed.netloc + parsed.path)
    return nextLinks

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    global Visited

    try:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            return False

        # Make sure link is in provided domain constraints
        if parsed.netloc not in {"www.ics.uci.edu", "www.cs.uci.edu", "www.informatics.uci.edu", "www.stat.uci.edu", "www.today.uci.edu"}:
            return False
        if parsed.netloc == "www.today.uci.edu" and parsed.path != "/department/information_computer_sciences/":
            return False

        # Regex expression to not allow repeating directories
        # Source: https://support.archive-it.org/hc/en-us/articles/208332963-Modify-crawl-scope-with-a-Regular-Expression
        # Note: Not yet sure if this is working or not, will need more testing
        # Seems to work better with 'r' than without (or work in general, not sure)
        if re.match(r"^.*?(/.+?/).*?\1.*$|^.*?/(.+?/)\2.*$", parsed.path):
            return False
        
        if re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz"
            # Added 
            + r"img|sql)$", parsed.path.lower()):
            return False

        if url in Visited or url in Blacklist:
            return False

        return True
        

    except TypeError:
        print ("TypeError for ", parsed)
        raise