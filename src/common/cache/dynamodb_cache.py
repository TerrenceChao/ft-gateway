import os
import time
import json
from datetime import datetime, timedelta
from typing import Any
import boto3
from .cache import Cache
from ...configs.conf import DYNAMODB_URL, TABLE_CACHE
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


dynamodb = boto3.resource("dynamodb")


class DynamoDbCache(Cache):
    def __init__(self, dynamodb: Any):
        self.db = dynamodb

    def get(self, key: str):
        err_msg: str = None
        result = None

        try:
            table = self.db.Table(TABLE_CACHE)
            res = table.get_item(Key={"cache_key": key})
            if "Item" in res:
                val = res["Item"]["value"]
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

            table.put_item(Item=item)
            result = True

        except Exception as e:
            err_msg = e.__str__()
            log.error(err_msg)

        return result, err_msg
    
    
def get_cache():
    try:
        cache = DynamoDbCache(dynamodb)
        yield cache
    except Exception as e:
        log.error(e.__str__())
        raise
    finally:
        pass
