import re
from collections import Counter, defaultdict
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from tokenizer import tokenize, computeWordFrequencies
import tempfile

# 1) Unique pages
unique_urls = set()

# 2) Longest page
longest_page_url = None
longest_page_word_count = 0

# 3) Word frequencies
global_word_freq = defaultdict(int) 

# 4) Subdomain
subdomain_pages = defaultdict(set)

# Stopwords
STOPWORDS = set()
with open("stopwords.txt", "r") as f:
    for line in f:
        STOPWORDS.add(line.strip().lower())

def extract_visible_text(html):
    """
    Remove scripts/styles and return visible text only.
    """
    soup = BeautifulSoup(html, "lxml")

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    return soup.get_text(separator=" ")

def get_subdomain(url):
    """
    Return subdomain if within uci.edu, else None.
    """
    parsed = urlparse(url)
    host = parsed.netloc.lower()

    if host.endswith("uci.edu"):
        return host
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
    Called once per successfully crawled page (status == 200).
    """
    global longest_page_url, longest_page_word_count

    # enforce uniqueness by URL
    if url in unique_urls:
        return
    unique_urls.add(url)

    # extract visible text
    text = extract_visible_text(raw_html)

    # tokenize using PartA
    tokens = tokenize_text_via_tempfile(text)

    # normalize + remove stopwords
    tokens = [t for t in tokens if t not in STOPWORDS]

    # low-information page filter
    if len(tokens) < 50:
        return

    # update longest page
    if len(tokens) > longest_page_word_count:
        longest_page_word_count = len(tokens)
        longest_page_url = url

    # update word frequencies
    page_freq = computeWordFrequencies(tokens) or {}
    for w, c in page_freq.items():
        global_word_freq[w] += c

    # update subdomain stats
    subdomain = get_subdomain(url)
    if subdomain:
        subdomain_pages[subdomain].add(url)



def get_unique_page_count():
    return len(unique_urls)


def get_longest_page():
    return longest_page_url, longest_page_word_count


def get_top_50_words():
    # sort global_word_freq by count desc
    items = sorted(global_word_freq.items(), key=lambda x: x[1], reverse=True)
    return items[:50]


def get_subdomain_stats():
    """
    Returns list of (subdomain, count) sorted alphabetically.
    """
    return sorted(
        [(sd, len(pages)) for sd, pages in subdomain_pages.items()],
        key=lambda x: x[0]
    )

def write_report_files():
    with open("report_unique_count.txt", "w") as f:
        f.write(str(get_unique_page_count()) + "\n")

    lp_url, lp_words = get_longest_page()
    with open("report_longest_page.txt", "w") as f:
        f.write(f"{lp_url}\t{lp_words}\n")

    with open("report_top50.txt", "w") as f:
        for w, c in get_top_50_words():
            f.write(f"{w}, {c}\n")

    with open("report_subdomains.txt", "w") as f:
        for sd, n in get_subdomain_stats():
            f.write(f"{sd}, {n}\n")