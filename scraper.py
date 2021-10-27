import re
from urllib.parse import urlparse
from lxml import html

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    if(resp.status == 200):
        str = html.fromstring(resp.raw_response.content)
        myList = list(i[2] for i in str.iterlinks())
        return myList
    return list()

def is_valid(url):
    try:
        parsed = urlparse(url)
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
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower()) and re.match(r".*(\.ics\.uci\.edu|\.cs\.uci\.edu"
            + r"|\.informatics\.uci\.edu|\.stat\.uci\.edu"
            + r"|\.today\.uci\.edu\/department\/information_computer_sciences)", parsed.netloc.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise