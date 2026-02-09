import re
from urllib.parse import urlparse, urljoin, urldefrag, urlsplit, parse_qsl, urlencode, urlunsplit
import configparser
import logging
from bs4 import BeautifulSoup
import sys
import os
import hashlib
import csv

MIN_WORDS = 100
REPORT_DIR = "report"
UNIQUE_PAGES = set()
LONGEST_PAGE_URL = ""
LONGEST_PAGE_WORDS = 0
WORD_FREQ: dict[str, int] = {}
STOPWORDS = {
    "a","about","above","after","again","against","all","am","an","and","any","are",
    "aren't","as","at","be","because","been","before","being","below","between","both",
    "but","by","can", "can't","cannot","could","couldn't","did","didn't","do","does","doesn't",
    "doing","don't","down","during","each","few","for","from","further","had","hadn't",
    "has","hasn't","have","haven't","having","he","he'd","he'll","he's","her","here",
    "here's","hers","herself","him","himself","his","how","how's","i","i'd","i'll",
    "i'm","i've","if","in","into","is","isn't","it","it's","its","itself","let's","me",
    "more","most","mustn't","my","myself","no","nor","not","of","off","on","once","only",
    "or","other","ought","our","ours","ourselves","out","over","own","same","shan't","she",
    "she'd","she'll","she's","should","shouldn't","so","some","such","than","that","that's",
    "the","their","theirs","them","themselves","then","there","there's","these","they",
    "they'd","they'll","they're","they've","this","those","through","to","too","under",
    "until","up","very","was","wasn't","we","we'd","we'll","we're","we've","were","weren't",
    "what","what's","when","when's","where","where's","which","while","who","who's","whom",
    "why","why's","with","won't","would","wouldn't","you","you'd","you'll","you're","you've",
    "your","yours","yourself","yourselves"
}
SUBDOMAIN_COUNTS: dict[str, int] = {}

# configure logging, documentation: https://docs.python.org/3/howto/logging.html
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.propagate = False

if not logger.handlers:
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)


def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]


def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # 200: success; 204: no content; 301/302: redirect; 403: forbidden; 404: not found; 500: server error
    # resp.error: when status is not 200, you can check the error here, if needed.
    # If the status codes are between 600 and 606, the reason for the error is provided in resp.error
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    global LONGEST_PAGE_WORDS, LONGEST_PAGE_URL
    logger.info(f"START crawling URL: {url}")

    # Handle server status codes and redirects
    CACHE_SERVER_ERRORS = {600, 601, 602, 603, 604, 605, 606, 607, 608}

    # If the downloader gave no response object
    if resp is None:
        logger.error(f"DROP no response, url: {url}")
        return []
    
    # If it's a cache server error, log and drop completely since these are likely transient and not useful for extraction
    if resp.status in CACHE_SERVER_ERRORS:
        logger.info(f"DROPPED {url} due to cache server error={resp.status}")
        return []
    
    # If it's a redirect (301/302), log and return the redirect URL for crawling since these can lead to valid pages. The crawler will handle the redirect URL as a new crawl.
    if resp.status in {301, 302}:
        redirect_url = resp.raw_response.headers.get("Location")
        if redirect_url:
            logger.info(f"REDIRECT {url} TO {redirect_url}")
            return [urljoin(resp.url, redirect_url)] # return the redirect URL for crawler to handle as a new crawl
        else:
            logger.warning(f"DROPPED {url}: redirect without location header")
            return []      
    
    # If the server did not return 200 (OK), skip parsing links from it since it may be unreliable for extraction
    if resp.status != 200: #Comment (Quang): This one can miss the redirect links with code 301/302 which may lead to other valid pages. The code in other files already handle the redirect links correctly for us.
        logger.warning(f"DROPPED status={resp.status} error={resp.error} url={url}")
        return []
    
    # If raw response is None, cant access content attribute, so check this before
    if resp.raw_response is None:
        logger.error(f"DROPPED no raw_response, url: {url}")
        return []
    
    # If the response has no content, no links can be extracted 
    content = resp.raw_response.content
    if not content:
        logger.error(f"DROPPED no content, url: {url}")
        return [] 

    if no_data_wrapper(resp):
        return []

    if is_large_file(resp):
        logger.info(f"DROPPED large_file url={url}")
        return []

    # grab links in resp.raw_response.content
    try:
        logger.info(f"Begin analyzing content url={url}")
        soup = BeautifulSoup(content, 'html.parser')

        # Sources : https://stackoverflow.com/questions/30565404/remove-all-style-scripts-and-html-tags-from-an-html-page
        for tag in soup(["script", "style", "nav","footer","header"]):
            tag.decompose() # remove js code, css code, and boilerplate code; just keep main content
        text = soup.get_text(separator=" ").strip()

        if low_info_wrapper(text, url): # crawl pages with high textual info
            return []

        current_fp = compute_simhash(text)
        if is_near_duplicate_and_record(current_fp, url):
            return []  # dont extract links from near-duplicates
        
        add_unique_page(resp.url)
        update_word_frequencies(text)     # treat pages crawled as the pages to be analyzed for top 50 and largest page
        page_url = urldefrag(resp.url)[0] 
        wc = count_words(text)
        if wc > LONGEST_PAGE_WORDS:
            LONGEST_PAGE_WORDS = wc
            LONGEST_PAGE_URL = page_url

        # extract links
        extracted_links = set()
        for tag in soup.find_all('a', href=True):
            link = urljoin(resp.url, tag['href']) 
            clean_link = urldefrag(link)[0]
            clean_link = similar_no_info(clean_link) 
            extracted_links.add(clean_link)

        write_unique_pages_report()
        write_longest_page_report()
        write_top_50_words("common_words.txt")
        write_subdomains_report(SUBDOMAIN_COUNTS, "subdomains.txt")
            
        return list(extracted_links)

    except Exception as e:
        logger.warning(f"Error parsing {url}: {e}")
        return []


def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.

    try:
        url = urldefrag(url)[0]
        parsed = urlparse(url)

        if parsed.scheme not in set(["http", "https"]):
            return False
        
        # host must be in allowed domain set
        host = (parsed.hostname or "").lower()
        if not is_allowed_host(host):
            return False        
        
        # hard coding infinite trap handling from observation
        query_params = dict(parse_qsl(parsed.query, keep_blank_values=True))
        qkeys = {k.lower() for k in query_params.keys()}

        if host == "grape.ics.uci.edu":
            grape_revision_keys = {"version", "action", "format"}
            if qkeys & grape_revision_keys:
                logger.info(f"DROPPED grape_revision url={url}")
                return False
            grape_timeline_keys = {"from", "precision"}
            if qkeys & grape_timeline_keys:
                logger.info(f"DROPPED grape_timeline url={url}")
                return False

        if host == "wics.ics.uci.edu":
            wics_event_keys = {"tribe-bar-date", "eventdisplay", "ical", "outlook-ical"}
            if qkeys & wics_event_keys:
                logger.info(f"DROPPED wics_events url={url}")
                return False
            if re.search(r"/events/.*?/day/\d{4}-\d{2}-\d{2}(/|$)", path):
                logger.info(f"DROPPED wics_day_calendar url={url}")
                return False
            wics_noise_keys = {"share", "locale", "display", "next", "ref", "entry_point"}
            if qkeys & wics_noise_keys:
                logger.info(f"DROPPED wics_noise url={url}")
                return False

        if host == "cml.ics.uci.edu":
            cml_keys = {"page", "subpage"} # same without page and subpage query, seems redundant
            if qkeys & cml_keys:
                logger.info(f"DROPPED cml_redundant url={url}")
                return False

        
        if re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz|z"
            + r"|txt|xml|rss|svg"
            + r"|py|java|c|cpp|h|class|sh|sql|ipynb|nb|war"
            + r")$",
              parsed.path.lower()):
            return False
    
        # --- TRAP DETECTIONS ---
        #Reference: https://developers.google.com/search/docs/crawling-indexing/url-structure, https://support.archive-it.org/hc/en-us/articles/208332943-How-to-identify-and-avoid-crawler-traps, https://en.wikipedia.org/wiki/Spider_trap
        #1. Avoid infinite calendar trap: for example, URLs with /calendar/2024/01/01, /calendar/2024/01/01, etc.
        calendar_pattern = re.compile(r"/calendar/\d{4}/\d{1,2}/\d{1,2}")
        if calendar_pattern.search(parsed.path.lower()):
            logger.info(f"DROPPED infinite calendar URL: {url}")
            return False
        
        #2. Avoid session IDs in query session=, sid=, jseesionid=
        if parsed.query:
            query_params = dict(parse_qsl(parsed.query))
            session_keys = {"session", "sid", "jsessionid"}
            if any(key.lower() in session_keys for key in query_params):
                logger.info(f"DROPPED session ID URL: {url}")
                return False
            
        #3. Avoid spider traps / manual patterns
        #Example: very long numeric path segments (common traps)
        segments = [seg for seg in parsed.path.split("/") if seg]
        if any(len(seg) > 50 for seg in segments):
            logger.info(f"DROPPED suspicious long segment URL: {url}")
            return False
        
        # authentication/OAuth flow URL doesnt contain useful content
        path = parsed.path.lower()
        if any(key in path for key in ["/auth/", "/signin", "/login", "/logout", "/oauth"]): # filter authentication related urls
            logger.info(f"DROPPED suspicious long segment URL: {url}")
            return False
        
        # Pagination - allow only first 10 pages
        m = re.search(r"/page/(\d+)/?$", path)
        if m:
            page_num = int(m.group(1))
            if page_num > 10:
                logger.info(f"DROPPED path_pagination page={page_num} url={url}")
                return False

        if additional_trap_handling_wrapper(url, parsed, query_params):
            return False
        
        return True

    except TypeError:
        print ("TypeError for ", parsed)
        raise


def tokenize_text(text: str):
    # TODO handle aprostrophe
    # allow non-English characters for this assignment
    current = []
    for ch in text:
        if ch.isalnum():        
            current.append(ch.lower())
        else:
            if current:
                yield "".join(current)
                current.clear()

    if current:
        yield "".join(current)
        current.clear()


# --- Handling similar pages with no information --- 
def similar_no_info(url: str) -> str:
    """
    Source : Google AI Overview was used to understand how to utilize urlsplit(),
    parse_qsl

    Handle different URL string that points to the same page.
    This includes:
    1. Different fragments -> resolved using urldefrag()
    2. Relative cs Absolute path -> resolved using join()
    3. Query parameter order
    """
    url_components = urlsplit(url)
    scheme = url_components.scheme
    network_location = url_components.netloc.lower()
    path = url_components.path if url_components.path else "/" # if path is empty, path is a /
    query = url_components.query

    # 3. Query parameter order
    if query:
        logger.debug(f"raw query: {query}")
        params = parse_qsl(query, keep_blank_values=True) # returns a list of key, value pairs
        params.sort() # sort by key, then value -- ensures unique ordering for same query in different order
        query = urlencode(params)
        logger.debug(f"cleaned query: {query}")
    
    return urlunsplit((scheme, network_location, path, query, ""))


# --- Handling pages with thin content/junk --- 
def low_info_wrapper(text: str, url: str) -> bool:
    if not has_min_words(text):
        logger.info(f"DROPPED reason=min_words, url={url}")
        return True

    if has_repeated_tokens(text):
        logger.info(f"DROPPED reason=few_unique_tokens, url={url}")
        return True

    return False


def has_min_words(text: str) -> bool:
    count = 0
    for token in tokenize_text(text):
        count += 1
        if count >= MIN_WORDS:
            return True
    return False


def has_repeated_tokens(text: str) -> bool:
    """
    Handle pages that lacks diveristy in words, which may be junk
    """
    total = 0
    unique_tokens = set()

    for tok in tokenize_text(text):
        total += 1
        unique_tokens.add(tok)
        if total >= 500:  # Check the first 500 tokens
            break

    if total == 0:
        return True
    unique_ratio = len(unique_tokens) / total
    return unique_ratio < 0.05


# --- Handling 200, but no data ---
def no_data_wrapper(response) -> bool:
    '''
    Wrapper for 200, but no data.
    '''

    if not is_html_content_type(response):
        logger.info(f"DROPPED 200_no_data reason=non_html url={response.url}")
        return True

    return False


def is_html_content_type(response) -> bool:
    """ 
    Return true if the content is HTML (or text)
    i.e. If it is not text data, but instead is pdf or image, then don't crawl
    """
    try:
        headers = response.raw_response.headers 
        content_type = (headers.get("Content-Type") or "").lower()  
    except (AttributeError, TypeError):
        return True

    if content_type and ("text/html" not in content_type) and ("application/xhtml+xml" not in content_type): # content can be html even if the content_type is empty
        return False 

    return True


# --- Handling Large files, Low info --- 
def is_large_file(resp) -> bool:
    '''
    - Some large files are handled from being downloaded in is_valid() by filtering 
    non-HTML file such as files with extensions liks .pdf, .ipynb, .txt
    - This method is an additional filtering for large HTML files that could waste
    crawling budget
    - It also prevents any non-HTML files that doesn't have the matching extension
    in the is_valid() from being crawled
    '''
    max_html_bytes = 1_000_000
    max_other_bytes = 300_000

    try:
        headers = resp.raw_response.headers
        content_length = (headers.get("Content-Length") or "").strip()
        content_type = (headers.get("Content-Type") or "").lower()

        if content_length and content_length.isdigit():
            size_bytes = int(content_length)
            is_html = ("text/html" in content_type) or ("application/xhtml+xml" in content_type)
            limit = max_html_bytes if is_html else max_other_bytes
            return size_bytes > limit
    except Exception:
        pass
    return False


# --- Additional trap handling --- 
def additional_trap_handling_wrapper(url: str, query_params: dict) -> bool:
    qp_keys = {str(k).lower() for k in (query_params or {}).keys()}

    if is_query_trap(qp_keys):
        logger.info(f"DROPPED query_trap url={url}")
        return True
    if len(url) > 300:
        logger.info(f"DROPPED long_url len={len(url)} url={url}")
        return True

    return False

def is_query_trap(query_params: dict) -> bool:
    # generalized version of the hardcoded handling of traps in is_valid()
    NOISE_KEYS = {
        'share', 'action', 'format',
        'eventdisplay', 'outlook-ical',
        'ical', 'tribe-bar-date', 'lang', 'version', 'do'
    }
    
    if len(query_params) > 5:
        return True
    if any(key.lower() in NOISE_KEYS for key in query_params.keys()):
        return True

    return False


# --- Report ---
ALLOWED_BASE_HOSTS = {
    "ics.uci.edu",
    "cs.uci.edu",
    "informatics.uci.edu",
    "stat.uci.edu",
}
ALLOWED_SUFFIXES = (
    ".ics.uci.edu",
    ".cs.uci.edu",
    ".informatics.uci.edu",
    ".stat.uci.edu",
)

def is_allowed_host(host: str) -> bool:
    host = (host or "").lower()
    return host in ALLOWED_BASE_HOSTS or any(host.endswith(suf) for suf in ALLOWED_SUFFIXES)


def add_unique_page(fetched_url: str) -> bool:
    clean_url= urldefrag(fetched_url)[0]
    host = (urlparse(clean_url).hostname or "").lower()
    if not is_allowed_host(host):       # check in case redirected url is different (may be unnecessary)
        return False

    if clean_url in UNIQUE_PAGES:
        return False

    UNIQUE_PAGES.add(clean_url)
    SUBDOMAIN_COUNTS[host] = SUBDOMAIN_COUNTS.get(host, 0) + 1
    
    return True


def write_unique_pages_report() -> None:
    os.makedirs(REPORT_DIR, exist_ok=True)
    out_path = os.path.join(REPORT_DIR, "unique_pages.txt")
    with open(out_path, "w") as f:
        f.write(f"Unique pages: {len(UNIQUE_PAGES)}\n")
        f.write("\n")
        for u in sorted(UNIQUE_PAGES):
            f.write(u + "\n")


def count_words(text: str) -> int:
    num_words = 0
    for _ in tokenize_text(text):
        num_words += 1
    return num_words


def write_longest_page_report() -> None:            # longest page number does not omit stop words
    os.makedirs(REPORT_DIR, exist_ok=True)
    out_path = os.path.join(REPORT_DIR, "longest_page.txt")
    with open(out_path, "w") as f:
        f.write(f"Longest page (num of words): {LONGEST_PAGE_WORDS}\n")
        f.write(f"URL: {LONGEST_PAGE_URL}\n")


def update_word_frequencies(text: str) -> None:
    for token in tokenize_text(text):
        if token.isalnum() and len(token) <= 1:     # remove one letter, still include digit     
            continue
        if token.isdigit():
            continue
        if token in STOPWORDS:
            continue
        WORD_FREQ[token] = WORD_FREQ.get(token, 0) + 1


def write_top_50_words(out_path: str) -> None:
    os.makedirs(REPORT_DIR, exist_ok=True)
    out_path = os.path.join(REPORT_DIR, "common_words.txt")
    items = sorted(WORD_FREQ.items(), key=lambda kv: (-kv[1], kv[0]))[:50]
    with open(out_path, "w", encoding="utf-8") as f:
        for word, count in items:
            f.write(f"{word}, {count}\n")


def write_subdomains_report(subdomain_counts: dict[str, int], out_path: str) -> None:
    os.makedirs(REPORT_DIR, exist_ok=True)
    out_path = os.path.join(REPORT_DIR, "subdomains.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        for host in sorted(subdomain_counts.keys()): # sort in alphabetical order
            f.write(f"{host}, {subdomain_counts[host]}\n") 


# --- Simhash ---
SEEN_SIMHASHES: list[tuple[int, str]] = [] 
SIMHASH_THRESHOLD = 0.92 # not too strict, nor not too lenient

"""
Method (Source : Lecture 11 slides)
1. convert document into features and weights where words are weighted by frequency
2. For each word, generate a hash
3. Maintain a vector V, add weight if the bit is 1
4. compare two simhashes by how many bits atch

Limitation of this method:
- Possible collision in hash value
- Multiple pages may generate same fingerprint despite differing content

Note
2^64 possible fingerprints 
"""
def compute_simhash(text: str, bits: int = 64) -> int:
    # 1. Convert to features and weights
    weights = {}
    for token in tokenize_text(text):
        if token in STOPWORDS or len(token) <= 1:
            continue # filter stopwords, single letters
        weights[token] = weights.get(token, 0) + 1
    if not weights:
        return 0 # edge case  : empty page

    # 2. Generate hash
    V = [0] * bits
    for word, weight in weights.items():
        h_digest = hashlib.md5(word.encode('utf-8')).digest() # convert string to bytes, MD5 then computes hash object, and digest() returns raw hash bytes (md5 is in 16bytes or 128bits)
        h_int = int.from_bytes(h_digest, byteorder='big') # convert hash bytes to integer

        for i in range(bits):
            bit = (h_int >> i) & 1 # Check if the i-th bit of the hash is 1 or 0
            if bit == 1:
                V[i] += weight # 3. add weight for which the corresponding bit in the word's hash value is 1 
            else:
                V[i] -= weight # 3. subtract weight if 0

    # 4. fingerprint generation
    fingerprint = 0
    for i in range(bits): 
        if V[i] > 0:
            fingerprint |= (1 << i) # set the ith bit to 1 if the ith component of V is positive else 0
    
    return fingerprint # generate fingerprint for each text

def get_similarity(f1: int, f2: int, bits: int = 64) -> float:
    dist = (f1 ^ f2).bit_count()
    return (bits - dist) / bits

def is_near_duplicate_and_record(current_fp: int, url: str) -> bool:
    cur_url = urldefrag(url)[0]

    for seen_fp, seen_url in SEEN_SIMHASHES:
        sim = get_similarity(current_fp, seen_fp)
        if sim >= SIMHASH_THRESHOLD:
            logger.info(f"DUPLICATE DETECTED: {cur_url} is near-duplicate of {seen_url}")
            return True

    SEEN_SIMHASHES.append((current_fp, cur_url))
    return False