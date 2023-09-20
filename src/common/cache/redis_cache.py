import os
import time
import json
import re
from typing import Any
from redis import Redis
from .cache import Cache
from ...configs.conf import REDIS_HOST, REDIS_PORT, REDIS_USER, REDIS_PASS
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


redis = Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True,
    # ssl=True,
    # username=REDIS_USER,
    # password=REDIS_PASS,
)

if redis.ping():
    log.info("Connected to Redis")


class RedisCache(Cache):
    def __init__(self, redis: Redis):
        self.redis = redis
        
    def get(self, key: str):
        err_msg: str = None
        result = None

        try:
            val = self.redis.get(key)
            if val == None:
                return result, err_msg
            
            # log.info(val, "\n", val[0] == "{" and val[-1] =="}")
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
                log.debug(f'type:%s, val:%s' % (type(val), str(val)))
                val = json.dumps(val)
                log.debug(f'type:%s, val:%s' % (type(val), str(val)))

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
        cache = RedisCache(redis)
        yield cache
    except Exception as e:
        log.error(e.__str__())
        raise
    finally:
        pass
