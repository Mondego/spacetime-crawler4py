import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import nltk
nltk.download('punkt')

class maxWordCount():
    # This class counts the total number of words on every webpage/
    # Stores the maximum word count.
    maxWords = 0
    longestURL = ""
    
    def tokenizer(self, soup) -> list:
        # This function tokenizes the webpage and forms a token list.
        # Uses a soup object as parameter. Returns the token list.
        # Use this method to tokenize new webpage being crawled. 
        
        # The text is the string of all the words on the webpage without the HTML markup
        text = soup.get_text(strip=True)
        textWithoutSymbols = re.sub(r"[^A-Za-z0-9\s]+", "", text)
        # Tokenizes the text into a list.
        token_lst = nltk.word_tokenize(textWithoutSymbols)
        return token_lst
    
    @classmethod
    def updateURL(cls, token_lst, url) -> None:
        # This function updates the maximum number of words on the webpage recorded so far.
        # If the length of the current webpage's token_lst is greater than the
        # already recorded count, then update the current longest length.
        
        # Use this method to compare the new tokenlst returned from tokenizer, 
        # and compare with current maxWord number.
        if len(token_lst) > cls.maxWords:
            cls.maxWords = len(token_lst)
            cls.longestURL = url
            
        
            
if __name__ == "__main__":
    pass