import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import sys

# Represents num of unique pages
unique_pages = 0
# Dict that tracks num of tokens
token_dictionary = {}
# English stop words (NOT IMPLEMENTED YET, WAITING FOR EDSTEM THREAD ABOUT NTLK)
stop_words_set = set()
# Longest URL
longest_URL = ''
# Counter of Longest URL
counter_longest_URL = 0

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
        soup = BeautifulSoup(resp.raw_response.content, 'lxml') 
        # Tokenize the website soup.get_text (which returns a string of raw text from html)
        tokenize(soup.get_text(), url)
        # printFreq(token_dictionary)
        for scrapedURL in soup.find_all('a'):
            if(is_valid(scrapedURL.get('href'))):
                #appends defragmented url
                validURLs.append(scrapedURL.get('href').split('#')[0])
    # reponses that are either in the 600s or 400s
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
    currentPageCount = 0
    lines = soupText
    for word in lines.split():
        correct = ''
        for letter in word.lower():
            if (letter.isalnum() and letter.isascii()) or letter == "'":
                correct = ''.join([correct,letter])
            else:
                if(correct != ''):
                    if correct in token_dictionary:
                        token_dictionary[correct] += 1
                    else:
                        token_dictionary[correct] = 1
                    currentPageCount += 1
                    correct = ''
        if correct != '':
            if correct in token_dictionary:
                token_dictionary[correct] += 1
            else:
                token_dictionary[correct] = 1
            currentPageCount += 1
    global counter_longest_URL
    if currentPageCount > counter_longest_URL:
        counter_longest_URL = currentPageCount
        global longest_URL
        longest_URL = url
    return

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

def is_valid(url): 
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        # check if host even exists
        # startingDomains = ['https://www.ics.uci.edu', 'https://www.cs.uci.edu', 'https://www.informatics.uci.edu', 'https://www.stat.uci.edu']
        if parsed.hostname == None or len(parsed.hostname)==0:
            return False
        # if pdf is in the parsed path
        if 'pdf' in parsed.path:
            return False
        # check if hostname is in allowed domains
        acceptedDomains = ['ics.uci.edu','cs.uci.edu','informatics.uci.edu','stat.uci.edu']
        for validDomain in acceptedDomains:
            if '.'+validDomain in parsed.hostname or '/'+validDomain in parsed.hostname:
                break
        else:
            return False

        if parsed.scheme not in set(["http", "https"]):
            return False
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico|html|sql|ppsx"
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
