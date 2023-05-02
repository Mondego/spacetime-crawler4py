import re
from urllib.parse import urlparse, urljoin, urldefrag
from bs4 import BeautifulSoup
from helper import Helper
from hashlib import md5

def scraper(url, resp, sHelper: Helper):
    links = []
    try:
        links = extract_next_links(url, resp, sHelper)
    except AttributeError:
        pass
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp, sHelper: Helper):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content

    # using set instead of list to avoid returning duplicate links inside this page
    # also maybe helpful with question 4: "the number of unique pages detected in each subdomain"
    links_set = set()
    UReaL = resp.raw_response.url
    # If status is OK (= 200)
    if resp.status == 200 and is_valid(UReaL):
        
        # Cook the html into soup
        soup = BeautifulSoup(resp.raw_response.content, "lxml", from_encoding= "utf-8")
        texts = soup.find_all(string=True)
        tags = set([t.parent.name for t in texts])
        desired_tags = tags - sHelper.low_text_tags
        tokens = []
        for text in texts:
            if text.parent.name in desired_tags:
                tokens.extend(tokenize(text))
        page_len = len(tokens)

        # check low information page (word count <= 200) and exact match through hash freq
        # exact_hash = md5(texts.encode("utf-8")).hexdigest()
        if page_len > 200: #and exact_hash not in sHelper.known_exact_hash:
            #sHelper.known_exact_hash.add(exact_hash)
            tokens_dict = computeWordFrequencies(tokens)
            page_hash = simhash_page(tokens_dict)
            # check_near_dup() return True for similar pages
            # => if not similar
            if not(check_near_dup(page_hash, sHelper)):
                ready = [UReaL, page_len, page_hash]
                sHelper.add(ready, tokens_dict)

                # findAll('a') get all the <a> tag, where all the links are in the html, into a list
                for link in soup.findAll('a'):

                    # get the link from the tag
                    
                    linked = link.get('href')
                    linked = str(linked)
                    linked = linked.replace("\"", "")
                    linked = linked.replace("www.", "")
                    parsed = urlparse(linked)
                    # check if the URL doesn't have a hostname (netloc) => relative URL,
                    # and convert into absolute link by combining with the original link
                    if (parsed.netloc == ""):
                        linked = urljoin(UReaL, linked)
                    
                    # split the link into the unique link and the fragment.
                    # [0] to take the unique link only ([1] would be the fragment)
                    linked = urldefrag(linked)[0]

                    if len(linked) > 0:
                        if linked[-1] == "/":
                            linked = linked[:-1]

                    # adding scheme: links can unspecify the scheme,
                    # but if they still start with "//", the links still accessible in the web
                    if (parsed.scheme == "" and linked[0:2] == "//"):
                        linked = "http:" + linked

                    if parsed.netloc == "archive.ics.uci.edu" and parsed.path == "/ml/datasets.php":
                        linked = "http://archive.ics.uci.edu/ml/datasets.php"

                    # !!!: https://www.ics.uci.edu/ and http://www.ics.uci.edu/ will be hash to the same value since get_urlhash(url) doesnt hash scheme
                    links_set.add(linked)

    return list(links_set)

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        
        if '.'.join(parsed.netloc.split('.')[-3:]) not in set(["ics.uci.edu", "cs.uci.edu", "informatics.uci.edu", "stat.uci.edu"]):
            return False
        
        # trap 1:repeating path
        pars = parsed.path.split('/')
        if len(pars) != len(set(pars)):
            return False
        
        # pls fix
        if parsed.netloc == "archive-beta.ics.uci.edu":
            return False
        
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|mpg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz|r)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise

def simhash_page(tokDict):
    page_hash_list = [0]*128
    for word, freq in tokDict.items():
        hash = md5 (word.encode("utf-8")).hexdigest()
        a = int(hash,16)
        # !!! reverse order
        for i in range(128):
            val = -1
            if a%2 == 1:
                val = 1
            page_hash_list[i] += val * freq
            a = a//2
    page_hash = 0
    for bit in reversed(page_hash_list):
        v = 0
        if bit > 0:
            v = 1
        page_hash = (page_hash << 1) + v
    return page_hash

# return true if this page is a near duplicate of some page
def check_near_dup(x, tHelper: Helper):
    for entry in tHelper.log:
        y = entry[2]
        different_bits = x ^ y
        diff_count = 0
        for i in range(0,128):
            diff_count += different_bits & 1
            different_bits = different_bits >> 1
        # if 2 page is only 15/128 different => they are simmilar
        if diff_count <= 15:
            return True
    return False

def tokenize(text):
    master_tokens = []
    for line in text.splitlines():
        
        #Find all the tokens in the line, then add them to the main list
        tokens = re.findall("[a-zA-Z0-9]+[\"']*[a-zA-Z0-9]*", line.lower(), re.UNICODE)
        master_tokens.extend(tokens) 
    
    return master_tokens

def computeWordFrequencies(token_list):
    token_map = {}
    for token in token_list:
        if token in token_map:
            token_map[token] += 1
        else:
            token_map[token] = 1
    return token_map