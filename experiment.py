from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse,urlunparse
# urls = ['.stat.uci.edu/','.informatics.uci.edu/','.cs.uci.edu/','.ics.uci.edu/']
urls = ['https://stat.uci.edu/',
        'https://informatics.uci.edu/',
        'https://cs.uci.edu/',
        'https://ics.uci.edu/']
import os, sys, re
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import urllib.request, urllib.error, urllib.parse

def download_page_content(urls):
    for url in urls:

        response = urllib.request.urlopen(url)
        webContent = response.read().decode('UTF-8')
        name = url.split('.')[0]
        tag_name = name.split('//')[1]
        with open(f"/home/xiaofl/Desktop/cs121/hw2/spacetime-crawler4py/web_page/{tag_name}.html",'w') as f:
            f.write(webContent)
"""
find the Site map with: https://ics.uci.edu/feed/ ??? 
"""
    # savePage(url,)
def tokenize(text):
    PATTERN = r"\b(?:\w+(?:[-'\u2019]\w+)*|\w+)\b"
    text = text.lower()
    filtered = re.findall(PATTERN, text)
    return filtered

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
    
def find_all_pages(url:str):
    # current ly save all pages in a file 
    grab = requests.get(url)
    soup = BeautifulSoup(grab.content, 'lxml')
    if soup.body: 
        text_in_page = soup.body.get_text(' ', strip=True)
        tokenized_text= tokenize(text_in_page)
        print(f'***[test] the len of text in page is {len(tokenized_text)} content is {text_in_page}')
    for link in soup.find_all("a"):
        page_url = link.get('href')
        
        if page_url:
            #TODO: handle how to collect stats with fragment urls: counting unique page
            defrag_page_url = remove_fragment(page_url)
            absolute_url = handle_relative_url(base=url, url=defrag_page_url)
            print(absolute_url)
            # stats.url_depth[defrag_page_url] = current_depth +1
            if "#" in defrag_page_url:
                print(f'*******[warning] this url {defrag_page_url} has fragment origin is {page_url}')
    # with open("test1.txt", "w") as f: 
    # # traverse paragraphs from soup
    #     for link in soup.find_all("a"):
    #         data = link.get('href')
    #         f.write(data)
    #         f.write("\n")
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
def parse_robots_txt(domain):
    robots_txt_url = f"http://{domain}/robots.txt"
    try:
        response = requests.get(robots_txt_url)
        print(f'http://{domain}/robots.txt allow for robot')
        if response.status_code == 200:
            return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {robots_txt_url}: {e}")
    return ""
valid_domains = [
            "ics.uci.edu",
            "cs.uci.edu",
            "informatics.uci.edu",
            "stat.uci.edu"
        ]
# for d in valid_domains:
#     print(parse_robots_txt(d))
    
# print(is_valid(' '))
# find_all_pages('https://stat.uci.edu/')
# print(urljoin('https://stat.uci.edu/','mailto:communications@ics.uci.edu'))
# # print(tokenize('This\u2019is\u2019a'))
# print(remove_fragment('https://ics.uci.edu/happening/news/?filter%5Bunits%5D=19'))
# print(remove_fragment('https://recruit.ap.uci.edu/apply#donald-bren-school-of-information-and-computer-sciences'))
# import csv

# csvfile = r"/home/xiaofl/Desktop/cs121/hw2/spacetime-crawler4py/debug_log/experiment.csv"
# experiment = r'/home/xiaofl/Desktop/cs121/hw2/spacetime-crawler4py/debug_log/word_count.csv'
# with open(experiment, mode='a',newline='\n',encoding='utf-8') as csvfile:
#     t = '1111111wwwwwwwweeqwqwrqqweqwe'
#     filename = ['Word','Count']
#     writer = csv.DictWriter(csvfile,fieldnames=filename)
#     writer.writerow({'Word':'department','Count':500})

    
import requests
from bs4 import BeautifulSoup 
import time

from scraper_stats import scraper_stats
stats = scraper_stats()

def tokenizer(text):
    PATTERN = r"\b(?:\w+(?:[-'\u2019]\w+)*|\w+)\b"
    text = text.lower()
    filtered = re.findall(PATTERN, text)
    return filtered

def remove_stop_words(tokenize_text):
    stop_words = set(["0o", "0s", "3a", "3b", "3d", "6b", "6o", "a", "a1", "a2", "a3", "a4", "ab", "able", "about", "above", "abst", "ac", "accordance", "according", "accordingly", "across", "act", "actually", "ad", "added", "adj", "ae", "af", "affected", "affecting", "affects", "after", "afterwards", "ag", "again", "against", "ah", "ain", "ain't", "aj", "al", "all", "allow", "allows", "almost", "alone", "along", "already", "also", "although", "always", "am", "among", "amongst", "amoungst", "amount", "an", "and", "announce", "another", "any", "anybody", "anyhow", "anymore", "anyone", "anything", "anyway", "anyways", "anywhere", "ao", "ap", "apart", "apparently", "appear", "appreciate", "appropriate", "approximately", "ar", "are", "aren", "arent", "aren't", "arise", "around", "as", "a's", "aside", "ask", "asking", "associated", "at", "au", "auth", "av", "available", "aw", "away", "awfully", "ax", "ay", "az", "b", "b1", "b2", "b3", "ba", "back", "bc", "bd", "be", "became", "because", "become", "becomes", "becoming", "been", "before", "beforehand", "begin", "beginning", "beginnings", "begins", "behind", "being", "believe", "below", "beside", "besides", "best", "better", "between", "beyond", "bi", "bill", "biol", "bj", "bk", "bl", "bn", "both", "bottom", "bp", "br", "brief", "briefly", "bs", "bt", "bu", "but", "bx", "by", "c", "c1", "c2", "c3", "ca", "call", "came", "can", "cannot", "cant", "can't", "cause", "causes", "cc", "cd", "ce", "certain", "certainly", "cf", "cg", "ch", "changes", "ci", "cit", "cj", "cl", "clearly", "cm", "c'mon", "cn", "co", "com", "come", "comes", "con", "concerning", "consequently", "consider", "considering", "contain", "containing", "contains", "corresponding", "could", "couldn", "couldnt", "couldn't", "course", "cp", "cq", "cr", "cry", "cs", "c's", "ct", "cu", "currently", "cv", "cx", "cy", "cz", "d", "d2", "da", "date", "dc", "dd", "de", "definitely", "describe", "described", "despite", "detail", "df", "di", "did", "didn", "didn't", "different", "dj", "dk", "dl", "do", "does", "doesn", "doesn't", "doing", "don", "done", "don't", "down", "downwards", "dp", "dr", "ds", "dt", "du", "due", "during", "dx", "dy", "e", "e2", "e3", "ea", "each", "ec", "ed", "edu", "ee", "ef", "effect", "eg", "ei", "eight", "eighty", "either", "ej", "el", "eleven", "else", "elsewhere", "em", "empty", "en", "end", "ending", "enough", "entirely", "eo", "ep", "eq", "er", "es", "especially", "est", "et", "et-al", "etc", "eu", "ev", "even", "ever", "every", "everybody", "everyone", "everything", "everywhere", "ex", "exactly", "example", "except", "ey", "f", "f2", "fa", "far", "fc", "few", "ff", "fi", "fifteen", "fifth", "fify", "fill", "find", "fire", "first", "five", "fix", "fj", "fl", "fn", "fo", "followed", "following", "follows", "for", "former", "formerly", "forth", "forty", "found", "four", "fr", "from", "front", "fs", "ft", "fu", "full", "further", "furthermore", "fy", "g", "ga", "gave", "ge", "get", "gets", "getting", "gi", "give", "given", "gives", "giving", "gj", "gl", "go", "goes", "going", "gone", "got", "gotten", "gr", "greetings", "gs", "gy", "h", "h2", "h3", "had", "hadn", "hadn't", "happens", "hardly", "has", "hasn", "hasnt", "hasn't", "have", "haven", "haven't", "having", "he", "hed", "he'd", "he'll", "hello", "help", "hence", "her", "here", "hereafter", "hereby", "herein", "heres", "here's", "hereupon", "hers", "herself", "hes", "he's", "hh", "hi", "hid", "him", "himself", "his", "hither", "hj", "ho", "home", "hopefully", "how", "howbeit", "however", "how's", "hr", "hs", "http", "hu", "hundred", "hy", "i", "i2", "i3", "i4", "i6", "i7", "i8", "ia", "ib", "ibid", "ic", "id", "i'd", "ie", "if", "ig", "ignored", "ih", "ii", "ij", "il", "i'll", "im", "i'm", "immediate", "immediately", "importance", "important", "in", "inasmuch", "inc", "indeed", "index", "indicate", "indicated", "indicates", "information", "inner", "insofar", "instead", "interest", "into", "invention", "inward", "io", "ip", "iq", "ir", "is", "isn", "isn't", "it", "itd", "it'd", "it'll", "its", "it's", "itself", "iv", "i've", "ix", "iy", "iz", "j", "jj", "jr", "js", "jt", "ju", "just", "k", "ke", "keep", "keeps", "kept", "kg", "kj", "km", "know", "known", "knows", "ko", "l", "l2", "la", "largely", "last", "lately", "later", "latter", "latterly", "lb", "lc", "le", "least", "les", "less", "lest", "let", "lets", "let's", "lf", "like", "liked", "likely", "line", "little", "lj", "ll", "ll", "ln", "lo", "look", "looking", "looks", "los", "lr", "ls", "lt", "ltd", "m", "m2", "ma", "made", "mainly", "make", "makes", "many", "may", "maybe", "me", "mean", "means", "meantime", "meanwhile", "merely", "mg", "might", "mightn", "mightn't", "mill", "million", "mine", "miss", "ml", "mn", "mo", "more", "moreover", "most", "mostly", "move", "mr", "mrs", "ms", "mt", "mu", "much", "mug", "must", "mustn", "mustn't", "my", "myself", "n", "n2", "na", "name", "namely", "nay", "nc", "nd", "ne", "near", "nearly", "necessarily", "necessary", "need", "needn", "needn't", "needs", "neither", "never", "nevertheless", "new", "next", "ng", "ni", "nine", "ninety", "nj", "nl", "nn", "no", "nobody", "non", "none", "nonetheless", "noone", "nor", "normally", "nos", "not", "noted", "nothing", "novel", "now", "nowhere", "nr", "ns", "nt", "ny", "o", "oa", "ob", "obtain", "obtained", "obviously", "oc", "od", "of", "off", "often", "og", "oh", "oi", "oj", "ok", "okay", "ol", "old", "om", "omitted", "on", "once", "one", "ones", "only", "onto", "oo", "op", "oq", "or", "ord", "os", "ot", "other", "others", "otherwise", "ou", "ought", "our", "ours", "ourselves", "out", "outside", "over", "overall", "ow", "owing", "own", "ox", "oz", "p", "p1", "p2", "p3", "page", "pagecount", "pages", "par", "part", "particular", "particularly", "pas", "past", "pc", "pd", "pe", "per", "perhaps", "pf", "ph", "pi", "pj", "pk", "pl", "placed", "please", "plus", "pm", "pn", "po", "poorly", "possible", "possibly", "potentially", "pp", "pq", "pr", "predominantly", "present", "presumably", "previously", "primarily", "probably", "promptly", "proud", "provides", "ps", "pt", "pu", "put", "py", "q", "qj", "qu", "que", "quickly", "quite", "qv", "r", "r2", "ra", "ran", "rather", "rc", "rd", "re", "readily", "really", "reasonably", "recent", "recently", "ref", "refs", "regarding", "regardless", "regards", "related", "relatively", "research", "research-articl", "respectively", "resulted", "resulting", "results", "rf", "rh", "ri", "right", "rj", "rl", "rm", "rn", "ro", "rq", "rr", "rs", "rt", "ru", "run", "rv", "ry", "s", "s2", "sa", "said", "same", "saw", "say", "saying", "says", "sc", "sd", "se", "sec", "second", "secondly", "section", "see", "seeing", "seem", "seemed", "seeming", "seems", "seen", "self", "selves", "sensible", "sent", "serious", "seriously", "seven", "several", "sf", "shall", "shan", "shan't", "she", "shed", "she'd", "she'll", "shes", "she's", "should", "shouldn", "shouldn't", "should've", "show", "showed", "shown", "showns", "shows", "si", "side", "significant", "significantly", "similar", "similarly", "since", "sincere", "six", "sixty", "sj", "sl", "slightly", "sm", "sn", "so", "some", "somebody", "somehow", "someone", "somethan", "something", "sometime", "sometimes", "somewhat", "somewhere", "soon", "sorry", "sp", "specifically", "specified", "specify", "specifying", "sq", "sr", "ss", "st", "still", "stop", "strongly", "sub", "substantially", "successfully", "such", "sufficiently", "suggest", "sup", "sure", "sy", "system", "sz", "t", "t1", "t2", "t3", "take", "taken", "taking", "tb", "tc", "td", "te", "tell", "ten", "tends", "tf", "th", "than", "thank", "thanks", "thanx", "that", "that'll", "thats", "that's", "that've", "the", "their", "theirs", "them", "themselves", "then", "thence", "there", "thereafter", "thereby", "thered", "therefore", "therein", "there'll", "thereof", "therere", "theres", "there's", "thereto", "thereupon", "there've", "these", "they", "theyd", "they'd", "they'll", "theyre", "they're", "they've", "thickv", "thin", "think", "third", "this", "thorough", "thoroughly", "those", "thou", "though", "thoughh", "thousand", "three", "throug", "through", "throughout", "thru", "thus", "ti", "til", "tip", "tj", "tl", "tm", "tn", "to", "together", "too", "took", "top", "toward", "towards", "tp", "tq", "tr", "tried", "tries", "truly", "try", "trying", "ts", "t's", "tt", "tv", "twelve", "twenty", "twice", "two", "tx", "u", "u201d", "ue", "ui", "uj", "uk", "um", "un", "under", "unfortunately", "unless", "unlike", "unlikely", "until", "unto", "uo", "up", "upon", "ups", "ur", "us", "use", "used", "useful", "usefully", "usefulness", "uses", "using", "usually", "ut", "v", "va", "value", "various", "vd", "ve", "ve", "very", "via", "viz", "vj", "vo", "vol", "vols", "volumtype", "vq", "vs", "vt", "vu", "w", "wa", "want", "wants", "was", "wasn", "wasnt", "wasn't", "way", "we", "wed", "we'd", "welcome", "well", "we'll", "well-b", "went", "were", "we're", "weren", "werent", "weren't", "we've", "what", "whatever", "what'll", "whats", "what's", "when", "whence", "whenever", "when's", "where", "whereafter", "whereas", "whereby", "wherein", "wheres", "where's", "whereupon", "wherever", "whether", "which", "while", "whim", "whither", "who", "whod", "whoever", "whole", "who'll", "whom", "whomever", "whos", "who's", "whose", "why", "why's", "wi", "widely", "will", "willing", "wish", "with", "within", "without", "wo", "won", "wonder", "wont", "won't", "words", "world", "would", "wouldn", "wouldnt", "wouldn't", "www", "x", "x1", "x2", "x3", "xf", "xi", "xj", "xk", "xl", "xn", "xo", "xs", "xt", "xv", "xx", "y", "y2", "yes", "yet", "yj", "yl", "you", "youd", "you'd", "you'll", "your", "youre", "you're", "yours", "yourself", "yourselves", "you've", "yr", "ys", "yt", "z", "zero", "zi", "zz"])
    result = []
    for t in tokenize_text:
        if t not in stop_words:
            result.append(t)
    return result

def handle_high_textual_content(resp,threshold = 100):
    """
    get a resp, check if has more than 100 words and no urls
    consider this url as low textual content and skip it
    """
    # soup = BeautifulSoup(resp.raw_response.content, 'lmxl') for class
    soup = BeautifulSoup(resp.content, 'lxml')
    urls = []
    if soup.body == None:
        return None
    text_in_page = soup.body.get_text(' ', strip=True)
    tokenized_text = tokenizer(text_in_page)
    remove_stop_word_text = remove_stop_words(tokenized_text)
    num_word = len(remove_stop_word_text)
    try: 
        for link in soup.find_all("a"):
            urls.append(link.get('href'))
    except:
        return None
    if num_word < threshold and len(urls) ==0:
        return None
        
    return (urls,num_word)

def crawling(url):
    resp = requests.get(url)
    content = handle_high_textual_content(resp)
    if content == None:
        return list()
    else:
        urls,num_word = content[0],content[1]
        print(urls)
        print(num_word)

crawling('https://stat.uci.edu/')
    
def check_robots(domains:list):
    
    for d in domains:
        robots_url = f"http://{d}/robots.txt"
        
        try: 
            robots_response = requests.get(robots_url)
            if robots_response.status_code == 200:
                # Parse robots.txt to find rules for the user-agent
                robots_txt = robots_response.text
                robot_parser = robots_txt.split('\n')
                
                for line in robot_parser:
                    if line.startswith('User-agent'):
                        _, agent = line.split(': ')
                    elif line.startswith('Allow'):
                        print(line)
                        content = line.split(': ')
                        if len(content) ==2:
                            absolute_url = handle_relative_url(f'http://{d}',content[1].strip())
                            stats.allowed_path[agent].append(absolute_url)
                            print(stats.allowed_path)
                    elif line.startswith('Disallow'):
                        print(line)
                        content = line.split(': ')
                        if len(content) ==2:
                            absolute_url = handle_relative_url(f'http://{d}',content[1].strip())
                            stats.disallowed_path[agent].append(absolute_url)
                            print(stats.disallowed_path)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {robots_url}: {e}")

# valid_domains = [
#             "ics.uci.edu",
#             "cs.uci.edu",
#             "informatics.uci.edu",
#             "stat.uci.edu"
#         ]

# check_robots(valid_domains)
        


def crawl_domains_with_politeness(domains, delay=0.5):
    for domain in domains:
        # Check if the domain has a robots.txt file
        robots_url = f"{domain}/robots.txt"
        robots_response = requests.get(robots_url)
        
        if robots_response.status_code == 200:
            # Parse robots.txt to find rules for the user-agent
            robots_txt = robots_response.text
            robot_parser = robots_txt.split('\n')
            allowed = []
            disallowed = []
            user_agent = '*'
            
            for line in robot_parser:
                if line.startswith('User-agent'):
                    _, agent = line.split(': ')
                    if agent == '*':
                        user_agent = agent
                elif line.startswith('Allow'):
                    _, allowed_url = line.split(': ')
                    allowed.append(allowed_url.strip())
                elif line.startswith('Disallow'):
                    _, disallowed_url = line.split(': ')
                    disallowed.append(disallowed_url.strip())
            
            # Visit the allowed URLs while respecting the politeness delay
            for allowed_url in allowed:
                url = f"{domain}{allowed_url}"
                time.sleep(delay)
                response = requests.get(url)
                
                if response.status_code == 200:
                    # Extract URLs from the response content
                    soup = BeautifulSoup(response.content, 'html.parser')
                    links = soup.find_all('a', href=True)
                    for link in links:
                        print(link['href'])
                else:
                    print(f"Failed to fetch {url}")
        else:
            print(f"No robots.txt found for {domain}")


