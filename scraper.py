import re
from urllib.parse import urlparse
from urllib.parse import urldefrag
from bs4 import BeautifulSoup
import sys
from collections import defaultdict
from hashlib import blake2b
from threading import Lock
# [GLOBAL VARIABLES]
# Num of Unique Pages
unique_pages = 0
# Tracks total appearances of tokens amongst all scraped web pages
# Example : "it" : 5 -> means "it" has occured 5 times so far out of all pages scraped
token_dictionary = {}
# Set of Stop Words
stop_words_set = {'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',"ourselves", "hers", "between", "yourself", "but", "again", "there", "about", "once", "during", "out", "very", "having", "with", "they", "own", "an", "be", "some", "for", "do", "its", "yours", "such", "into", "of", "most", "itself", "other", "off", "is", "s", "am", "or", "who", "as", "from", "him", "each", "the", "themselves", "until", "below", "are", "we", "these", "your", "his", "through", "don", "nor", "me", "were", "her", "more", "himself", "this", "down", "should", "our", "their", "while", "above", "both", "up", "to", "ours", "had", "she", "all", "no", "when", "at", "any", "before", "them", "same", "and", "been", "have", "in", "will", "on", "does", "yourselves", "then", "that", "because", "what", "over", "why", "so", "can", "did", "not", "now", "under", "he", "you", "herself", "has", "just", "where", "too", "only", "myself", "which", "those", "i", "after", "few", "whom", "t", "being", "if", "theirs", "my", "against", "a", "by", "doing", "it", "how", "further", "was", "here", "than"}
# URL of the page that contains the most amount of tokens
maxWordsURL = ''
# Num of words in maxWordsUrl
maxWordsCount = 0
# Set to keep track of ics subdomains
ics_domains_info = defaultdict(lambda: set())
# {subdomain: set(all simhashes within this subdomain)}
subdomain_simhashes= defaultdict(lambda: set()) 
myLock = Lock()


# [MAIN FUNCTIONS]
def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    with myLock:
        validURLs = [] 
        # if repsonse is 200, we crawl the website
        if(resp.status == 200):

            # Beautiful Soup
            currURLSoup = BeautifulSoup(resp.raw_response.content, 'lxml') 
            
            # Tokenize the website currURLSoup.get_text 
            # (which returns a non html text)
            text = currURLSoup.get_text()
            # If textual information on website is below 500 words, avoid and do not crawl
            if len(text) <= 500: return []
            
            tokenize(text, url)

            # [SIM HASH]
            # 1. Get the simhash of the text of beautiful soup
            hash = getSimHash(tokenize_feature(text))
            # 2. Extract the domain of the current URL
            domain = extract_domain(url)
            # 3. Check if there is similarity between the hashed 
            #    text of the current webpage and any other URLs
            #    of the same "domain family"
            #    EG : If current URL is youtube.com/hi, then we check youtube.com/hello, etc.
            similar = find_similar(hash, subdomain_simhashes[domain])
            # 4. IF no similarity is found, add the current hashed text
            #    to the data structure
            if not similar:
                subdomain_simhashes[domain].add(hash)
            # 5. Otherwise, if the two ARE similar, we return 
            #    since we do not want to parse this url or its children
            #    since it is low info / too similar to one of the subdomains
            elif similar:
                return []
            
            # Access unique_pages & update it
            global unique_pages
            unique_pages += 1
            # [ADDING VALID URLS TO LIST]
            # For every link within <a></a>
            for scrapedURL in currURLSoup.find_all('a'):
                defragmented = urldefrag(scrapedURL.get('href'))[0]
                if scrapedURL.get('href') is None:
                    continue
                # Check if scrapedURL is relative path
                if not ('://' in defragmented or '//' in defragmented):
                    parsed = urlparse(url)
                    if parsed.hostname != None:
                        defragmented = parsed.scheme + "://" + parsed.hostname + defragmented
                    else:
                        defragmented = ""
                
                validURLs.append(defragmented)
                # todo: delete once finish finish testing
                # else:
                #     record_invalid_urls(scrapedURL.get('href'))
            
            # [ICS DOMAIN HANDLING]
            # If the url's domain is ics.uci.edu, record it
            ics_domains = 'ics.uci.edu'
            if '.'+ics_domains in url or '/'+ics_domains in url:
                record_ics_domains(url)
            generate_report()
            
        # For reponses that are NOT 200
        else:
            if(resp.status >= 600):
                with open('./Logs/Error.log','a') as file:
                    file.writelines(str(resp.status)+ " " + resp.error + '\n')
            else:
                # with open('./Logs/Error.log','a') as file:
                #     file.writelines(str(resp.status)+ " " + str(resp.raw_response.content)+ '\n')
                pass
                
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
def printFreq(hashmap: dict) -> None:
    sortedHashmap = dict(sorted(hashmap.items(), key= lambda item: item[1],reverse=True))
    counter = 0
    for mapping in sortedHashmap:
        if counter == 50:
            break
        print(mapping, "->", sortedHashmap[mapping]) 
        counter += 1
    return

# Function : Record Invalid URLs
# Use : Test function that logs any urls that are invalid 
def record_invalid_urls(url: str) -> None:
    """For Testing Purposes"""
    with open("./Logs/invalid.txt", "a") as file:
        file.writelines("{url}\n".format(url=url))

# Function : Record ICS Domains
# Use : Processes the URL and adds it to ics_domains_info
def record_ics_domains(url: str) -> None:
    global ics_domains_info
    parsed = urlparse(url)
    hostname = parsed.hostname 
    
    if hostname != None and len(hostname) >= 3 and hostname[0:4] == "www.":
        hostname = hostname[4::]

    if hostname != None and hostname != "ics.uci.edu":
        ics_domains_info[hostname].add(url)
    
# Function : Generate Report
# Use : Creates report.txt which has the following :
#       1. Unique Pages Found
#       2. URL with the most amount of words
#       3. Subdomains found under ICS domain
#       4. Other statistics
def generate_report() -> None:
    """Generate the Final Report"""
    global ics_domains_info
    with open('./Logs/report.txt', 'w') as file:
        unique_pages_str = "Unique pages: {count}\n".format(count=unique_pages)
        longest_page = "Longest Page: {url} Total Words: {word_count}\n".format\
                     (url=maxWordsURL, word_count=maxWordsCount)
        
        ics_str = "Number of Subdomains found under ICS domain: {count}\n".format(count = len(ics_domains_info))
        common_words = get_most_common_words()

        file.writelines(unique_pages_str)
        file.writelines(longest_page)
        file.writelines(common_words)
        file.writelines(ics_str)

        for key, value in sorted(ics_domains_info.items(), key=lambda item : item[0]):
            file.writelines("{key}: {info}\n".format(key=key, info=len(value)))

# Function : Get Most Common Words
# Use : Used in report generation
#       gets the 50 most common words of
#       all parsed pages
def get_most_common_words() -> str:
    sortedToken = sorted(token_dictionary.items(), key= lambda item: item[1],reverse=True)  
    i = 0
    string = "------------\n50 Most Common Words\n"
    while i < len(sortedToken) and i < 50:
        string += str(sortedToken[i][0]) + ": " + str(sortedToken[i][1]) + '\n'
        i += 1

    return string + "------------\n"

# Function : Tokenize Feature
# Use : Used in simhashing, returns a dictionary
#       of a text's tokens and their frequency
#       [Token:str] -> [Frequency:int]
def tokenize_feature(soupText: str) -> defaultdict(int):
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

# Function : Extract Domain
# Use : Given a url, extracts its domain
def extract_domain(url: str) -> str:
    """return the subdomain of the url"""
    parsed = urlparse(url)
    hostname = parsed.hostname 
    
    if hostname != None and len(hostname) >= 3 and hostname[0:4] == "www.":
        hostname = hostname[4::]
    
    if hostname is None:
        return ""
    else:
        return hostname
    
# Given a counter, returns the string representation of a simhash
def getSimHash(myCounter):
    # Hash function
    hashFunction = blake2b
    # list that is initialized with 512 zeros, each will represent a binary value
    myVector = [0]*512
    # For [Str] -> [Frequency]
    for mystr, freq in myCounter.items():
        # Get the hexvalue of the string using the hash function
        hexValue = hashFunction(mystr.encode('utf-8')).hexdigest()
        # Conver the hex value into binary
        binValue = bin(int(hexValue,16))[2::]
        binValue = "0"*(512-len(binValue))+binValue
        for index, let in enumerate(binValue):
            mult = 1 if int(let) == 1 else -1 
            myVector[index] += mult*freq
    return ''.join(['0' if x<= 0 else '1' for x in myVector])
    
# Compares hashes to determine similarity
def similar(arr1,arr2) -> bool:
    total = 0
    for a,b in zip(arr1,arr2):
        if a == b:
            total += 1
    return (total/512) >= .8

# Traverses subdomain set to determine if a duplicate exists
def find_similar(myHash,mySet):
    for aHash in mySet:
        if similar(aHash,myHash):
            return True
    return False