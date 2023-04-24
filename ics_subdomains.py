import re
from urllib.parse import urlparse
# for tracking question #4

class icsSubdomains:

    subdomainDict = {} # key: directory -> val: counter

    @classmethod
    def addToSubdomain(cls, link:urlparse) -> None:
        """ If a subdomain exists and has not been found before, add it to this dictionary. If it has been found, increment the counter for that subdomain. """
        path_subdomain = re.sub("\/[^\/]*$", "", link.path)
        subdomain = link.netloc + path_subdomain + '/'

        # Strips the page, and returns [site]/[most recent directory]"""
        # i.e. www.ics.uci.edu.com/about/us -> www.ics.uci.edu.com/about/
        try:
            cls.subdomainDict[subdomain] += 1
        except KeyError: # directory does not exist
            cls.subdomainDict[subdomain] = 1
