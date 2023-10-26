import re
import requests
from urllib.parse import urlparse, urljoin, urldefrag
from bs4 import BeautifulSoup
from collections import Counter
from difflib import SequenceMatcher

seed = "https://ics.uci.edu/" 
# seed = "https://sami.ics.uci.edu/research.html"

# linkSet will transform list of links into a set to remove duplicates
linkSet = set()

# pagewordCounts dictionary will hold url and word count
pageWordCounts = {}

# subdomainCounts dictionary will hold subdomains and their frequency
subdomainCounts = {}

# wordCounter will hold number of times a certain word is read
wordCounter = Counter()

# list of stopwords
stopWords = stopwords = set([
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", 
    "are", "aren't", "as", "at", "be", "because", "been", "before", "being", "below", 
    "between", "both", "but", "by", "can't", "cannot", "could", "couldn't", "did", "didn't", 
    "do", "does", "doesn't", "doing", "don't", "down", "during", "each", "few", "for", 
    "from", "further", "had", "hadn't", "has", "hasn't", "have", "haven't", "having", "he", 
    "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself", "him", "himself", 
    "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", 
    "isn't", "it", "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my", 
    "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", 
    "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", 
    "she'll", "she's", "should", "shouldn't", "so", "some", "such", "than", "that", "that's", 
    "the", "their", "theirs", "them", "themselves", "then", "there", "there's", "these", "they", 
    "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too", "under", 
    "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", 
    "weren't", "what", "what's", "when", "when's", "where", "where's", "which", "while", "who", 
    "who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd", 
    "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves"
])


def scraper(url, resp):
    if is_valid(url):
        print("Testing URL: " , url)
        try:
            resp = requests.get(url)
        except:
            print("Timeout")

        # Store number of unique pages
        links = extract_next_links(url, resp)

        if links is not None:
            for link in links:
                if link not in linkSet:
                    linkSet.add(link)
        else:
            print("No more links here! Moving on...")

        links.remove(url)

        print("Extracted Links:")
        if(links is not None):
            linkSet.update(links)
            # Find number of unique pages
            uniquePages = len(linkSet)
            print("Number of Unique Pages: ", uniquePages)
        
        # Store word count for the current URL
        content = resp.text
        pageWordCounts[url] = count_words(content)

        # Update wordCounter for each tokenized word, not including stop words
        tokens = tokenize(content)
        for word in tokens:
            if word not in stopWords:
                wordCounter[word] += 1

        parsed_url = urlparse(url)
        if parsed_url.netloc.endswith('ics.uci.edu'):
            
            # Extract the subdomain part
            subdomain = parsed_url.netloc.rsplit('.', 2)[0]

            if subdomain == 'ics':
                subdomain = parsed_url.netloc.rsplit('.', 3)[1]
            
            # Increment count for the subdomain or initialize it if it doesn't exists
            subdomainCounts[subdomain] = subdomainCounts.get(subdomain, 0) + 1

        # if links is not None:
            # for link in links:
        # if linkSet is not None:
        #     for link in linkSet:
        #         print(link)
    else:
        print(url, " is not a valid URL for crawling.")



    # Find the url of the longest page in terms of words count
    if pageWordCounts:
        longest_page_url = max(pageWordCounts, key=pageWordCounts.get)
        print("Longest page URL:", longest_page_url)
        print("Number of words:", pageWordCounts[longest_page_url])

    # Get the 50 most common words
    most_common_words = wordCounter.most_common(50)
    print("50 most common words:", most_common_words)

    # Print out the counts for each subdomain
    sorted_subdomains = sorted(subdomainCounts.items(), key=lambda x: x[0])  # Sort by subdomain name
    for subdomain, count in sorted_subdomains:
        print(f"http://{subdomain}.ics.uci.edu, {count}")

    # returns a list of links
    return [link for link in linkSet if is_valid(link)]
    # return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    link_list = []


    # checking if we actually got the page
    # do we have to check utf-8 encoding?
    # print(resp.status_code)
    # print(resp.headers)
    if resp.status_code == 200:
        try:
            # use BeautifulSoup library to parse the HTML content of the page
            # print("Raw Content: ", raw)

            soup = BeautifulSoup(resp.text, 'html.parser')

            # this code is mid i think
            # we want to eliminate the possibility of a 404 page which doesnt return 
            # an error 404 code, such as http://cs.uci.edu/page
            # title_tag = soup.find("title")
            # invalid_title = "Page not found"

            # # checks if Page not found is title, if so break of function
            # if title_tag and invalid_title:
            #     return

            # print("Parsed Content: ", soup.prettify())



            # in the HTML, we want to find all '<a>' tags and extract the link, the 'href'
            for curr in soup.find_all('a'):
                link = curr.get('href')
                if link:
                    # we then use 'urllib.parse: urljoin' in order to combine the relative URL's with our base URL in order to get our final URL
                    url_joined = urljoin(url, link)

                    # Use 'urllibe.parse: urldefrag' to remove the fragment, as in this assignment we ignore the fragment 
                    if "#" in url_joined:
                        url_joined = urldefrag(url_joined).url
                   
                    final_url = url_joined

                    # checks validity of our final_url - if it is valid, then we can add it to our list of links
                    if is_valid(final_url):
                        link_list.append(final_url)

        except Exception as e:
            print("ERROR: Error parsing " + url + str(e))       
    # if the response code was something other than 200, means there was an error - print it so we can see
    else:
        print("Error: " + str(resp.status_code))
        return

    return link_list


# FUNCTION: is_valid(url) - checks the validity of a URL:str passed in - returns a boolean True or False
def is_valid(url):
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False

        # List of disallowed file extensions
        invalid = [
            "css", "js", "bmp", "gif", "jpg", "jpeg", "ico",
            "png", "tif", "tiff", "mid", "mp2", "mp3", "mp4",
            "wav", "avi", "mov", "mpeg", "ram", "m4v", "mkv", "ogg", "ogv", "pdf",
            "ps", "eps", "tex", "ppt", "pptx", "doc", "docx", "xls", "xlsx", "names",
            "data", "dat", "exe", "bz2", "tar", "msi", "bin", "7z", "psd", "dmg", "iso",
            "epub", "dll", "cnf", "tgz", "sha1", "thmx", "mso", "arff", "rtf", "jar", "csv",
            "rm", "smil", "wmv", "swf", "wma", "zip", "rar", "gz"
        ]

        # List of valid domains we can crawl in
        domains = ["ics.uci.edu", "cs.uci.edu", "informatics.uci.edu", "stat.uci.edu"]

        # Check if the parsed domain matches any of the allowed domains
        domain_check = any(parsed.netloc.endswith("." + domain) or parsed.netloc == domain for domain in domains)

        # Check if the path doesn't have invalid extensions
        extension_check = not any(parsed.path.lower().endswith("." + filetype) for filetype in invalid)

        # return the boolean expression determined by the logical AND of domain_match and extension_match
        # if the url exists in our valid domains and does not fall under any of the invalid extensions, return True, else return False
        return domain_check and extension_check

    except TypeError:
        print("TypeError for ", parsed)
        raise

def tokenize(content):
    # Strip HTML markup
    soup = BeautifulSoup(content, 'html.parser')
    newContent = soup.get_text()

    # Splits words and creates list, non word characters act as the break
    # cleanTokens will set all tokens lower case and will discard any tokens with length less than 2 letters
    tokens = re.split(r'\W+', newContent)
    cleanTokens = []
    for token in tokens:
        if len(token) > 2:
            token.lower()
            cleanTokens.append(token)

    return cleanTokens


def count_words(content):
    # Strip HTML markup
    soup = BeautifulSoup(content, 'html.parser')
    newContent = soup.get_text()

    # Use regex to count the number of words in the content
    words = re.findall(r'\w+', newContent)
    return len(words)



resp = requests.get(seed)
urlsss = scraper(seed, resp)

print("URL's Scraped From Seed")
for i in urlsss:
    print(i)


# ------------------------------------------------------------------- OLD DRIVER CODE - KEEP JUST IN CASE----------------------------------------------------------------------------

# test_urls = [
#     # These are all for validity checker
#     # "https://www.ics.uci.edu/page",
#     # "http://cs.uci.edu/page",
#     # "https://informatics.uci.edu/page",
#     # "https://stat.uci.edu/page",
#     # "https://www.google.com/page",
#     # "ftp://invalid-url.com/ftp-page",
#     # "https://www.linkedin.com/feed/",
#     # "https://drive.google.com/drive/u/0/my-drive",
#     # "https://www.youtube.com/watch?v=_ITiwPMUzho&ab_channel=LofiGhostie",
#     # "https://www.youtube.com/watch?v=TUEju_i3oWE&ab_channel=Insomniac",
#     # "https://github.com/gregkhanoyan/IR23F-A2-G33#things-to-keep-in-mind",
#     # "https://canvas.eee.uci.edu/courses/58552/assignments/1243743",
#     # These are actual links that can be crawled
#     # "https://ics.uci.edu/academics/undergraduate-academic-advising/",
#     # "https://ics.uci.edu/academics/undergraduate-academic-advising/change-of-major/",
#     # "https://grape.ics.uci.edu/wiki/public/wiki/cs122b-2019-winter",

#     # "http://www.ics.uci.edu",
#     "https://sami.ics.uci.edu/"

# ]

# for url in test_urls:
#     if is_valid(url):
#         print("Testing URL: " , url)
#         try:
#             resp = requests.get(url)
#         except:
#             print("Timeout")
#         # Store number of unique pages
#         links = extract_next_links(url, resp)

#         if links is not None:
#             for link in links:
#                 if link not in linkSet:
#                     test_urls.append(link)
#         else:
#             print("No more links here! Moving on...")

#         test_urls.remove(url)

#         print("Extracted Links:")
#         if(links is not None):
#             linkSet.update(links)
#             # Find number of unique pages
#             uniquePages = len(linkSet)
#             print("Number of Unique Pages: ", uniquePages)


#         # Store word count for the current URL
#         content = resp.text
#         pageWordCounts[url] = count_words(content)

#         # Update wordCounter for each tokenized word, not including stop words
#         tokens = tokenize(content)
#         for word in tokens:
#             if word not in stopWords:
#                 wordCounter[word] += 1

#         parsed_url = urlparse(url)
#         if parsed_url.netloc.endswith('ics.uci.edu'):
#             # Extract the subdomain part
#             subdomain = parsed_url.netloc.rsplit('.', 2)[0]

#             if subdomain == 'ics':
#                 subdomain = parsed_url.netloc.rsplit('.', 3)[1]
            
#             # Increment count for the subdomain or initialize it if it doesn't exists
#             subdomainCounts[subdomain] = subdomainCounts.get(subdomain, 0) + 1

#         # if links is not None:
#             # for link in links:
#         # if linkSet is not None:
#         #     for link in linkSet:
#         #         print(link)
#     else:
#         print(url, " is not a valid URL for crawling.")



# # Find the url of the longest page in terms of words count
# if pageWordCounts:
#     longest_page_url = max(pageWordCounts, key=pageWordCounts.get)
#     print("Longest page URL:", longest_page_url)
#     print("Number of words:", pageWordCounts[longest_page_url])

# # Get the 50 most common words
# most_common_words = wordCounter.most_common(50)
# print("50 most common words:", most_common_words)

# # Print out the counts for each subdomain
# sorted_subdomains = sorted(subdomainCounts.items(), key=lambda x: x[0])  # Sort by subdomain name
# for subdomain, count in sorted_subdomains:
#     print(f"http://{subdomain}.ics.uci.edu, {count}")

# for url in test_urls:
#     if is_valid(url):
#         print(f"{url} is a valid URL for crawling.")
#     else:
#         print(f"{url} is not a valid URL for crawling.")
