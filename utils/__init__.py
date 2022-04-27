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

# potentially delete this
def tokenize_n_preprocess(url):
    stop_words=set(stopwords.words("english"))  # get the stop_words in english
    stemmer = PorterStemmer()  # create a PorterStemmer object to stem any word
    tokenizer = RegexpTokenizer("\w+") # only tokenize words
    page = requests.get(url)
    soup = BeautifulSoup(page.content.decode("utf-8", "ignore"), "lxml")
    text_list = [stemmer.stem(word) for word in tokenizer.tokenize(soup.text.lower()) if word not in stop_words]
    return text_list

# potentially delete this
def get_contenthash(url):
    LOW_INFORMATION_VALUE = 100    
    text_list = tokenize_n_preprocess(url)

    if len(text_list) <= LOW_INFORMATION_VALUE:
        return sha256("error".encode("utf-8")).hexdigest() # return a consistent hash key error
    else:
        text = " ".join(text_list)
        frequency_dict = get_text_freq(text) 
        threshold_near_duplicate = floor(len(frequency_dict) * 0.90)
        top_text = " ".join(list(frequency_dict.keys())[:threshold_near_duplicate]) # top 90% of most frequent tokens in web page
        return sha256(top_text.encode("utf-8", errors="replace")).hexdigest()

# potentially delete this
def get_longest_text(url, current_longest):
    text_list = tokenize_n_preprocess(url)
    if len(text_list) >= current_longest:
        return len(text_list)
    else:
        return current_longest  

def get_text_freq(text):
    """Returns a dictionary where each key is a token and its respective value is its frequency in argument text"""
    freq_list = sorted(nltk.FreqDist(text).items(), key=lambda x:x[1], reverse=True)
    result = defaultdict(int)
    for pair in freq_list:
        result[pair[0]] = pair[1]
    return result

def update_most_common_words(url, current_most_common_words, top_words=50):
    """Updates top 50 most common words"""
    text_list = tokenize_n_preprocess(url)
    text = " ".join(text_list)
    new_most_common = get_text_freq(text)
    result = defaultdict(int)
    count = 0
    for new_pair, cur_pair in zip(new_most_common.items(), current_most_common_words.items()):
        if count >= top_words:
            break
        result[new_pair[0]] += new_pair[1]
        result[cur_pair[0]] += cur_pair[1]
        count += 1
    
    return result

def how_many_subdomains(url, sub_domains):
    """Finds how many subdomains in ics.uci.edu"""
    parsed = urlparse(url)
    page = parsed.scheme + "://" + parsed.netloc + parsed.path
    if url.find('ics.uci.edu') > 0:
        sub_domains[page] += 1

def get_content_info(url, current_longest, current_most_common_words, current_subdomain_count, top_words=50):
    LOW_INFORMATION_VALUE = 100    
    text_list = tokenize_n_preprocess(url)
    text = " ".join(text_list)

    # gets url content hash
    if len(text_list) <= LOW_INFORMATION_VALUE:
        hash = sha256("error".encode("utf-8")).hexdigest() # return a consistent hash key error
    else:
        frequency_dict = get_text_freq(text) 
        threshold_near_duplicate = floor(len(frequency_dict) * 0.90)
        top_text = " ".join(list(frequency_dict.keys())[:threshold_near_duplicate]) # top 90% of most frequent tokens in web page
        hash =  sha256(top_text.encode("utf-8", errors="replace")).hexdigest()
    
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
    how_many_subdomains(url, current_subdomain_count)
    
    return hash, current_longest, current_subdomain_count, result




    



    