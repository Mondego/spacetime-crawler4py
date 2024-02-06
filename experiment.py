from bs4 import BeautifulSoup
import requests

# urls = ['.stat.uci.edu/','.informatics.uci.edu/','.cs.uci.edu/','.ics.uci.edu/']
urls = ['https://stat.uci.edu/',
        'https://informatics.uci.edu/',
        'https://cs.uci.edu/',
        'https://ics.uci.edu/']
import os, sys, re
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import urllib.request, urllib.error, urllib.parse

def download_page_content(urls):
    for url in urls:

        response = urllib.request.urlopen(url)
        webContent = response.read().decode('UTF-8')
        name = url.split('.')[0]
        tag_name = name.split('//')[1]
        with open(f"/home/xiaofl/Desktop/cs121/hw2/spacetime-crawler4py/web_page/{tag_name}.html",'w') as f:
            f.write(webContent)
"""
find the Site map with: https://ics.uci.edu/feed/ ??? 
"""
    # savePage(url,)


def find_all_pages(url:str):
    # current ly save all pages in a file 
    grab = requests.get(url)
    soup = BeautifulSoup(grab.text, 'html.parser')
    for link in soup.find_all("a"):
        data = link.get('href')
        print(data)
    # with open("test1.txt", "w") as f: 
    # # traverse paragraphs from soup
    #     for link in soup.find_all("a"):
    #         data = link.get('href')
    #         f.write(data)
    #         f.write("\n")

import csv

csvfile = r"/home/xiaofl/Desktop/cs121/hw2/spacetime-crawler4py/debug_log/experiment.csv"
experiment = r'/home/xiaofl/Desktop/cs121/hw2/spacetime-crawler4py/debug_log/word_count.csv'
with open(experiment, mode='a',newline='\n',encoding='utf-8') as csvfile:
    t = '1111111wwwwwwwweeqwqwrqqweqwe'
    filename = ['Word','Count']
    writer = csv.DictWriter(csvfile,fieldnames=filename)
    writer.writerow({'Word':'department','Count':500})

    
    