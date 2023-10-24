import re
import requests
from urllib.parse import urlparse, urljoin, urldefrag
from bs4 import BeautifulSoup

# Seed URL: http://www.ics.uci.edu

"""
    EXPLANATION:

    Currently, the driver code at the bottom first takes a list of URL's to test. The first marked portion of those URL's
    are invalid URL's used to test the 'is_valid(url)' function, which works as so:

    is_valid(url):
        The function takes a URL 'url' of type string. It then parses the URL into a URL scheme object, which basically means it is now an object with
        recognized URL structure, 'parsed'. We check if it is not an 'http' or 'https' URL, and if it is not, we return False.

        Next, we recognize a list of invalid filetype extensions we want to ignore, which was provided in the skeleton code. We also recognize a list of
        valid domains we can crawl in. These are the ones provided to us by the assignment specifications. 

        We then check whether or not the parsed URL object we created, 'parsed' contains the valid domains we can crawl in. We do this by checking the network
        location aspect of the URL, 'netloc', and checking if it ends with .'domain', or if it simply exists here, whatever the valid domain in this case may be.
        We do the same for checking if any extensions are invalid.

        Next, we return the boolean expression determined by the logical AND of domain_check and extension_check. 
        If the url exists in our valid domains and does not fall under any of the invalid extensions, return True, else return False.
     
    The driver code iterates through each URL in the testing list and uses the 'requests' library to retrieve a 'Response' object, which we need for our HTML parsing.
    We pass this 'Response' object, 'resp' and a string URL 'url', into the 'extract_next_links(url, resp)' function, which works as so:

    extract_next_links(url, resp):
        We first create an empty list to store our list of links, 'link_list'. We then check for a valid status code of 200, which means we successfully retrieve the
        page we want. 
        
        Next we use the BeautifulSoup library to parse the request HTML, using 'resp.text' as our source parameter to be parsed through. Our goal of this
        function is to extract every link from this webpage, so we need to find every element in the HTML with an <a> tag, as that corresponds to an href (HTML hyperlink).
        For every <a> tag, we want to return the corresponding href. 
        
        We then 'urllib.parse: urljoin' in order to combine the relative URL's with our base URL in order to get our final URL (a bit confused on this, need more 
        explanation on what this means lmao). 

        We then defragment the URL, that is, remove everything after any "#" characters in the URL, as we ignore fragments for this assignment.

        Finally, we check the validity of our final URL, by using the 'is_valid(url)' function. If the URL is valid, we can append it to our list of URL's, 'link_list'.

        We check for errors and finally return our list of links/URL's, extracting from each page/URL we are parsing, as 'link_list'.

    We then print all of the links just to see our code in action and ensure everything looks good.
    We also print whether or not a link is valid and can be crawled.

    NEED TO DO:

    - deal with duplicate links in extract_next_links(url, resp) function
    - everything else lmao

"""

def scraper(url, resp):
    # list of valid links
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

    # NEED TO
    # parse the web response, 'resp', extract information from here answering deliverable questions
    # return list of URL's scrapped from that page
    #   return only valid URL's
    #   defragment URL's (remove fragment)
    #   use library (BeautifulSoup, lxml)


def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status_code: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again    
    #         resp.raw_response.content: the content of the page! (NOT CORRECT VARIABLE)
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content

    # retrieving final page URL after redirects - keep this Greg for testing/matching after implementation
    # actual_url = resp.url

    link_list = []

    # checking if we actually got the page
    # do we have to check utf-8 encoding?
    # print(resp.status_code)
    # print(resp.headers)
    if resp.status_code == 200:
        try:
            # use BeautifulSoup library to parse the HTML content of the page
            # print("Raw Content: ", raw)

            soup = BeautifulSoup(resp.text, 'html.parser')
            # print("Parsed Content: ", soup.prettify())

            # in the HTML, we want to find all '<a>' tags and extract the link, the 'href'
            for curr in soup.find_all('a'):
                link = curr.get('href')
                if link:
                    # we then use 'urllib.parse: urljoin' in order to combine the relative URL's with our base URL in order to get our final URL
                    url_joined = urljoin(url, link)

                    # Use 'urllibe.parse: urldefrag' to remove the fragment, as in this assignment we ignore the fragment 
                    if "#" in url_joined:
                        url_joined = urldefrag(url_joined).url
                   
                    final_url = url_joined

                    # checks validity of our final_url - if it is valid, then we can add it to our list of links
                    if is_valid(final_url):
                        link_list.append(final_url)

        except Exception as e:
            print("ERROR: Error parsing " + url + str(e))       
    # if the response code was something other than 200, means there was an error - print it so we can see
    else:
        print("Error: " + str(resp.status_code))

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
        domain_check = any(parsed.netloc.endswith("." + domain) or parsed.netloc == domain for domain in domains)

        # Check if the path doesn't have invalid extensions
        extension_check = not any(parsed.path.lower().endswith("." + filetype) for filetype in invalid)

        # return the boolean expression determined by the logical AND of domain_match and extension_match
        # if the url exists in our valid domains and does not fall under any of the invalid extensions, return True, else return False
        return domain_check and extension_check

    except TypeError:
        print("TypeError for ", parsed)
        raise

# DRIVER CODE

test_urls = [
    # These are all for validity checker
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
    # These are actual links that can be crawled
    "https://ics.uci.edu/academics/undergraduate-academic-advising/",
    "https://ics.uci.edu/academics/undergraduate-academic-advising/change-of-major/",
    "https://grape.ics.uci.edu/wiki/public/wiki/cs122b-2019-winter"
]

for url in test_urls:
    if is_valid(url):
        print("Testing URL: " , url)
        resp = requests.get(url)
        links = extract_next_links(url, resp)
        print("Extracted Links:")
        for link in links:
            print(link)
    else:
        print(url, " is not a valid URL for crawling.")

# for url in test_urls:
#     if is_valid(url):
#         print(f"{url} is a valid URL for crawling.")
#     else:
#         print(f"{url} is not a valid URL for crawling.")


