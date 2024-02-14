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
def handle_high_textual_content(url,soup,stats = stats,threshold = 1000):
    """
    if the file is too large, return none
    get a resp, check if has more than 100 words and no urls
    consider this url as low textual content and skip it
    """
    # not crawling crawled url
    if url in stats.crawled_urls:
        return None
    
    urls = []
    if soup.body == None:
        return None
    raw_text = soup.body.get_text(' ', strip=True)

    stats.update_word_count(raw_text)
    # stats.print_word_count()
    # stats.update_word_count_csv()
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
    if stats.is_near_duplicate(text_in_page,url):
        return None




    
    if num_word > stats.page_with_most_text['wordcount']:
        stats.page_with_most_text['url'] = url
        stats.page_with_most_text['wordcount'] = num_word
        stats.update_csv(url,stats.page_word_count_file,count = num_word)
    stats.update_csv(url,stats.crawled_urls_file)
    return (urls,num_word)

def handle_ics_subdomain(url, stats = stats):
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
    try:
        result = urlparse(url)
        return any([result.scheme, result.netloc])
    except ValueError:
        return False

def check_robots(domain,stats=stats):
    robots_url = f"http://{domain}/robots.txt"
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
                    content = line.split(': ')
                    if len(content) ==2:
                        absolute_url = handle_relative_url(f'http://{domain}',content[1].strip())
                        stats.allowed_path[agent].append(absolute_url)
                        
                elif line.startswith('Disallow'):
                    content = line.split(': ')
                    if len(content) ==2:
                        absolute_url = handle_relative_url(f'http://{domain}',content[1].strip())
                        stats.disallowed_path[agent].append(absolute_url)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {robots_url}: {e}")

def remove_fragment(url):
    parsed_url = urlparse(url)
    defrag_page_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, parsed_url.params, parsed_url.query,'' ))
    defrag_page_url= defrag_page_url.rstrip('/')
    return defrag_page_url

def handle_relative_url(base,url):
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

    for allowed_url in allowed['*']:
        if path.startswith(urlparse(allowed_url).path):
            return True
    for disallowed_url in disallowed['*']:
        if path.startswith(urlparse(disallowed_url).path):
            return False
    return True

def is_trap(url,stats= stats,threshold = 1000):
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
    # print(f'this url {url} is trap')
    # assert False, f'{stats.repeat_url_counter}'
    stats.update_csv(url,stats.trap_detection_file)
    return True


################
#for d in valid_domains:
#    check_robots(d,stats)

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]
    
def extract_next_links(url, resp):
    
    next_urls = []
    if resp.status == 307 or resp.status ==308: 
        #TODO: still need to figure out redirect urls 
        print(f"Redirect URL: {url}")
        stats.update_csv(url,stats.redirect_file,redirect =resp.url)
        return list()

    if resp.status != 200:
        return list() 
 
    MAX_FILE_SIZE = 10 * 1024 * 1024
    # print('[test] len of current url content is:',len(resp.raw_response.content))
    if len(resp.raw_response.content)> MAX_FILE_SIZE:
        print(f'the file in url {url} is too large')
        return list()
    
    handle_ics_subdomain(url)
    soup = bs4.BeautifulSoup(resp.raw_response.content,'lxml')

    content = handle_high_textual_content(url,soup)
    print("dup_count: ",stats.dup_count)
    
    # url crawled

    # if fail to pass the high_textual content function requirements
    if content == None:
        return list()
    else:
        stats.crawled_urls.add(url)
        stats.unique_pages += 1
        print("URLS_CRAWELED: ", stats.unique_pages)
        print(f'current url is {resp.url}')
        urls,num_word = content[0],content[1]
        for sub_url in urls: 
            # first remove fragment: 
            if is_url(sub_url):
                absoluted_url = handle_relative_url(base=url,url=sub_url)
                url_without_fragment = remove_fragment(absoluted_url)
                next_urls.append(url_without_fragment)
        return next_urls
def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        # print(f'in is_valid {parsed}')
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

# def is_valid(url):
#     # Decide whether to crawl this url or not. 
#     # If you decide to crawl it, return True; otherwise return False.
#     # There are already some conditions that return False.
#     try:
#         parsed = urlparse(url)
#         if parsed.scheme not in set(["http", "https"]):
#             return False
        
#         ## make sure the url is under the given domains, if not return false
#         valid_domains = [
#             "ics.uci.edu",
#             "cs.uci.edu",
#             "informatics.uci.edu",
#             "stat.uci.edu"
#         ]
#         if not any(domain in parsed.netloc for domain in valid_domains):
#             return False
        
#         return not re.match(
#             r".*\.(css|js|bmp|gif|jpe?g|ico"
#             + r"|png|tiff?|mid|mp2|mp3|mp4"
#             + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
#             + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
#             + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
#             + r"|epub|dll|cnf|tgz|sha1"
#             + r"|thmx|mso|arff|rtf|jar|csv"
#             + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

#     except TypeError:
#         print ("TypeError for ", parsed)
#         raise

