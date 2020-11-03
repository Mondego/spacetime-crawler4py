from bs4 import BeautifulSoup

class Recorder:
    def __init__(self):
        self.uniqueUrls = 0
        self.urls = set()
        self.words = dict()

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

    def add_words(self, resp):
        soup = BeautifulSoup(resp, features="html.parser", from_encoding="iso-8859-1")
        text = soup.get_text()
        # Code taken from Assignment 1 Part A
        # Mapping all the words from the line to be lowercase while also spiting the word into a list by whitespace
        resp_words = list(map(lambda x: x.lower().strip(), text.split(' ')))

        # filtering out all the non alphanumeric chars
        resp_words = list(map(lambda word: ''.join(list(filter(lambda x: x.isalnum(), [char for char in word]))), resp_words))

        resp_words = list(filter(lambda word: word != '', resp_words))

        for word in resp_words:
            if word in self.words:
                self.words[word] += 1
            else:
                self.words[word] = 1

    def add_url(self, url):
        len_before = len(self.urls)
        self.urls.add(url)
        if(len(self.urls) != len_before):
            self.uniqueUrls += 1

    def already_scrapped(self, url):
        return url in self.urls

    def print_report(self):
        print('Unique pages: {}'.format(self.uniqueUrls))
        print('Most common words:')

        # getting the 50 most common words
        frequency_list = []
        for key in self.words:
            if self.is_stop_word(key):
                continue
            frequency_list.append({key: self.words[key]})

        sorted_list = sorted(frequency_list, key=lambda word: list(word.values())[0], reverse=True)
        for i in range(50):
            curr_word = sorted_list[i]
            print('{} -> {}'.format(list(curr_word.keys())[0], list(curr_word.values())[0]))