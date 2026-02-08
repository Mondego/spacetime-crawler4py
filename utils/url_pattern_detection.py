import hashlib
import re
from urllib.parse import urlparse, parse_qs

def get_url_parts(url):
    """Breaks url string into domain, path, query params"""
    parsed_url = urlparse(url)
    
    domain, path = parsed_url.netloc, parsed_url.path
    query_str = parsed_url.query
    query_str_dict = parse_qs(query_str)
    query_str_dict={k:v[0] for k,v in query_str_dict.items()}
    return domain, path, query_str_dict


def get_segment_category(seg):
    """detects segment's category and returns it, otherwise it returns the segment"""
    seg = seg.lower().strip()
    UUID_RE = re.compile(
        r"^[0-9a-fA-F]{8}-"
        r"[0-9a-fA-F]{4}-"
        r"[1-5][0-9a-fA-F]{3}-"
        r"[89abAB][0-9a-fA-F]{3}-"
        r"[0-9a-fA-F]{12}$"
    )

    DATE_RE = re.compile(
        r"^\d{4}[-/]\d{2}[-/]\d{2}$"
    )

    INT_RE = re.compile(r"^\d+$")

    DASHED_SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)+$")

    HEX_RE = re.compile(r"^[0-9a-fA-F]{8,}$")


    if UUID_RE.match(seg):
        return "UUID"

    if DATE_RE.match(seg):
        return "DATE"

    if INT_RE.match(seg):
        return "INT"

    if HEX_RE.match(seg):
        return "HEX"

    if DASHED_SLUG_RE.match(seg):
        return "SLUG"

    return seg

def drop_control_query_params(query_dict):
    """remove common tracking query params"""
    DROP_QUERY_KEY_PATTERNS = [
        re.compile(r"^utm_", re.IGNORECASE),
        re.compile(r"^_g", re.IGNORECASE),
        re.compile(r"session", re.IGNORECASE),
        re.compile(r"^sid$", re.IGNORECASE),
    ]
    filtered_params = {
        key: val
        for key, val in query_dict.items()
        if not any(p.search(key.lower()) for p in DROP_QUERY_KEY_PATTERNS)
    }
    return filtered_params

    

def hash_url_pattern(url_str):
    return hashlib.sha256(url_str.encode('utf-8')).hexdigest()
    
def get_url_pattern_hash(url):
    """convert url string to url pattern """
    domain, path, query_str_dict = get_url_parts(url)

    path_list = map(get_segment_category,path.split('/'))
    query_str_dict = drop_control_query_params(query_str_dict)
    query_list = [f"{key.lower()}={get_segment_category(val)}" for key, val in sorted(query_str_dict.items())]
 
    path_str = '/'.join(path_list)
    query_str = "&".join(query_list) 
    url_pattern = f"{domain}{path_str}?{query_str}"
    return hash_url_pattern(url_pattern)
    
def hash_url_pattern(url_str):
    return hashlib.sha256(url_str.encode('utf-8')).hexdigest()




        



if __name__=="__main__":
    get_url_pattern_hash("https://ics.uci.edu/events?qparam1=123&qparam2=45def&qparam3=3a269590-909d-431b-8bdf-516b02bd181f")
    get_url_pattern_hash("https://ics.uci.edu/event/master-of-computer-science-information-session-02-09-26/")
    get_url_pattern_hash("https://uci.zoom.us/meeting/register/l39e8nu_Qy-CT5pi0VeL_g#/registration")
    get_url_pattern_hash("https://edstem.org/us/courses/90198/discussion/7629727")
    get_url_pattern_hash("https://mail.google.com/mail/u/0/#inbox")