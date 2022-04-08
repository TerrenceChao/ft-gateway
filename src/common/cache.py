import os
import time
import json
import re
from typing import Any
from redis import Redis
import logging as log


cache_host = os.getenv("CACHE_HOST", "localhost")
cache_port = int(os.getenv("CACHE_PORT", "6379"))
cache_user = os.getenv("CACHE_USERNAME", "myuser")
cache_pass = os.getenv("CACHE_PASSWORD", "qwer1234")


redis = Redis(
    host=cache_host,
    port=cache_port,
    decode_responses=True,
    # ssl=True,
    # username=cache_user,
    # password=cache_pass,
)

log.basicConfig(level=log.INFO)
if redis.ping():
    log.info("Connected to Redis")


class Cache:
    def __init__(self, redis: Redis):
        self.redis = redis
        
    def get(self, key: str):
        err_msg: str = None
        result = None

        try:
            val = self.redis.get(key)
            if val == None:
                return result, err_msg
            
            # print(val, "\n", val[0] == "{" and val[-1] =="}")
            result = json.loads(val) if val[0] == "{" and val[-1] =="}" else val

        except Exception as e:
            err_msg = e.__str__()
            log.error(err_msg)

        return result, err_msg

    def set(self, key: str, val: Any, ex: int = None):
        err_msg: str = None
        result = False

        try:
            if type(val) == dict:
                print(val)
                print(type(val))
                val = json.dumps(val)
                print(val)
                print(type(val))

            if not ex:
                self.redis.set(key, val)
            else:
                self.redis.set(key, val, ex)
                
            result = True

        except Exception as e:
            err_msg = e.__str__()
            log.error(err_msg)

        return result, err_msg


def get_cache():
    try:
        cache = Cache(redis)
        yield cache
    except Exception as e:
        log.error(e.__str__())
        raise
    finally:
        pass
