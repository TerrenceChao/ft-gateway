# from .redis import redis
# from ..infra.cache.redis_cache_adapter import RedisCacheAdapter
# # gw_cache = RedisCacheAdapter(redis)

from .dynamodb import async_db_resource
from ..infra.cache.dynamodb_cache_adapter import DynamoDbCacheAdapter

gw_cache = DynamoDbCacheAdapter(async_db_resource)
