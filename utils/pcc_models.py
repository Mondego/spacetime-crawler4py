from rtypes import pcc_set, dimension, primarykey


@pcc_set
class Register(object):
    crawler_id = primarykey(str)
    load_balancer = dimension(tuple) # initially empty; filled in when the server assigns a cache endpoint 
    fresh = dimension(bool)
    invalid = dimension(bool)

    def __init__(self, crawler_id, fresh):
        self.crawler_id = crawler_id
        self.load_balancer = tuple()
        self.fresh = fresh
        self.invalid = False
