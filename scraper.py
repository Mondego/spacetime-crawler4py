import re
from urllib.parse import urlparse
from urllib.parse import urljoin
from urllib.parse import urldefrag
from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize
from utils.config import Config
import nltk
import pickle
from bs4 import BeautifulSoup
nltk.download('punkt')

def scraper(url, resp, config):
    
    links = extract_next_links(url, resp, config)
    list_domains = set()
    for seed_url in config.seed_urls:
        parsed_url = urlparse(seed_url)
        list_domains.add(parsed_url.netloc)
    res = [link for link in links if is_valid(link, list_domains)]
    #max length of the page missing
    url_dict = {"urls_done":[], "max_length_page_url":"", "max_page_length":0}
    try:
        with open('FileDumps/' + 'AllUrls' + '.pickle', 'rb') as handle:
            urls_done = pickle.load(handle)['urls_done']
            urls_done += res
            pickle.dump(urls_done, handle, protocol=pickle.HIGHEST_PROTOCOL)    
    except (OSError, IOError, EOFError) as e:
        url_dict["urls_done"] = res
        pickle.dump(url_dict, open('FileDumps/' + 'AllUrls' + '.pickle', 'wb'))

    return [link for link in links if is_valid(link, list_domains)]

def extract_next_links(url, resp, config):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content

    if not is_valid_page(resp):
        return []

    #html_text = resp.raw_response.content
    #soup = BeautifulSoup(html_text, "html.parser").find_all("a")
    #links = clean_and_filter_urls([link.get("href") for link in soup], url)
    #return links 
    # commenting text due to merge conflicts

    def clean_and_filter_urls(urls, curUrl):
        list = []
        for url in urls:
            url = url.split('#')[0]
            if(len(url) == 0):
                continue
            list.append(url)
        return list

    def is_valid_page(resp):
        if(resp.status>400):
            return False
        return True


    if resp.status != 200:
        print("Incorrect response")
        return list()
    html = resp.raw_response.content
    soup = BeautifulSoup(html, 'html.parser')
    urls_extracted = set()
    fdist = {}
    try:
        with open('FileDumps/' + "AllTokens" + '.pickle', 'rb') as handle:
            fdist = pickle.load(handle)
    except (OSError, IOError, EOFError) as e:
        pickle.dump(fdist, open('FileDumps/' + 'AllTokens' + '.pickle', 'wb'))

    data_url = None
    try:
        with open('FileDumps/' + 'AllUrls' + '.pickle', 'rb+') as handle:
            data_loaded = pickle.load(handle)
            max_len_file = data_loaded["max_page_length"]
            print(len(html), max_len_file)
            if len(html) > max_len_file:
                data_loaded["max_length_page_url"] = url
                data_loaded["max_page_length"] = len(html)
                #print(data_loaded["max_page_length"], data_loaded["max_length_page_url"])
                pickle.dump(data_loaded,open('FileDumps/' + 'AllUrls' + '.pickle', 'wb'))
    except (OSError, IOError, EOFError) as e:
        url_dict = {"urls_done":[], "max_length_page_url": url, "max_page_length":len(html)}
        pickle.dump(url_dict, open('FileDumps/' + 'AllTokens' + '.pickle', 'wb'))
     
    data = soup.get_text()          
    tokens = word_tokenize(data)
    for token in tokens:
        if token in fdist.keys():
            fdist[token] += 1
        else:
            fdist[token] = 1
   
    for link in soup.find_all('a'):
        path = link.get('href')
        if path and path.startswith('/'):
            path = urljoin(url, path)
            defrag_path = urldefrag(path) #defragment the URL
            urls_extracted.add(defrag_path.url) 
            parsed_url = urlparse(defrag_path.url)
            text_file_save = str(parsed_url.netloc + parsed_url.path).replace('/','_')
            #print(path, text_file_save)
            #f = open("FileDumps/" + text_file_save + ".txt", "w")
            #f.write(''.join(tokens))
            #f.close()
            
    with open('FileDumps/' + 'AllTokens' + '.pickle', 'wb') as handle:
        pickle.dump(fdist, handle, protocol=pickle.HIGHEST_PROTOCOL)        
           
    #save the URL and webpage on local disk
    return list(urls_extracted)

def is_valid(url, list_domains):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        #check seed_url hostnames for validity
        #check if fragme
        if parsed.scheme not in set(["http", "https"]):
            return False
        if parsed.netloc not in list_domains:
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
