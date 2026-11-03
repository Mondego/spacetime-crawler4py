import os
from spacetime import Node
from utils.pcc_models import Register

def init(df, user_agent, fresh):
    print("DEBUG 1: Registration function started!", flush=True)

    reg = df.read_one(Register, user_agent)

    if reg and not reg.load_balancer:
        print("DEBUG: Removing incomplete registration...", flush=True)

        df.delete_one(Register, reg)
        df.commit()
        df.push_await()

        print("DEBUG: Old registration removed.", flush=True)
        reg = None
    print(f"DEBUG: Existing balancer = {reg.load_balancer if reg else None}", flush=True)
    print(f"DEBUG: Existing invalid = {reg.invalid if reg else None}", flush=True)
    print(f"DEBUG: Existing fresh = {reg.fresh if reg else None}", flush=True)
    print(f"DEBUG 2: Existing registration? {reg is not None}", flush=True)

    if not reg:
        print("DEBUG 3: Creating new registration...", flush=True)

        reg = Register(user_agent, fresh)
        df.add_one(Register, reg)
        df.commit()

        print("DEBUG 4: Pushing registration...", flush=True)
        df.push_await()

        print("DEBUG 5: Registration pushed!", flush=True)

    print("DEBUG 6: Waiting for load balancer...", flush=True)

    while not reg.load_balancer:

        print("DEBUG 7: Calling pull_await()...", flush=True)

        df.pull_await()

        print(
            f"DEBUG 8: Received update. "
            f"Balancer={reg.load_balancer}, Invalid={reg.invalid}",
            flush=True
        )

        if reg.invalid:
            raise RuntimeError("User agent string is not acceptable.")

        if reg.load_balancer:
            print("DEBUG 9: Load balancer assigned!", flush=True)

            df.delete_one(Register, reg)
            df.commit()
            df.push()

    return reg.load_balancer
# def init(df, user_agent, fresh):
#     reg = df.read_one(Register, user_agent)
#     if not reg:
#         reg = Register(user_agent, fresh)
#         df.add_one(Register, reg)
#         df.commit()
#         df.push_await()
#     while not reg.load_balancer:
#         df.pull_await()
#         if reg.invalid:
#             raise RuntimeError("User agent string is not acceptable.")
#         if reg.load_balancer:
#             df.delete_one(Register, reg)
#             df.commit()
#             df.push()
#     return reg.load_balancer
#
def get_cache_server(config, restart):
    init_node = Node(
        init, Types=[Register], dataframe=(config.host, config.port))
    return init_node.start(
        config.user_agent, restart or not os.path.exists(config.save_file))