import atexit
import os
import tempfile
from collections import defaultdict
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import urlparse, urldefrag

from bs4 import BeautifulSoup

from tokenizer import tokenize, computeWordFrequencies

# 1) Unique pages
unique_urls = set()


# 2) Longest page
longest_page_url = None
longest_page_word_count = 0

# 3) Word frequencies
global_word_freq = defaultdict(int) 

# 4) Subdomain
subdomain_pages = defaultdict(set)

# Per-page word counts (for "old style" logging / debugging)
page_word_count: Dict[str, int] = {}

# Stopwords
STOPWORDS: Set[str] = set()
HERE = os.path.dirname(os.path.abspath(__file__))

_STOPWORDS_PATH = os.path.join(HERE, "stopwords.txt")
with open(_STOPWORDS_PATH, "r", encoding="utf-8") as f:
    for line in f:
        w = line.strip().lower()
        if w:
            STOPWORDS.add(w)

#Helpers

def _defrag_url(url: str) -> str:
    """Remove fragment"""
    return urldefrag(url)[0]

def extract_visible_text(html):
    """
    Remove scripts/styles and return visible text only.
    """
    soup = BeautifulSoup(html, "html.parser", from_encoding="utf-8")

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    return soup.get_text(separator=" ")

def get_subdomain(url):
    # Use hostname to ensure we match ".uci.edu" even if there is a port (e.g., :8080)
    host = urlparse(url).hostname
    if host and host.lower().endswith("uci.edu"):
        return host.lower()
    return None

def tokenize_text_via_tempfile(text):
    """
    We write `text` to a temporary file and call tokenize(path).
    """
    # Ensure text is str
    if not isinstance(text, str):
        text = str(text)

    with tempfile.NamedTemporaryFile(mode="w", delete=True, encoding="utf-8") as tmp:
        tmp.write(text)
        tmp.flush()
        return tokenize(tmp.name) or []

def record_page(url, raw_html):
    """
    Called by scraper once per successfully crawled page (status == 200).
    """
    global longest_page_url, longest_page_word_count

    if not url:
        return False

    url = _defrag_url(url)

    # Uniqueness (per assignment definition)
    if url in unique_urls:
        return False
    unique_urls.add(url)

    # Subdomain stats (unique pages per host)
    sd = get_subdomain(url)
    if sd:
        subdomain_pages[sd].add(url)
    
    # Extract visible text and tokenize
    text = extract_visible_text(raw_html)
    tokens = tokenize_text_via_tempfile(text)

    # Normalize + stopword removal
    tokens = [t for t in tokens if t.isalpha() and t not in STOPWORDS and len(t) >= 2]
    
    # checks if page is high quality
    if len(tokens) < 50:
        return False

    # Per-page word count (for longest + debug logs)
    wc = len(tokens)
    page_word_count[url] = wc

    # Longest page
    if wc > longest_page_word_count:
        longest_page_word_count = wc
        longest_page_url = url

    # Global word frequencies
    page_freq = computeWordFrequencies(tokens) or {}
    for w, c in page_freq.items():
        global_word_freq[w] += c

    return True
   
    

#Getters

def get_unique_page_count() -> int:
    return len(unique_urls)

def get_unique_pages() -> set:
    return unique_urls


def get_longest_page() -> Tuple[Optional[str], int]:
    return longest_page_url, longest_page_word_count


def get_top_50_words() -> List[Tuple[str, int]]:
    return sorted(global_word_freq.items(), key=lambda x: x[1], reverse=True)[:50]


def get_subdomain_stats() -> List[Tuple[str, int]]:
    """
    Returns list of (subdomain, count) sorted alphabetically.
    Count is number of unique pages in that subdomain.
    """
    return sorted(((sd, len(pages)) for sd, pages in subdomain_pages.items()), key=lambda x: x[0])


def write_report_files() -> None:
    """
    Writes:
    - report_unique_count.txt
    - report_longest_page.txt
    - report_top50.txt
    - report_subdomains.txt
    """
    # Required report outputs
    with open("report_unique_count.txt", "w", encoding="utf-8") as f:
        f.write(str(get_unique_page_count()) + "\n")

    lp_url, lp_words = get_longest_page()
    with open("report_longest_page.txt", "w", encoding="utf-8") as f:
        f.write(f"{lp_url}\t{lp_words}\n")

    with open("report_top50.txt", "w", encoding="utf-8") as f:
        for w, c in get_top_50_words():
            f.write(f"{w}, {c}\n")

    with open("report_subdomains.txt", "w", encoding="utf-8") as f:
        for sd, n in get_subdomain_stats():
            f.write(f"{sd}, {n}\n")

atexit.register(write_report_files)