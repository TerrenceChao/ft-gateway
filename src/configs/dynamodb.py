import json
from datetime import datetime, timedelta
from typing import Any
import boto3
from ..repositories.cache import Cache
from ..configs.conf import DYNAMODB_URL, TABLE_CACHE
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


dynamodb = boto3.resource("dynamodb")
