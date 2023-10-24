# Deliverable Report

1. **How many unique pages did you find?**

    Uniqueness for the purposes of this assignment is ONLY established by the URL, but 
    discarding the fragment part. So, for example, http://www.ics.uci.edu#aaa and http://www.ics.uci.edu#bbb are the same URL. 
    Even if you implement additional methods for textual similarity detection, please keep considering the above definition of 
    unique pages for the purposes of counting the unique pages in this assignment.

2. **What is the longest page in terms of the number of words?**
  
    (HTML markup doesn’t count as words)

3. **What are the 50 most common words in the entire set of pages crawled under these domains?**
    
    Ignore English stop words, which can be found, for example, here (https://www.ranks.nl/stopwords). Submit the list of common words ordered by frequency.

4. **How many subdomains did you find in the ics.uci.edu domain?**

    Submit the list of subdomains ordered alphabetically and the number of unique pages detected in each subdomain.
    The content of this list should be lines containing URL, number, for example:
    http://vision.ics.uci.edu, 10 (not the actual number here)
