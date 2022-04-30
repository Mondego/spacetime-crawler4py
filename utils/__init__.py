import os
import logging
from hashlib import sha256
from urllib.parse import urlparse
from nltk.probability import FreqDist
import copy


import requests                             # possibly delete this
from bs4 import BeautifulSoup               # delete this?
from math import floor                      # delete this?
import re

stopwords = ["a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't", "as",
             "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can't",
             "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down",
             "during", "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have", "haven't",
             "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself", "him", "himself",
             "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's",
             "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of",
             "off", "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own",
             "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such", "than",
             "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there", "there's", "these",
             "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too", "under",
             "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what",
             "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's",
             "with", "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours",
             "yourself", "yourselves"]


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
    page = requests.get(url)
    soup = BeautifulSoup(page.content.decode("utf-8", "ignore"), "lxml")

    words = (soup.get_text(" ", strip=True)).lower()
    retList = re.sub(r'[a-zA-Z0-9]+', ' ', words)

    retList = set(words.split())
    for word in retList.copy():
        if word in stopwords:
            retList.remove(word)
    return retList

def get_text_freq(text):
    """Returns a dictionary where each key is a token and its respective value is its frequency in argument text"""
    freq_list = sorted(FreqDist(text).items(), key=lambda x:x[1], reverse=True)
    result = dict()
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
    result = dict(int)
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

