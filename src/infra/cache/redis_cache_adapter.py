import os
import time
import json
import re
from typing import Any, Dict, List, Set, Optional
from redis import Redis
from ...domains.cache import ICache
from ...configs.exceptions import ServerException
import logging


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class RedisCacheAdapter(ICache):
    def __init__(self, redis: Redis):
        self.redis = redis

    async def get(self, key: str):
        val = None
        result = None
        try:
            val = await self.redis.get(key)
            if val == None:
                return result

            # log.info(val, "\n", val[0] == "{" and val[-1] =="}")
            result = json.loads(
                val) if val[0] == "{" and val[-1] == "}" else val
            return result

        except Exception as e:
            log.error(f"cache.get fail \
                    key:%s, val:%s, result:%s, err:%s",
                      key, val, result, e.__str__())
            raise ServerException(msg="r_server_error")

    async def set(self, key: str, val: Any, ex: int = None):

        try:
            if isinstance(val, Dict):
                log.debug(f'type:%s, val:%s' % (type(val), str(val)))
                val = json.dumps(val)
                log.debug(f'type:%s, val:%s' % (type(val), str(val)))

            if not ex:
                return await self.redis.set(key, val)
            else:
                return await self.redis.set(key, val, ex)

        except Exception as e:
            log.error(f"cache.set fail \
                    key:%s, val:%s, ex:%s, err:%s",
                      key, val, ex, e.__str__())
            raise ServerException(msg="r_server_error")

    async def delete(self, key: str):
        try:
            await self.redis.delete(key)
        except Exception as e:
            log.error(f"cache.delete fail \
                    key:%s, err:%s",
                      key, e.__str__())
            raise ServerException(msg="r_server_error") 

    async def smembers(self, key: str) -> Optional[Set[Any]]:
        # TODO: implement
        return set()

    async def sismember(self, key: str, value: Any) -> bool:
        # TODO: implement
        return False

    async def sadd(self, key: str, values: List[Any], ex: int = None) -> int:
        # TODO: implement
        return 0

    async def srem(self, key: str, value: Any, ex: int = None) -> int:
        # TODO: implement
        return 0
