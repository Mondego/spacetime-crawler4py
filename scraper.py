import re
import random, string
from urllib.parse import urlparse
from urllib.parse import urldefrag
from bs4 import BeautifulSoup
import csv
import math
import nltk
nltk.download('punkt')
from nltk.tokenize import word_tokenize
from collections import defaultdict
from collections import Counter
from operator import itemgetter
from threading import Lock

from simhash import Simhash, SimhashIndex

# max_word_count_global = dict(word_count = 0, url = '')
# high_freq_words_global = defaultdict(int)
max_word_count_mutex = Lock()
high_freq_word_count_mutex = Lock()
simhash_index_mutex = Lock()
simhash_indexes = SimhashIndex(list(), k=3)
csv_lock = Lock()

def filter_to_allow_subdomains(parsed):
    return  re.match(r".*\.(stat|ics|cs)\.uci\.edu", parsed.netloc.lower()) or (
                re.match(r"today\.uci\.edu", parsed.netloc.lower()) and
                re.match(r"department/information_computer_sciences/.*", parsed.path.lower())
            )

def scraper(url, resp, pages, max_word_count_global, high_freq_words_global):
    links = extract_next_links(url, resp, pages, max_word_count_global, high_freq_words_global)
    # print(links)
    return [link for link in links if is_valid(link)]

def extract_content(soup):
    ex_data = {}
    title = soup.title
    #corner cases handling
    if title is None:  # title is null 
        return ex_data
    if 'error 404' in str(title): # error pages returned w/ text format 
        return ex_data 

    for script in soup(["script", "style"]): # Remove script, style 
        script.extract()
    text = soup.get_text() # get text 
    # data cleaning 
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = [chunk for chunk in chunks if chunk] # make data to list 

    ex_data['title'] = title
    ex_data['text'] = text 
    return ex_data 

def save_contents(content):
    csv_lock.acquire()
    try:
        csv_file = open('scrapped.csv', 'a', encoding='utf-8', newline='')
        writer = csv.writer(csv_file)
        writer.writerow(content.values())
        csv_file.close()
    finally:
        csv_lock.release()

def extract_next_links(url, resp, pages, max_word_count_global, high_freq_words_global):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content

    # Return empty list if 600+ error(maybe want to change for a more specific status code filtering mechanism)
    # if resp.status > 600:
    #     return list()
    new_links = list()
    if resp.status == 200:
        soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
        contents = extract_content(soup)
        if 'title' not in contents: # corner-case exception 
            return new_links
        contents['url'] = url
        pages.add(url)
        save_contents(contents)
        process_content(contents, max_word_count_global, high_freq_words_global)
        for link in soup.find_all('a'):
            extracted_link = link.get('href')
            if extracted_link:
                extracted_link,_ = urldefrag(extracted_link) #defragment URL
            if extracted_link not in pages:
                new_links.append(extracted_link)
    return new_links

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        
        if re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|ppsx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower()):
            return False
        # print("Matching {} and the regex matching is {}".
        #     format(parsed.netloc.lower(), re.match(r".*\.(stat|ics|cs)\.uci\.edu", parsed.netloc.lower())))
        # return re.match(r".*\.(stat|ics|cs)\.uci\.edu", parsed.netloc.lower())
        return filter_to_allow_subdomains(parsed)

    except TypeError:
        print ("TypeError for ", parsed)
        raise

# TODO: Implement this
def process_content(content, max_word_count_global, high_freq_words_global):
    #update max word counts and word freq dict
    tokens = tokenize(content['text'])
    is_close_duplicate = check_close_duplicates(tokens)
    if not is_close_duplicate:
        update_max_count(tokens, content['url'], max_word_count_global)
        update_max_freq_words(tokens, high_freq_words_global)
        #update unique urls
        # update_unique_url(content['url'])
        # with open("processed_text.txt", 'w') as f:
        #     f.write('URL with Max No.of words \n')
        #     for key, value in max_word_count_global.items():
        #         f.write('%s:%s\n' % (key, value))
        #     f.write('50 high freq words \n')
        #     for key, value in high_freq_words_global.items():
        #         f.write('%s:%s\n' % (key, value))

def tokenize(text):
    #read stopwords #stopwords in nltk and prof's link look different
    f = open('stopwords.txt')
    stopwords = f.read().splitlines()
    file_format_text = '\n'.join(phrase for phrase in text if phrase)
    tokens = word_tokenize(file_format_text)
    #filter tokens
    final_tokens = []
    for token in tokens:
        if len(token) < 3 or token.lower() in stopwords or token.isnumeric():
            continue
        final_tokens.append(token.lower())
    return final_tokens

def update_max_count(tokens,url, max_word_count_global):
    # global max_word_count_global
    current_word_count = len(tokens)
    max_word_count_mutex.acquire()
    try:
        if max_word_count_global['word_count'] < current_word_count:
            max_word_count_global['word_count'] = current_word_count
            max_word_count_global['url'] = url
    finally:
        max_word_count_mutex.release()

def update_max_freq_words(tokens, high_freq_words_global):
    # global high_freq_words_global
    current_word_frequencies = defaultdict(int)
    for token in tokens:
        current_word_frequencies[token] += 1
    high_freq_word_count_mutex.acquire()
    try:
        combined_dict = Counter(current_word_frequencies) + Counter(high_freq_words_global)
        #update global dict with top 50 of combined dict
        high_freq_words_global = dict(sorted(combined_dict.items(), key = itemgetter(1), reverse = True)[:50])
    finally:
        high_freq_word_count_mutex.release()


# def update_unique_url(url):
#     #might require preprocessing of URLs before adding them to global set.
#     global unique_urls_global
#     unique_urls_global.add(url)


def check_close_duplicates(tokens):
    s1 = Simhash(tokens)
    simhash_index_mutex.acquire()
    try:
        if len(simhash_indexes.get_near_dups(s1)) == 0:
            simhash_indexes.add(get_random_string(), s1)
            return False
        return True
    finally:
        simhash_index_mutex.release()

def get_random_string():
    return ''.join(random.choices(string.ascii_uppercase +
                             string.digits, k=64))