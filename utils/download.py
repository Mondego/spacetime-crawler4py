import requests
import cbor
import time
import json
from utils.response import Response

def download(url, config, logger=None):
    host, port = config.cache_server
    resp = requests.get(
        f"http://{host}:{port}/",
        params=[("q", f"{url}"), ("u", f"{config.user_agent}")])
    
    # resp = requests.get(url)
    try:
        if resp and resp.content:
            
            return Response(cbor.loads(resp.content))
            # resp_dict = {"url":url,"status":resp.status_code,"response":resp.content}
            # return Response(resp_dict)
            
    except (EOFError, ValueError) as e:
        print("Error:", e)
    logger.error(f"Spacetime Response error {resp} with url {url}.")
    return Response({
        "error": f"Spacetime Response error {resp} with url {url}.",
        "status": resp.status_code,
        "url": url})
