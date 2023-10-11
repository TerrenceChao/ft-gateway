import requests
from fastapi import APIRouter, \
    Request, Depends, \
    Cookie, Header, Path, Query, Body, Form, \
    File, UploadFile, status, \
    HTTPException
from pydantic import EmailStr
from ...domains.user.value_objects.auth_vo import SignupVO, SignupConfirmVO, LoginVO
from ..req.authorization import verify_token_by_logout
from ..res.response import res_success
from ...domains.user.services.auth_service import AuthService
from ...infra.cache.dynamodb_cache_adapter import DynamoDbCacheAdapter
from ...apps.service_api_dapter import ServiceApiAdapter
from ...configs.dynamodb import dynamodb
from ...configs.region_hosts import get_auth_region_host, get_match_region_host
import logging as log

log.basicConfig(filemode='w', level=log.INFO)

# using dynamodb as cache
_auth_service = AuthService(
    ServiceApiAdapter(requests), DynamoDbCacheAdapter(dynamodb))

"""
    1. get public key
    2. signup
    3. signup & confirm
    4. login
    5. logout
        
"""
router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
    responses={404: {"description": "Not found"}},
)


def get_auth_host(region: str = Header(...)):
    return get_auth_region_host(region=region)


def get_match_host(region: str = Header(...)):
    return get_match_region_host(region=region)


@router.get("/welcome")
def get_public_key(timestamp: int = 0,
                   auth_host=Depends(get_auth_host),
                   ):
    pubkey, msg = _auth_service.get_public_key(auth_host, timestamp)
    return res_success(data=pubkey, msg=msg)


# "meta": "{\"region\":\"jp\",\"role\":\"teacher\",\"pass\":\"secret\"}"
@router.post("/signup", status_code=201)
def signup(region: str = Header(...), body: SignupVO = Body(...),
           auth_host=Depends(get_auth_host),
           ):
    data, msg = _auth_service.signup(auth_host, body.email, body.meta, region)
    return res_success(data=data, msg=msg)


@router.post("/signup/confirm", status_code=201)
def confirm_signup(body: SignupConfirmVO = Body(...),
                   auth_host=Depends(get_auth_host),
                   ):
    data, msg = _auth_service.confirm_signup(auth_host, body)
    return res_success(data=data, msg=msg)


"""login
request:
  1. 前端傳送需加上 current_region (不一定等於 region)
  2. login時, 透過 pubkey 將 { current_region, "role", pass } 加密，再傳送
      body: {
        email: abc@mail.com
        meta: encrypt({ current_region, "role", pass })
        pubkey: xxxxasdfasdfasdfasdf
      }

TODO: 考慮 local/remote region 問題。
      
process:
  1. {gateway} ask {auth_service}, 驗證資訊
      body: {
        email: abc@mail.com
        meta: encrypt({ current_region, "role", pass })
        pubkey: xxxxasdfasdfasdfasdf
      }

  2. {auth_service} 從 DB 驗證資料：
      Y: 驗證合法
        a) {auth_service} 記錄 "current_region" {在自己區域}的 cahce 中
        TODO:{auth_service}[cache]:
          'abc@mail.com': {
            region: xxx
            current_region: xxx
            online: True
            socketid: ??????(for region)
          }
        b) 回傳{email____region____role____role_id____token}
        c) {gateway} 透過 rold_id 找尋 match 中的資料，一併回傳前端
        TODO:{gateway}[cache]:
          'abc@mail.com': {
            region: xxx
            current_region: xxx
            role_id: 12345678
            token: JWT
            online: True
            socketid: ??????(for region)
          }

      N: 驗證失敗 {DB有資料 但密碼錯誤}, reject client

      N: 驗證失敗 {DB找不到資料}
        a) {auth_service} 去 S3 尋找 {email:region}, 
              i) 連 S3 都沒有 >> 沒註冊過
              
              ii) 如果 region == current_region >>>>>>> A.{表示根本沒註冊成功!!} B.{有可能 API 打錯 auth_service}
                  回傳 {gateway}
                    res_body: {
                      msg: 'user not found' {log_level:嚴重問題...}
                    }

              iii) 如果 region != current_region, 回傳 {gateway} 去別地方找 {重複login流程}
                    res_body: {
                      email: 'abc@mail.com',
                      region: xxxx
                    }
"""


"""_summary_

目前機制：同一時間只允許同一使用者登入，不允許同一使用者在多個裝置/入口登入
TODO: 登入時，其他裝置需要登出。

未來機制：同一時間允許同一使用者在多個裝置/入口登入
TODO: current_region 和其他 metadata 需改為多份
"""


@router.post("/login", status_code=201)
def login(current_region: str = Header(...),
          body: LoginVO = Body(...),
          auth_host=Depends(get_auth_host),
          match_host=Depends(get_match_host),
          ):
    data, msg = _auth_service.login(
        auth_host, match_host, current_region, body)
    return res_success(data=data, msg=msg)


@router.post("/logout", status_code=201)
def logout(token: str = Header(...),
           role_id: int = Body(..., embed=True),
           verify=Depends(verify_token_by_logout)
           ):
    data, msg = _auth_service.logout(role_id, token)
    return res_success(data=data, msg=msg)


@router.put('/password/update', status_code=200)
def update_password(token: str = Header(...),
           email: EmailStr = Body(..., embed=True),
           ):
    # TODO: update password
    pass

@router.put('/password/reset', status_code=200)
def reset_password(token: str = Header(...),
           email: EmailStr = Body(..., embed=True),
           ):
    # TODO: reset password
    pass
