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


'''
    1. change account's email
        
    2. change password (while logged in)
        1. request with new pass & old pass
        
    3. forgot password
        1. send link(url + querystring) to email
        2. request with new pass 
        
'''
router = APIRouter(
    prefix='/auth',
    tags=['Auth V2'],
    responses={404: {'description': 'Not found'}},
)


def get_auth_host_for_signup(region: str = Header(...)):
    return get_auth_region_host(region=region)

def get_auth_host(current_region: str = Header(...)):
    return get_auth_region_host(region=current_region)

def get_match_host(current_region: str = Header(...)):
    return get_match_region_host(region=current_region)


@router.post('/google/signup', status_code=201)
def google_signup(auth_host = Depends(get_auth_host_for_signup)):
    pass


@router.post('/google/login', status_code=201)
def google_login(auth_host = Depends(get_auth_host)):
    pass


@router.post('/facebook/signup', status_code=201)
def facebook_signup(auth_host = Depends(get_auth_host_for_signup)):
    pass


@router.post('/facebook/login', status_code=201)
def facebook_login(auth_host = Depends(get_auth_host)):
    pass
