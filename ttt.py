from urllib.parse import urlparse

x = urls = [
    "https://www8.cao.go.jp",
    "https://police.uci.edu",
    "https://portal.uci.edu",
    "https://twitter.com",
    "https://www.stat.uci.edu",
    "http://www.redcross.org",
    "https://repository.lib.ncsu.edu",
    "https://www.informatics.uci.edu",
    "https://hengruicai.github.io",
    "https://www.ehs.uci.edu"]
#     "https://www.who.int",
#     "https://www.php.net",
#     "https://www.dokuwiki.org",
#     "http://youtube.com",
#     "http://www.uci.edu",
#     "https://www.weforum.org",
#     "http://www.informatics.ics.uci.edu",
#     "http://directory.uci.edu",
#     "http://www.youtube.com",
#     "https://cscw.acm.org",
#     "http://catalogue.uci.edu",
#     "http://www.ehs.uci.edu",
#     "http://www.informatics.uci.edu",
#     "https://www.ics.uci.edu",
#     "http://jigsaw.w3.org",
#     "http://html5up.net",
#     "http://www.ics.uci.edu",
#     "http://www.mckinsey.com",
#     "http://creativecommons.org",
#     "https://www.basicbooks.com",
#     "http://udsauci.weebly.com",
#     "http://validator.w3.org",
#     "https://www.wyzant.com",
#     "http://intranet.ics.uci.edu",
#     "https://seal.ics.uci.edu",
#     "https://www.choc.org",
#     "https://campusgroups.uci.edu",
#     "http://engineering.uci.edu",
#     "https://ehs.ucop.edu",
#     "http://hai.ics.uci.edu",
# ]

valid_domains = {"ics", "stat", "informatics", "cs"} # set of valid domains 
for url in x:
    parsed = urlparse(url)
    parsed_broken = parsed.netloc.split('.')
    if not any(domain in url for domain in valid_domains):
        print(f"{url} is not valid")
