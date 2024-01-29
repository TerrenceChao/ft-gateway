# from .redis import redis
# from ..infra.cache.redis_cache_adapter import RedisCacheAdapter
# # gw_cache = RedisCacheAdapter(redis)

from .dynamodb import dynamodb
from ..infra.cache.dynamodb_cache_adapter import DynamoDbCacheAdapter
gw_cache = DynamoDbCacheAdapter(dynamodb)