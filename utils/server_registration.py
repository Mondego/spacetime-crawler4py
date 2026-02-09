import os
from spacetime import Node # Node is a small client that can connect to the course server (styx) and exchange messages
from utils.pcc_models import Register # crawler uses this Register data model to identify itself to the server 


"""
Ensure that the server can identify the crawler by USERAGENT, decide whether it is a
fresh crawl or a resume, and assign it to a cache endpoint 

"""
def init(df, user_agent, fresh): # fresh indicates whether this is a fresh crawl
    reg = df.read_one(Register, user_agent) # in the register table, find the object whose primary key (crawler_id) == user_agent
    if not reg:
        reg = Register(user_agent, fresh) # create a new registration record
        df.add_one(Register, reg) # add it to the dataframe
        df.commit()
        df.push_await() # send it to the server and wait till it is delivered
    while not reg.load_balancer: 
        df.pull_await() # waits for server to respond with an assignment 
        if reg.invalid: 
            raise RuntimeError("User agent string is not acceptable.")
        if reg.load_balancer:
            df.delete_one(Register, reg) # once the load_balancer is set, the file cleans up the registration record 
            df.commit()
            df.push()
    return reg.load_balancer 

def get_cache_server(config, restart):
    """
    Identifies the user, know whether it is a fresh crawl r not,
    and route the request through a course cache system
    """

    init_node = Node(
        init, Types=[Register], dataframe=(config.host, config.port)) # creates a Node that will run the init function, and connect to the server at the specified host and port
    return init_node.start(
        config.user_agent, restart or not os.path.exists(config.save_file)) # fresh crawl if you explicitly ask for a restart or you dont have a saved state in the frontier