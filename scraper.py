import re
import lxml
from bs4 import BeautifulSoup
from urllib.parse import urlparse


def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]


def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page.
    # Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    if resp.status != 200:
        print(f"Error: {resp.error}")
        return None
    links = []
    trap_duration = 10  # Number of seconds to spend in redirects before breaking iterations
    bad_count = 300  # Minimum number of words for "low textual content" pages
    # Should use lxml by default as long as lxml is installed in environment.
    soup_content = BeautifulSoup(resp.raw_response.content)
    for hyperlink in soup_content.find_all('a'):
        hyperlink_href = hyperlink.get('href')
        if not is_valid(hyperlink_href):  # Skip invalid links based on rules set in is_valid()
            continue
        if hyperlink_href == resp.url:  # Skip duplicate links
            continue
        # Check for redirection traps, break loop after trap_duration seconds of redirects.
        # Can change depending on crawler log file output
        try:
            r = requests.head(hyperlink_href, allow_redirects=True, timeout=trap_duration)
            # Skips low content pages
            if r.url == hyperlink_href and len(soup_content.text.strip().split() > bad_count):
                links.append(hyperlink_href)
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            continue
    return links


def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            return False
        if not re.match(r'(?:.+\.(?:i?cs|stat|informatics)\.uci\.edu$)', parsed.netloc):
            return False
        if not re.match(r'^/.*', parsed.path):
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
        print("TypeError for ", parsed)
        raise
