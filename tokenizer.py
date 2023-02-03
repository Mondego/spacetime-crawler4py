import re
from collections import defaultdict
from bs4 import BeautifulSoup

def tokenize(soup_content):
    #gets all the text from the html page and gets rid of all punctuation except for ' and -
    html_text = re.sub(r'[^\w\'-]+', ' ', soup_content.get_text()) #got the regex formula using ChatGPT
    html_text = re.sub(r'[^\w]+', ' ', html_text) #gets rid of all non alphanumeric
    html_text = html_text.replace("-", " ") #gets rid of the hyphen
    html_text = html_text.lower() #make everything lowercase
    text_list = html_text.split() #puts all the words into a list
    return text_list

def compute_word_frequencies(token_list):
    stopwords = {'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', 'as',
                      'at', 'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by',
                      'cannot', 'could', 'did', 'do', 'does', 'doing', 'down', 'during', 'each', 'few', 'for', 'from',
                      'further', 'had', 'has', 'have', 'having', 'he', 'her', 'here', 'hers', 'herself', 'him',
                      'himself', 'his', 'how', 'i', 'if', 'in', 'into', 'is', 'it', 'its', 'itself', 'me', 'more',
                      'most', 'my', 'myself', 'no', 'nor', 'not', 'of', 'off', 'on', 'once', 'only', 'or', 'other',
                      'ought', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'same', 'she', 'should', 'so', 'some',
                      'such', 'than', 'that', 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there', 'these',
                      'they', 'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was', 'we',
                      'were', 'what', 'when', 'where', 'which', 'while', 'who', 'whom', 'why', 'with', 'would', 'you',
                      'your', 'yours', 'yourself', 'yourselves'}
    apostrophe_stopwords = {"aren't", "can't", "couldn't", "didn't", "doesn't", "don't", "hadn't", "hasn't",
                                 "haven't", "he'd", "he'll", "he's", "here's", "how's", "i'd", "i'll", "i'm", "i've",
                                 "isn't", "it's", "let's", "mustn't", "shan't", "she'd", "she'll", "she's", "shouldn't",
                                 "that's", "there's", "they'd", "they'll", "they're", "they've", "wasn't", "we'd",
                                 "we'll", "we're", "we've", "weren't", "what's", "when's", "where's", "who's", "why's",
                                 "won't", "wouldn't", "you'd", "you'll", "you're", "you've"}
    frequencies = defaultdict(int)
    for token in token_list:
        if (token not in stopwords and token not in apostrophe_stopwords):
            frequencies[token] += 1
    return frequencies

def token_print(frequencies):
    double_sorted = sorted(sorted(frequencies.items(), key=(lambda x: x[0])), key=(lambda x: x[1]), reverse=True)
    for key, value in double_sorted[:50]:
        print(key, value, sep=' - ')


if __name__ == '__main__':
    token_print(compute_word_frequencies(tokenize('README.md', True)))
