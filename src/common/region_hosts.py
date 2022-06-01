import os
import logging
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from ..routers.res.response import res_err


log = logging.getLogger()
log.setLevel(logging.ERROR)


auth_region_hosts = {
    # "default": os.getenv("REGION_HOST_AUTH", "http://localhost:8082/auth/api/v1/auth-nosql"),
    "jp": os.getenv("JP_REGION_HOST_AUTH", "http://localhost:8082/auth/api/v1/auth-nosql"),
    "ge": os.getenv("GE_REGION_HOST_AUTH", "http://localhost:8082/auth/api/v1/auth-nosql"),
    "us": os.getenv("US_REGION_HOST_AUTH", "http://localhost:8082/auth/api/v1/auth-nosql"),
}

match_region_hosts = {
    # "default": os.getenv("REGION_HOST_MATCH", "http://localhost:8083/match/api/v1/match-nosql"),
    "jp": os.getenv("JP_REGION_HOST_MATCH", "http://localhost:8083/match/api/v1/match-nosql"),
    "ge": os.getenv("GE_REGION_HOST_MATCH", "http://localhost:8083/match/api/v1/match-nosql"),
    "us": os.getenv("US_REGION_HOST_MATCH", "http://localhost:8083/match/api/v1/match-nosql"),
}


class RegionException(HTTPException):
    def __init__(self, region: str):
        self.msg = f"invalid region: {region}"
        self.status_code = status.HTTP_400_BAD_REQUEST


def get_auth_region_host(region: str):
    try:
        region = region.lower()
        return auth_region_hosts[region]
    except Exception as e:
        log.error(e.__str__())
        raise RegionException(region=region)
    finally:
        pass

def get_match_region_host(region: str):
    try:
        region = region.lower()
        return match_region_hosts[region]
    except Exception as e:
        log.error(e.__str__())
        raise RegionException(region=region)
    finally:
        pass


