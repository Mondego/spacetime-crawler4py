import re
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
from bs4 import BeautifulSoup
from utils.response import Response


# COMPLETE: filter out urls that are not with the following domains .ics.uci.edu/, .cs.uci.edu/, .informatics.uci.edu/,
                    # .stat.uci.edu/,today.uci.edu/department/information_computer_sciences/
# COMPLETE: make sure to defragment the URLs, i.e. remove the fragment part.

# TODO: detect and avoid infinite traps - lecture 7
# TODO: detect and avoid sets of similar pages with no information - lecture 12 (COMPLETED???)

# TODO: crawl all pages with high textual information content - lecture 12 (completed??)
# TODO: store UNIQUE urls in frontier.py - lecture 11

# TODO: Detect and avoid crawling very large files, especially if they have low information value - lecture 12
# TODO: implement robotparser for robots.txt in extract_next_links (EC)

# TODO: make comments throughout utils.py, frontier.py and scraper.py

# Do we utilize sitemaps????


def scraper(url: str, resp: Response) -> list:
    links = extract_next_links(url, resp)
    scraped = [link for link in links if is_valid(link)]
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

    #which website to add to frontier and list
    # check if the website has any data. if not then we skip
    # check if website is similar to another website. if it is then we skip
    # check if website has a lot of data and low information. if it is then skip. ***** how do we check this? *****

    #crawler traps
    #avoid calendars bc it causes infinite loop. other traps.

    if resp.status == 200 and resp.raw_response != None:
        soup = BeautifulSoup(resp.raw_response.content, "lxml")
        for anchor in soup.find_all("a"):
            if anchor.has_attr("href"):
                parse_href = urlparse(anchor["href"])

                # fix this
                link = parse_href.scheme + "://" + parse_href.netloc + parse_href.path 
                if parse_href.query != "": # if there is a query in URL
                    link += "?" + parse_href.query

                if parse_href.scheme != "" and parse_href.netloc != "":
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
        
        return does_not_include_file_extension and valid_domain

    except TypeError:
        print ("TypeError for ", parsed)
        raise

if __name__ == "__main__":
    url_test = "http://sli.ics.uci.edu/Classes/2015W-273a.pdf?action=download&upname=06-vcdim.pdf"
    print(is_valid(url_test))
