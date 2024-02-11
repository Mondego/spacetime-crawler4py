import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords # This is used to acecss a list of stopwords (common words to be filtered out)
from nltk.tokenize import word_tokenize
from collections import Counter # This is used to count words efficiently

# Download necesarry NLTK rewoures if not already exists
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)


def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

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
                if filter_rule in href_link: # only accept uci.edu links 
                    links.add(href_link)
            print(f"***Links Length = {len(links)}***")
        else:
            print(resp.error) # print the error code 
            return list()
    except:
        print("Something went wrong :3")
        
    return list(links)
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
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
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())
    except TypeError as e:
        print ("TypeError for ", parsed)
        raise
"""
# Process content from a list of URLs
def fetch_and_process_urls(urls):
    # Initialize counter object for word counting
    word_count = Counter()

    # Loop through each URL in the provided list.
    for url in urls:
        try:
            resp = requests.get(url, timeout=500) # Make an HTTP GET request to fetch the webpage and added timeout for dealing with redirects
            if resp.status == 200:

                text = BeautifulSoup(resp.raw_response.content, 'html.parser').get_text().lower()
                words = tokenizer(text) # Tokenize the text into words

                # Filter out stopwords from the list of words
                filtered_words = [word for word in words if word not in stopwords.words('english')]
                word_count.update(filtered_words)  # Update word frequencies based on the current webpage
        except Exception as e:
            print(f"Failed to process {url} : {e}")
    
    return word_count

# tokenizer function to split text into words
def tokenizer(text: str) -> list:
    # Tokenize the text into words
    tokens = word_tokenize(text.lower())
    # Filter out tokens that are not aplhanumeric or are in the list of English stopwords
    # Examples of stop words in English are “a,” “the,” “is,” “are,” etc.
    filtered_tokens = [token for token in tokens if token.isalnum() and token not in stopwords.words('english')]
    return filtered_tokens
"""