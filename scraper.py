import hashlib
import re
from collections import Counter
from urllib.parse import urlparse, urljoin, urldefrag, parse_qs, unquote
from bs4 import BeautifulSoup
from stats import record_page

# constants
MAX_PAGE_BYTES = 10 * 1024 * 1024
MIN_WORDS = 20
MIN_UNIQUE_WORDS = 8
MAX_SAME_PAGES = 3

# these are to track the pages processed
processed_urls = set()
fingerprints = Counter()


def scraper(url, resp):
    return extract_next_links(url, resp)


def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content

    # only allow successful responses, status of 200 means it's successful
    if resp is None or resp.status != 200:
        return []

    raw = resp.raw_response
    if raw is None or not raw.content:
        return []

    if len(raw.content) > MAX_PAGE_BYTES:
        return []

    # check the content type and avoid parsing non-HTML and XHTML content
    content_type = raw.headers.get("Content-Type", "")
    media_type = content_type.split(";", 1)[0].strip().lower()
    if media_type and media_type not in {
        "text/html", "application/xhtml+xml"
    }:
        return []

    # use final response url
    baseURL = raw.url or resp.url or url

    try:
        baseURL = urldefrag(baseURL)[0]
    except (TypeError, ValueError):
        return []

    # reject pages redirected outside allowed
    if not is_valid(baseURL):
        return []

    # avoid parsing same defragmented url
    if baseURL in processed_urls:
        return []

    # parse the html
    soup = BeautifulSoup(raw.content, "html.parser")
    link = baseURL
    base_tag = soup.find("base", href=True)

    if base_tag:
        try:
            candidate = urljoin(baseURL, base_tag["href"].strip())
            if urlparse(candidate).scheme in {"http", "https"}:
                link = candidate
        except (TypeError, ValueError):
            pass

    # remove non=content elements before extracting the page text
    for element in soup(["script", "style", "noscript", "template"]):
        element.decompose()

    text = soup.get_text(separator=" ", strip=True)
    tokens = re.findall(r"[a-zA-Z]+", text.lower())

    # record each url
    record_page(baseURL, text)
    processed_urls.add(baseURL)

    # we don't care for empty html or pages without any useful content
    if not tokens:
        return []

    counts = Counter(tokens)
    unique_words = len(counts)

    # now handling low information, the idea is that both little text and little
    # vocabulary will be rejected
    low_information = (
            len(tokens) < MIN_WORDS and unique_words < MIN_UNIQUE_WORDS
    )

    if low_information:
        return []

    # ignore whitespace and cases when detecting identical text
    normalized_text = " ".join(text.casefold().split())
    fingerprint = hashlib.sha256(normalized_text.encode("utf-8")).hexdigest()

    # expand only the first few pages with identical text
    fingerprints[fingerprint] += 1
    if fingerprints[fingerprint] > MAX_SAME_PAGES:
        return []

    # collect distinct and valid links without their fragments
    links = []
    seen_links = set()

    for tag in soup.find_all("a", href=True):
        href = tag["href"].strip()
        if not href:
            continue

        try:
            next_url = urldefrag(urljoin(link, href))[0]
        except (TypeError, ValueError):
            continue

        # skip exact same links, previously processed links, and duplicates
        if next_url == baseURL or next_url in processed_urls or next_url in seen_links:
            continue

        if is_valid(next_url):
            seen_links.add(next_url)
            links.append(next_url)

    return links


# calendar trap avoiding
def is_calendar(parsed):
    path = parsed.path.lower()
    params = parse_qs(parsed.query, keep_blank_values=True)
    keys = {key.lower() for key in params}

    # common calendar navigation parameters
    if keys & {"ical", "ical_export"}:
        return True

    calendar_path = re.search(
        r"/(?:calendar|calendars|events)(?:/|$)", path
    )

    if not calendar_path:
        return False

    # calendar formatting like /events/2026/10 or like /calendar/2026-10-30/
    dated_listing = re.search(
        r"/(?:calendar|calendars|events)/"
        r"(?:day/|week/|month/)?"
        r"\d{4}(?:[-/]\d{1,2}){1,2}/?$",
        path
    )

    if dated_listing:
        return True

    # date navigation on calendar/listing endpoints only
    listing_endpoint = re.search(
        r"/(?:calendar|calendars|events)"
        r"(?:/(?:day|week|month|list))?/?$",
        path
    )

    navigation_keys = {"date", "day", "week", "month", "year", "tribe-bar-date", "eventdate"}

    return bool(listing_endpoint and keys & navigation_keys)


# attempt to avoid traps
def is_trap(url):
    parsed = urlparse(url)
    path = parsed.path.lower()

    # check if is calendar
    if is_calendar(parsed):
        return True

    # avoid excessively long urls
    if len(url) > 2048:
        return True

    # avoid urls with very long path depths
    segments = [s for s in path.split("/") if s]

    if len(segments) > 12:
        return True

    # avoid repeated path segments like /a/a/a/a/
    for block_size in range(1, len(segments) // 4 + 1):
        window_size = block_size * 4

        for start in range(len(segments) - window_size + 1):
            block = segments[start:start + block_size]
            window = segments[start:start + window_size]

            if window == block * 4:
                return True

    # avoid very long query strings
    if len(parsed.query) > 300:
        return True

    # avoid urls with excessive query parameters
    params = parse_qs(parsed.query, keep_blank_values=True)
    if sum(len(values) for values in params.values()) > 10:
        return True

    return False


def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False

        # only crawl the four domains
        allowed = ["ics.uci.edu",
                   "cs.uci.edu",
                   "informatics.uci.edu",
                   "stat.uci.edu"]

        # accepting subdomains of our main domains
        hostname = parsed.hostname
        if hostname is None:
            return False
        if not any(hostname == domain or hostname.endswith("." + domain)
                   for domain in allowed):
            return False

        # rejecting non-ASCII urls
        if not url.isascii():
            return False

        # check if trap
        if is_trap(url):
            return False

        path = unquote(parsed.path).lower()
        blocked_extentions = (
            ".css", ".js", ".bmp", ".gif", ".jpg", ".jpeg",
            ".ico", ".png", ".tif", ".tiff", ".mid", ".mp2",
            ".mp3", ".mp4", ".wav", ".avi", ".mov", ".mpeg",
            ".ram", ".m4v", ".mkv", ".ogg", ".ogv", ".pdf",
            ".ps", ".eps", ".tex", ".ppt", ".pptx", ".doc",
            ".docx", ".xls", ".xlsx", ".names", ".data",
            ".dat", ".exe", ".bz2", ".tar", ".msi", ".bin",
            ".7z", ".psd", ".dmg", ".iso", ".epub", ".dll",
            ".cnf", ".tgz", ".sha1", ".thmx", ".mso",
            ".arff", ".rtf", ".jar", ".csv", ".rm", ".smil",
            ".wmv", ".swf", ".wma", ".zip", ".rar", ".gz",
            ".svg", ".webp", ".avif", ".woff", ".woff2",
            ".ttf", ".otf", ".ics", ".xml", ".json"
        )
        if path.endswith(blocked_extentions):
            return False

        # reject anything with these in them bc of the wiki images
        wiki = {
            "/wiki/file:",
            "/wiki/image:",
            "/special:filepath/",
            "/special:redirect/file/"
        }

        if any(pattern in path for pattern in wiki):
            return False

        # also reject any image-serving endpoints
        if path.endswith(("/thumb.php", "/img_auth.php")):
            return False

        # some wiki pages use query parameters with images
        query = parse_qs(parsed.query)
        for title in query.get("title", []):
            if title.lower().startswith(("file:", "image:")):
                return False

        return True
    # a little confused here, can i change this? don't want crawler to crash if it
    # encounters an url we want to reject
    except (TypeError, ValueError) as e:
        print(f"Invalid URL {url!r}: {e}")
        return False
