import requests
from fastapi import APIRouter, Depends, Header, Query
from ..res.response import res_success
from ...apps.service_api_dapter import ServiceApiAdapter
from ...configs.region_hosts import get_auth_region_host, get_match_region_host
from src.domains.user.services.sso_auth_service import FBAuthService, GoogleAuthService
from src.configs.dynamodb import dynamodb
from src.infra.cache.dynamodb_cache_adapter import DynamoDbCacheAdapter
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

fb_auth_service = FBAuthService(ServiceApiAdapter(requests), DynamoDbCacheAdapter(dynamodb))
google_auth_service = GoogleAuthService(ServiceApiAdapter(requests), DynamoDbCacheAdapter(dynamodb))

@router.post('/google/dialog', status_code=201)
def google_dialog(auth_host = Depends(get_auth_host_for_signup),
                  role: str = Query(...)
                  ):
    return google_auth_service.dialog(auth_host, role)


@router.post('/google/login', status_code=201)
def google_login(auth_host=Depends(get_auth_host),
                match_host=Depends(get_match_host),
                code: str = Query(...),
                state: str = Query(...)):
    data = google_auth_service.login(auth_host, match_host, code, state)
    return res_success(data=data)


@router.post('/fb/dialog', status_code=201)
def facebook_dialog(auth_host = Depends(get_auth_host_for_signup),
                    role: str = Query(...)):
    return fb_auth_service.dialog(auth_host, role)


@router.post('/fb/login', status_code=201)
def facebook_login(auth_host=Depends(get_auth_host),
                match_host=Depends(get_match_host),
                code: str = Query(...),
                state: str = Query(...)):
    data = fb_auth_service.login(auth_host, match_host, code, state)
    return res_success(data=data)

