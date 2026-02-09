import re
from urllib.parse import urlparse, urljoin, urldefrag
from bs4 import BeautifulSoup
from analytics import record_page

def scraper(url, resp):
    if resp.status == 200 and resp.raw_response and resp.raw_response.content:
        record_page(resp.url, resp.raw_response.content)

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
    #checks if the page was recieved
    if resp.status != 200 or not resp.raw_response:
        return []
    
    hyperlinks = set() # Use a set to prevent adding the same link twice per page
    try:
        soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
        for anchor in soup.find_all('a'):
            href = anchor.get('href')
            if href:
                # Resolve relative links (e.g., '/about') into full URLs
                full_url = urljoin(url, href)
                # Requirement: Remove the fragment part of the URL
                clean_url = urldefrag(full_url)[0]
                hyperlinks.add(clean_url)
    except Exception as e:
        print(f"Error extracting links from {url}: {e}")
        
    return list(hyperlinks)

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        if not url or len(url) > 300:
            return False

        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        
        allowed_domains = [".ics.uci.edu", ".cs.uci.edu", 
                           ".informatics.uci.edu", ".stat.uci.edu"]
        if not any(parsed.netloc.endswith(d) for d in allowed_domains):
            return False
        
        if re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico|png|tiff?|mid|mp2|mp3|mp4|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1|thmx|mso|arff|rtf|jar|csv|rm|smil|wmv|swf|wma|zip|rar|gz)$", 
            parsed.path.lower()):
            return False
        
        if re.search(r'(/[^/]+)\1{2,}', parsed.path):
            return False
        
        if len(parsed.path.split('/')) > 10:
            return False
        
        if re.search(r'(action|do|rev|format|timeline)=(diff|history|edit|old|revisions|admin|txt|raw)', (parsed.query.lower() + parsed.path.lower())):
            return False

        if any(keyword in url.lower() for keyword in ["calendar", "wp-content", "login"]):
            return False
        
        return True

    except Exception as e:
        print(f"Validation error for {url}: {e}")
        return False

