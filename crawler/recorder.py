from bs4 import BeautifulSoup

class Recorder:
    def __init__(self):
        self.uniqueUrls = 0
        self.urls = set()
        self.words = dict()

    def add_words(self, resp):
        soup = BeautifulSoup(resp, features="html.parser")
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
           frequency_list.append({key: self.words[key]})

        sorted_list = sorted(frequency_list, key=lambda word: list(word.values())[0], reverse=True)
        for i in range(50):
            curr_word = sorted_list[i]
            print('{} -> {}'.format(list(curr_word.keys())[0], list(curr_word.values())[0]))