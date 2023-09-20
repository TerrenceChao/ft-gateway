import os
from functools import lru_cache
from pydantic import BaseSettings

# cache
## dynamodb
LOCAL_DB = "http://localhost:8000"
DYNAMODB_URL = os.getenv("DYNAMODB_URL", LOCAL_DB)
TABLE_CACHE = os.getenv("TABLE_CACHE", "cache")
## redis
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_USER = os.getenv("REDIS_USERNAME", None)
REDIS_PASS = os.getenv("REDIS_PASSWORD", None)


JWT_SECRET = os.getenv("TOKEN_EXPIRE_TIME", None)
TOKEN_EXPIRE_TIME = int(os.getenv("TOKEN_EXPIRE_TIME", 60 * 60 * 24 * 7))

# default = 5 mins (300 secs)
SHORT_TERM_TTL = int(os.getenv("SHORT_TERM_TTL", "300"))
# default = 14 days (14 * 86400 secs)
LONG_TERM_TTL = int(os.getenv("LONG_TERM_TTL", "1209600"))

FT_BUCKET = os.getenv("FT_BUCKET", "foreign-teacher")
MULTIPART_THRESHOLD = int(os.getenv("MULTIPART_THRESHOLD", 512))
MAX_CONCURRENCY = int(os.getenv("MAX_CONCURRENCY", 10))
MULTIPART_CHUNKSIZE = int(os.getenv("MULTIPART_CHUNKSIZE", 128))

# aws config
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY", None)
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", None)


class Settings(BaseSettings):
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings():
    return Settings()

