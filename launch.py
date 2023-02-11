from configparser import ConfigParser
from argparse import ArgumentParser

from utils.server_registration import get_cache_server
from utils.config import Config
from utils.statistics import write_statistics
from crawler import Crawler
from collections import defaultdict

import signal
import sys

pages = set()
max_word_count_global = dict(word_count = 0, url = '')
high_freq_words_global = defaultdict(int)

def signal_handler(sig, frame):
    print('You pressed Ctrl+C, writing statistics to output!')

    write_statistics(pages, max_word_count_global, high_freq_words_global)

    sys.exit(0)


def main(config_file, restart):
    cparser = ConfigParser()
    cparser.read(config_file)
    config = Config(cparser)
    config.cache_server = get_cache_server(config, restart)
    crawler = Crawler(config, restart, pages, max_word_count_global, high_freq_words_global)
    crawler.start()


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--restart", action="store_true", default=False)
    parser.add_argument("--config_file", type=str, default="config.ini")
    args = parser.parse_args()
    signal.signal(signal.SIGINT, signal_handler)
    main(args.config_file, args.restart)
