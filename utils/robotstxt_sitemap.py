import time
from utils.response import Response
from utils.config import Config
from logging import Logger
from utils.download import download


def get_sitemap_urls(seed_urls: list[str], config: Config, logger: Logger=None) -> list[str]:
    '''Return the sitemap urls from each seed url's robots.txt page'''
    sitemap_urls = list()
    for url in seed_urls:
        response = download(url + '/robots.txt', config, logger)
        if response.status == 200:
            sitemap_urls += _extract_sitemap_urls(response)
        time.sleep(config.time_delay)
    return sitemap_urls

def _extract_sitemap_urls(resp: Response) -> list[str]:
    '''
    Return all the sitemap urls from the response.
    To be called by get_sitemap_urls, does the work of grabbing
      the sitemaps from each robots.txt page.
    '''
    extracted_urls = list()
    if resp.raw_response is None:
        # shouldn't happen, but just in case
        return extracted_urls

    for line in resp.raw_response.text.split('\n'):
        if line.startswith('Sitemap'):
            extracted_urls.append(line.split()[1])
    return extracted_urls