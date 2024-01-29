import os
import time
import json
from datetime import datetime, timedelta
from typing import Any, List, Set, Optional
from ...domains.cache import ICache
from ...configs.dynamodb import dynamodb
from ...configs.conf import DYNAMODB_URL, TABLE_CACHE
from ...configs.exceptions import ServerException
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


class DynamoDbCacheAdapter(ICache):
    def __init__(self, dynamodb: Any):
        self.db = dynamodb
        self.__cls_name = self.__class__.__name__
        
    def is_json_obj(self, val: Any) -> (bool):
        return (val[0] == "{" and val[-1] == "}") or \
            (val[0] == "[" and val[-1] == "]")

    def get(self, key: str):
        res = None
        result = None
        try:
            table = self.db.Table(TABLE_CACHE)
            res = table.get_item(Key={"cache_key": key})
            if "Item" in res and "value" in res["Item"]:
                val = res["Item"]["value"]
                result = json.loads(val) if self.is_json_obj(val) else val

            return result

        except Exception as e:
            log.error(f"cache {self.__cls_name}.get fail \
                key:%s, res:%s, result:%s, err:%s",
                      key, res, result, e.__str__())
            raise ServerException(msg="d2_server_error")


    def set(self, key: str, val: Any, ex: int = None):
        res = None
        result = False
        try:
            val_type = type(val)
            if val_type == dict or val_type == list:
                val = json.dumps(val)

            table = self.db.Table(TABLE_CACHE)
            item = {
                "cache_key": key,
                "value": val,
            }
            if ex:
                ttl = datetime.now() + timedelta(seconds=ex)
                ttl = int(ttl.timestamp())
                item.update({"ttl": ttl})

            res = table.put_item(Item=item)
            result = True
            return result

        except Exception as e:
            log.error(f"cache {self.__cls_name}.set fail \
                    key:%s, val:%s, ex:%s, res:%s, result:%s, err:%s",
                      key, val, ex, res, result, e.__str__())
            raise ServerException(msg="d2_server_error")

    def delete(self, key: str):
        try:
            table = self.db.Table(TABLE_CACHE)
            table.delete_item(Key={'cache_key': key})
        except Exception as e:
            log.error(f"cache {self.__cls_name}.set fail \
                    key:%s, err:%s",
                      key, e.__str__())
            raise ServerException(msg="d2_server_error")

    def smembers(self, key: str) -> (Optional[Set[Any]]):
        values = self.get(key)
        if values is None:
            return None
        
        if not isinstance(values, list):
            raise ServerException(msg="invalid set-members type")
        
        return set(values)

    def sismember(self, key: str, value: Any) -> (bool):
        set_members = self.smembers(key)
        if set_members is None:
            return False
        
        return value in set_members

    def sadd(self, key: str, values: List[Any], ex: int = None) -> (int):
        if not isinstance(values, list):
            raise ServerException(msg="invalid input type, values should be list")

        set_values = set(values)

        update_count = 0
        set_members = self.smembers(key)
        if set_members is None:
            self.set(key, list(set_values), ex)

        else:
            new_set_members = set_members | set_values
            self.set(key, list(new_set_members), ex)
            
        update_count = len(values)
        return update_count

    def srem(self, key: str, value: Any) -> (int):
        update_count = 0
        set_members = self.smembers(key)
        if set_members is None:
            return update_count

        if value in set_members:
            set_members.remove(value)
            self.set(key, list(set_members))
            update_count = 1
        else:
            update_count = 0

        return update_count




def get_cache():
    try:
        cache = DynamoDbCacheAdapter(dynamodb)
        yield cache
    except Exception as e:
        log.error(e.__str__())
        raise
    finally:
        pass
