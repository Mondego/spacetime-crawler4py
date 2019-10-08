from rtypes import pcc_set, dimension, primarykey

@pcc_set
class Register(object):
    crawler_id = primarykey(str)
    load_balancer = dimension(tuple)

    def __init__(self, crawler_id):
        self.crawler_id = crawler_id
        self.load_balancer = tuple()
