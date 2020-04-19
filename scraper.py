import re
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup

visitedURLs = {}  #set of already crawled urls

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    # Implementation requred.
    extractedLinks = [] 
    
    #create main domain for incomplete extracted links
    parsed = urlparse(url)
    linkDomain = parsed.scheme + "://" + parsed.netloc
    
    # only crawl valid urls with status 200-299 OK series
        #https://developer.mozilla.org/en-US/docs/Web/HTTP/Status
    
    # we don't necessarily need to check if the url is valid in this stage
    # since is_valid will then be called on the links in extractedLinks
    
    # we don't need to check if its already been visited because
    # the politeness aspect is already set up for us.
    
    if resp.status >= 200 and resp.status <= 299:
        # use beautiful soup here to get html content
        html_content = resp.raw_response.content
        soup = BeautifulSoup(html_content, 'html.parser')

        # findall urls listed on this html doc
        for link in soup.findall('a', href=True):
            tempLink = link.get('href')
            # link may be incomplete - but!! it may be a complete link
            # to a different domain, so let's check if it's a path first
            # by checking if its an "absolute" url or a "relative" url
            #       https://html.com/anchors-links/#Absolute_vs_Relative_URLs
            if tempLink.startswith("http"):     # absolute url will always have scheme
                completeLink = tempLink
            else:                               # relative url - always relative to the base url so
                completeLink = urljoin(url, tempLink)       # we can simply urljoin  with original url
                
            extractedLinks.append(completeLink)
                
            # save (write) data to text files while crawling for report data
                    
    return extractedLinks

def is_valid(url):
    try:
        # remove fragment
        url = url.split("#", 1)[0]
        parsed = urlparse(url)
        
        if parsed.scheme not in set(["http", "https"]):
            return False
        
        checkext = not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())
        
        # check if domain/path matches requirements
        checkdomain = (re.match(r"(www.)?[-a-z0-9.]*\.ics\.uci\.edu", parsed.hostname) or \
            re.match(r"(www.)?[-a-z0-9.]*\.cs\.uci\.edu", parsed.hostname) or \
            re.match(r"(www.)?[-a-z0-9.]*\.informatics\.uci\.edu", parsed.hostname) or \
            re.match(r"(www.)?[-a-z0-9]*\.stat\.uci\.edu", parsed.hostname) or \
            (re.match(r"(www.)?today\.uci\.edu", parsed.hostname) and \
            (re.match(r"\/department\/information_computer_sciences\/.*", parsed.path))))
        
        if checkext and checkdomain:
            return True
        else:
            return False

    except TypeError:
        print ("TypeError for ", parsed)
        raise
