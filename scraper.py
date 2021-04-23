import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup


def scraper(url, resp):
	#save url
    f = open("urls.txt",'a')
    file.write(url)
    file.write('\n')
    file.close()

    #check if resp is greater than 400
    if not resp:
        return list()

    if resp.raw_response.status_code > 400:
        return list()

    if resp.raw_response.status > 400:
        return list()

    if resp.status > 400:
        return list()

    # check if this is a valid url
    if not is_valid(url):
        return list()

    tokens = tokenize(resp.raw_response.content)





	links = extract_next_links(url, resp)
	return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    # Implementation requred.
    return list()

def is_valid(url):
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False

        accetable_domains = [".ics.uci.edu", ".cs.uci.edu", ".informatics.uci.edu", 
        ".stat.uci.edu", "today.uci.edu"]
        if not any(domain in parsed.netloc for domain in accetable_domains):
        	return False

        if "today.uci.edu" in parsed.netloc:
            if "department/information_computer_sciences" not in parsed.path:
                return False

        # check if its a calendar, needs implementation



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
        raise

def tokenize(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    text = soup.get_text()

    
