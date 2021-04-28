import re
import nltk
from nltk.tokenize import RegexpTokenizer
from urllib.parse import urlparse
from configparser import ConfigParser
from bs4 import BeautifulSoup
from collections import defaultdict, OrderedDict
nltk.download('punkt')

'''
crawler meat:
Your task is to:
    1. parse the Web response
    2. extract enough information from the page (if it's a valid page) so to be able to answer the questions for the report
    3. return the list of URLs "scrapped" from that page. 


questions to answer:

1. How many unique pages did you find? Uniqueness for the purposes of this assignment is ONLY established by the URL, but discarding the fragment part. 
    So, for example, http://www.ics.uci.edu#aaa and http://www.ics.uci.edu#bbb are the same URL. Even if you implement additional methods for textual 
    similarity detection, please keep considering the above definition of unique pages for the purposes of counting the unique pages in this assignment.
        - solution: discard anything after the # and store in a global set, get length of set at end
        
2. What is the longest page in terms of the number of words? (HTML markup doesn’t count as words)
        - solution: use nltk to tokenize the webpage (picked this library for efficiency) and the filter out all non alnum words.
                    then compare word count with that of previous webpages to determine which webpage is the longest

3. What are the 50 most common words in the entire set of pages crawled under these domains? (Ignore English stop words, which can be found, for example, 
    here (Links to an external site.)) Submit the list of common words ordered by frequency.
        - solution: 

4. How many subdomains did you find in the ics.uci.edu domain? Submit the list of subdomains ordered alphabetically and the number of unique pages 
    detected in each subdomain. The content of this list should be lines containing URL, number, for example:
    http://vision.ics.uci.edu, 10 (not the actual number here)
        - solution: regex check to see if there is any part before ics.uci.edu, retrieve just that part (subdomain) and add to a dict
                    dict will have {url : unique_url_set} (eg. {'vision.ics.uci.edu' : (vision.ics.uci.edu/hello/my?name, ...)})
                    then add the defragmented url to the corresponding set
                    in the end return the domain and len(unique_url_set)

Some important notes:
1. Make sure to return only URLs that are within the domains and paths mentioned above! (see is_valid function in scraper.py -- you need to change it)
2. Make sure to defragment the URLs, i.e. remove the fragment part.
3. You can use whatever libraries make your life easier to parse things. Optional dependencies you might want to look at: BeautifulSoup, lxml (nudge, nudge, wink, wink!)
4. Optionally, in the scraper function, you can also save the URL and the web page on your local disk.
'''

'''
GLOBAL VARIABLES TO ANSWER QUESTIONS
'''
# unique_urls will contain all unique pages to answer question 1
unique_urls = set()
# subdomains will contain key: subdomain, value: set(unique_urls) to answer question 4
subdomains = defaultdict(set)
#url and word count of webpage with the most words
longest_page = ("www", float("-inf"))
# dictionary to count word frequency
word_count = defaultdict(int)
# put in all words not in stop word
stop_words = set()
with open('stop_words.txt') as f:
    for line in f:
        stop_words.add(line.strip())



# reading all acceptable domains from config file
config = ConfigParser()
config.read('config.ini')
valid_domains = config['CRAWLER']['SEEDURL'].split(',')

def scraper(url, resp):
    global longest_page
    # resp.raw_response.content gives HTML content, which we can pass to BeautifulSoup(content, 'lxml')
    # then to get all text on the page, use soup.get_text() -> answer the different qs/do stuff with it
    # then call extract_next_links() to get all links on this page -> we can validate the links with is_valid()

    # dictionary to keep track of output file writes, we will use subdomains dict for #4 output and longest_page tuple for #2 output
    output = OrderedDict()
    output['WEBPAGE AND RESPONSE STATUS'] = f'{url} ---- {resp.status}'

    url_no_fragment = sanitize_url(url)

    if resp.status == 200 and url_no_fragment not in unique_urls:
        # received webpage -> convert to beautifulsoup object
        soup = BeautifulSoup(resp.raw_response.content, 'lxml')

        # Avoid webpages without less than one div because these commonly do not hold much valuable information
        if len(soup.find_all("div")) < 1:
            return []

        text = soup.get_text()
        
        # QUESTION 1 CODE: substring url to discard fragment and add to unique_urls
        unique_urls.add(url_no_fragment)
        output['QUESTION 1 : Number of Unique URLs'] = len(unique_urls)

        # QUESTION 2 CODE: tokenize the webpage to get the number of words and then determine if it is the longest webpage
        word_tokens = []
        reg_tokenizer = RegexpTokenizer('\s+', gaps=True)
        kdsajkfas = re.compile(r'\W')
        for word in reg_tokenizer.tokenize(text):
            if not re.match(r'^(\W+|^[\w+])$', word):
                sanitized_word = kdsajkfas.sub("", word)
                if len(sanitized_word) > 1: 
                    word_tokens.append(sanitized_word)

        if len(word_tokens) < 150:
            return []

        word_token_count = len(word_tokens)        
        if word_token_count > longest_page[1]:
            longest_page = (url, word_token_count)        
        
        # QUESTION 3 CODE: get the 50 most common words across all the pages crawled
        for word in word_tokens:
            if word.lower() not in stop_words:
                word_count[word.lower()] += 1
            else:
                word_tokens.remove(word)

        if len(word_tokens) < 150:
            return []

        frequency = sorted(word_count.items(), key = lambda f: f[1], reverse = True)
        common_50 = [w[0] for w in frequency[:50]]

        output['QUESTION 3: 50 Most Common Words'] = common_50

        # QUESTION 4 CODE: do regex check to see if anything before ics in ics.uci.edu, retrieve it, add to dict along w defragmented url
        parsed_url = re.search(r'(https?:\/\/)(\w*\.?ics\.uci\.edu)+(.*)', url_no_fragment)
        if parsed_url:
            subdomain = parsed_url.group(2)
            subdomains[subdomain].add(url_no_fragment)

        # retrieve all valid links on page and return them (to be added to frontier)
        links = extract_next_links(url, resp)
        write_output(output)
        ret_links = [link for link in links if is_valid(link)]
        return ret_links
        
    return []

def extract_next_links(url, resp):
    # lxml is the recommended page parser from assignment spec -> faster than html.parser
    page_soup = BeautifulSoup(resp.raw_response.content, "lxml")
    urlparts = urlparse(url)
    next_links = []

    # for all links (identifiable by the <a> tag), get the link and add to frontier
    for atag in page_soup.find_all("a"):
        new_link = atag.get("href")
        if new_link and len(new_link) > 1 and new_link[0] == '/':
            if new_link[1] == '/':
                new_link = 'https:' + new_link
            else:
                new_link = urlparts.scheme + "://" + urlparts.netloc + new_link

        if is_valid(new_link):
            next_links.append(new_link)
    return next_links

def is_valid(url) -> bool:
    if not url:
        return False

    try:
        url_no_fragment = sanitize_url(url)
        if url_no_fragment in unique_urls:
            return False
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
            
        return re.search(r"(ics.uci.edu|cs.uci.edu|informatics.uci.edu|stat.uci.edu)", parsed.netloc.lower()) is not None and not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4|Z|odc"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1|nb|txt"
            + r"|thmx|mso|arff|rtf|jar|csv|ppsx|img"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower()) and re.search(
            r"\/(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4|Z|odc"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1|nb|txt|uploads"
            + r"|thmx|mso|arff|rtf|jar|csv|ppsx|img"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)\/", parsed.path.lower()) is None

            

    except TypeError:
        print ("TypeError for ", parsed)
        raise

def sanitize_url(url):
    url_no_fragment = url.split('#')[0]
    url_no_fragment = url_no_fragment.split("/?replytocom=")[0]
    url_no_fragment = url_no_fragment.split("/?share=")[0]
    url_no_fragment = url_no_fragment.split("/?ical=")[0]
    url_no_fragment = url_no_fragment.split("?do=")[0]
    url_no_fragment = url_no_fragment.split("?action=")[0]
    url_no_fragment = url_no_fragment.split("?version=")[0]
    url_no_fragment = url_no_fragment.split("?afg")[0]
    if url_no_fragment and url_no_fragment[-1] == "/":
        url_no_fragment = url_no_fragment[:-1]

    return url_no_fragment

def write_output(output_dict):
    with open('output.txt', 'a') as file:

        # for number 1
        for k,v in output_dict.items():
            file.write(k+'\t')
            file.write(str(v)+"\n")
        
        # for number 2
        file.write('QUESTION 2 : Longest Webpage\n')
        file.write(longest_page[0]+"\t")
        file.write(str(longest_page[1])+"\n")

        file.write('QUESTION 4: Subdomains and Number of Pages Within\n')
        for k,v in sorted(subdomains.items()):
            file.write(k+"\t")
            file.write(str(len(v))+"\n")
        
        file.write("-----------------------------------\n")

    if len(unique_urls) > 6000:
        with open("unique_urls.txt", "a") as f:
            f.write(str(unique_urls)+'\n')
            f.write("-----------------------------------------------------\n")