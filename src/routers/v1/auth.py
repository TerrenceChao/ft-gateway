import os
import time
import json
from typing import List, Dict, Any
from fastapi import APIRouter, \
    Request, Depends, \
    Cookie, Header, Path, Query, Body, Form, \
    File, UploadFile, status, \
    HTTPException
from pydantic import EmailStr
from ...db.nosql import auth_schemas
from ..res.response import res_success, res_err
from ...common.cache import get_cache
from ...common.service_requests import get_service_requests
import logging as log


region_auth_hosts = {
    # "default": os.getenv("REGION_HOST_AUTH", "http://localhost:8082/auth/api/v1/auth-nosql"),
    "jp": os.getenv("JP_REGION_HOST_AUTH", "http://localhost:8082/auth/api/v1/auth-nosql"),
    "ge": os.getenv("EU_REGION_HOST_AUTH", "http://localhost:8082/auth/api/v1/auth-nosql"),
    "us": os.getenv("US_REGION_HOST_AUTH", "http://localhost:8082/auth/api/v1/auth-nosql"),
}

region_match_hosts = {
    # "default": os.getenv("REGION_HOST_MATCH", "http://localhost:8083/match/api/v1/match-nosql"),
    "jp": os.getenv("JP_REGION_HOST_MATCH", "http://localhost:8083/match/api/v1/match-nosql"),
    "ge": os.getenv("EU_REGION_HOST_MATCH", "http://localhost:8083/match/api/v1/match-nosql"),
    "us": os.getenv("US_REGION_HOST_MATCH", "http://localhost:8083/match/api/v1/match-nosql"),
}


# default = 5 mins (300 secs)
SHORT_TERM_TTL = int(os.getenv("SHORT_TERM_TTL", "300"))
# default = 14 days (14 * 86400 secs)
LONG_TERM_TTL = int(os.getenv("LONG_TERM_TTL", "1209600"))


log.basicConfig(level=log.INFO)


def gen_confirm_code():
    code = int(time.time() ** 6 % 1000000)
    code = code if (code > 100000) else code + 100000
    print(f"confirm_code: {code}")
    return code


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


@router.get("/welcome")
def get_public_key(region: str = Header(...), timestamp: int = 0,
                   requests=Depends(get_service_requests),
                   cache=Depends(get_cache)
                   ):
    region = region.lower()
    auth_host = region_auth_hosts[region]

    slot = timestamp % 100
    pubkey, cache_err = cache.get(f"pubkey_{slot}")
    if not pubkey or cache_err:
        pubkey, err = requests.get(f"{auth_host}/security/pubkey", params={"ts": timestamp})
        if err:
            return res_err(msg="cannot get public_key")
        else:
            cache.set(f"pubkey_{slot}", pubkey)

    return res_success(data=pubkey)


@router.post("/signup")
def signup(region: str = Header(...), email: EmailStr = Body(...), meta: str = Body(...),
           requests=Depends(get_service_requests),
           cache=Depends(get_cache)
           ):
    data, cache_err = cache.get(email)
    if data or cache_err:
        return res_err(msg="registered or registering")

    print("\n\n\ndata?\n", data)
    region = region.lower()
    auth_host = region_auth_hosts[region]
    confirm_code = gen_confirm_code()
    res, msg, err = requests.post2(f"{auth_host}/sendcode/email", json={
        "email": email,
        "confirm_code": confirm_code,
        "sendby": "no_exist",  # email 不存在時寄送
    })

    if msg == "email_sent":
        email_playload = {
            "email": email,
            "confirm_code": confirm_code,
            "meta": meta,
        }
        cache.set(email, email_playload, ex=SHORT_TERM_TTL)
        return res_success()

    elif err:
        return res_err(msg=err)

    else:
        cache.set(email, { "region": region }, SHORT_TERM_TTL)
        return res_err(msg="email registered")


@router.post("/signup/conform")
def confirm_signup(region: str = Header(...), email: EmailStr = Body(...), pubkey: str = Body(...), confirm_code: str = Body(...),
                   requests=Depends(get_service_requests),
                   cache=Depends(get_cache)
                   ):
    region = region.lower()
    auth_host = region_auth_hosts[region]
    user, cache_err = cache.get(email)
    print("\n\n\n\n\n~~~user\n", user, type(user))

    if not user or cache_err:
        return res_err(msg="no signup data")

    if user == {}:
        return res_err(msg="registering")

    if confirm_code != str(user["confirm_code"]):
        return res_err(msg="wrong confirm_code")

    # "registering": empty data, but TTL=30sec
    cache.set(email, {}, ex=30)
    payload = {
        "email": email,
        "meta": user["meta"],
        "pubkey": pubkey,
    }

    res, err = requests.post(f"{auth_host}/signup", json=payload)
    if err:
        return res_err(msg=err)

    updated, cache_err = cache.set(email, res, ex=LONG_TERM_TTL)
    if not updated or cache_err:
        return res_err(msg="cannot cache user data")
    else:    
        return res_success(data=res)


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
@router.post("/login")
def login(
    current_region: str = Header(...),
    email: EmailStr = Body(...),
    meta: str = Body(...),
    pubkey: str = Body(...),
    requests=Depends(get_service_requests),
    cache=Depends(get_cache)
):
    current_region = current_region.lower()
    auth_host = region_auth_hosts[current_region]
    match_host = region_match_hosts[current_region]
    payload = {
        "email": email,
        "meta": meta,
        "pubkey": pubkey,
        "client_region": current_region,
    }

    auth_res, msg, err = requests.post2(f"{auth_host}/login", json=payload)

    # found in DB
    if msg == "error_password":
        return res_err(msg="error_password")

    # not found in DB and S3
    if msg == "not_registered":
        return res_err(msg="user not found")  # 沒註冊過

    # found in S3, and region == "current_region"(在 meta, 解密後才會知道)(S3記錄:註冊在該auth_service卻找不到)
    if msg == "register_fail":
        return res_err(msg="register fail")  # {log_level:嚴重問題}

    # found in S3, and region != "current_region"(在 meta, 解密後才會知道)(找錯地方)
    # S3 有記錄但該地區的 auth-service 沒記錄，auth 從 S3 找 region 後回傳
    if msg == "wrong_region":
        print("\n\nhas record in S3, but no record in DB of the region")
        print("no token in the region, request for another region")
        region = auth_res["region"]  # 換其他 region 再請求一次
        auth_host = region_auth_hosts[region]
        match_host = region_match_hosts[region]
        auth_res, err = requests.post(f"{auth_host}/login", json=payload)
        if err:
            return res_err(msg=err)
        
    if err:
        return res_err(msg=err)


    # 驗證合法, save into cache
    auth_res.update({
        "current_region": current_region,
        "socketid": "xxx",  # TODO: socketid???
        "online": True,
    })
    updated, cache_err = cache.set(email, auth_res, ex=LONG_TERM_TTL)
    if not updated or cache_err:
        return res_err(msg="set cache fail")

    # 驗證合法 >> 取得 match service 資料
    role, role_id = auth_res["role"], auth_res["role_id"]
    match_res, err = requests.get(f"{match_host}/{role}/{role_id}/matchdata")

    return res_success(data={
        "auth": auth_res,
        "match": match_res if not err else None,
    })


@router.get("/logout")
def logout(email: EmailStr, token: str = Header(...),
           requests=Depends(get_service_requests),
           cache=Depends(get_cache)
           ):
    user, cache_err = cache.get(email)
    if not user or not "token" in user or cache_err:
        return res_err(msg="logged out")

    if user["token"] != token:
        return res_err(msg="access denied")

    # TODO: 是保留部分資訊，還是需要完全刪除 cache?
    for key in ["token", "socketid", "role_id"]:
        if key in user:
            del user[key]

    user["online"] = False
    # "LONG_TERM_TTL" for redirct notification
    updated, cache_err = cache.set(email, user, ex=LONG_TERM_TTL)
    if not updated or cache_err:
        return res_err(msg="set cache fail")
    
    return res_success()
