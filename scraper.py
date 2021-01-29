import re
from urllib.parse import urlparse
import pickle
from bs4 import BeautifulSoup
from word_freq import WordFreq
import report


# TODO: How many subdomains did you find in the ics.uci.edu domain?
def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]


def extract_next_links(url, resp):
    # pickle.dumps
    print(resp.raw_response)
    # Implementation requred.
    # 1. parse resp
    #   1.1 get all url
    #   1.2 clean up hmtl 
    #   1.3 tokenize + filter stop word + count work
    print("hello "+url)
    print(is_valid(url))
    return list()


def extract_word_freq(url, content):
    soup = BeautifulSoup(content, 'html.parser')
    pure_content = soup.get_text()
    parsed_content = WordFreq(pure_content)
    # tokenize
    token_lst = parsed_content.tokenize()
    # filter out stop word
    filtered_lst = parsed_content.filter_stop(token_lst)
    # get number of words in this page
    page_len = len(filtered_lst)
    Report.page_length = max(Report.page_length, page_len)
    if page_len > Report.page_length:
        Report.page_length = page_len
        Report.longest_page_url = url

    for i in filtered_lst:
        if i not in Report.word_freq:
            Report.word_freq[i] = 0
        Report.word_freq[i] += 1


def is_valid(url):
    # TODO: change it to verify the url is in xxx domains
    
    # * *.ics.uci.edu/*
    # 	* 
    # *.cs.uci.edu/*
    # 	* 
    # *.informatics.uci.edu/*
    # 	* 
    # *.stat.uci.edu/*
    # 	* 
    # today.uci.edu/department/information_computer_sciences/*
    if re.match(r".*\.((ics|cs|informatics|stat).uci.edu|today.uci.edu/department/information_computer_sciences)(\/.*)?", url):
        return True
    else: 
        return False


    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
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