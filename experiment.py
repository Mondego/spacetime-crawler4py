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
for d in valid_domains:
    print(parse_robots_txt(d))
    
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

    
    