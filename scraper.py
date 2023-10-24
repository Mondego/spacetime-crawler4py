import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup

# Seed URL : 

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

    actual_url = resp.url

    if resp.status == 200:
        soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
        links = [link.get('href') for link in soup.find_all('a')]
        links = [urlparse(url, link) for link in links]
    else:
        print(resp.error)

    return list()

def is_valid(url):
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False

        # List of disallowed file extensions
        invalid = [
            "css", "js", "bmp", "gif", "jpg", "jpeg", "ico",
            "png", "tif", "tiff", "mid", "mp2", "mp3", "mp4",
            "wav", "avi", "mov", "mpeg", "ram", "m4v", "mkv", "ogg", "ogv", "pdf",
            "ps", "eps", "tex", "ppt", "pptx", "doc", "docx", "xls", "xlsx", "names",
            "data", "dat", "exe", "bz2", "tar", "msi", "bin", "7z", "psd", "dmg", "iso",
            "epub", "dll", "cnf", "tgz", "sha1", "thmx", "mso", "arff", "rtf", "jar", "csv",
            "rm", "smil", "wmv", "swf", "wma", "zip", "rar", "gz"
        ]

        # List of valid domains we can crawl in
        domains = ["ics.uci.edu", "cs.uci.edu", "informatics.uci.edu", "stat.uci.edu"]

        # Check if the parsed domain matches any of the allowed domains
        domain_match = any(parsed.netloc.endswith("." + domain) or parsed.netloc == domain for domain in domains)

        # Check if the path doesn't have invalid extensions
        extension_match = not any(parsed.path.lower().endswith("." + filetype) for filetype in invalid)

        # return the boolean expression determined by the logical AND of domain_match and extension_match
        # if the url exists in our valid domains and does not fall under any of the invalid extensions, return True, else return False
        return domain_match and extension_match

    except TypeError:
        print("TypeError for ", parsed)
        raise

# DRIVER

test_urls = [
    "https://www.ics.uci.edu/page",
    "http://cs.uci.edu/page",
    "https://informatics.uci.edu/page",
    "https://stat.uci.edu/page",
    "https://www.google.com/page",
    "ftp://invalid-url.com/ftp-page",
    "https://www.linkedin.com/feed/",
    "https://drive.google.com/drive/u/0/my-drive",
    "https://www.youtube.com/watch?v=_ITiwPMUzho&ab_channel=LofiGhostie",
    "https://www.youtube.com/watch?v=TUEju_i3oWE&ab_channel=Insomniac",
    "https://github.com/gregkhanoyan/IR23F-A2-G33#things-to-keep-in-mind",
    "https://canvas.eee.uci.edu/courses/58552/assignments/1243743",
    "https://ics.uci.edu/academics/undergraduate-academic-advising/",
    "https://ics.uci.edu/academics/undergraduate-academic-advising/change-of-major/"
]

for url in test_urls:
    if is_valid(url):
        print(f"{url} is a valid URL for crawling.")
    else:
        print(f"{url} is not a valid URL for crawling.")