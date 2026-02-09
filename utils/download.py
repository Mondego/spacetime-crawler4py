import requests
import cbor # packaging format for data sent 
import time
from threading import Lock
from urllib.parse import urlparse
from utils.response import Response

#Reference for politeness implementation: https://dev.to/h0tb0x/webcrawling-is-just-a-brute-force-algorithm-2meg, https://www.packtpub.com/en-us/product/python-web-scraping-9781782164364/chapter/1-introduction-to-web-scraping-1/section/crawling-your-first-website-ch01lvl1sec05, https://realpython.com/python-thread-lock/    
domain_last_accessed = {} # Track last access time for each domain to enforce politeness
domain_locks = {} # Locks for each domain to ensure thread safety when updating access times
global_lock = Lock() # Global lock to protect access to domain_locks

# Download page content using the cache server. Handles politeness, server codes, large content, and dead pages. Return resp or None.
def download(url, config, logger=None):
    # Per domain politeness
    parsed = urlparse(url)
    domain = parsed.netloc.lower()

    # Create per-domain lock safely with global lock
    with global_lock:
        if domain not in domain_locks:
            domain_locks[domain] = Lock()

    # Enforce politeness atomically with the domain-specific lock
    with domain_locks[domain]:
        last_access = domain_last_accessed.get(domain)
        if last_access is not None: # if we have accessed this domain before, check if we need to wait
            elapsed = time.time() - last_access
            if elapsed < config.time_delay:
                time.sleep(config.time_delay - elapsed)

        # Update access time "before" request 
        domain_last_accessed[domain] = time.time()

    # Cache server request
    host, port = config.cache_server
    try:
        resp = requests.get(
            f"http://{host}:{port}/",
            params=[("q", f"{url}"), ("u", f"{config.user_agent}")], timeout=10)
    
        # If the cache server returns a valid response, we parse it and return a Response object.
        if resp and resp.content:
            return Response(cbor.loads(resp.content))
        
    except (requests.RequestException, EOFError, ValueError) as e:
        if logger:
            logger.warning(f"Download exception for {url}: {e}")
        return None
    
    # Malformed response from cache server
    if logger:
        logger.error(f"Spacetime Response error {resp} with url {url}.")

    return Response({
        "error": f"Spacetime Response error {resp} with url {url}.",
        "status": resp.status_code,
        "url": url})