class Config(object):
    def __init__(self, config):
        self.user_agent = config["IDENTIFICATION"]["USERAGENT"]
        assert self.user_agent != "DEFAULT AGENT", f"useragent has to be set in config.ini"

        self.threads_count = int(config["LOCAL PROPERTIES"]["THREADCOUNT"])
        self.save_file = config["LOCAL PROPERTIES"]["SAVE"]

        self.host = config["CONNECTION"]["HOST"]
        self.port = int(config["CONNECTION"]["PORT"])

        self.seed_url = config["CRAWLER"]["SEEDURL"]

        self.cache_server = None