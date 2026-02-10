import re
from urllib.parse import urlparse, urljoin, urldefrag
from bs4 import BeautifulSoup
from analytics import record_page

url_pattern_counts = {}

ALLOWED_DOMAINS = [".ics.uci.edu", ".cs.uci.edu", 
                           ".informatics.uci.edu", ".stat.uci.edu"]


def scraper(url, resp):
    if resp.status == 200 and resp.raw_response and resp.raw_response.content:
        
        # It returns False if the word count is < 50.
        is_high_quality = record_page(resp.url, resp.raw_response.content)
        
        # 2. STOP if content is low quality (Instruction: Avoid low information pages)
        if not is_high_quality:
            return []
            
        # 3. STOP if the file is massive (Instruction: Avoid very large files)
        if len(resp.raw_response.content) > 1_000_000:
            return []
            
        # 4. Process links only if the page passed the checks above
        links = extract_next_links(url, resp)
        return [link for link in links if is_valid(link)]
        
    return []


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
    #checks if the page was recieved
    if resp.status != 200 or not resp.raw_response:
        return []
    if not hasattr(resp, 'raw_response') or not resp.raw_response: return []
    if not resp.raw_response.content or len(resp.raw_response.content) < 250: return []
    
    hyperlinks = set() # Use a set to prevent adding the same link twice per page

    try:
        soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
        for anchor in soup.find_all('a'):
            href = anchor.get('href')
            if href:
                full_url = urljoin(resp.url, href)
                clean_url = urldefrag(full_url)[0]
                
                # Check duplication against clean_url, not full_url
                if clean_url in hyperlinks:
                    continue

                parsed = urlparse(clean_url)
                
                # Use hostname to safely handle ports
                if parsed.hostname and any(parsed.hostname.endswith(d) for d in ALLOWED_DOMAINS):
                    hyperlinks.add(clean_url)
    except Exception as e:
        print(f"Error extracting links from {url}: {e}")
        
    return list(hyperlinks)

def is_valid(url):
    global url_pattern_counts
    try: 
        parsed = urlparse(url)

        if not url  or url.strip() in ['-', '#'] or len(url) > 300:
            return False
        
        full_url_low = url.lower()
        path_low = parsed.path.lower()
        
        host = parsed.hostname
        if not any(host == d.strip(".") or host.endswith(d) for d in ALLOWED_DOMAINS):
            return False
        
        if re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico|png|tiff?|mid|mp2|mp3|mp4|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            r"|epub|dll|cnf|tgz|sha1|thmx|mso|arff|rtf|jar|csv|rm|smil|wmv|swf|wma|zip|rar|gz"
            r"|patch|diff|git|ipynb|emx|mpg|scm|ss|rkt|nb|nbp|bib|odp|db|war|dtd|sql|img"
            r"|ics|ical|xml|json)$", path_low):
            return False
        
        trap_patterns = [
            # Slide & Presentation Traps (~ziv, ~dsm, etc.)
            r".*/~[a-zA-Z0-9]+/.*(sld|tsld)[0-9]+\.htm.*",
            r".*/~[a-zA-Z0-9]+/(presentations|slides)/.*",
            
            # Wiki maintenance & revisions
            r".*/doku\.php/projects:maint-.*",
            r".*/doku\.php/.*(\?do=diff|\&rev=).*",
            
            # Legacy archives (Pre-2023)
            r".*/~[a-zA-Z0-9]+/(courses|teaching|class|assignments|homeworks|grad/courses)/(19|20[0-2])[0-9].*",
            
            # Recursive publications & technical silos
            r".*/~[a-zA-Z0-9]+/publications/[ar][0-9]+[A-Z]?\.html.*",
            r".*/~[a-zA-Z0-9]+/(papers|softwares|benchmarks|bibs|junkyard)/.*",
            
            # Calendar & Event Loops
            r".*(\?tribe|eventdisplay|ical|outlook-ical|eventdate=).*",
            r".*/events/.*(month|list|tag|page/|today|week).*",
            r".*/events/20[0-2][0-9]-[0-9]{2}.*",
            
            # GitLab & Mailman sinks
            r"^https?://gitlab\.ics\.uci\.edu/.*(/-/|/tags|/branches|/commits|/starrers|/forks|/activity|/users).*",
            r"^https?://mailman\.ics\.uci\.edu/.*",
            
            # Photo galleries and image browsing
            r'.*/gallery/.*(\?|&)(page|image|photo)=.*',
            r'.*/photos/.*[0-9]{3,}.*',
            r'.*/images?/.*[0-9]{3,}.*',
            
            # Pagination traps
            r'.*/page/[0-9]{2,}.*',
            r'.*[\?&]page=[0-9]{2,}.*',
            
            # Date-based archives (can create infinite combinations)
            r'.*/[0-9]{4}/[0-9]{2}/[0-9]{2}.*',
            r'.*/archive/[0-9]{4}.*',
            
            # Search and filter combinations
            r'.*[\?&](filter|sort|order|search|query)=.*',
            
            # Session IDs and tracking parameters
            r'.*[\?&](session|sid|token|key|PHPSESSID)=.*',
            
            # PDF viewers and document processors
            r'.*/pdfviewer.*',
            r'.*[\?&](view|viewer|display)=.*',
            
            # Printer-friendly and share versions
            r'.*[\?&](print|share|format)=.*',
            
            # Comment and reply chains
            r'.*[\?&](replytocom|comment)=.*',
            
            # Version control and diff pages
            r'.*/diff/.*',
            r'.*/compare/.*',
        ]
        for pattern in trap_patterns:
            if re.search(pattern, full_url_low):
                return False
        
        # catches repeating directories /abc/abc/abc
        if re.search(r'(/.+?)\1{2,}', path_low):
            return False
        

        # Detect path depth (prevent extremely deep paths)
        path_segments = [p for p in parsed.path.split('/') if p]
        if len(path_segments) > 15:  # Maximum depth limit
            return False
        
        # Detect too many duplicate segments in path
        if len(path_segments) > 0 and len(path_segments) > len(set(path_segments)) + 3:
            return False
        
        # Blocks infinite commit/tree hashes and repeating folders
        if any(x in parsed.path.lower() for x in ['/commit/', '/tree/', '/blob/', '/raw/', '/src/','/pix/']):
            return False
        if re.search(r'(/[^/]+)\1{2,}', parsed.path):
            return False
        
        if len(parsed.path.split('/')) > 10:
            return False
        # Combined check for query and path to catch shuffled Wiki/Apache params
        trap_params = [
            'action=', 'do=', 'rev=', 'format=', 'timeline=', 'image=', 
            'tab_details=', 'tab_files=', 'ns=', 'share=', 'diff=', 
            'view=', 'day=', 'month=', 'year=', 'idx=', 'c=', 'o=', 'sort='
        ]
        
        if any(param in full_url_low for param in trap_params):
            return False

        # Blocks known trouble spots like infinite calendars and helpdesks
        if any(keyword in parsed.path.lower() for keyword in [
            "/calendar/", "/wp-content/", "/login", "/events/page/", 
            "/doku.php", "/~eppstein/pix/"]):
            return False
        
        # Track URL patterns to detect traps (removing numbers to find patterns)
        pattern = re.sub(r'\d+', 'N', url)
        url_pattern_counts[pattern] = url_pattern_counts.get(pattern, 0) + 1
        
        # If we've seen this pattern too many times, it's likely a trap
        if url_pattern_counts[pattern] > 30:
            return False
        return True

    except Exception as e:
        print(f"Validation error for {url}: {e}")
        return False

