import csv
from urllib.parse import urlparse,urlunparse,urljoin
from collections import defaultdict


##  we use this code to process the subdomain
## we first store all the unique subdomain in csv file, and after process stop we print out the sorted subdomains
def process_csv(csv_file):
    # subdomains = defaultdict(lambda: {'pages': '', 'count': 0})
    subdomains_dict = defaultdict(int)
    unique_urls = set()
    unique_subdomains = set()
    with open(csv_file, mode='r', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['URL', 'Word Count',"redirect"]
        reader = csv.DictReader(csvfile,fieldnames=fieldnames)
        for row in reader:
            url = row['URL']
            if url not in unique_urls:
                unique_urls.add(url)
                parsed_url = urlparse(url)
                subdomain = urlunparse((parsed_url.scheme, parsed_url.netloc, '', '', '','' ))
                # print(f'subdomain i found: {subdomain}')
                unique_subdomains.add(subdomain)
                subdomains_dict[subdomain] +=1

    sorted_subdomains = sorted(subdomains_dict.items(), key=lambda x: x[0], reverse=False)
    result = []
    print(f'total {len(unique_subdomains)} of ics.uci.edu subdomains')
    print(unique_subdomains,'\n')
    for subdomain, count in sorted_subdomains:
        print(f'subdomain {subdomain}, count {count}')

    # return result
    
process_csv('/home/xiaofl14/cs121/hw2/spacetime-crawler4py/debug_log/subdomains_file.csv')