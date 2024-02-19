import re
from urllib.parse import urlparse, urljoin, urldefrag
from bs4 import BeautifulSoup
from collections import Counter
from collections import defaultdict
from simhash import Simhash
import csv
# from simhash import Simhash, SimhashIndex

class ScraperStats:
    """
    this class is called in scraper and launch for update the stats after program finish run
    this class handle to collect stats for: 
        1. word count 
        2. longest page with word number 
        3. unique pages 
        4. simhash values for unique pages 
        5. subdomains 
        6. crawled urls 
    this class also has helper function to 
        1. save stats to csv file 
        2. compute the simhash 
    and store stop words
    """

    def __init__(self):
        # tracks how many unique pages visited
        self.unique_pages = 0
        # Variable that tracks the longest page we've found
        self.longest_page = 0
        # tracks the most common 50 words
        self.word_count = Counter()
        # counts the number of subdomains (Using it to answer this question: How many subdomains did you find in the ics.uci.edu domain? )
        self.num_subdomains = {}
        self.stop_words = set(["a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during", "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves"])
        
        self.TRAP_PARAMS = {"action=download","action=login","action=edit"}
        # depth["ics.uci.edu/event"] = 3 
        # Keeps track of depth of domain
        self.domain_counts = defaultdict(int)
        self.trap_urls = []

        ####################################################
        # Lucas Changes: 

        self.crawled_urls = set()
        self.subdomains = set()
        self.page_with_most_text = {'url':'','wordcount':0}

        ## save to csv
        self.page_word_count_file = r"./debug_log/page_word_count.csv"
        self.trap_detection_file = r'./debug_log/trap_file.csv'
        self.subdomains_file = r'./debug_log/subdomains_file.csv'
        self.final_subdomains_file = r'./debug_log/final_subdomains_file.csv'
        self.redirect_file = r'./debug_log/redirect_file.csv'
        self.crawled_urls_file = r'./debug_log/crawled_urls_file.csv'
        self.word_count_file = r'./debug_log/word_count_file.csv'
        ## for robot.txt
        self.allowed_path = set()
        self.disallowed_path = set()

        ## for repeat detection
        self.repeat_url_counter = defaultdict(int)
        ####################################################

        #n-grams
        self.grams=3
        #simhash_index stores all the simhash values for all the pages
        self.simhash_index=list()
        self.dup_count=0

    def update_pages(self):
        self.unique_pages += 1
        print("UNIQUE_PAGES: ",self.unique_pages)

    def update_traps(self, url):
        self.trap_urls.append(url)
    
    def update_longest_page(self, text):
        words = text.split()
        currLen = len(words)
        if currLen > self.longest_page:
            self.longest_page = currLen
    
    def update_word_count(self, text):
        words = re.findall(r'\b[a-z]{3,}\b', text.lower())
        filtered_words = [word for word in words if word not in self.stop_words]
        # print(f'filtered words',filtered_words)
        self.word_count.update(filtered_words)
    
    def update_subdomain_count(self, url):
        parsed_url = urlparse(url)
        if parsed_url.netloc.endswith("ics.uci.edu"):
            subdomain = parsed_url.netloc
        else:
            subdomain = None

        if subdomain:
            if subdomain not in self.num_subdomains:
                self.num_subdomains[subdomain] = 0
            self.num_subdomains[subdomain] += 1
    
    def report(self):
        # return f'Unique Pages: {self.unique_pages}. Top 50 words: {self.word_count.most_common(50)}'
        return f'Unique Pages: {self.unique_pages}. Num Subdomains: {self.num_subdomains}'

    def print_unique_pages(self):
        # return f'Unique Pages: {self.unique_pages}. Top 50 words: {self.word_count.most_common(50)}'
        return f'Unique Pages: {self.unique_pages}'
    
    
    ## Lucas's functions: 
    # only need to keep track the most words' url and word count,
    # and trap urls to see if the trap we detect are actual trap 
    # and subdomain csv to store all unique subdomain from ics.uci.edu
    def update_csv(self,url,csv_file,count = 0,redirect = ''):
        with open(csv_file, mode='a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['URL', 'Word Count',"redirect"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow({'URL': url, 'Word Count': count,'redirect':redirect})
            
    def print_word_count(self):
        top_50 = self.word_count.most_common(50)
        print(top_50)
    
    def update_word_count_csv(self):
        with open(self.word_count_file, mode='a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['word', 'Count']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            top_50 = self.word_count.most_common(50)
            print(f'top 50 is {top_50}')
            for word, count in top_50:
                print(f'word {word}: count: {count}')
                writer.writerow({'word': word, 'Count': count})

    def get_features(self,tokens):
        # Extract features using a sliding window of width 3
        features = ["".join(tokens[i:i + self.grams]) for i in range(max(len(tokens) - self.grams + 1, 1))]
        return features

    def compute_simhash(self,text):
        words = re.findall(r'\b\w+\b', text.lower())
        # Extract features from tokens
        features = self.get_features(words)
        # Calculate the Simhash value for the features
        return Simhash(features)

    def is_near_duplicate(self,text,url):
        # Check if the Simhash value for the given html_doc is similar to any previously crawled pages
        simhash_class = self.compute_simhash(text)
        
        # if list is empty add the current simhash class
        if len(self.simhash_index) == 0: 
            self.simhash_index.append(simhash_class)
        else: 
            for simhash in self.simhash_index:
                if simhash_class.similarity(simhash) > 0.75:
                    print(f'duplicate url {url}')
                    self.dup_count+=1
                    return True
            # if pass the for loop check add this unique class to list and return false
            self.simhash_index.append(simhash_class)
            return False
        
    def subdomain_unique_pages(self):
        subdomain_stats = {}
        for url in self.subdomains:
            parsed_url = urlparse(url)
            subdomain = parsed_url.netloc
            path = parsed_url.path
            if subdomain not in subdomain_stats:
                subdomain_stats[subdomain] = set()
            subdomain_stats[subdomain].add(path)

        result = {}
        sorted_subdomains = sorted(subdomain_stats.keys())
        for subdomain in sorted_subdomains:
            result[subdomain] = len(subdomain_stats[subdomain])
        for s, l in result.items():
            print(s, ' : ',l)
            self.update_csv(s,self.final_subdomains_file,count=l)
        return result



stats = ScraperStats()