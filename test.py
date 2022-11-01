import re
from urllib.parse import urlparse
from scraper import isBadDomain
from scraper import is_valid
s = {
"http://www.ics.uci.edu/~eppstein/pix/sdcbcw/1.html",
"http://www.economics.uci.edu/people/officehours.php",
"google.com.php/asdf",
"http://www.ics.uci.edu/~eppstein",
"www.ics.uci.edu/~agelfand/figs/largeFam3-"}
#parsed = url.urlparse(s1)
#if re.search('pix', parsed.path):
#    print("yes")
'''

print(isBadDomain(urlparse(s1).hostname ))
print(urlparse(s2).hostname)
print(isBadDomain( urlparse(s2).hostname))
print(isBadDomain (urlparse(s3).hostname))
'''
for string in s:
    print(is_valid(string), string)