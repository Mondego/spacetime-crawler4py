import re
import requests
from urllib.parse import urlparse, urljoin, urldefrag
from bs4 import BeautifulSoup
from collections import Counter

# Seed URL: http://www.ics.uci.edu

"""
    EXPLANATION:

    Currently, the driver code at the bottom first takes a list of URL's to test. The first marked portion of those URL's
    are invalid URL's used to test the 'is_valid(url)' function, which works as so:

    is_valid(url):
        The function takes a URL 'url' of type string. It then parses the URL into a URL scheme object, which basically means it is now an object with
        recognized URL structure, 'parsed'. We check if it is not an 'http' or 'https' URL, and if it is not, we return False.

        Next, we recognize a list of invalid filetype extensions we want to ignore, which was provided in the skeleton code. We also recognize a list of
        valid domains we can crawl in. These are the ones provided to us by the assignment specifications. 

        We then check whether or not the parsed URL object we created, 'parsed' contains the valid domains we can crawl in. We do this by checking the network
        location aspect of the URL, 'netloc', and checking if it ends with .'domain', or if it simply exists here, whatever the valid domain in this case may be.
        We do the same for checking if any extensions are invalid.

        Next, we return the boolean expression determined by the logical AND of domain_check and extension_check. 
        If the url exists in our valid domains and does not fall under any of the invalid extensions, return True, else return False.
     
    The driver code iterates through each URL in the testing list and uses the 'requests' library to retrieve a 'Response' object, which we need for our HTML parsing.
    We pass this 'Response' object, 'resp' and a string URL 'url', into the 'extract_next_links(url, resp)' function, which works as so:

    extract_next_links(url, resp):
        We first create an empty list to store our list of links, 'link_list'. We then check for a valid status code of 200, which means we successfully retrieve the
        page we want. 
        
        Next we use the BeautifulSoup library to parse the request HTML, using 'resp.text' as our source parameter to be parsed through. Our goal of this
        function is to extract every link from this webpage, so we need to find every element in the HTML with an <a> tag, as that corresponds to an href (HTML hyperlink).
        For every <a> tag, we want to return the corresponding href. 
        
        We then 'urllib.parse: urljoin' in order to combine the relative URL's with our base URL in order to get our final URL (a bit confused on this, need more 
        explanation on what this means lmao). 

        We then defragment the URL, that is, remove everything after any "#" characters in the URL, as we ignore fragments for this assignment.

        Finally, we check the validity of our final URL, by using the 'is_valid(url)' function. If the URL is valid, we can append it to our list of URL's, 'link_list'.

        We check for errors and finally return our list of links/URL's, extracting from each page/URL we are parsing, as 'link_list'.

    We then print all of the links just to see our code in action and ensure everything looks good.
    We also print whether or not a link is valid and can be crawled.

    NEED TO DO:

        MISC.
        - Deal with duplicate links in 'extract_next_links(url, resp)' function

    Deliverables:
        - Determine how many unique pages we found (unique = URL - fragment)
            - should be easy, since we already defragment in 'extract_next_links(url, resp)'
        - Determine the longest page in terms of the number of words (HTML markup doesn't count as words)
            - Need to find a way to calculate word number without HTML markup code
            - can def use some library for this (explore BeautifulSoup)
            - Word Length count printed?
        - Determine the 50 most common words in the entire set of pages crawled under these domains. Submit list in order of frequency
            - Use Assignment 1 Code
            - Ignore "English Stop Words: https://www.ranks.nl/stopwords"
        - Determine how many subdomains we found in the 'ics.uci.edu' domain. Submit list of subdomains ordered alphabetically and 
        number of unique pages detected in each subdomain. 
            - Content should be like so: {URL, number} e.g. {http://vision.ics.edu, 10}
    
    
    Scraper Function:
        I feel like some of what needs to be in the 'scraper(url, resp)' function is already in 'extract_next_links(url, resp)'.
        I will look soon and try to move it around. This is what the scraper function is supposed to do:
            - Receive a URL and corresponding Web Response (url, resp)
            - Parse the Web Response
                - extract information from the page (if valid) to answer deliverable questions above ^^^^
                - return a list of URL's scrapped from that page
                    - make sure to only return URL's that are within the domains allowed (is_valid(url) function deals w/ this)
                    - Defragment URL's - done in 'extract_next_links(url, resp)' but triple check cuz this is major
    
    Politeness
        I haven't even looked at what we need to do to obey politeness rules.
            - Learn how to implement robots.txt politeness policies
    
    Check for a Correct Crawl - HARD PART - READ ALL!
        - Honor politeness delay for each site (robots.txt)
        - Crawl all pages with high textual information content
            - not sure what defines high here
        - Detect and avoid infinite traps
        - Detect and avoid sets of similar pages w/ no information
            - Decide and discuss a reasonable definition for low information page + defend it in the TA talk
        - Detect redirects and if the page redirects your crawler, index the redirected content
        - Detect and avoid deal URL's that return a 200 status but no data
            - https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html                   could be useful here
        - Detect and avoid crawling very large files, esp. if they have low information content
        - Transform relative URL's to absolute URL's - I think I did this in 'extract_next_links(url, resp)'
        - Ensure we send the server a request with ASCII URL
            - make sure that the URL being requested is ics.uci.edu, not <a href="ics.uci.edu">
        - Write simple automatic trap detection systems (???)
        - Use openlab/tmux (??? on tmux, never used it before)
    
    CRAWLER MUST BEHAVE CORRECTLY BY: Friday, 10/27 by 9:00 PM
    DEPLOYMENT STAGE: Monday, 10/30 to Friday, 11/3 by 9:00 PM
        - Crawler must crawl 3 times during deployment stage

"""

def scraper(url, resp):
    # list of valid links
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

    # NEED TO
    # parse the web response, 'resp', extract information from here answering deliverable questions
    # return list of URL's scrapped from that page
    #   return only valid URL's
    #   defragment URL's (remove fragment)
    #   use library (BeautifulSoup, lxml)


def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status_code: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again    
    #         resp.raw_response.content: the content of the page! (NOT CORRECT VARIABLE)
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content

    # retrieving final page URL after redirects - keep this Greg for testing/matching after implementation
    # actual_url = resp.url

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

# DRIVER CODE

test_urls = [
    # These are all for validity checker
    "https://www.ics.uci.edu/page",
    "http://cs.uci.edu/page",
    "https://informatics.uci.edu/page",
    "https://stat.uci.edu/page",
    "https://www.google.com/page",
    "ftp://invalid-url.com/ftp-page",
    "https://www.linkedin.com/feed/",
    "https://drive.google.com/drive/u/0/my-drive",
    "https://www.youtube.com/watch?v=_ITiwPMUzho&ab_channel=LofiGhostie",
    "https://www.youtube.com/watch?v=TUEju_i3oWE&ab_channel=Insomniac",
    "https://github.com/gregkhanoyan/IR23F-A2-G33#things-to-keep-in-mind",
    "https://canvas.eee.uci.edu/courses/58552/assignments/1243743",
    # These are actual links that can be crawled
    "https://ics.uci.edu/academics/undergraduate-academic-advising/",
    "https://ics.uci.edu/academics/undergraduate-academic-advising/change-of-major/",
    "https://grape.ics.uci.edu/wiki/public/wiki/cs122b-2019-winter"
]

# linkSet transforms list of links into a set to remove duplicates
linkSet = set()
# pagewordCounts dictionary holds url and word count
pageWordCounts = {}
# subdomainCounts dictionary hold subdomains and it's frequency
subdomainCounts = {}
wordCounter = Counter()
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

def tokenize(content):
    tokens = re.split(r'\W+', content)
    cleanTokens = [token.lower() for token in tokens if token and len(token) > 2]

    return cleanTokens


def count_words(content):
    # Use regex to count the number of words in the content
    words = re.findall(r'\w+', content)
    return len(words)


for url in test_urls:
    if is_valid(url):
        print("Testing URL: " , url)
        resp = requests.get(url)

        # Store number of unique pages
        links = extract_next_links(url, resp)
        print("Extracted Links:")
        linkSet.update(links)

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
            
            # Increment count for the subdomain or initialize it if it doesn't exists
            subdomainCounts[subdomain] = subdomainCounts.get(subdomain, 0) + 1

        for link in links:
            print(link)
    else:
        print(url, " is not a valid URL for crawling.")

# Find number of unique pages
uniquePages = len(linkSet)
print("Number of Unique Pages: ", uniquePages)

# Find the url of the longest page in terms of words count
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

# for url in test_urls:
#     if is_valid(url):
#         print(f"{url} is a valid URL for crawling.")
#     else:
#         print(f"{url} is not a valid URL for crawling.")


