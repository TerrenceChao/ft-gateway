import os
from fastapi import HTTPException, status
import logging


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


auth_region_hosts = {
    # "default": os.getenv("REGION_HOST_AUTH", "http://localhost:8082/auth/api/v1/auth-nosql"),
    "jp": os.getenv("JP_REGION_HOST_AUTH", "http://localhost:8082/auth/api/v1/auth-nosql"),
    "ge": os.getenv("GE_REGION_HOST_AUTH", "http://localhost:8082/auth/api/v1/auth-nosql"),
    "us": os.getenv("US_REGION_HOST_AUTH", "http://localhost:8082/auth/api/v1/auth-nosql"),
}

auth_region_v2_hosts = {
    # "default": os.getenv("REGION_HOST_AUTH", "http://localhost:8082/auth/api/v2/auth-nosql"),
    "jp": os.getenv("JP_REGION_HOST_AUTH", "http://localhost:8082/auth/api/v2/auth-nosql"),
    "ge": os.getenv("GE_REGION_HOST_AUTH", "http://localhost:8082/auth/api/v2/auth-nosql"),
    "us": os.getenv("US_REGION_HOST_AUTH", "http://localhost:8082/auth/api/v2/auth-nosql"),
}

match_region_hosts = {
    # "default": os.getenv("REGION_HOST_MATCH", "http://localhost:8083/match/api/v1/match-nosql"),
    "jp": os.getenv("JP_REGION_HOST_MATCH", "http://localhost:8083/match/api/v1/match-nosql"),
    "ge": os.getenv("GE_REGION_HOST_MATCH", "http://localhost:8083/match/api/v1/match-nosql"),
    "us": os.getenv("US_REGION_HOST_MATCH", "http://localhost:8083/match/api/v1/match-nosql"),
}

search_region_hosts = {
    # "default": os.getenv("REGION_HOST_SEARCH", "http://localhost:8084/search/api/v1"),
    "jp": os.getenv("JP_REGION_HOST_SEARCH", "http://localhost:8084/search/api/v1"),
    "ge": os.getenv("GE_REGION_HOST_SEARCH", "http://localhost:8084/search/api/v1"),
    "us": os.getenv("US_REGION_HOST_SEARCH", "http://localhost:8084/search/api/v1"),
}

media_region_hosts = {
    "default": os.getenv("REGION_HOST_MEDIA", "http://localhost:8085/media/api/v1"),
    "jp": os.getenv("JP_REGION_HOST_MEDIA", "http://localhost:8085/media/api/v1"),
    "ge": os.getenv("GE_REGION_HOST_MEDIA", "http://localhost:8085/media/api/v1"),
    "us": os.getenv("US_REGION_HOST_MEDIA", "http://localhost:8085/media/api/v1"),
}

payment_region_hosts = {
    "default": os.getenv("REGION_HOST_PAYMENT", "http://localhost:8086/payment/api/v1"),
    "jp": os.getenv("JP_REGION_HOST_PAYMENT", "http://localhost:8086/payment/api/v1"),
    "ge": os.getenv("GE_REGION_HOST_PAYMENT", "http://localhost:8086/payment/api/v1"),
    "us": os.getenv("US_REGION_HOST_PAYMENT", "http://localhost:8086/payment/api/v1"),
}


class RegionException(HTTPException):
    def __init__(self, region: str):
        self.msg = f"invalid region: {region}"
        self.status_code = status.HTTP_400_BAD_REQUEST


def get_auth_region_host(region: str):
    try:
        return auth_region_hosts[region]
    except Exception as e:
        log.error(f"get_auth_region_host fail, region:%s err:%s", region, e.__str__())
        raise RegionException(region=region)

def get_auth_region_v2_host(region: str):
    try:
        return auth_region_v2_hosts[region]
    except Exception as e:
        log.error(f"get_auth_region_v2_host fail, region:%s err:%s", region, e.__str__())
        raise RegionException(region=region)

def get_match_region_host(region: str):
    try:
        return match_region_hosts[region]
    except Exception as e:
        log.error(f"get_match_region_host fail, region:%s err:%s", region, e.__str__())
        raise RegionException(region=region)

def get_search_region_host(region: str):
    try:
        return search_region_hosts[region]
    except Exception as e:
        log.error(f"get_search_region_host fail, region:%s err:%s", region, e.__str__())
        raise RegionException(region=region)

def get_media_region_host(region: str):
    try:
        default_host = media_region_hosts['default']
        return media_region_hosts.get(region, default_host)
    except Exception as e:
        log.error(f"get_media_region_host fail, region:%s err:%s", region, e.__str__())
        raise RegionException(region=region)
    
def get_payment_region_host(region: str):
    try:
        default_host = payment_region_hosts['default']
        return payment_region_hosts.get(region, default_host)
    except Exception as e:
        log.error(f"get_payment_region_host fail, region:%s err:%s", region, e.__str__())
        raise RegionException(region=region)

