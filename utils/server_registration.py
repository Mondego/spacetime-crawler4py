from spacetime import Node
from utils.pcc_models import Register

def init(df, user_agent):
    reg = df.read_one(Register, user_agent)
    if not reg:
        reg = Register(user_agent)
        df.add_one(Register, reg)
        df.commit()
        df.push_await()
    while not reg.load_balancer:
        df.pull_await()
        if reg.load_balancer:
            df.delete_one(Register, reg)
            df.commit()
            df.push()
    return reg.load_balancer

def get_cache_server(config):
    init_node = Node(init, Types=[Register], dataframe=(config.host, config.port))
    return init_node.start(config.user_agent)