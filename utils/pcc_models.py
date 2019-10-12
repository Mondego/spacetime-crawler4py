from rtypes import pcc_set, dimension, primarykey


@pcc_set
class Register(object):
    crawler_id = primarykey(str)
    load_balancer = dimension(tuple)
    fresh = dimension(bool)
    invalid = dimension(bool)

    def __init__(self, crawler_id, fresh):
        self.crawler_id = crawler_id
        self.load_balancer = tuple()
        self.fresh = fresh
        self.invalid = False
