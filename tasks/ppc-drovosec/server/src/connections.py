import logging
from datetime import timedelta

import redis

r = redis.Redis(host='localhost', port=6379, db=0)

MAX_CONNS = 75

key = "connections"

def get_connections() -> int:
    x = r.get(key)
    if x is None:
        return 0
    return int(x.decode())

def add_connection():
    logging.info("[CONN] added conn")
    r.incr(key)

def remove_connection():
    logging.info("[CONN] removed conn")
    r.decr(key)
    conns = get_connections()
    if conns < 0:
        reset_connections()

def reset_connections():
    logging.info("[CONN] reset conns")
    r.set(key, "0")



def check_in(ip: str):
    r.setex(ip, timedelta(seconds=15), "kek")

def is_rate_limited(ip) -> bool:
    have = r.get(ip)
    return have is not None


CONNECTIONS = set()