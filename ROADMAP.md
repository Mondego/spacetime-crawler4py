How We Take a W On This Project
==============
    
# Current Code Breakdown:

  Currently, the driver code at the bottom first takes a list of URL's to test. The first marked portion of those URL's
  are invalid URL's used to test the 'is_valid(url)' function, which works as so:

  **is_valid(url):** **UPDATE**
  
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

  **extract_next_links(url, resp):** **UPDATE**
  
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

  # NEED TO DO:

  ***MISC.***
  - Verify web page word count
  - fix subdomain typo - **fix this part of the deliverables as a whole lmao**
  - **FIND A WAY TO CALCULATE DELIVERABLE STATISTICS INDEPENDENT OF SCRAPER.PY?**
  - **NO DRIVER CODE**
  - Check for HTML Response codes other than 200 (e.g. 403 Forbidden)
  - Deal with duplicate links in 'extract_next_links(url, resp)' function
  - **Page Similarity** (ASCII?) + **AVOID TRAPS!!!!!!!!!!!**
  - Longest page URL being invalid - why is it considering this if it throws a 404 error?
  - **SUBDOMAINS - NUMBER AND ORDERED ALPHABETICALLY**
  - check for head being empty (**timed out**)
  - **CHECK FOR INVALID PAGES -> REAL PAGE BUT ERROR STATEMENTS IN HEAD**
  - Define what we consider pages with "high textual information content" and crawl **only** those pages - ignore low information content
      - Detect and avoid crawling very large files, esp. if they have low information content
      - Decide and discuss a reasonable definition for low information page + defend it in the TA talk
  - Politeness
  - - Detect and avoid deal URL's that return a 200 status but no data
      - https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html could be useful here
  - Detect redirects and if the page redirects your crawler, index the redirected content
  -  Ensure we send the server a request with ASCII URL
      - make sure that the URL being requested is ics.uci.edu, not <a href="ics.uci.edu">
  - tmux


 # Deliverables:
 
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
  
  **Politeness**      
  - Learn how to implement **robots.txt** politeness policies
  
  ***CRAWLER MUST BEHAVE CORRECTLY BY:*** Friday, 10/27 by 9:00 PM
  
  ***DEPLOYMENT STAGE:*** Monday, 10/30 to Friday, 11/3 by 9:00 PM
      - Crawler must crawl 3 times during deployment stage
