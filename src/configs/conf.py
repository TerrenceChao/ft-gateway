import os
from functools import lru_cache
from pydantic import BaseSettings
from typing import Set
from .constants import Apply

# cache
# dynamodb
LOCAL_DB = "http://localhost:8000"
DYNAMODB_URL = os.getenv("DYNAMODB_URL", LOCAL_DB)
TABLE_CACHE = os.getenv("TABLE_CACHE", "cache")
# redis
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_USER = os.getenv("REDIS_USERNAME", None)
REDIS_PASS = os.getenv("REDIS_PASSWORD", None)


JWT_SECRET = os.getenv("JWT_SECRET", None)
JWT_ALGORITHM = os.getenv("ALGORITHM", "HS256")
TOKEN_EXPIRE_TIME = int(os.getenv("TOKEN_EXPIRE_TIME", 60 * 60 * 24 * 7))

# default = 20 secs
REQUEST_INTERVAL_TTL = int(os.getenv("REQUEST_INTERVAL_TTL", "20"))
# default = 5 mins (300 secs)
SHORT_TERM_TTL = int(os.getenv("SHORT_TERM_TTL", "300"))
# default = 14 days (14 * 86400 secs)
LONG_TERM_TTL = int(os.getenv("LONG_TERM_TTL", "1209600"))

MAX_TAGS = int(os.getenv("MAX_TAGS", "7"))

FT_BUCKET = os.getenv("FT_BUCKET", "foreign-teacher")
MULTIPART_THRESHOLD = int(os.getenv("MULTIPART_THRESHOLD", 512))
MAX_CONCURRENCY = int(os.getenv("MAX_CONCURRENCY", 10))
MULTIPART_CHUNKSIZE = int(os.getenv("MULTIPART_CHUNKSIZE", 128))

# aws config
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY", None)
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", None)

# company apply status (my_status, status)
MY_STATUS_OF_COMPANY_APPLY = os.getenv("MY_STATUS_OF_COMPANY_APPLY", "confirm")
STATUS_OF_COMPANY_APPLY = os.getenv("STATUS_OF_COMPANY_APPLY", None)
MY_STATUS_OF_COMPANY_REACTION = os.getenv("MY_STATUS_OF_COMPANY_REACTION", "confirm,pending")
STATUS_OF_COMPANY_REACTION = os.getenv("STATUS_OF_COMPANY_REACTION", "confirm")


# teacher apply status (my_status, status)
MY_STATUS_OF_TEACHER_APPLY = os.getenv("MY_STATUS_OF_TEACHER_APPLY", "confirm")
STATUS_OF_TEACHER_APPLY = os.getenv("STATUS_OF_TEACHER_APPLY", None)
MY_STATUS_OF_TEACHER_REACTION = os.getenv("MY_STATUS_OF_TEACHER_REACTION", "confirm,pending")
STATUS_OF_TEACHER_REACTION = os.getenv("STATUS_OF_TEACHER_REACTION", "confirm")

def parse_list(statuses: str):
    if statuses is None or statuses.strip() == "":
        return []
    
    apply_enums: Set[Apply] = set([Apply(s.lower().strip()) for s in statuses.split(",") if s.strip() != ""])
    return list({ a.value for a in apply_enums })
    
MY_STATUS_OF_COMPANY_APPLY = parse_list(MY_STATUS_OF_COMPANY_APPLY)
STATUS_OF_COMPANY_APPLY = parse_list(STATUS_OF_COMPANY_APPLY)
MY_STATUS_OF_COMPANY_REACTION = parse_list(MY_STATUS_OF_COMPANY_REACTION)
STATUS_OF_COMPANY_REACTION = parse_list(STATUS_OF_COMPANY_REACTION)

MY_STATUS_OF_TEACHER_APPLY = parse_list(MY_STATUS_OF_TEACHER_APPLY)
STATUS_OF_TEACHER_APPLY = parse_list(STATUS_OF_TEACHER_APPLY)
MY_STATUS_OF_TEACHER_REACTION = parse_list(MY_STATUS_OF_TEACHER_REACTION)
STATUS_OF_TEACHER_REACTION = parse_list(STATUS_OF_TEACHER_REACTION)


# check README.md for more details
class Settings(BaseSettings):
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings():
    return Settings()
