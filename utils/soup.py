from bs4 import BeautifulSoup as bs4

def get_soup(resp):
    if resp.raw_response == None:
        return None

    page_text = resp.raw_response.text
    soup = bs4(page_text, 'html.parser')
    return soup
