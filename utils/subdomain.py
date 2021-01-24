from urllib.parse import urlparse

import re

class SubDomainPrinter:
    def __init__(self, config, restart: bool):
        self.config = config
        self.domain = config.domain

    # takes a list of urls and prints subdomains to file
    def print_sub_doms_to_file(self, urls: list) -> None:
        with open(self.config.subdomain_file, "a") as file:
            for url in urls:
                dom = urlparse(url).hostname
                if self._is_subdomain(dom):
                    file.write(dom + '\n')
    
    # checks if domain is a subdomain
    def _is_subdomain(self, sub_dom: str) -> bool:
        re_string = f"^((.+)\.)+{re.escape(self.domain)}$"
        pattern = re.compile(re_string)
        return pattern.match(sub_dom)