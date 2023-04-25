import urllib.request


class Robot_Parse:
    def __init__(self, url):
        self.url = url
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

    def read_robots(self):
        if self.inserted_robots:
            open_file = open(self.url)
            print(open_file.read())

if __name__ == "__main__":
    save = Robot_Parse("https://www.reddit.com/robots.txt")
    save.read_robots()
    