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
    stopwords = {'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', "aren't",
                 'as', 'at', 'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by',
                 "can't", 'cannot', 'could', "couldn't", 'did', "didn't", 'do', 'does', "doesn't", 'doing', "don't",
                 'down', 'during', 'each', 'few', 'for', 'from', 'further', 'had', "hadn't", 'has', "hasn't", 'have',
                 "haven't", 'having', 'he', "he'd", "he'll", "he's", 'her', 'here', "here's", 'hers', 'herself', 'him',
                 'himself', 'his', 'how', "how's", 'i', "i'd", "i'll", "i'm", "i've", 'if', 'in', 'into', 'is', "isn't",
                 'it', "it's", 'its', 'itself', "let's", 'me', 'more', 'most', "mustn't", 'my', 'myself', 'no', 'nor',
                 'not', 'of', 'off', 'on', 'once', 'only', 'or', 'other', 'ought', 'our', 'ours', 'ourselves', 'out',
                 'over', 'own', 'same', "shan't", 'she', "she'd", "she'll", "she's", 'should', "shouldn't", 'so',
                 'some', 'such', 'than', 'that', "that's", 'the', 'their', 'theirs', 'them', 'themselves', 'then',
                 'there', "there's", 'these', 'they', "they'd", "they'll", "they're", "they've", 'this', 'those',
                 'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was', "wasn't", 'we', "we'd", "we'll",
                 "we're", "we've", 'were', "weren't", 'what', "what's", 'when', "when's", 'where', "where's", 'which',
                 'while', 'who', "who's", 'whom', 'why', "why's", 'with', "won't", 'would', "wouldn't", 'you', "you'd",
                 "you'll", "you're", "you've", 'your', 'yours', 'yourself', 'yourselves'}
    frequencies = defaultdict(int)
    for token in token_list:
        if (token not in stopwords):
            frequencies[token] += 1
    return frequencies


def token_print(frequencies):
    double_sorted = sorted(sorted(frequencies.items(), key=(lambda x: x[0])), key=(lambda x: x[1]), reverse=True)
    for key, value in double_sorted[:50]:
        print(key, value, sep=' - ')


if __name__ == '__main__':
    token_print(compute_word_frequencies(tokenize('<p>This is a test</p>')))
