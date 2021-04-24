import re
from urllib.parse import urlparse
from urllib.parse import urldefrag # for removing fragments form url
from bs4 import BeautifulSoup

longest_file_len = 0;

def scraper(url, resp):
	links = extract_next_links(url, resp)
	return [link for link in links if is_valid(link)]

### **************************** ###
### *** CURRENTLY INCOMPLETE *** ###
### **************************** ###
def extract_next_links(url, resp):
    extracted_links = list();

    # create if files doesn't exist
    # otherwise write into files the url, context and longest 
    # text file in each appropriate file
    # using with automatically closese all files after the with statement
    with open("url.txt", "a", encoding='utf-8') as url_file, open("context.txt", "a", encoding='utf-8') as context_file, open("longestpage.txt", "a", encoding='utf-8') as longest_file:
        #check if resp is greater than 400
        if not resp:
            return extracted_links   

        if resp.raw_response.status_code > 400:
            return extracted_links

        if resp.raw_response.status > 400:
            return extracted_links

        if resp.status > 400:
            return extracted_links

        # check if this is a valid url
        if not is_valid(url):
            return extracted_links

        if is_valid(url) and (resp.status == 200 or resp.status == 201 or resp.status == 202):
            resp_raw_response = resp.raw_response.content
            soup = BeautifulSoup(resp_raw_response, 'html.parser')
            url_file.write(url+'\n')

            word_list = list()
            for i in soup.txt.split():
                if i:
                    word_list.append(i)

            longest_file.write(url + " " + str




        # tokens = tokenize(resp.raw_response.content)

    # Implementation requred.
    return extracted_links;

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

    
