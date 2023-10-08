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
from ...configs.exceptions import ClientException, \
    UnauthorizedException, \
    NotFoundException, \
    DuplicateUserException, \
    ServerException
from ...infra.db.nosql import auth_schemas
from ..res.response import res_success
from ...apps.service_api_dapter import ServiceApiAdapter
from ...configs.region_hosts import get_auth_region_host, get_match_region_host
from ...configs.conf import SHORT_TERM_TTL, LONG_TERM_TTL
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


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


@router.post("/email/change", status_code=201)
def change_account_email():
    pass


@router.post("/password/change", status_code=201)
def change_password():
    pass


@router.post("/password/forgot", status_code=201)
def forgot_password():
    pass


@router.put("/password/reset")
def reset_password(token: str):
    pass
