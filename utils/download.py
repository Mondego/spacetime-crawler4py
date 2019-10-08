import requests
import cbor
import time

from utils.response import Response

def download(url, cache_server, config, logger):
    host, port = cache_server
    stime = time.perf_counter()
    resp = requests.get(f"http://{host}:{port}/?q={url}&u={config.user_agent}")
    etime = time.perf_counter()
    if etime - stime > 0.5:
        logger.error(f"Timeout {config.user_agent} {etime - stime}")
    if resp:
        return Response(cbor.loads(resp.content))
    logger.error(f"Spacetime Response error {resp} with url {url}.")
