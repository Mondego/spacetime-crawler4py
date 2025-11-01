import re
from urllib.parse import urlparse, urldefrag, urlunparse, parse_qs
from lxml import html, etree
import configparser
from utils import STOPWORDS

INVALID_PATH_STRINGS = ("/wp-json/", "/oembed/", "/xmlrpc.php", "wp-login.php")
TRAP_QUERY = (
"filter", "term=", "do=", "tab_files=", "image=", "tab_details=", "ns=", "idx=", "redirect_to=", "C=", "O=",
"tribe-bar-date=", "ical=", "tribe__ecp_custom_")


def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]


def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    next_links = list()
    if resp.status == 200 and resp.raw_response:
        if not resp.raw_response.content:
            return []
        try:
            parsed_resp = html.fromstring(resp.raw_response.content)
        except etree.ParserError as e:
            print(f"parser error at {resp.raw_response.url}: {e}")
            return []
        parsed_resp.make_links_absolute(resp.raw_response.url)
        links = parsed_resp.xpath("//a/@href")
        valid_links = [link for link in links if is_valid(link)]  # get all valid links
        for link in valid_links:
            next_links.append(normalize_url(link))
    elif resp.status != 200:
        print("status ")
    return next_links


def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    # parsed (.scheme = http?s, hostname='ics.uci.edu'(netloc includes :port), path='/files/image.png', query =...)
    try:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            return False
        if not is_allowed_domain(parsed.hostname):
            return False
        if path_has_sus_word(parsed.path):
            return False
        if is_trap_query(parsed.query):
            return False
        if is_grape_trap(parsed.hostname, parsed.path, parsed.query):
            return False
        if not is_under_page_limit(parsed.path):
            return False
        if is_helpdesk_id_query(parsed.hostname, parsed.query):
            return False
        if has_git_dash(parsed.hostname, parsed.path, parsed.query):
            return False
        if is_events_date_trap(parsed.path, parsed.query):
            return False
        if invalid_datasets_page(parsed.path, parsed.query):
            return False
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4|sql"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1|class|apk|xml|json|ini"
            + r"|thmx|mso|arff|rtf|jar|csv|ya?ml|log|ttf"
            + r"|py|txt|ipynb|r|cpp|mht|war|c|tmpl|fnt|java"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print("TypeError for ", parsed)
        raise


def is_allowed_domain(hostname):
    parser = configparser.ConfigParser()
    parser.read("config.ini")
    temp = parser["ALLOWED_HOSTNAME"]["hostname"]
    ALLOWED_HOSTS = [host.strip() for host in temp.split(',')]
    # print(ALLOWED_HOSTS)
    return any(hostname == host or hostname.endswith("." + host) for host in ALLOWED_HOSTS)


def is_under_page_limit(path):
    PAGE_LIMIT = 500
    if "/page/" in path:
        match = re.search(r"/page/(\d+)/?", path)
        if match:
            page = match.group(1)
            return int(page) <= PAGE_LIMIT
    return True


def is_trap_query(query):
    return any(q in query for q in TRAP_QUERY)


def is_grape_trap(host, path, query):
    if "grape." in host and ("timeline" in path or "version=" in query or "format=" in query or "action=" in query):
        return True
    return False


def is_helpdesk_id_query(host, query):
    if "helpdesk" in host and "id" in query:
        return True
    return False


def has_git_dash(host, path, query):
    if "git" in host:
        if "/-/wikis/" in path :
            return False
        elif "/-/" in path:
            return True
        if "sort" in query:
            return True
    return False


def path_has_sus_word(path):
    return any(p in path for p in INVALID_PATH_STRINGS)


# to do: event/2000-01-01 event/month/... etc
def is_events_date_trap(path, query):
    DATE_REGX = re.compile(r"\b\d{4}-(0[1-9]|1[0-2])\b")
    if "eventDate=" in query and DATE_REGX.search(query):
        return True
    if "/events/" in path and DATE_REGX.search(path):
        return True
    return False


# : datasets?search=
def invalid_datasets_page(path, query):
    query_dict = parse_qs(query, keep_blank_values=True)
    if "datasets" in path:
        sort = (query_dict.get("sort") or [""])[0]
        orderBy = (query_dict.get("orderBy") or [""])[0]
        search = (query_dict.get("search") or [""])[0]
        # print(f"sort:{sort}, orderBy:{orderBy}, search:{search}")
        if search != "":
            return True
        if not (sort == "desc" and orderBy == "NumHits" ):
            return True

        idx = query.find("search=")
        if idx != -1 and query[idx + len("search="):] != "":
            # print(f"search={query[idx + 7:]}")
            return True

    return False


def normalize_url(url):
    """
    Assume url is already absolute. i.e. not a relative path
    :param url:
    :return:
    """
    defrag_url, frag = urldefrag(url)
    parsed_url = urlparse(defrag_url)
    netloc = _remove_default_port(_strip_www(parsed_url.netloc), parsed_url.scheme)
    normalized = urlunparse((parsed_url.scheme, netloc, parsed_url.path, "", parsed_url.query, ""))
    return normalized


def _remove_default_port(netloc, scheme):
    """
    :param netloc: the netloc string from urlparse object. example : "abcd.com:1234"
    :param scheme: e.g. "https"
    :return: a netloc without default port for http or https
    """
    if ':' not in netloc:
        return netloc
    host, port = netloc.split(":")
    if not port.isdigit():
        print(f"port -> [{port}] is not a number")
        return netloc
    if (scheme == "http" and port == "80") or (scheme == "https" and port == "443"):
        return host
    return netloc

def count_word(raw_content):
    pass


def _strip_www(netloc):
    if netloc.startswith('www.'):
        return netloc[4:]
    return netloc


if __name__ == "__main__":
    _url = "https://ics.uci.edu/page/3/?post_type=tribe_events&eventDisplay=day&eventDate=2026-02-07"
    test_url = "https://gitlab.ics.uci.edu/sgroup/test5/-/commit/56a0be976cc4370acfda4df43b2b35828abd9576?view=parallel"
    parsed = urlparse(_url)
    _hostname = parsed.hostname
    _path = parsed.path
    _query = parsed.query
    _DATE_REGX= re.compile(r"\b\d{4}-(0[1-9]|1[0-2])\b")
    # print(_DATE_REGX.search(_url))
    # print(f"invalid datasets page ? : {invalid_datasets_page(_path, _query)}")

    # print(f"calendar trap:{is_events_date_trap(_path)}")
    print(is_valid(test_url))
    # print(f"is allowed domain ? url {_hostname} : {is_allowed_domain(_hostname)}")
    # print(f"is trap query ? query {_query} : {is_trap_query(_query)}")
    # print(f"path : {parsed.path} , under limit? {is_under_page_limit(parsed.path)}")
    # print(f"is valid? {is_valid(_url)}")
