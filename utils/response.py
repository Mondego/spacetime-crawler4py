import pickle

class Response(object):
    """
    Wrapper object around what the cache server sent back
    Cache server sends a dictionary that contains : the URL, the HTTP status 
    and an optional error message
    """
    def __init__(self, resp_dict):
        self.url = resp_dict["url"]
        self.status = resp_dict["status"]
        self.error = resp_dict["error"] if "error" in resp_dict else None
        try:
            self.raw_response = (
                pickle.loads(resp_dict["response"]) # response is in bytes, and is turned back into Python object 
                if "response" in resp_dict else
                None) # raw_response is a python object 
        except TypeError:
            self.raw_response = None
