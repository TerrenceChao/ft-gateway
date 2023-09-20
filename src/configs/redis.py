from typing import Any
from redis import Redis
from ..repositories.cache import Cache
from .conf import REDIS_HOST, REDIS_PORT, REDIS_USER, REDIS_PASS
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


redis = Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True,
    # ssl=True,
    username=REDIS_USER,
    password=REDIS_PASS,
)

if redis.ping():
    log.info("Connected to Redis")
