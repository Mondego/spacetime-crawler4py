import re
from urllib.parse import urlparse
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import nltk
nltk.download('punkt')

Blacklist = set()
Visited = set()
Stop_Words = {"a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during", "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves"}
Longest_Page = ()
Common_Words = {}

def scraper(url, resp) -> list:
    links = extract_next_links(url, resp)
    valid_links = [link for link in links if is_valid(link)]
    if resp.status == 200:
        word_token_list = tokenize_response(resp) #gather all tokens from webpage
        check_longest_page(url, len(word_token_list)) #check if Longest_Page needs to be updated
        compute_word_frequencies(word_token_list) #find frequencies of each token and insert into Common_Words
        #print(Common_Words)
        #print(Longest_Page)
    return valid_links

# get data from website and tokenize it taking out everything that isn't a word
def tokenize_response(resp):
    content = resp.raw_response.content
    soup = BeautifulSoup(content, "html.parser")
    tokens = nltk.tokenize.word_tokenize(soup.get_text()) # uses nltk to tokenize webpage
    word_tokens = [t for t in tokens if not re.match('[\W]+', t)]
    return word_tokens

# assign new value to Longest_Page if current page is longer
def check_longest_page(url, word_token_list_len):
    global Longest_Page
    if Longest_Page and Longest_Page[1] < word_token_list_len:
        Longest_Page = (url, word_token_list_len)
    elif not Longest_Page:
        Longest_Page = (url, word_token_list_len)

# increment word count in Common_Words for all words found on this page
def compute_word_frequencies(tokenList):
    # for loop which adds count to Common_Words dictionary 
    global Common_Words
    for token in tokenList:
        if token in Common_Words:
            Common_Words[token] += 1
        elif token not in Common_Words and not in_stop_words(token): # checks to see if token is a stop word if it has not been added to Common_Words
            Common_Words[token] = 1

# returns true if a word is a stop word otherwise returns False
def in_stop_words(token):
    if token in Stop_Words:
        return True
    return False

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
    nextLinks = set()
    global Blacklist
    global Visited

    #temporary
    #if resp.status != 200:
    #    print(resp.status + resp.error)

    # If status is bad or link already visited add it to a blacklist to avoid
    if resp.status != 200 or url in Blacklist or url in Visited:
        Blacklist.add(url)
        return set()

    soup = BeautifulSoup(resp.raw_response.content, "html.parser")
    for link in soup.find_all('a'):
        href = link.attrs.get('href')

        # If link is relative make it absolute
        if bool(urlparse(url).netloc):
            href = urljoin(url, href)

        # Stop duplicates of same link by splitting 
        # (ex #ref40, #ref45 etc of same link)
        # not sure if including '?' is necessary, neef further testing
        href = href.split('#')[0]
        href = href.split('?')[0]

        if is_valid(href):
            nextLinks.add(href)

    # Add current url to list of visited urls so we don't end up visiting already visited links
    parsed = urlparse(url)
    Visited.add(parsed.scheme + '://' + parsed.netloc + parsed.path)
    return nextLinks

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    global Visited
    global Blacklist

    if url in Visited or url in Blacklist:
        return False

    try:
        parsed = urlparse(url)
    except TypeError:
        print(f'TypeError for {url}')
        raise

    if parsed.scheme not in {"http", "https"}:
        return False

    # Make sure link is in provided domain constraints
    if parsed.netloc not in {"www.ics.uci.edu", "www.cs.uci.edu", "www.informatics.uci.edu", "www.stat.uci.edu", "www.today.uci.edu"}:
        return False

    if parsed.netloc == "www.today.uci.edu" and parsed.path != "/department/information_computer_sciences/":
        return False

    # Regex expression to not allow repeating directories
    # Source: https://support.archive-it.org/hc/en-us/articles/208332963-Modify-crawl-scope-with-a-Regular-Expression
    # Note: Not yet sure if this is working or not, will need more testing
    # Seems to work better with 'r' than without (or work in general, not sure)
    if re.match(r"^.*?(/.+?/).*?\1.*$|^.*?/(.+?/)\2.*$", parsed.path):
        return False

    if re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz"
            # Added
            + r"img|sql)$", parsed.path.lower()):
        return False
    return True
