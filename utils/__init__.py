import os
import logging
from hashlib import sha256
from urllib.parse import urlparse

import nltk                             # potentially  delete this
from nltk.corpus import stopwords      # possibly delete this
from nltk.stem import PorterStemmer     # possibly delete this
from nltk.tokenize import RegexpTokenizer # possibly delete this
import requests                             # possibly delete this
from bs4 import BeautifulSoup               # delete this?
from math import floor                      # delete this?
from collections import defaultdict         # delete this
import re

def get_logger(name, filename=None):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    if not os.path.exists("Logs"):
        os.makedirs("Logs")
    fh = logging.FileHandler(f"Logs/{filename if filename else name}.log")
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter(
       "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger


def get_urlhash(url):
    parsed = urlparse(url)
    # everything other than scheme.
    return sha256(
        f"{parsed.netloc}/{parsed.path}/{parsed.params}/"
        f"{parsed.query}/{parsed.fragment}".encode("utf-8")).hexdigest()

def normalize(url):
    if url.endswith("/"):
        return url.rstrip("/")
    return url

def tokenize_n_preprocess(url):
    stop_words=set(stopwords.words("english"))  # get the stop_words in english
    stemmer = PorterStemmer()  # create a PorterStemmer object to stem any word
    tokenizer = RegexpTokenizer("\w+") # only tokenize words
    page = requests.get(url)
    soup = BeautifulSoup(page.content.decode("utf-8", "ignore"), "lxml")
    text_list = [stemmer.stem(word) for word in tokenizer.tokenize(soup.text.lower()) if word not in stop_words]
    return text_list

def get_text_freq(text):
    """Returns a dictionary where each key is a token and its respective value is its frequency in argument text"""
    freq_list = sorted(nltk.FreqDist(text).items(), key=lambda x:x[1], reverse=True)
    result = defaultdict(int)
    for pair in freq_list:
        result[pair[0]] = pair[1]
    return result

def how_many_subdomains(url, sub_domains):
    """Finds how many subdomains in ics.uci.edu"""
    parsed = urlparse(url)
    page = str(parsed.scheme + "://" + parsed.netloc + parsed.path)
    if url.find('ics.uci.edu') > 0:
        sub_domains[page] += 1
    return sub_domains

# Assignment 1 Code
def tokenize(filename):
    retList = []
    with open(filename, "r", encoding="utf8") as file:
        for line in file:
            retList += re.findall(r'[a-zA-Z0-9]+', line)
    return retList

# Assignment 1 Code
# iterating through the list made in tokenize and creating a dict O(n)
# Final O(n)
def computeWordFrequencies(tokenList):
    d = defaultdict(int)
        
    for i in tokenList:
            d[i.lower()] += 1

    return d

# Assignment 1 Code
# sort dictionary in order O(n log n)
# iterate through dictionary O(n)
# Final O(n) + O(n log n) = O(n)
def print_formatted(fc3i):
    tStr = ""
    fc3 = sorted(fc3i.items(), key=lambda x: x[1], reverse=True)
    for i in fc3:
        tStr += str(f"{i[0]} -> {i[1]} ")
    print(tStr)
    
# Assignment 1 Code
def intersect(f1, f2):
    f1list = pa.tokenize(f1)
    f2list = pa.tokenize(f2)

    f1set = set()
    f2set = set()

    for i in f1list:
        f1set.add(i.lower())

    for i in f2list:
        f2set.add(i.lower())

    print (len(f1set.intersection(f2set)))

# NEW CODE TO IMPLEMENT
# def get_content_info(url, current_longest,  current_subdomain_count, current_most_common_words, top_words=50):
#     LOW_INFORMATION_VALUE = 100  
    
#     page = requests.get(url)
#     soup = BeautifulSoup(page.content, "lxml")
#     text = soup.text
#     token_list = tokenize(text)
#     word_frequencies = computeWordFrequencies(token_list)

#     # gets url content hash
#     if len(token_list) <= LOW_INFORMATION_VALUE:
#         hash_ = sha256("error".encode("utf-8")).hexdigest() # return a consistent hash key error
#     else:
#         frequency_dict = get_text_freq(text) 
#         threshold_near_duplicate = floor(len(frequency_dict) * 0.80)
#         top_text = " ".join(list(frequency_dict.keys())[:threshold_near_duplicate]) # top 80% of most frequent tokens in web page
#         hash_ =  sha256(top_text.encode("utf-8", errors="replace")).hexdigest()
    
#     # updates longest text num
#     if len(text_list) >= current_longest:
#         current_longest = len(text_list)

#     # updates most common words
#     new_most_common = get_text_freq(text)
#     result = defaultdict(int)
#     count = 0
#     for new_pair, cur_pair in zip(new_most_common.items(), current_most_common_words.items()):
#         if count >= top_words:
#             break
#         result[new_pair[0]] += new_pair[1]
#         result[cur_pair[0]] += cur_pair[1]
#         count += 1
    
#     # update subdomain dict
#     current_subdomain_count = how_many_subdomains(url, current_subdomain_count)
    
#     return hash_, current_longest, current_subdomain_count, result


"""
ARCHIVED CODE BELOW
"""

def get_content_info(url, current_longest,  current_subdomain_count, current_most_common_words, top_words=50):
    LOW_INFORMATION_VALUE = 100  
    
    text_list = tokenize_n_preprocess(url)
    text = " ".join(text_list)

    # gets url content hash
    if len(text_list) <= LOW_INFORMATION_VALUE:
        hash_ = sha256("error".encode("utf-8")).hexdigest() # return a consistent hash key error
    else:
        frequency_dict = get_text_freq(text) 
        threshold_near_duplicate = floor(len(frequency_dict) * 0.80)
        top_text = " ".join(list(frequency_dict.keys())[:threshold_near_duplicate]) # top 80% of most frequent tokens in web page
        hash_ =  sha256(top_text.encode("utf-8", errors="replace")).hexdigest()
    
    # updates longest text num
    if len(text_list) >= current_longest:
        current_longest = len(text_list)

    # updates most common words
    new_most_common = get_text_freq(text)
    result = defaultdict(int)
    count = 0
    for new_pair, cur_pair in zip(new_most_common.items(), current_most_common_words.items()):
        if count >= top_words:
            break
        result[new_pair[0]] += new_pair[1]
        result[cur_pair[0]] += cur_pair[1]
        count += 1
    
    # update subdomain dict
    current_subdomain_count = how_many_subdomains(url, current_subdomain_count)
    
    return hash_, current_longest, current_subdomain_count, result

# potentially delete this
# def get_contenthash(url):
#     LOW_INFORMATION_VALUE = 100    
#     text_list = tokenize_n_preprocess(url)

#     if len(text_list) <= LOW_INFORMATION_VALUE:
#         return sha256("error".encode("utf-8")).hexdigest() # return a consistent hash key error
#     else:
#         text = " ".join(text_list)
#         frequency_dict = get_text_freq(text) 
#         threshold_near_duplicate = floor(len(frequency_dict) * 0.90)
#         top_text = " ".join(list(frequency_dict.keys())[:threshold_near_duplicate]) # top 90% of most frequent tokens in web page
#         return sha256(top_text.encode("utf-8", errors="replace")).hexdigest()

# potentially delete this
# def get_longest_text(url, current_longest):
#     text_list = tokenize_n_preprocess(url)
#     if len(text_list) >= current_longest:
#         return len(text_list)
#     else:
#         return current_longest  

# DON'T USE THIS
# def update_most_common_words(url, current_most_common_words, top_words=50):
#     """Updates top 50 most common words"""
#     text_list = tokenize_n_preprocess(url)
#     text = " ".join(text_list)
#     new_most_common = get_text_freq(text)
#     result = defaultdict(int)
#     count = 0
#     for new_pair, cur_pair in zip(new_most_common.items(), current_most_common_words.items()):
#         if count >= top_words:
#             break
#         result[new_pair[0]] += new_pair[1]
#         result[cur_pair[0]] += cur_pair[1]
#         count += 1
    
#     return result

    



    