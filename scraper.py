import re
from urllib.parse import urlparse, urlunparse
from bs4 import BeautifulSoup
import nltk 
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

def scraper(url, resp):
    links = extract_next_links(url, resp)
    x=  [link for link in links if is_valid(link)]
    return x

def extract_next_links(url, resp):
    # Implementation required.
    filter_rule = "uci.edu" #accept all links with this rule 
    links = set() # use this to avoid repeated links 
    try:
        if resp.status == 200: # check if url can be crawled, ask for permission 
            soup = BeautifulSoup(resp.raw_response.content, 'html.parser') # bts content into a varaible that we can further parse 
            hyperlinks = soup.find_all('a') # extract all hyper links 
            for link in hyperlinks:
                href_link = link.get('href')
                parsed = urlparse(href_link)
                parsed = parsed._replace(fragment='') # remove the fragment 
                parsed = urlunparse(parsed) # stitch it back together 
                links.add(parsed)
                
        else:
            print(resp.error) # print the error code 
            return list()
    except:
        print("Link or file type is not of html parsability")
        
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    return list(links)

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        valid_domains = {"ics", "stat", "informatics", "cs"} # set of valid domains 
        if type(url) != str:
            url = url.decode('utf-8') # make it into a string

        parsed = urlparse(url)

        broken = parsed.netloc.split('.') # [ics, uci, edu]
        if not any(domain in broken for domain in valid_domains):
            return False
        
        if parsed.scheme not in set(["http", "https"]): ## not https will also avoid 
            return False
        
        if (parsed.query != ""): # b/c we care about queries, we also want to check for improper urls here 
            return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4|jav"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names|jar"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.query.lower()) 


        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4|jav"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names|jar"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower()) # accepts files of this type  

    except TypeError:
        print ("TypeError for ", parsed)
        raise

def checkSum_Hash(words_only):
    sums = set()

    for word in range(len(words_only)):
        if (word + 4) < len(words_only): # 0-4, 1-5, 2-6, making sure its in the range 
            checksum = 0 # sum the the 4-word-sub
            N_GRAM = ''.join(words_only[word:word+4])
            for i in N_GRAM: # iterate through words adding the ASCII values of the char 
                for let in i:
                    checksum += ord(let)

            sums.add(checksum)
            checksum = 0

    return tuple(set([num for num in sums if num % 15 == 0]))
    
# name me 