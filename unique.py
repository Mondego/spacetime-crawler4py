class Unique:
    """
    Unique objects helps determine unique urls,
    ignoring the fragmented parts of the url, and
    counts the number of unique urls
    """
    def __init__(self):
        """
        Initializer takes in a url 
        """
        url_list = set() #contains all the unique urls
        url_counter = 0 #counts how many unique urls are crawled to

    def remove_fragment(self, url:str):
        """
        remove_fragment loops through a given url and
        will remove the fragment that is at the end of the
        url. This function will run O(N), as it goes through every
        character of the url.
        """
        no_fragment = True #
        new_url = "" #url to return as it will be unique
        for c in url: #loops through url O(N) time
            if no_fragment:
                if 35 == ord(c): #determines the # which is a sign of a fragment
                    no_fragment = False #makes it false to prevent adding fragment characters
                else:
                    new_url += c #increment every character before the fragment

        url_list.add(new_url) #adds the unique url to the set
        return new_url


if __name__ == "__main__":
    store = Unique()
    print(store.remove_fragment("asefdsfd#dasfsdfa"))