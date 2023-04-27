from configparser import ConfigParser
from argparse import ArgumentParser

from utils.server_registration import get_cache_server
from utils.config import Config
from crawler import Crawler


def main(config_file, restart):
    cparser = ConfigParser()
    cparser.read(config_file)
    config = Config(cparser)
    config.cache_server = get_cache_server(config, restart)
    crawler = Crawler(config, restart)
    crawler.start()


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--restart", action="store_true", default=False)     # run with --restart=True
    parser.add_argument("--config_file", type=str, default="config.ini")     # keep as is, don't need to type into CLI
    args = parser.parse_args()
    main(args.config_file, args.restart)        # have to tell it to restart in cmd line arguments
