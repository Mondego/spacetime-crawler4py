import re
from urllib.parse import urlparse
from urllib.parse import urldefrag
from bs4 import BeautifulSoup
import sys
from collections import defaultdict
from utils.download import download 
from hashlib import blake2b




# Represents num of unique pages
unique_pages = 0
# A dictionary that tracks total appearances of tokens amongst all scraped web pages
# Example : "it" : 5 -> means it has occured 5 times so far out of all pages scraped
token_dictionary = {}
# English stop words (NOT IMPLEMENTED YET, WAITING FOR EDSTEM THREAD ABOUT NTLK)

stop_words_set = {'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',"ourselves", "hers", "between", "yourself", "but", "again", "there", "about", "once", "during", "out", "very", "having", "with", "they", "own", "an", "be", "some", "for", "do", "its", "yours", "such", "into", "of", "most", "itself", "other", "off", "is", "s", "am", "or", "who", "as", "from", "him", "each", "the", "themselves", "until", "below", "are", "we", "these", "your", "his", "through", "don", "nor", "me", "were", "her", "more", "himself", "this", "down", "should", "our", "their", "while", "above", "both", "up", "to", "ours", "had", "she", "all", "no", "when", "at", "any", "before", "them", "same", "and", "been", "have", "in", "will", "on", "does", "yourselves", "then", "that", "because", "what", "over", "why", "so", "can", "did", "not", "now", "under", "he", "you", "herself", "has", "just", "where", "too", "only", "myself", "which", "those", "i", "after", "few", "whom", "t", "being", "if", "theirs", "my", "against", "a", "by", "doing", "it", "how", "further", "was", "here", "than"}
# URL of the page that contains the most amount of tokens
maxWordsURL = ''
# Counter of Longest URL
counter_longest_URL = 0
maxWordsCount = 0
# for keeping track of ics subdomains
ics_domains_info = defaultdict(lambda: set())
# near detection
subdomain_simhashes= defaultdict(lambda: set()) # {subdomain: set(all simhashes within this subdomain)}
url_simhash = {}

### CHANGE TO TEST FOR INVALID URLS
def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    validURLs = [] 
    # if repsonse is 200, we crawl the website
    if(resp.status == 200):
        # Access unique_pages & update it
        global unique_pages
        unique_pages += 1
        

    
        # Beautiful Soup
        currURLSoup = BeautifulSoup(resp.raw_response.content, 'lxml') 

        # Tokenize the website currURLSoup.get_text 
        # (which returns a non html text)
        text = currURLSoup.get_text()
        tokenize(text, url)
        hash = getSimHash(tokenize_feature(text))

        # simhash----
        
        subdomain = extract_subdomain(url)
        found = find_similar(hash, subdomain_simhashes[subdomain])
        if not found:
            subdomain_simhashes[subdomain].add(hash)
        
        if found:
            return []



        # For every URL found in the current URL's soup
        for scrapedURL in currURLSoup.find_all('a'):
            if(is_valid(scrapedURL.get('href'))):
                # appends defragmented url
                defragmented = urldefrag(scrapedURL.get('href'))[0]
                validURLs.append(defragmented)
            # TODO: delete once finish finish testing
            # else:
            #     record_invalid_urls(scrapedURL.get('href'))
        
        # if ics domains, then records down info
        ics_domains = 'ics.uci.edu'
        if '.'+ics_domains in url or '/'+ics_domains in url:
            record_ics_domains(url)
        generate_report()
        
    # reponses that are either in the 600s or 400s
    # ELSE response != 200
    else:
        if(resp.status >= 600):
            with open('./Logs/Error.log','a') as file:
                file.writelines(str(resp.status)+ " " + resp.error + '\n')
        else:
            # with open('./Logs/Error.log','a') as file:
            #     file.writelines(str(resp.status)+ " " + str(resp.raw_response.content)+ '\n')
            pass
            
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    return validURLs


# Function : Tokenize
# Use : Given a string of raw text from HTML file, 
#       tokenizes it and adds it to token_dictionary
def tokenize(soupText, url):
    # Represents the number of tokens of the current page being tokenized
    currTokenCount = 0
    # Looping Start : 
    for word in soupText.split():
        correct = ''
        for letter in word.lower():
            if (letter.isalnum() and letter.isascii()) or letter == "'":
                correct = ''.join([correct,letter])
            else:
                if(correct != '' and correct not in stop_words_set):
                    if correct in token_dictionary:
                        token_dictionary[correct] += 1
                    else:
                        token_dictionary[correct] = 1
                    # If we have detected a token, increment count
                    currTokenCount += 1
                    correct = ''
        if correct != '' and correct not in stop_words_set:
            if correct in token_dictionary:
                token_dictionary[correct] += 1
            else:
                token_dictionary[correct] = 1
            # Edge case, same thing as above, increment count
            currTokenCount += 1

    global maxWordsCount
    # If the current page's word count > currMax
    if currTokenCount > maxWordsCount:
        # Then update current max & max url
        maxWordsCount = currTokenCount
        global maxWordsURL
        maxWordsURL = url
    return

def is_valid(url): 
    # Pre initialized variables
    acceptedDomains = ['ics.uci.edu','cs.uci.edu','informatics.uci.edu','stat.uci.edu']
    invalidFiles = ['.tex','.zip','.pdf','.csv','.ps','.gz','.ppt','.m','mat']
    parsed = urlparse(url)
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        # Check if host exists
        if parsed.hostname == None or len(parsed.hostname)==0:
            return False
        # Check if url is PDF
        if 'pdf' in parsed.path or '/wp-content/' in parsed.path or "~cs224" in parsed.path:
            return False
        # check if hostname is in allowed domains
        for invalidQuery in invalidFiles:
            if invalidQuery in parsed.query:
                return False
        for validDomain in acceptedDomains:
            if '.'+validDomain in parsed.hostname or '/'+validDomain in parsed.hostname:
                break
        else:
            return False

        if parsed.scheme not in set(["http", "https"]):
            return False
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico|html|sql|ppsx"
            + r"|png|tiff?|mid|mp2|mp3|mp4|bib|nb|r|m|c"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise

# [HELPER FUNCTIONS]
# Function : printFreq
# Use : Given a dictionary, prints it in sorted order of value
def printFreq(hashmap) -> None:
    sortedHashmap = dict(sorted(hashmap.items(), key= lambda item: item[1],reverse=True))
    counter = 0
    for mapping in sortedHashmap:
        if counter == 50:
            break
        print(mapping, "->", sortedHashmap[mapping]) 
        counter += 1
    return


def record_invalid_urls(url: str) -> None:
    """For Testing Purposes"""
    with open("./Logs/invalid.txt", "a") as file:
        file.writelines("{url}\n".format(url=url))


def record_ics_domains(url: str) -> None:
    """Record down information for ics subdomains"""
    global ics_domains_info
    parsed = urlparse(url)
    hostname = parsed.hostname 
    
    if hostname != None and len(hostname) >= 3 and hostname[0:4] == "www.":
        hostname = hostname[4::]

    if hostname != None and hostname != "ics.uci.edu":
        ics_domains_info[hostname].add(url)
    

def generate_report() -> None:
    """Generate the Final Report"""
    global ics_domains_info
    with open('./Logs/report.txt', 'w') as file:
        unique_pages_str = "Unique pages: {count}\n".format(count=unique_pages)
        longest_page = "Longest Page: {url} Total Words: {word_count}\n".format\
                     (url=maxWordsURL, word_count=maxWordsCount)
        
        ics_str = "ICS domain number: {count}\n".format(count = len(ics_domains_info))
        common_words = common_words_str()

        file.writelines(unique_pages_str)
        file.writelines(longest_page)
        file.writelines(ics_str)
        file.writelines(common_words)

        for key, value in ics_domains_info.items():
            file.writelines("{key}: {info}\n".format(key=key, info=value))


def common_words_str() -> str:
    """return a string for 50 common words"""
    sortedToken = sorted(token_dictionary.items(), key= lambda item: item[1],reverse=True)  
    i = 0;
    string = ""
    while i < len(sortedToken) and i < 50:
        string += str(sortedToken[i][0]) + '\n'
        i += 1

    return string


# added after simhash
def tokenize_feature(soupText):
    # Represents the number of tokens of the current page being tokenized
    token_list = defaultdict(int)

    # Looping Start : 
    for word in soupText.split():
        correct = ''
        for letter in word.lower():
            if (letter.isalnum() and letter.isascii()) or letter == "'":
                correct = ''.join([correct,letter])
            else:
                if(correct != '' and correct not in stop_words_set):
                    # If we have detected a token, increment count
                    token_list[correct] += 1
                    correct = ''
        if correct != '' and correct not in stop_words_set:
            token_list[correct] += 1
            # Edge case, same thing as above, increment count
    return token_list


def extract_subdomain(url: str) -> str:
    """return the subdomain of the url"""
    parsed = urlparse(url)
    hostname = parsed.hostname 
    
    if hostname != None and len(hostname) >= 3 and hostname[0:4] == "www.":
        hostname = hostname[4::]
    
    if hostname is None:
        return ""
    else:
        return hostname
    

def getSimHash(myCounter):
    hashFunction = blake2b
    myVector = [0]*512
    for mystr, freq in myCounter.items():
        hexValue = hashFunction(mystr.encode('utf-8')).hexdigest()
        binValue = bin(int(hexValue,16))[2::]
        binValue = "0"*(512-len(binValue))+binValue
        for index, let in enumerate(binValue):
            mult = 1 if int(let) == 1 else -1 
            myVector[index] += mult*freq
    return ''.join(['0' if x<= 0 else '1' for x in myVector])
    

def similar(arr1,arr2) -> bool:
    total = 0
    for a,b in zip(arr1,arr2):
        if a == b:
            total += 1
    return (total/512) >= .75


def find_similar(myHash,mySet):
    for aHash in mySet:
        if similar(aHash,myHash):
            return True
    return False