import re
from urllib.parse import urljoin, urlparse
import urllib.robotparser
from bs4 import BeautifulSoup
from utils.response import Response


# COMPLETE: filter out urls that are not with the following domains .ics.uci.edu/, .cs.uci.edu/, .informatics.uci.edu/,
                    # .stat.uci.edu/,today.uci.edu/department/information_computer_sciences/
# COMPLETE: make sure to defragment the URLs, i.e. remove the fragment part.
# COMPLETE: crawl all pages with high textual information content - lecture 12
# COMPLETE:  detect and avoid sets of similar pages with no information - lecture 12
# COMPLETE: store UNIQUE urls (based on content) in frontier.py - lecture 11
# COMPLETE: implement robotparser for robots.txt in extract_next_links (EC)
# COMPLETE: transform relative path URLS to absolute path URLS




# TODO: detect and avoid infinite traps - lecture 7
# TODO: add more file extensions to is_valid function
# TODO: Detect and avoid crawling very large files, especially if they have low information value - lecture 12
# TODO: make comments throughout utils.py, frontier.py and scraper.py

# Do we utilize sitemaps????


def scraper(url: str, resp: Response) -> list:
    scraped = extract_next_links(url, resp)
    return scraped

def extract_next_links(url: str, resp: Response):
    """"
    Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content

    url: the URL that was used to get the page
    resp.url: the actual url of the page
    resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    resp.error: when status is not 200, you can check the error here, if needed.
    resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
            resp.raw_response.url: the url, again
            resp.raw_response.content: the content of the page!
    """
    hyperlinks = list()

    if resp.status == 200 and resp.raw_response is not None:
        soup = BeautifulSoup(resp.raw_response.content, "lxml")
        for anchor in soup.find_all("a"):
            if anchor.has_attr("href"):
                parse_href = urlparse(anchor["href"])

                if parse_href != "":
                    link = urljoin(url, anchor["href"]) # transforms relative path to absolute path
                else:
                    link = parse_href.scheme + "://" + parse_href.netloc + parse_href.path 

                if parse_href.query != "": # if there is a query in URL
                    link += "?" + parse_href.query

                if is_valid(link):
                    hyperlinks.append(link) # notice: link does not include fragmnet

    elif resp.status == 200:
        print("Status is not 200 for a URL.")
    elif resp.raw_response is None:
        print("There is no content in found in a URL.")

    return list(set(hyperlinks))

def is_valid(url):
    """
    Decide whether to crawl this url or not.

    Domains and paths to only consider valid:
        *.ics.uci.edu/*
        *.cs.uci.edu/*
        *.informatics.uci.edu/*
        *.stat.uci.edu/*
        today.uci.edu/department/information_computer_sciences/*
    """

    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]): # if scheme does  not have http or https, the url is invalid (return False)
            return False 

        # check robots.txt if permission to parse, continues if so
        if checkrobot(url, parsed) == False:
            print("Cannot crawl according to robot.txt")
            return False
        
        # Updated: 4/29/2022, 9:50 am
        # check if the url length is long, if it is its likely a trap
        if '#' in parsed.geturl() or len(str(parsed.geturl()))> 200:
            return False

        # found regex expressions here: https://support.archive-it.org/hc/en-us/articles/208332943-Identify-and-avoid-crawler-traps-
        traps = not re.match(r"^.*/[^/]{300,}$" # should remove long invalid URLs
                + r"^.*calendar.*$"# removes calendars
                + r"^.*?(/.+?/).*?\1.*$|^.*?/(.+?/)\2.*$" #repeating directories
                + r"^.*(/misc|/sites|/all|/themes|/modules|/profiles|/css|/field|/node|/theme){3}.*$" #extra directories
                + r".*\/20\d\d-\d\d*", parsed.path.lower())  # removes monthly archives

        # url is valid (set to True) if it doesn't have any of below file extensions in the path 
        does_not_include_file_extension = not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names|calendar"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())
        
        # url is valid (set to True) if the domain matches with the domain patterns below
        valid_domain = re.match(r".*\.ics\.uci\.edu|\.cs\.uci\.edu|\.informatics\.uci\.edu|\.stat\.uci\.edu|"
            + r"today\.uci\.edu\/department\/information_computer_sciences", parsed.netloc.lower()) is not None
        
        return does_not_include_file_extension and valid_domain and traps

    except TypeError:
        print ("TypeError for ", parsed)
        raise
    
def checkrobot(url, parsed):
    """
    Checks if a url's robot.txt allows for crawling or not.

    Creates the location to the robots.txt for each site and names it urlrobot,
    then requests to access it and if no error then it reads the robot.txt
    If allowed to fetch, returns true, else false
    """
    try:
        urlrobot = "http://" + parsed.netloc + "/robots.txt"
        robotparser = urllib.robotparser.RobotFileParser()
        robotparser.set_url(urlrobot)
        robotparser.read()
        if not robotparser.can_fetch("*", url):
            return False
    except:
        # if there are no robots.txt for the website, return false
        pass


if __name__ == "__main__":
    url_test = "http://sli.ics.uci.edu/Classes/2015W-273a.pdf?action=download&upname=06-vcdim.pdf"
    print(is_valid(url_test))
