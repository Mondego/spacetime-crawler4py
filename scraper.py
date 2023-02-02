import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup

pages = set()

def filter_to_allow_subdomains(parsed):
    return  re.match(r".*\.(stat|ics|cs)\.uci\.edu", parsed.netloc.lower()) or (
                re.match(r"today\.uci\.edu", parsed.netloc.lower()) and
                re.match(r"department/information_computer_sciences/.*", parsed.path.lower())
            )

def scraper(url, resp):
    links = extract_next_links(url, resp)
    # print(links)
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

    # Return empty list if 600+ error(maybe want to change for a more specific status code filtering mechanism)
    # if resp.status > 600:
    #     return list()
    new_links = list()
    if resp.status == 200:
        soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
        for link in soup.find_all('a'):
            extracted_link = link.get('href')
            if extracted_link not in pages:
                new_links.append(extracted_link)
                pages.add(extracted_link)
    return new_links

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        
        if re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower()):
            return False
        # print("Matching {} and the regex matching is {}".
        #     format(parsed.netloc.lower(), re.match(r".*\.(stat|ics|cs)\.uci\.edu", parsed.netloc.lower())))
        # return re.match(r".*\.(stat|ics|cs)\.uci\.edu", parsed.netloc.lower())
        return filter_to_allow_subdomains(parsed)

    except TypeError:
        print ("TypeError for ", parsed)
        raise
