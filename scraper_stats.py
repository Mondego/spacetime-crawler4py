import csv
import re
class scraper_stats:
    """
    1. How many unique pages did you find? Uniqueness for the purposes of this assignment is ONLY established by the URL, but
    discarding the fragment part. So, for example, http://www.ics.uci.edu#aaa and http://www.ics.uci.edu#bbb are the same URL. Even if
    you implement additional methods for textual similarity detection, please keep considering the above definition of unique pages for the
    purposes of counting the unique pages in this assignment.
    2. What is the longest page in terms of the number of words? (HTML markup doesn’t count as words)
    3. What are the 50 most common words in the entire set of pages crawled under these domains ? (Ignore English stop words, which
    can be found, for example, here
    (https://www.ranks.nl/stopwords) ) Submit the list of common words ordered by frequency.
    4. How many subdomains did you find in the ics.uci.edu domain? Submit the list of subdomains ordered alphabetically and the number of
    unique pages detected in each subdomain. The content of this list should be lines containing URL, number, for example:
    http://vision.ics.uci.edu, 10 (not the actual number here)
    """
    def __init__(self) -> None:
        self.word_count_dict = dict()
        self.page_word_count = dict()
        # self.page_word_count_file = r"/home/xiaofl/Desktop/cs121/hw2/spacetime-crawler4py/debug_log/page_word_count.csv"
        # self.word_count_file = r'/home/xiaofl/Desktop/cs121/hw2/spacetime-crawler4py/debug_log/word_count.csv'
        self.page_word_count_file = r"./debug_log/page_word_count.csv"
        self.word_count_file = r'./debug_log/word_count.csv'
        self.abnormal_file = r'./debug_log/abnormal_file.csv'
        self.subdomains_file = r'./debug_log/subdomains_file.csv'
        self.stop_words = ["a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during", "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves"]
        
        #TODO: avoid infinite trap by set up depth limits, 100 might be good? 
        self.url_depth = {'https://www.ics.uci.edu':0,
                          'https://www.cs.uci.edu':0,
                          'https://www.informatics.uci.edu':0,
                          'https://www.stat.uci.edu':0}

        # TODO: how to find the subdomains of a given url
        self.subdomains = set()
    
    #TODO: how to collect the number of subdomains
        
    def report_the_stats(self):
        # need to avoid the stop words:
        print(f'word count: {self.word_count_dict}')
        print()
        print(f'word per page: {self.page_word_count}')

    def update_stats(self,url,text):

        # TODO: should I used the tokenized text or before tokenize, 
        # currently is using soup.body.get_text(), it may include many symbols
        tokenized = self.tokenize(text)
        self.update_page_word_count_csv(url,len(tokenized))
        self.update_count_words_csv(tokenized)

    def tokenize(self,text):
        PATTERN = r"\b(?:\w+(?:[-'\u2019]\w+)*|\w+)\b"
        text = text.lower()
        filtered = re.findall(PATTERN, text)
        return filtered
    
    def update_subdomain_csv(self, url):
        with open(self.subdomains_file, mode='a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['URL','reason']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            # if there are fragment, there should have redundant url
            writer.writerow({'URL': url})
    
    def update_abnormal_url_csv(self, url,reason):
        with open(self.abnormal_file, mode='a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['URL','reason']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            # if there are fragment, there should have redundant url
            writer.writerow({'URL': url,'reason':reason})
            
    def update_page_word_count_csv(self, url, word_count):
        with open(self.page_word_count_file, mode='a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['URL', 'Word Count']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            # if there are fragment, there should have redundant url
            writer.writerow({'URL': url, 'Word Count': word_count})

    def update_count_words_csv(self,filtered:str):
        # TODO: improve the regular expression pattern 
    
        for t in filtered:
            if t not in self.stop_words:
                if t not in self.word_count_dict:
                    self.word_count_dict[t] = 1
                else:
                    self.word_count_dict[t] +=1
        # update the word count csv
        with open(self.word_count_file, mode='w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Word', 'Count']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            for word, count in self.word_count_dict.items():
                writer.writerow({'Word': word, 'Count': count})

stats = scraper_stats()