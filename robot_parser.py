import urllib.request
import io

class Robot_Parse:
    def __init__(self, url):
        self.url_copy = url
        self.url = url
        self.made_request = False
        if self.url[-10:] == "robots.txt":
            self.inserted_robots = True
        else:
            self.inserted_robots = False

    def insert_robots(self):
        self.inserted_robots = True
        if self.url[-1] != "/":
            self.url += "robots.txt"
        else:
            self.url += "/robots.txt"

    def robots_request(self):
        self.made_request = True
        web_request = urllib.request.urlopen(self.url, data=None)
        self.data = io.TextIOWrapper(web_request, encoding='utf-8')
        
    def robots_read(self):
        print(self.data.read())

    def original_url(self):
        return self.url_copy
if __name__ == "__main__":
    save = Robot_Parse("https://www.reddit.com/robots.txt")
    save.robots_request()
    save.robots_read()
    