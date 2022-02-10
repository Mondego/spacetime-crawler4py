import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link, url)]


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
        print(f"ERROR {resp.status} downloading {resp.url}")
        return []

    soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
    found_links = soup.find_all('a', href=True)
    links = []

    for link in found_links:
        l = link["href"]

        # probably ineficient way to find fragments, but should work?
        # removing the stuff after the fragment means:
        # https://domain.com/path
        # https://domain.com/path#1 --> https://domain.com/path
        # but since frontier doesn't add duplicate URLs, we won't add the 2nd URL
        
        ind = l.find('#')
        if ind != -1:
            links.append(l[:ind])
        else:
            links.append(l)

    return links


def is_valid(url, oldUrl = None):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)

        if parsed.scheme not in {"http", "https"}:
            return False

        if not re.match(r".*\.(ics|cs|informatics|stat|today)\.uci\.edu$", parsed.hostname):
            return False

        # note that today.uci.edu is an exact match for the hostname, while the other hostnames can be different 
        # ie: "vision.ics.edu" and "hello.ics.edu" are both valid vs just "today.uci.edu"
        if parsed.hostname == "www.today.uci.edu" and not \
            re.match(r"^/department/information_computer_sciences/", parsed.path):
            return False

        # this clause makes sure that the new url is not exactly the same except for a different query parameter
        # note that oldUrl has a default value None and so this check will not be run if no oldUrl value is passed in
        if oldUrl != None:
            # in the case that a page with query param is linked from another page with query param
            if "=" in oldUrl and "?" in oldUrl and "=" in url and "?" in url:
                if oldUrl.split("=")[1] == url.split("=")[1]:
                    print("page duplicate: ", url, " ", oldUrl)
                    return False
            # in the case that a page with query param is linked from a base url
            elif "?" in url and "=" in url:
                if oldUrl == url.split("?")[0] or oldUrl+"/" == url.split("?")[0]:
                    print("page duplicate: ", url, " ", oldUrl)
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
        # raise
        return False
