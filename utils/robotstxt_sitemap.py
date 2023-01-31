from response import Response
from config import Config
from logging import Logger
from download import download


def get_sitemap_urls(seed_urls: list[str], config: Config, logger: Logger=None) -> list[str]:
    '''Return the sitemap urls from each url's robots.txt page'''
    sitemap_urls = list()
    for url in seed_urls:
        response = download(url, config, logger)
        sitemap_urls += _extract_sitemap_urls(response)
    return sitemap_urls

def _extract_sitemap_urls(resp: Response) -> list[str]:
    pass