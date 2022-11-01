import os
import time
import json
from typing import List, Dict, Any
from fastapi import APIRouter, \
    Request, Depends, \
    Cookie, Header, Path, Query, Body, Form, \
    File, status, \
    HTTPException
from pydantic import EmailStr
from ...exceptions.auth_except import ClientException, \
    UnauthorizedException, \
    NotFoundException, \
    DuplicateUserException, \
    ServerException
from ...db.nosql import auth_schemas
from ..res.response import res_success
from ...common.service_requests import get_service_requests
from ...common.region_hosts import get_auth_region_host, get_match_region_host
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


# default = 5 mins (300 secs)
SHORT_TERM_TTL = int(os.getenv("SHORT_TERM_TTL", "300"))
# default = 14 days (14 * 86400 secs)
LONG_TERM_TTL = int(os.getenv("LONG_TERM_TTL", "1209600"))



"""
    1. change account's email
        
    2. change password (while logged in)
        1. request with new pass & old pass
        
    3. forgot password
        1. send link(url + querystring) to email
        2. request with new pass 
        
"""
router = APIRouter(
    prefix="/auth",
    tags=["Auth V2"],
    responses={404: {"description": "Not found"}},
)


def get_auth_host(region: str = Header(...)):
    return get_auth_region_host(region=region)


def get_match_host(region: str = Header(...)):
    return get_match_region_host(region=region)


@router.post("/email/change")
def change_account_email():
    pass


@router.post("/password/change")
def change_password():
    pass




@router.post("/password/forgot")
def forgot_password():
    pass

@router.put("/password/reset")
def reset_password(token: str):
    pass