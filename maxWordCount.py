from urllib.parse import urlparse
from bs4 import BeautifulSoup
import nltk
nltk.download('punkt')

class maxWordCount():
    # This class counts the total number of words on every webpage/
    # Stores the maximum word count.
    
    def __init__(self):
        self.maxWords = 0
    
    def tokenizer(self, soup) -> list:
        # This function tokenizes the webpage and forms a token list.
        # Uses a soup object as parameter. Returns the token list.
        # Use this method to tokenize new webpage being crawled. 
        
        # The text is the string of all the words on the webpage without the HTML markup
        text = soup.get_text(strip=True)
        # Tokenizes the text into a list.
        token_lst = nltk.word_tokenize(text)
        return token_lst
    
    def updateMaxCount(self, token_lst) -> None:
        # This function updates the maximum number of words on the webpage recorded so far.
        # If the length of the current webpage's token_lst is greater than the
        # already recorded count, then update the current longest length.
        
        # Use this method to compare the new tokenlst returned from tokenizer, 
        # and compare with current maxWord number.
        if len(token_lst) > self.maxWords:
            self.maxWords = len(token_lst)
        
            
if __name__ == "__main__":
    pass