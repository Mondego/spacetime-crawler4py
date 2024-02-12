import re
from urllib.parse import urlparse,urlunparse,urljoin
import bs4, requests
import csv
from scraper_stats import stats
response = requests.get('https://www.nytimes.com/',headers={'User-Agent': 'Mozilla/5.0'})



#TODO: I am not sure this stats object will be only intialized once 


def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]
    
def follow_robots(url):
    pass

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
    # check if the url has the scheme if not this is relative url 
    # this function will return the relative url with its base
    if not url.startswith(("http://", "https://")):
        stats.update_abnormal_url_csv(url, 'relative url')
        # print(f'relative url : {url}, the base is {base}')
        absolute_url = urljoin(base, url)
        stats.update_abnormal_url_csv(absolute_url, 'absolute url')
        return absolute_url
    else:
        return url
    
def extract_next_links(url, resp):
    try: 
        current_depth = stats.url_depth[resp.url]
        print(f'current url depth is {stats.url_depth[url]}')
    except:
        stats.update_abnormal_url_csv(url,'Not in depth record')
        current_depth = 1
    print(f'from scraper: current url is {url}, status is {resp.status}, is there error {resp.error},')
   
    #TODO: current depth limit is 100, if depth exceed 100 consider as trap
    if current_depth > 100:
        return list()
    if resp.status != 200:
        return list()
    
    # Handle redirect url
    if resp.status ==307 or resp.status ==308 :
        stats.update_abnormal_url_csv(url,'redirect')
        url = resp.url 
 
    MAX_FILE_SIZE = 10 * 1024 * 1024
    # print('[test] len of current url content is:',len(resp.raw_response.content))
    if len(resp.raw_response.content)> MAX_FILE_SIZE:
        print(f'the file in url {url} is too large')
        return list()
    
    #collecting subdomain: 
    subdomain = extract_subdomain(url)
    stats.update_subdomain_csv(url)
    stats.subdomains.add(subdomain)

    #TODO: get all text from given url: not sure if the current implementation capture all the text content
    soup = bs4.BeautifulSoup(resp.raw_response.content,'lxml')

    # avoid crawling empty content url 
    if soup.body == None:
        print(f'empty url {url}')
        return list()
    if soup.body:
        text_in_page = soup.body.get_text(' ', strip=True)
        # print(f'***[test] the len of text in page is {len(text_in_page)} content is {text_in_page}')
        stats.update_stats(url=url,text=text_in_page)
    
    #TODO: for next urls: 
    url_list = []
    for link in soup.find_all("a"):
        page_url = link.get('href')
        if page_url:
            #TODO: handle how to collect stats with fragment urls: counting unique page
            defrag_page_url = remove_fragment(page_url)
            
            # make relative url to absolute url
            defrag_page_url = handle_relative_url(base=url,url=defrag_page_url)
            stats.url_depth[defrag_page_url] = current_depth +1
            
            # prevent store repeat url
            if "#" not in defrag_page_url and defrag_page_url not in stats.page_word_count:
                url_list.append(defrag_page_url)
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

