import os
import time
import json
import re
from typing import Any, Dict, Optional
from redis import Redis
from ...domains.cache import ICache
from ...configs.redis import redis
from ...configs.exceptions import ServerException
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


class RedisCacheAdapter(ICache):
    def __init__(self, redis: Redis):
        self.redis = redis
        self.__cls_name = self.__class__.__name__

    def get(self, key: str):
        val = None
        result = None
        try:
            val = self.redis.get(key)
            if val == None:
                return result

            # log.info(val, "\n", val[0] == "{" and val[-1] =="}")
            result = json.loads(
                val) if val[0] == "{" and val[-1] == "}" else val
            return result

        except Exception as e:
            log.error(f"cache {self.__cls_name}.get fail \
                    key:%s, val:%s, result:%s, err:%s",
                      key, val, result, e.__str__())
            raise ServerException(msg="r_server_error")

    def set(self, key: str, val: Any, ex: int = None):

        try:
            if isinstance(val, Dict):
                log.debug(f'type:%s, val:%s' % (type(val), str(val)))
                val = json.dumps(val)
                log.debug(f'type:%s, val:%s' % (type(val), str(val)))

            if not ex:
                return self.redis.set(key, val)
            else:
                return self.redis.set(key, val, ex)

        except Exception as e:
            log.error(f"cache {self.__cls_name}.set fail \
                    key:%s, val:%s, ex:%s, err:%s",
                      key, val, ex, e.__str__())
            raise ServerException(msg="r_server_error")


def get_cache():
    try:
        cache = RedisCacheAdapter(redis)
        yield cache
    except Exception as e:
        log.error(e.__str__())
        raise
    finally:
        pass
