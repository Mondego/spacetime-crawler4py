import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup


def scraper(worker,frontier,url, resp,config,writingFile,stopwords):


    links = extract_next_links(worker,frontier,url, resp,config,writingFile,stopwords)
    
    return [link for link in links if is_valid(link)]

def extract_next_links(worker,frontier,url, resp,config, writingFile,stopwords):
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
    texts = soup.get_text()

    tokens = list(set(tokenize(texts,stopwords)))
    
    
    if simHash(tokens) not in frontier.visitedSimHashes:
        #TODO complete simhash
        writingFile.write("PAGE::"+url)
        writingFile.write(sorted(tokens))
        for link in soup.find_all('a'):
            
            link = toAbsolute(url,link)
            
            if link not in frontier.visited:
                if "?" in link:
                    link = link[:link.index("?")] # this takes out the fragment
                links.append(link.get('href'))

        return links
    ### END by hitoki 4/26/2023 10:52pm
    
    return list()

#added by Hitoki 4/27/2023 1:19am
def toAbsolute(url, newlink):
    #TODO make relative to absolute
    return newlink 

#added by Hitoki 4/27/2023 1:24am
def simHash(words):
    #TODO
    return -1

#added by Hitoki 4/27/2023 1:12am
def tokenize(text,stopwords)->list:
    """The tokenize function is a modified function from Assignment 1 Part A of Hitoki Kdahashi's submission (37022201)
    This function takes in a string text, splits it by white spaces, and attempt to check the validity of each word.
    A word is valid if it is not in the stopwords list, or that it is more than 1 character long, and obeys the regular expression ^[a-zA-Z0-9]$, or that it has to be alphanumerical.
    
    THIS FUNCTION DOES NOT REMOVE DUPLICATES
    
    Args:
        text (str): text scraped from the crawler
        stopwords (list[str]): list of string of stopwords in english dictionary.

    Returns:
        List[str]: A list of token strings
        
    Complexity:
        O(n) where n is the number of characters in the text because this function loops through every line and for every line it iterates through every character in that line. Thus the function grow in linear time based on the input N.
    """
    text = text.split(" ") 
    words = []
    numOfStopWordsDetected = 0
    # iterate avery line
    for word in text:
        #reset currentword
        currentWord = ""
        for i in word: 
            
            #if word is upfront in the stopwords list or that if it is less than or equal to 1 characters long then discard it.
            if word.lower() in stopwords or len(word) <= 1:
                numOfStopWordsDetected+=1
                continue
            try:
                # if current char is alphanumerical, then it is in the sequence of the token
                if re.match('^[a-zA-Z0-9]$',i): 
                    # if i.isalnum():
                    currentWord+=i
                    # print(currentWord)
                else:
                    
                    # if current word is "" then no sequence of alphanumerical strings are being appeneded
                    if currentWord == "": continue
                    
                    # if word in stopword list then discard the word
                    if currentWord.lower() in stopwords or len(currentWord) <= 1:
                        currentWord = ""
                        numOfStopWordsDetected+=1
                        continue
                    
                    #add to wordlist
                    words.append(currentWord.lower())
                    currentWord = ""
                
            except:
                continue
    print("Number of stopwords detected:",numOfStopWordsDetected)
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


if __name__ == "__main__":
    print(is_valid(""))