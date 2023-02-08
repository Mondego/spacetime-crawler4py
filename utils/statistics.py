from urllib.parse import urlparse
from collections import defaultdict
import tldextract

def write_statistics(pages):
    subdomains_count = update_subdomain_count(pages)
    with open('statistics.txt', 'w+') as f:
        f.write('Number of unique pages: ' + str(len(pages)))
        for key, value in subdomains_count.items():
            f.write('%s:%s\n' % (key, value))

def update_subdomain_count(urls):
    subdomains_count = defaultdict(int)
    for url in urls:
        parsed_url_parts = urlparse(url)
        domain = parsed_url_parts.netloc.split('.')
        if(len(domain)) > 3:
            if domain[1] == 'ics':
                subdomains_count[url] += 1
    return dict(sorted(subdomains_count.items()))