import re
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from collections import defaultdict

_visitedLinks = defaultdict(int)

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]  #list of links to be added to the Frontier


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
    
    if resp.status != 200: # this means we didn't get the page
        print("u suck")

        return list()
    
  #  print("URL", urlparse(url)== urlparse("https://www.ics.uci.edu"))
    soup = BeautifulSoup(resp.raw_response.content, "html.parser")

    hyperlinks = soup.find_all(href=True) #finds all elements w/ an href
    words = soup.find_all("p")
   # for w in words:
        #print(w.text)
    #print(results.prettify())


    linksToAdd = list()
    for link in hyperlinks:
        if urlparse(link['href']) == urlparse(url): # avoid adding the link that we are currently exploring into the frontier
            print("SAME LINK")
            continue
        if not bool(urlparse(link['href']).netloc) and link['href'] != "#": #not absolute
          #  print(link['href'])
          #  print("NOT ABSOLUTE")
            link = urljoin(url, link['href'])     # convert relative URLs to absolute
           # print("new link", link)
            linksToAdd.append(link)
            _visitedLinks[link] += 1
        else:
            linksToAdd.append(link['href'])
            _visitedLinks[link['href']] += 1
    
   # print("URL", urlparse(url).netloc == urlparse("https://www.ics.uci.edu").netloc)
        #print("RESPONSE", resp.raw_response.content)

    return linksToAdd    #!need a way to remove websites that have already been scraped


def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        if parsed.netloc not in (urlparse("https://www.ics.uci.edu").netloc, urlparse("https://www.cs.uci.edu").netloc, urlparse("").netloc, urlparse("https://www.informatics.uci.edu").netloc, urlparse("https://www.stat.uci.edu").netloc):
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
