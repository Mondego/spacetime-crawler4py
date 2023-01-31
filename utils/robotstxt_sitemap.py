import time
from response import Response
from config import Config
from logging import Logger
from download import download


def get_sitemap_urls(seed_urls: list[str], config: Config, logger: Logger=None) -> list[str]:
    '''Return the sitemap urls from each url's robots.txt page'''
    sitemap_urls = list()
    for url in seed_urls:
        response = download(url, config, logger)
        if response.status == 200:
            sitemap_urls += _extract_sitemap_urls(response)
        time.sleep(config.time_delay)
    return sitemap_urls

def _extract_sitemap_urls(resp: Response) -> list[str]:
    '''Return all the sitemap urls from the response'''
    extracted_urls = list()
    if resp.raw_response is None:
        # shouldn't happen, but just in case
        return extracted_urls

    for line in resp.raw_response.split():
        if line.startswith('Sitemap'):
            extracted_urls.append(line.split()[1])
    return extracted_urls