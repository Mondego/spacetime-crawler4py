from cgitb import html
import re
import shelve
import os
import sys

from utils import get_logger, get_urlhash
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin, urldefrag, urlunparse
from threading import RLock

#q1 - unique pages
visitedPages = set()

#q2 - longest page for number of words
longestPages = ["", 0]

#q3 - 50 most common words
wordCount = dict()

#q4 - how many subdomains, list in alphabetical order as well as unique pages per subdomain
subDomainCount = dict()

stopWords = {"a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during", "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours	ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves"}            

domains = ["ics\.uci\.edu", "cs\.uci\.edu", "informatics\.uci\.edu" ,"stat\.uci\.edu"]

disallowQueriesDomains = ["swiki.ics.uci.edu", "wiki.ics.uci.edu", "archive.ics.uci.edu", "cbcl.ics.uci.edu"]
shelveName = 'ans.shelve'
sn1 = 'visitedPages.shelve'
sn2 = 'longestPages.shelve'
sn3 = 'wordCount.shelve'
sn4 = 'subDomainCount.shelve'
answerLock = RLock()
noShelve = False

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    if not is_valid(url):   #this is useful if the frontier was corrupted
        return list()       #with invalid urls
    global visitedPages
    global save1
    global save2
    global save3
    global save4
    global noShelve
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    ret = list()
    if resp.url in visitedPages:
        return ret
    if resp.status != 200:
        print("Error in getting url, code:", resp.status)
        return ret
    if not resp.raw_response:
        return ret

    soup = BeautifulSoup(resp.raw_response.content, 'html.parser')

    #update answers
    answerLock.acquire()
    if noShelve:
        save1 = shelve.open(sn1, writeback=True)
        save2 = shelve.open(sn2, writeback=True)
        save3 = shelve.open(sn3, writeback=True)
        save4 = shelve.open(sn4, writeback=True)
        noShelve = False
    visitedPages.add(resp.url)
    urlhash = get_urlhash(resp.url)
    save1[urlhash] = url
    save1.sync()
    
    longestPage(soup, url)
    save2[sn2] = longestPages
    save2.sync()

    addTokens(soup)
    #sync performed in function already

    domain = urlparse(resp.url).hostname
    if re.match(r'.*\.ics\.uci\.edu$', domain):
        subDomainCount[domain] = subDomainCount.get(domain, 0) + 1
        save4[domain] = subDomainCount[domain]
        save4.sync()

    dumpAnswers()
    answerLock.release()
    #finish updating answers

    links =  soup.findAll("a")
    for link in links:
        href = link.get('href')
        href = urldefrag(href)[0] # assume we want to remove fragments

        href = urljoin(url, href) #join for relative URLS
        # if URL is blacklisted for queries, remove query string
        parsed = urlparse(href)
        if parsed.hostname in disallowQueriesDomains:
            parsed = parsed._replace(query='') #remove query string
            href = urlunparse(parsed)
        # if a component was found that already exists, the whole page is likely a trap
        # do not crawl further
        #if isTrap(parsed):
        #    print("Potential trap found")
        #    return list()
        ret.append(href)
        
      
    return ret

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        # https://docs.python.org/3/library/urllib.parse.html
        # scheme://netloc/path;parameters?query#fragment
        parsed = urlparse(url)
        if isBadDomain(str(parsed.hostname)):
            return False
        if parsed.scheme not in set(["http", "https"]):
            return False
        
        #temp for debugging
        if parsed.hostname in disallowQueriesDomains and parsed.query != '':
            return False
        #end temp for debugging

        if url in visitedPages:
            return False

        #check if the path is a calendar because they are traps
        if isTrap(parsed):
            return False

        #avoid any directory named pix or figs in path
        if (re.search(r'(pix|figs)', parsed.path)):
            return False
        
        #ignore ics trap computing
        if re.search(r'ics\.uci\.edu\/+(grad|ugrad|honors)', url):
            return False
        #ignore ml
        if re.search(r'archive\.ics\.uci\.edu\/ml', url):
            return False
        #ignore anything adding paths after index.php
        if (re.search(r'index.php\/',url)):
            return False
            
        invalidPattern = re.compile(r".*\.(css|js|bmp|gif|jpe?g|ico"
        + r"|png|tiff?|mid|mp2|mp3|mp4"
        + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
        + r"|mpg|bam"
        + r"|ps|eps|tex|ppt|pptx|ppsx|doc|docx|xls|xlsx|names"
        + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
        + r"|epub|dll|cnf|tgz|sha1"
        + r"|thmx|mso|arff|rtf|jar|csv"
        + r"|apk|war|img|txt"
        + r"|shar|h|cpp|c|cp|makefile|py|lif"
        + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$")
        
        ret =  not re.match(invalidPattern, parsed.path.lower()) and not any(re.match(invalidPattern, x) for x in parsed.query.lower().split('&'))
        return ret
        
    except TypeError:
        print ("TypeError for ", parsed)
        raise

#Helper Functions
def isTrap(parsed):
    path = parsed.path.lower()
    #check if there is pdf in between
    if any(x in path for x in ['?replytocom=', '/pdf/', "#comment-", "events"]):
        return True

    #check if it's in a calendar
    # if 'wics' in path and bool(re.search('/events/.*?/', path)):
    #     return True

    # if 'today' in path and bool(re.search('/calendar/.*?/', path)):
    #     return True

    # if re.match(r'\/calendar\/.+ | \/events\/.+', path) or re.match(r'.*?\/(.+?)\/.?\1.* | .*?\/(.+?)\/.?\2.*', path) or re.match(r'.*\..+\/', path):
    #     print('Path is trap:', path)
    #     return True

    #https://support.archive-it.org/hc/en-us/articles/208332963-Modify-your-crawl-scope-with-a-Regular-Expression
    if re.match(r'^.*?(/.+?/).*?\1.*$|^.*?/(.+?/)\2.*$', path):
        return True
    return False


def isBadDomain(domain):
    # we want to be able to check against subdomains: hentai.ics.uci.edu
    if domain is None:
        return True
    for d in domains:
        if re.match(r'.*\.'+d+'$', domain):
            return False
    return True

def addTokens(soup):
    global save3
    tokenList = re.split("[^a-zA-Z0-9]",soup.get_text())
    # remove empty strings and stopWords
    tokenList = list(filter(lambda str: len(str) > 1 and str not in stopWords, tokenList))
    for i in range(len(tokenList)):
        token = tokenList[i].lower()
        wordCount[token] = wordCount.get(token, 0) + 1
        save3[token] = wordCount[token]
        save3.sync()

def longestPage(soup, url):
    tokenList = re.split("[^a-zA-Z0-9]",soup.get_text())
    tokenList = list(filter(lambda str: str != "" and str not in stopWords, tokenList))
    if len(tokenList) > longestPages[1]:
        longestPages[0], longestPages[1] = url, len(tokenList)


def dumpAnswers():
    logger = get_logger("SCRAPER")
    try:
        file = open("answers.txt", "w")
        file.write(f"Q1: Number of unique URLs: {len(visitedPages)}\n")

        file.write(f"Q2: Longest Page and the number of words\n")
        file.write(f'{longestPages[0]} => {longestPages[1]}\n')

        #q3 - 50 most common words, sort by occurence
        file.write("Q3: Top 50 words:\n")
        for k, v in sorted(wordCount.items(), key=lambda x: -x[1])[:50]:
            file.write(f"{k} : {v}\n")

        #q4 - how many subdomains, list in alphabetical order as well as unique pages per subdomain
        file.write("\nQ4: List of subdomain and page per subdomain\n")
        for k,v in sorted(subDomainCount.items(), key=lambda x: x[0]):
            file.write(f"{k} : {v}\n")

        logger.info(f"Saving answers shelve with visited pages of length {len(visitedPages)}")

    except Exception as e:
        print(f"Error writing output: {e}\n")

def loadGlobals(name):
    logger = get_logger("SCRAPER")
    logger.info("Logger called for opening answers shelve") 
    global save1
    global save2
    global save3
    global save4
    global noShelve
    if os.path.exists(name):
        global longestPages, wordCount, subDomainCount, visitedPages
        try:
            d = shelve.open(name)
            longestPages = d['longestPages']
            wordCount = d['wordCount']
            subDomainCount =  d['subDomainCount']
            visitedPages = d['visitedPages']
            logger.info(f"Shelve file found, visited Page len = {len(visitedPages)}") 
            logger.info(f"Size of 4 objects: \nLongestPages:{sys.getsizeof(longestPages)}\nWordCount:{sys.getsizeof(wordCount)}\nSubDomainCount:{sys.getsizeof(subDomainCount)}\nvisitedPages:{sys.getsizeof(visitedPages)} ")
            save1 = shelve.open(sn1, writeback=True)
            save2 = shelve.open(sn2, writeback=True)
            save3 = shelve.open(sn3, writeback=True)
            save4 = shelve.open(sn4, writeback=True)
            for url in visitedPages:
                urlhash = get_urlhash(url)
                save1[urlhash] = url
            save1.sync()

            save2[sn2]=longestPages
            save2.sync()
            
            for k,v in wordCount.items():
                save3[k]=v
            save3.sync()
            
            for k,v in subDomainCount.items():
                save4[k]=v
            save4.sync()


        finally:
            d.close()
            os.remove(name)
            
    else:
        logger.info("Shelve file not found; checking for 2nd version")
        if os.path.exists(sn1) and os.path.exists(sn2) and os.path.exists(sn3) and os.path.exists(sn4):
            logger.info("Shelve file ver 2 found. Loading values")
            save1 = shelve.open(sn1, writeback=True)
            for v in save1.values():
                visitedPages.add(v)
            save2 = shelve.open(sn2, writeback=True)
            longestPages = save2[sn2]
            save3 = shelve.open(sn3, writeback=True)
            for k,v in save3.items():
                wordCount[k] = v 
            save4 = shelve.open(sn4, writeback=True)
            for k,v in save4.items():
                subDomainCount[k] = v
        else:
            logger.info("No shelves found, globals init to 0")
            noShelve = True
