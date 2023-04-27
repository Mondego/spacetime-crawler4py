import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup


def scraper(url, resp,config,writingFile):


    links = extract_next_links(url, resp,config,writingFile)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp,config, writingFile):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    
    
    
    ### Start Added by Hitoki 4/26/2023 10:52pm
    
    soup = BeautifulSoup(resp.raw_response.content, 'html.parser') # beautifulsoup for html.
    
    #finding all links
    links = list()
    for link in soup.find_all('a'):
        links.append(link.get('href'))
    
    texts = soup.get_text()

    tokens = tokenize(texts)
    
    ### END by hitoki 4/26/2023 10:52pm
    
    
    return links


def tokenize(text)->list:
    """The tokenize function reads in a text file and returns a list of the tokens in that file. 
        This function deos not remove duplicate tokens and will add the strings as lower alphabets.
    

    Args:
        filePath (string): string to the file or filepath.

    Returns:
        List[str]: A list of token strings
        
    Complexity:
        O(n) where n is the number of characters in the file because this function loops through every line and for every line it iterates through every character in that line. Thus the function grow in linear time based on the input N.
    """
    # f = open(filePath,"r") # using utf-8 to open non-english character words
    with open(filePath,"r",errors="ignore") as f:
        # tokens = []
        words = []
        currentWord = ""
        # iterate avery line
        for line in f: 
            #iterate every char in line
            for i in line: 
                try:
                    # if current char is alphanumerical, then it is in the sequence of the token
                    if re.match('^[a-zA-Z0-9]$',i): 
                        # if i.isalnum():
                        currentWord+=i
                        # print(currentWord)
                    else:
                        
                        # if current word is "" then no sequence of alphanumerical strings are being appeneded
                        if currentWord == "": continue
                        
                        # add to wordlist
                        words.append(currentWord.lower())
                        currentWord = ""
                    
                except:
                    continue

        
    return words
       

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

    except TypeError:
        print ("TypeError for ", parsed)
        raise
