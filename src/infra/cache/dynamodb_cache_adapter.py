import os
import time
import json
from datetime import datetime, timedelta
from typing import Any, Optional
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

    def get(self, key: str):
        res = None
        result = None
        try:
            table = self.db.Table(TABLE_CACHE)
            res = table.get_item(Key={"cache_key": key})
            if "Item" in res and "value" in res["Item"]:
                val = res["Item"]["value"]
                result = json.loads(
                    val) if val[0] == "{" and val[-1] == "}" else val

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
            if type(val) == dict:
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


def get_cache():
    try:
        cache = DynamoDbCacheAdapter(dynamodb)
        yield cache
    except Exception as e:
        log.error(e.__str__())
        raise
    finally:
        pass
