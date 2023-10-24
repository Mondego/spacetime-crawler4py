import re
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup

# Seed URL: http://www.ics.uci.edu






def scraper(url, resp):
    # list of valid links
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

    # parse the web response, 'resp', extract information from here answering deliverable questions
    # return list of URL's scrapped from that page
    #   return only valid URL's
    #   defragment URL's (remove fragment)
    #   use library (BeautifulSoup, lxml)





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

    # retrieving final page URL after redirects - keep this Greg for testing/matching after implementation
    # actual_url = resp.url

    link_list = []

    # checking if we actually got the page
    if resp.status == 200:
        try:
            # use BeautifulSoup library to parse the HTML content of the page
            soup = BeautifulSoup(resp.raw_response.content, 'html.parser')

            # in the HTML, we want to find all '<a>' tags and extract the link, the 'href'
            for curr in soup.find_all('a'):
                link = curr.get('href')
                if link:
                    # we then use 'urllib.parse' in order to combine the relative URL's with our base URL in order to get our final URL
                    final_url = urljoin(url, link)

                    # checks validity of our final_url - if it is valid, then we can add it to our list of links
                    if is_valid(final_url):
                        link_list.append(final_url)

        except Exception as e:
            print(f"ERROR: Error parsing {url}: {str(e)}")       
    # if the response code was something other than 200, means there was an error - print it so we can see
    else:
        print(f"Error {resp.status} for {url}: {resp.error}")

    return link_list


# FUNCTION: is_valid(url) - checks the validity of a URL:str passed in - returns a boolean True or False
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

# DRIVER CODE

# test_urls = [
#     "https://www.ics.uci.edu/page",
#     "http://cs.uci.edu/page",
#     "https://informatics.uci.edu/page",
#     "https://stat.uci.edu/page",
#     "https://www.google.com/page",
#     "ftp://invalid-url.com/ftp-page",
#     "https://www.linkedin.com/feed/",
#     "https://drive.google.com/drive/u/0/my-drive",
#     "https://www.youtube.com/watch?v=_ITiwPMUzho&ab_channel=LofiGhostie",
#     "https://www.youtube.com/watch?v=TUEju_i3oWE&ab_channel=Insomniac",
#     "https://github.com/gregkhanoyan/IR23F-A2-G33#things-to-keep-in-mind",
#     "https://canvas.eee.uci.edu/courses/58552/assignments/1243743",
#     "https://ics.uci.edu/academics/undergraduate-academic-advising/",
#     "https://ics.uci.edu/academics/undergraduate-academic-advising/change-of-major/"
# ]

# for url in test_urls:
#     if is_valid(url):
#         print(f"{url} is a valid URL for crawling.")
#     else:
#         print(f"{url} is not a valid URL for crawling.")
