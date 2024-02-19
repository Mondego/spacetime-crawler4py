import re
from urllib.parse import urlparse,urlunparse,urljoin
import bs4, requests
import csv
from crawling_function import stats

response = requests.get('https://www.nytimes.com/',headers={'User-Agent': 'Mozilla/5.0'})
valid_domains = [
            "ics.uci.edu",
            "cs.uci.edu",
            "informatics.uci.edu",
            "stat.uci.edu"
        ]  

###############
def handle_high_textual_content(url,soup,stats = stats,threshold = 100):
    """
    1. if the file is too large, return none
    get a resp, check if has more than 100 words and no urls
    consider this url as low textual content and skip it
    2. if the file content has redundant we return None
    
    else 
    return the urls in this page, and word count 
    """
    urls = []
    if soup.body == None:
        return None
    
    # print(f'url soup is not none {url}')
    raw_text = soup.body.get_text(' ', strip=True)

    stats.update_word_count(raw_text)
    text_in_page = raw_text.split()
    # print(f'test what is text in page: {text_in_page}')
    num_word = len(text_in_page)
    try: 
        for link in soup.find_all("a"):
            urls.append(link.get('href'))
    except:
        return None
    if num_word < threshold and len(urls) ==0:
        return None
    if stats.is_near_duplicate(raw_text,url):
        return None
    if num_word > stats.page_with_most_text['wordcount']:
        stats.page_with_most_text['url'] = url
        stats.page_with_most_text['wordcount'] = num_word
        stats.update_csv(url,stats.page_word_count_file,count = num_word)
    # stats.update_csv(url,stats.crawled_urls_file)
    return (urls,num_word)

def handle_ics_subdomain(url, stats = stats):
    """
    only looking for domain with ics.uci.edu
    if the domain has more than ics uci edu, we determine it as ics uci edu subdomain
    """
    parsed_url = urlparse(url)
    domain_parts = parsed_url.netloc.split('.')
    ics_uci_domain_parts = "ics.uci.edu".split('.')

    if len(domain_parts) < len(ics_uci_domain_parts):
        return False

    for i in range(len(ics_uci_domain_parts)):
        if domain_parts[-(i+1)] != ics_uci_domain_parts[-(i+1)]:
            return False
    stats.update_csv(url,stats.subdomains_file)
    stats.subdomains.add(url)
    return True


def is_url(url):
    """
    make sure the urls from href is a actual url 
    """
    try:
        result = urlparse(url)
        return any([result.scheme, result.netloc])
    except ValueError:
        return False
    
def handle_robots(text,domain,stats = stats):
    """
    this code will make the content in robots 
    and add the absolute url to allowed, disallowed url set
    """
    robot_parser = text.split('\n')
    for line in robot_parser:
        if line.startswith('User-agent'):
            _, agent = line.split(': ')
        elif line.startswith('Allow'):
            content = line.split(': ')
            if len(content) ==2:
                absolute_url = handle_relative_url(f'http://{domain}',content[1].strip())
                stats.allowed_path.add(absolute_url)
                
        elif line.startswith('Disallow'):
            content = line.split(': ')
            if len(content) ==2:
                absolute_url = handle_relative_url(f'http://{domain}',content[1].strip())
                stats.disallowed_path.add(absolute_url)
    


def remove_fragment(url):
    """
    only accept scheme, netloc (domain), path, params, query, empty the fragment
    """
    parsed_url = urlparse(url)
    defrag_page_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, parsed_url.params, parsed_url.query,'' ))
    defrag_page_url= defrag_page_url.rstrip('/')
    return defrag_page_url

def handle_relative_url(base,url):
    """
    if a url is not start with "http://", "https://" will be considered as relative url 
    1. we will need the base url the url that contain the current url crawled, 
    2. join the base url and the current relative url 
    """
    if not url.startswith(("http://", "https://")):
        # print(f'relative url : {url}, the base is {base}')
        absolute_url = urljoin(base, url)
        return absolute_url
    else:
        return url
    

def is_robot_allowed_url(url, allowed = stats.allowed_path , disallowed = stats.disallowed_path):
    """
    2. if urls are allowed by robot, return true
    3. if urls are not found in allowed and specified disallowed, return false
    1. if urls are not specified by robot, return true
    """
    parsed_url = urlparse(url)
    path = parsed_url.path

    for allowed_url in allowed:
        if path.startswith(urlparse(allowed_url).path):
            return True
    for disallowed_url in disallowed:
        if path.startswith(urlparse(disallowed_url).path):
            return False
    # print(f'is_robot_allowed_url is working')
    return True

def is_trap(url,stats= stats,threshold = 200):
    """
    we count the number of certain scheme domain path 
    if certain scheme domain path occur more than threshold: 200 time we consider it as trap 
    """
    # RAP_PARAMS = {"action=download","action=login","action=edit"}
    parsed_url = urlparse(url)
    # print(f'path {parsed_url.path == ""} ?')
    # means this url is like https://ics.uci.edu
    if parsed_url.path == "":
        return False
    preserved_parts = (parsed_url.scheme, parsed_url.netloc, parsed_url.path, '', '', '')
    preserved_url = urlunparse(preserved_parts)
    if stats.repeat_url_counter[preserved_url] < threshold:
        stats.repeat_url_counter[preserved_url] +=1 
        return False
   
    stats.update_csv(url,stats.trap_detection_file)
    return True


################


def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]
    
def extract_next_links(url, resp):
    """
    return empty list 
        1. if status code is 404, 
        2. if url already crawled,
        3. if status code start with 3xx, 
            we handle redirect url by return empty list
            because resp did not provide us redirect url  
        4. if resp is none or resp raw response is none 
        5. if size of url is too large more than 10 * 1024 * 1024 length
        6. if content of url is highly similar (handled in handle_high_textual_content )
        
    """
    if resp.status == 404:
        return list()
    
    # not crawling crawled url
    if url in stats.crawled_urls:
        return list()
    
    stats.crawled_urls.add(url)
    stats.update_csv(url,stats.crawled_urls_file)
    if resp.status in (301,302,307,308): 
        stats.update_csv(url,stats.redirect_file,redirect =resp.url)
        return list()

    if resp.status != 200 or resp==None or resp.raw_response == None:
        return list()
    
    if url.endswith("/robots.txt"):
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        text = resp.raw_response.text
        handle_robots(text,domain)
        return list()
    next_urls = []
     
 
    MAX_FILE_SIZE = 10 * 1024 * 1024
    # print('[test] len of current url content is:',len(resp.raw_response.content))
    if len(resp.raw_response.content)> MAX_FILE_SIZE:
        # print(f'the file in url {url} is too large')
        return list()
    
    handle_ics_subdomain(url)
    soup = bs4.BeautifulSoup(resp.raw_response.content,'html.parser')
    content = handle_high_textual_content(url,soup)
    # print("dup_count: ",stats.dup_count)
    # url crawled

    # if fail to pass the high_textual content function requirements
    if content == None:
        return list()
    else:
        
        stats.unique_pages += 1
        # print(f'current url is {resp.url}')
        urls,num_word = content[0],content[1]
        for sub_url in urls: 
            # first remove fragment: 
            if is_url(sub_url):
                absoluted_url = handle_relative_url(base=url,url=sub_url)
                url_without_fragment = remove_fragment(absoluted_url)
                next_urls.append(url_without_fragment)
        return next_urls
    
def is_valid(url):
    """
    return false: 
     1. if the url is not in given domains 
     2. if the url is not allowed by robot.txt
     3. already crawled url 
     4. we update to not accept ppsx urls
    """
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        
        # prevent repeat url
        if url in stats.crawled_urls:
            # print(f'repeat url: {url}, {stats.crawled_urls}')
            return False

        # follow the robot.txt
        if not is_robot_allowed_url(url):
            return False

        # handle the trap here
        if is_trap(url):
            return False
        ## make sure the url is under the given domains, if not return false
        valid_domains = [
            "ics.uci.edu",
            "cs.uci.edu",
            "informatics.uci.edu",
            "stat.uci.edu"
        ]
        if not any(parsed.netloc.endswith(domain) for domain in valid_domains):
            return False

        #need to exclude "pdf" in the middle of a path
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz|ppsx|odc)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise

