class Unique:
    def __init__(url: str):
        """
        Unique objects helps determine unique urls,
        ignoring the fragmented parts of the url, and
        counts the number of unique urls
        """
        url_list = [] #
        unique_url_counter = 0

    def url_to_unique(url:str):
        no_fragment = True
        new_url = ""
        for c in url:
            if no_fragment:
                if 35 == ord(c):
                    no_fragment = False
                else:
                    new_url += c
        return new_url
