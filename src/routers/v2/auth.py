import requests
from fastapi import APIRouter, Depends, Header, Query
from fastapi.responses import RedirectResponse
from ..res.response import res_success
from ...apps.service_api_dapter import ServiceApiAdapter
from ...configs.region_hosts import get_auth_region_v2_host, get_match_region_host
from src.domains.user.services.sso_auth_service import FBAuthService, GoogleAuthService
from src.configs.dynamodb import dynamodb
from src.infra.cache.dynamodb_cache_adapter import DynamoDbCacheAdapter
from src.domains.user.value_objects.auth_vo import SSOLoginVO
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
    return get_auth_region_v2_host(region=region)

def get_auth_host(current_region: str = Header(...)):
    return get_auth_region_v2_host(region=current_region)

def get_match_host(current_region: str = Header(...)):
    return get_match_region_host(region=current_region)

fb_auth_service = FBAuthService(ServiceApiAdapter(requests), DynamoDbCacheAdapter(dynamodb))
google_auth_service = GoogleAuthService(ServiceApiAdapter(requests), DynamoDbCacheAdapter(dynamodb))

@router.get('/google/dialog')
def google_dialog(auth_host = Depends(get_auth_host_for_signup),
                  role: str = Query(...)
                  ):
    redirect_path = google_auth_service.dialog(auth_host, role)
    return RedirectResponse(redirect_path)


@router.get('/google/login')
def google_login(code: str = Query(...),
                state: str = Query(...)):
    sso_service_vo = SSOLoginVO(
        code=code,
        state=state,
        sso_type='google',
    )
    data = google_auth_service.login(sso_service_vo)
    return res_success(data=data)


@router.get('/fb/dialog')
def facebook_dialog(auth_host = Depends(get_auth_host_for_signup),
                    role: str = Query(...)):
    redirect_path = fb_auth_service.dialog(auth_host, role)
    return RedirectResponse(redirect_path)


@router.get('/fb/login')
def facebook_login(code: str = Query(...),
                    state: str = Query(...)):
    sso_login_vo = SSOLoginVO(
        code=code,
        state=state,
        sso_type='fb',
    )
    data = fb_auth_service.login(sso_login_vo)
    return res_success(data=data)

