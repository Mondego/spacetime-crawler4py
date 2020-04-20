import re
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup

visitedURLs = {}  #set of already crawled urls
uniqueURLs = set()  # set
subDomains = {}  # dict {url hostname, num of unique urls}

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    # Implementation requred.
    extractedLinks = [] 
    
    # only crawl valid urls with status 200-299 OK series
        #https://developer.mozilla.org/en-US/docs/Web/HTTP/Status
    
    # we don't necessarily need to check if the url is valid in this stage
    # since is_valid will then be called on the links in extractedLinks
    
    # we don't need to check if its already been visited because
    # the politeness aspect is already set up for us.
    
    url_counter = 0
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
                
         # before adding a url to dict, check if it's valid, not already crawled, unique
            if is_valid(completeLink):
                # check uniqueness --> remove fragment
                completeLink = completeLink.split("#", 1)[0]

                if completeLink not in uniqueURLs:  #not yet crawled
                    url_counter += 1
                    uniqueURLs.add(completeLink)  #might not need to save these b/c we 
                                                    #just need to specify how many unique urls we found

        # subdomain check
        mainURL = urlparse(url)
        URL_hostname = mainURL.hostname
        if URL_hostname == None:
            URL_hostname = ""
        if re.match(r"(www.)?[-a-z0-9.]+\.ics\.uci\.edu", URL_hostname):
            subDomains[URL_hostname] = url_counter  #stores the number of unique pages found in each subdomain
     
    
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
