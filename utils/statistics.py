from urllib.parse import urlparse
from collections import defaultdict
import tldextract

def write_statistics(pages, max_word_count_global, high_freq_words_global):
    subdomains_count = update_subdomain_count(list(pages))
    with open('statistics.txt', 'w+') as f:
        f.write('Number of unique pages : ' + str(len(pages))+'\n')
        f.write('Subdomain count \n')
        for key, value in subdomains_count.items():
            f.write('%s -- %s\n' % (key, value))

    with open("processed_text.txt", 'w') as f:
            f.write('URL with Max No.of words \n')
            for key, value in max_word_count_global.items():
                f.write('%s:%s\n' % (key, value))
            f.write('50 high freq words \n')
            for key, value in high_freq_words_global.items():
                f.write('%s:%s\n' % (key, value))

def update_subdomain_count(urls):
    subdomains_count = defaultdict(int)
    for url in urls:
        parsed_url_parts = urlparse(url)
        if (url == '' or parsed_url_parts.netloc == '' or isinstance(parsed_url_parts.netloc, str) is False):
            continue
        domain = parsed_url_parts.netloc.split('.')
        if (len(domain)) > 3:
            if domain[1] == 'ics':
                url_string = parsed_url_parts.scheme + '://' + parsed_url_parts.netloc
                subdomains_count[url_string] += 1
    return dict(sorted(subdomains_count.items()))