import re
from urllib.parse import urlparse,urlunparse,urljoin
import bs4, requests
import csv

response = requests.get('https://www.nytimes.com/',headers={'User-Agent': 'Mozilla/5.0'})





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
        self.page_word_count_file = r"/home/xiaofl/Desktop/cs121/hw2/spacetime-crawler4py/debug_log/page_word_count.csv"
        self.word_count_file = r'/home/xiaofl/Desktop/cs121/hw2/spacetime-crawler4py/debug_log/word_count.csv'
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

#TODO: I am not sure this stats object will be only intialized once 
stats = scraper_stats()

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]
    

def extract_subdomain(url):
    url = urlparse(url)
    subdomain = url.netloc.split('.')
    if len(subdomain) > 3:
        # more than just ics.uci.edu ex. 
        return '.'.join(subdomain[:-3])
    else:
        return None

def remove_fragment(url):
    parsed_url = urlparse(url)
    defrag_page_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, parsed_url.params, parsed_url.query,'' ))
    defrag_page_url= defrag_page_url.rstrip('/')
    return defrag_page_url

def handle_relative_url(base,url):
    if not url.startswith(("http://", "https://")):
        print(f'relative url : {url}, the base is {base}')
        absolute_url = urljoin(base, url)
        return absolute_url
    else:
        return url
    
def extract_next_links(url, resp):
    current_depth = stats.url_depth[resp.url]
    print(f'from scraper: current url is {url}, status is {resp.status}, is there error {resp.error}, current url depth is {stats.url_depth[url]}')
    # print(f'resp.url is {resp.url}')
    # print(f'resp.status is {resp.status}, and type of status is {type(resp.status)} resp.status == 200 is {resp.status == 200}')
    # print(f'resp.error is {resp.error}')
    #TODO: current depth limit is 100, 
    if stats.url_depth[url] > 100:
        return list()
    if resp.status != 200:
        return list()
    
    # Handle redirect url
    if resp.status ==307 or resp.status ==308 :
        url = resp.url 
    
    # TODO: Honor the politeness delay for each site
    # Crawl all pages with high textual information content
    # TODO: Detect and avoid infinite traps
    # TODO: Detect and avoid sets of similar pages with no information
    # TODO: [has confusion] Detect redirects and if the page redirects your crawler, index the redirected content
    # TODO: Detect and avoid dead URLs that return a 200 status but no data (click here to see what the different HTTP status codes mean
    # (https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html) )
    # TODO: Detect and avoid crawling very large files, especially if they have low information value
    MAX_FILE_SIZE = 10 * 1024 * 1024
    print('[test] len of current url content is:',len(resp.raw_response.content))
    if len(resp.raw_response.content)> MAX_FILE_SIZE:
        print(f'the file in url {url} is too large')
        return list()
    
    #collecting subdomain: 
    subdomain = extract_subdomain(url)
    stats.subdomains.add(subdomain)

    
    #TODO: get all text from given url: not sure if the current implementation capture all the text content
    soup = bs4.BeautifulSoup(resp.raw_response.content,'lxml')

    # avoid crawling empty content url 
    if soup.body == None:
        print(f'empty url {url}')
        return list()
    if soup.body:
        text_in_page = soup.body.get_text(' ', strip=True)
        print(f'***[test] the len of text in page is {len(text_in_page)} content is {text_in_page}')
        stats.update_stats(url=url,text=text_in_page)
    
    #TODO: for next urls: 
    url_list = []
    for link in soup.find_all("a"):
        page_url = link.get('href')
        if page_url:
            #TODO: handle how to collect stats with fragment urls: counting unique page
            defrag_page_url = remove_fragment(page_url)
            defrag_page_url = handle_relative_url(base=url,url=defrag_page_url)
            stats.url_depth[defrag_page_url] = current_depth +1
            if "#" in defrag_page_url:
                print(f'*******[warning] this url {defrag_page_url} has fragment origin is {page_url}')
            # assert '#' not in defrag_page_url, f'{defrag_page_url} has fragment, fragment should be deleted'
            
            # prevent duplicate
            elif "#" not in defrag_page_url and defrag_page_url not in stats.page_word_count:
                url_list.append(defrag_page_url)
    # print(f'what is the content: {text_in_page}')
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    # assert False, 'force to stop here'
    # print(f'current url list {url_list}')
    return url_list

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        
        ## make sure the url is under the given domains, if not return false
        valid_domains = [
            "ics.uci.edu",
            "cs.uci.edu",
            "informatics.uci.edu",
            "stat.uci.edu"
        ]
        if not any(domain in parsed.netloc for domain in valid_domains):
            return False
        
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise

