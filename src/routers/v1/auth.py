import json
from typing import List, Dict, Any
from unicodedata import name
from fastapi import APIRouter, \
  Request, Depends, \
  Cookie, Header, Path, Query, Body, Form, \
  File, UploadFile, status, \
  HTTPException
from ...db.nosql import schemas

router = APIRouter(
  prefix="/auth-nosql",
  tags=["auth"],
  responses={404: {"description": "Not found"}},
)



"""到註冊頁面時，取得的 public_key (auth)
1. 將 public_key 存放在 cache
2. 註冊時將透過此 public_key 將整個 payload 加密

request:
querystring => ts=1234567890123

process:
1. 透過 ts(timestamp) 從 cache 取得特定 public_key
2. 若 cache 沒有, 從 {auth_service} 取得 public_key, 將 public_key 緩存

Returns:
    str: pubkey
"""
@router.get("/welcome")
def get_public_key():
  return "pubkey"


"""signup
request:
1. 前端傳送 region 取得用戶註冊地
2. 註冊時將透過 pubkey 將整個 payload 加密，再傳送; TODO:這時不會送 pubkey.
    body: {
      email: abc@mail.com
      meta: encrypt({ "region", "role", pass }) 
    }  TODO: no public_key in body

process:
1.  is the email in cache?
    Y: email is registered or is registering. X)reject client
    N: step 2
2. ask {auth_service}, is the email registered?
    Y: cache email's metadata(email,region,role_id). X)reject client
    N: step 3
3. generate confirm_code, binding with email in "cahce"
    [cache]:
      'abc@mail.com': {
        email: abc@mail.com
        meta: encrypt({ "region", "role", pass })
        confirm_code: xxxxxx
      }
4. ask {auth_service} to send confirm_code by email
5. response client {msg:success} 

Returns:
    str: 'success'
"""
@router.post("/signup")
def signup(email: str = Body(...), meta: str = Body(...)):
  user = schemas.FTUser(
    email=email,
    meta=meta,
  )
  pass


"""signup/conform
request:
1. body: { email, confirm_code, pubkey }

process:
1. 透過 cache 從 email payload 中驗證 confirm_code
    Y: del confirm_code, TODO: send payload(as bellow) to {auth_service}
      body: {
        email: abc@mail.com
        meta: encrypt({ "region", "role", pass })
        pubkey: xxxxasdfasdfasdfasdf
      }
      TODO: 不等待 {auth_service} 回應，直接response client {msg:success} 
      TODO: 此時 cache 剩下:
        [cache]:
          'abc@mail.com': {empty} TTL(30 secs)
      TODO: Few secs later, client fetch token itself
          
    N: reject client
      TODO: 此時 cache 剩下:
        [cache]:
          'abc@mail.com': {
            email: abc@mail.com
            meta: encrypt({ "region", "role", pass })
            confirm_code: xxxxxx
          }

Returns:
    str: 'success'
"""
@router.post("/signup/conform")
def confirm_signup(email: str = Body(...), pubkey: str = Body(...), confirm_code: str = Body(...)):
  user = schemas.FTUser(
    email=email,
    pubkey=pubkey,
    confirm_code=confirm_code,
  )
  pass


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
            socketId: ??????(for region)
          }
        b) 回傳{region____role_id____token}
        c) {gateway} 透過 rold_id 找尋 match 中的資料，一併回傳前端
        TODO:{gateway}[cache]:
          'abc@mail.com': {
            region: xxx
            current_region: xxx
            role_id: 12345678
            token: JWT
            online: True
            socketId: ??????(for region)
          }
          
      N: 驗證失敗 {DB找不到資料}
        a) {auth_service} 去 S3 尋找 {email:region}, 
              i) 如果 region == current_region >>>>>>> A.{表示根本沒註冊成功!!} B.{有可能 API 打錯 auth_service}
                  回傳 {gateway}
                    res_body: {
                      msg: 'user not found' {log_level:嚴重問題...}
                    }

              ii) 如果 region != current_region, 回傳 {gateway} 去別地方找 {重複login流程}
                    res_body: {
                      email: 'abc@mail.com',
                      region: xxxx
                    }
        
      N: 驗證失敗 {DB有資料 但密碼錯誤}, reject client

"""
@router.post("/login")
def login(email: str = Body(...), meta: str = Body(...), pubkey: str = Body(...)):
  user = schemas.FTUser(
    email=email,
    meta=meta,
    pubkey=pubkey,
  )
  pass


@router.get("/logout")
def logout(email: str = Body(...), token: str = Body(...)):
  user = schemas.FTUser(
    email=email, 
    token=token,
  )
  pass