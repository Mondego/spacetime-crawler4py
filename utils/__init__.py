import os
import logging
from hashlib import sha256
from urllib.parse import urlparse

from nltk.corpus import stopwords      # possibly delete this
from nltk.stem import PorterStemmer     # possibly delete this
from nltk.tokenize import RegexpTokenizer # possibly delete this
import requests                             # possibly delete this
from bs4 import BeautifulSoup

def get_logger(name, filename=None):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    if not os.path.exists("Logs"):
        os.makedirs("Logs")
    fh = logging.FileHandler(f"Logs/{filename if filename else name}.log")
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter(
       "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger


def get_urlhash(url):
    parsed = urlparse(url)
    # everything other than scheme.
    return sha256(
        f"{parsed.netloc}/{parsed.path}/{parsed.params}/"
        f"{parsed.query}/{parsed.fragment}".encode("utf-8")).hexdigest()

def normalize(url):
    if url.endswith("/"):
        return url.rstrip("/")
    return url


# potentially delete this
def get_contenthash(url):

    stop_words=set(stopwords.words("english"))  # get the stop_words in english
    stemmer = PorterStemmer()  # create a PorterStemmer object to stem any word
    tokenizer = RegexpTokenizer("\w+") # only tokenize words

    try:
        page = requests.get(url)
        soup = BeautifulSoup(page.content.decode("utf-8", "ignore"), "lxml")
        text_list = [stemmer.stem(word) for word in tokenizer.tokenize(soup.text.lower()) if word not in stop_words]
        new_text = " ".join(text_list)

        return sha256(new_text.encode("utf-8", errors="replace")).hexdigest()
    except Exception:
        return sha256("error".encode("utf-8", errors="replace")).hexdigest()
    


    