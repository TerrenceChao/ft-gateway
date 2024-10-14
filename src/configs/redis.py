from redis import Redis
from .conf import REDIS_HOST, REDIS_PORT, REDIS_USER, REDIS_PASS
import logging


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


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
