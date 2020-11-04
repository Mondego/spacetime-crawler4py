from bs4 import BeautifulSoup
from urllib.parse import urlparse
import json
import sys

class Recorder:
    def __init__(self):
        self.uniqueUrls = 0
        self.urls = set()
        self.words = dict()
        self.longestUrlContent = 0
        self.longestUrl = ''
        self.uniqueDomains = dict()

        if ('--restart' not in sys.argv):
            self.load_data()

    def save(self):
        misc_stats = {}
        misc_stats['uniqueUrls'] = self.uniqueUrls
        misc_stats['longestUrl'] = self.longestUrl
        misc_stats['longestUrlContent'] = self.longestUrlContent
        with open('misc_stats.json', 'w') as outfile:
            json_dump = json.dumps(misc_stats, indent=4)
            print(json_dump, file=outfile)

        with open('domainCount.json', 'w') as outfile:
            json_dump = json.dumps(self.uniqueDomains, indent=4)
            print(json_dump, file=outfile)

        with open('word_count.json', 'w') as outfile:
            json_dump = json.dumps(self.words, indent=4)
            print(json_dump, file=outfile)

        urls = list(self.urls)
        urls_obj = {}
        urls_obj['urls'] = urls
        with open('urls.json', 'w') as outfile:
            json_dump = json.dumps(urls_obj, indent=4)
            print(json_dump, file=outfile)

    def load_data(self):
        with open('word_count.json') as json_file:
            self.words = json.load(json_file)

        with open('domainCount.json') as json_file:
            self.uniqueDomains = json.load(json_file)

        with open('misc_stats.json') as json_file:
            data = json.load(json_file)
            self.uniqueUrls = data['uniqueUrls']
            self.longestUrl = data['longestUrl']
            self.longestUrlContent = data['longestUrlContent']
        
        with open('urls.json') as json_file:
            self.urls = set(json.load(json_file)['urls'])

    def is_stop_word(self, word):
        stop_words = [
            "a",
            "about",
            "above",
            "after",
            "again",
            "against",
            "all",
            "am",
            "an",
            "and",
            "any",
            "are",
            "aren't",
            "as",
            "at",
            "be",
            "because",
            "been",
            "before",
            "being",
            "below",
            "between",
            "both",
            "but",
            "by",
            "cant",
            "cannot",
            "could",
            "couldnt",
            "did",
            "didnt",
            "do",
            "does",
            "doesnt",
            "doing",
            "dont",
            "down",
            "during",
            "each",
            "few",
            "for",
            "from",
            "further",
            "had",
            "hadnt",
            "has",
            "hasnt",
            "have",
            "havent",
            "having",
            "he",
            "hed",
            "hell",
            "hes",
            "her",
            "here",
            "heres",
            "hers",
            "herself",
            "him",
            "himself",
            "his",
            "how",
            "hows",
            "i",
            "id",
            "ill",
            "im",
            "ive",
            "if",
            "in",
            "into",
            "is",
            "isnt",
            "it",
            "its",
            "its",
            "itself",
            "lets",
            "me",
            "more",
            "most",
            "mustnt",
            "my",
            "myself",
            "no",
            "nor",
            "not",
            "of",
            "off",
            "on",
            "once",
            "only",
            "or",
            "other",
            "ought",
            "our",
            "ours	ourselves",
            "out",
            "over",
            "own",
            "same",
            "shant",
            "she",
            "shed",
            "shell",
            "shes",
            "should",
            "shouldnt",
            "so",
            "some",
            "such",
            "than",
            "that",
            "thats",
            "the",
            "their",
            "theirs",
            "them",
            "themselves",
            "then",
            "there",
            "theres",
            "these",
            "they",
            "theyd",
            "theyll",
            "theyre",
            "theyve",
            "this",
            "those",
            "through",
            "to",
            "too",
            "under",
            "until",
            "up",
            "very",
            "was",
            "wasnt",
            "we",
            "wed",
            "well",
            "were",
            "weve",
            "were",
            "werent",
            "what",
            "whats",
            "when",
            "whens",
            "where",
            "wheres",
            "which",
            "while",
            "who",
            "whos",
            "whom",
            "why",
            "whys",
            "with",
            "wont",
            "would",
            "wouldnt",
            "you",
            "youd",
            "youll",
            "youre",
            "youve",
            "your",
            "yours",
            "yourself",
            "yourselves"
        ]

        return word in stop_words

    def add_words(self, resp, url):
        soup = BeautifulSoup(resp, features="html.parser", from_encoding="iso-8859-1")
        text = soup.get_text()
        # Code taken from Assignment 1 Part A
        # Mapping all the words from the line to be lowercase while also spiting the word into a list by whitespace
        resp_words = list(map(lambda x: x.lower().strip(), text.split(' ')))

        # filtering out all the non alphanumeric chars
        resp_words = list(map(lambda word: ''.join(list(filter(lambda x: x.isalnum(), [char for char in word]))), resp_words))

        resp_words = list(filter(lambda word: len(word) > 1, resp_words))

        for word in resp_words:
            if word in self.words:
                self.words[word] += 1
            else:
                self.words[word] = 1
        
        if len(resp_words) > self.longestUrlContent:
            print('Found new longest page: {} words'.format(len(resp_words)))
            self.longestUrlContent = len(resp_words)
            self.longestUrl = url

    def add_url(self, url):
        len_before = len(self.urls)
        self.urls.add(url)
        if(len(self.urls) != len_before):
            self.uniqueUrls += 1

        # counting the number of pages in each domain
        netloc = urlparse(url).netloc
        if netloc in self.uniqueDomains:
            self.uniqueDomains[netloc] += 1
        else:
            self.uniqueDomains[netloc] = 1

    def finish_crawl_report(self):
        self.save()