import json
from datetime import datetime, timedelta
from typing import Any, List, Set, Optional
from ...domains.cache import ICache
from ...apps.resources.handlers.cache_resource import DynamodbCacheResourceHandler
from ...configs.conf import DYNAMODB_URL, TABLE_CACHE
from ...configs.exceptions import ServerException
import logging


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class DynamoDbCacheAdapter(ICache):
    def __init__(self, async_db_resource: DynamodbCacheResourceHandler):
        self.aio_db = async_db_resource


    def is_json_obj(self, val: Any) -> (bool):
        return (val[0] == "{" and val[-1] == "}") or \
            (val[0] == "[" and val[-1] == "]")

    async def get(self, key: str):
        res = None
        result = None
        try:
            db = await self.aio_db.access()
            table = await db.Table(TABLE_CACHE)
            res = await table.get_item(Key={"cache_key": key})
            if "Item" in res and "value" in res["Item"]:
                val = res["Item"]["value"]
                result = json.loads(val) if self.is_json_obj(val) else val

            return result

        except Exception as e:
            log.error(f"cache.get fail \
                key:%s, res:%s, result:%s, err:%s",
                      key, res, result, e.__str__())
            raise ServerException(msg="d2_server_error")


    async def set(self, key: str, val: Any, ex: int = None):
        res = None
        result = False
        try:
            val_type = type(val)
            if val_type == dict or val_type == list:
                val = json.dumps(val)

            db = await self.aio_db.access()
            table = await db.Table(TABLE_CACHE)
            item = {
                "cache_key": key,
                "value": val,
            }
            if ex:
                ttl = datetime.now() + timedelta(seconds=ex)
                ttl = int(ttl.timestamp())
                item.update({"ttl": ttl})

            res = await table.put_item(Item=item)
            result = True
            return result

        except Exception as e:
            log.error(f"cache.set fail \
                    key:%s, val:%s, ex:%s, res:%s, result:%s, err:%s",
                      key, val, ex, res, result, e.__str__())
            raise ServerException(msg="d2_server_error")

    async def delete(self, key: str):
        try:
            db = await self.aio_db.access()
            table = await db.Table(TABLE_CACHE)
            await table.delete_item(Key={'cache_key': key})

        except Exception as e:
            log.error(f"cache.set fail \
                    key:%s, err:%s",
                      key, e.__str__())
            raise ServerException(msg="d2_server_error")

    async def smembers(self, key: str) -> (Optional[Set[Any]]):
        values = await self.get(key)
        if values is None:
            return None
        
        if not isinstance(values, list):
            raise ServerException(msg="invalid set-members type")
        
        return set(values)

    async def sismember(self, key: str, value: Any) -> (bool):
        set_members = await self.smembers(key)
        if set_members is None:
            return False
        
        return value in set_members

    async def sadd(self, key: str, values: List[Any], ex: int = None) -> (int):
        if not isinstance(values, list):
            raise ServerException(msg="invalid input type, values should be list")

        set_values = set(values)

        update_count = 0
        set_members = await self.smembers(key)
        if set_members is None:
            await self.set(key, list(set_values), ex)

        else:
            new_set_members = set_members | set_values
            await self.set(key, list(new_set_members), ex)
            
        update_count = len(values)
        return update_count

    async def srem(self, key: str, value: Any, ex: int = None) -> (int):
        update_count = 0
        set_members = await self.smembers(key)
        if set_members is None:
            return update_count

        if value in set_members:
            set_members.remove(value)
            await self.set(key, list(set_members), ex)
            update_count = 1
        else:
            update_count = 0

        return update_count
