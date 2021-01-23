from soup import get_soup

def print_page_links(resp):
    soup = get_soup(resp)

    if soup == None:
        print("soup is none")
        return

    for link in soup.find_all('a'):
        print(link.get('href'))

def print_page_text(resp):
    soup = get_soup(resp)

    if soup == None:
        print("soup is none")
        return

    for p_elem in soup.find_all('p'):
        print(p_elem.get_text())
