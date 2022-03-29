import os
import time
import json
# from pyparsing import rest_of_line
import requests
from redis import Redis
from typing import List, Dict, Any
from unicodedata import name
from fastapi import APIRouter, \
    Request, Depends, \
    Cookie, Header, Path, Query, Body, Form, \
    File, UploadFile, status, \
    HTTPException
from pydantic import EmailStr
from ...db.nosql import auth_schemas
from ..res.response import res_success, res_err
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


CACHE_HOST = os.getenv("CACHE_HOST", "localhost")
CACHE_PORT = int(os.getenv("CACHE_PORT", "6379"))
CACHE_USERNAME = os.getenv("CACHE_USERNAME", "myuser")
CACHE_PASSWORD = os.getenv("CACHE_PASSWORD", "qwer1234")
# default = 5 mins (300 secs)
CONFIRM_CODE_TTL = int(os.getenv("CONFIRM_CODE_TTL", "300"))
# default = 14 days (86400 * 14 secs)
LOGIN_TTL = int(os.getenv("LOGIN_TTL", "1209600"))


cache = Redis(
    host=CACHE_HOST,
    port=CACHE_PORT,
    decode_responses=True,
    # ssl=True,
    # username=CACHE_USERNAME,
    # password=CACHE_PASSWORD,
)

log.basicConfig(level=log.INFO)
if cache.ping():
    log.info("Connected to Redis")


def gen_confirm_code():
    code = int(time.time() ** 6 % 1000000)
    code = code if (code > 100000) else code + 100000
    print(f"confirm_code: {code}")
    return code


router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
    responses={404: {"description": "Not found"}},
)


@router.get("/welcome")
def get_public_key(region: str = Header(...), timestamp: int = 0):
    region = region.lower()
    auth_host = region_auth_hosts[region]

    slot = timestamp % 100
    pubkey = cache.get(f"pubkey_{slot}")
    if pubkey == None:
        res = requests.get(f"{auth_host}/security/pubkey",
                           params={"ts": timestamp})
        res = res.json()
        pubkey = res["data"]
        cache.set(f"pubkey_{slot}", pubkey)

    return res_success(data=pubkey)


@router.post("/signup")
def signup(region: str = Header(...), email: EmailStr = Body(...), meta: str = Body(...)):
    region = region.lower()
    auth_host = region_auth_hosts[region]
    if cache.get(email) != None:
        return res_err(msg="registered or registering")

    confirm_code = gen_confirm_code()
    res = requests.post(f"{auth_host}/sendcode/email", json={
        "email": email,
        "confirm_code": confirm_code,
        "sendby": "no_exist",  # email 不存在時寄送
    })
    res = res.json()

    if res["msg"] == "email_sent":
        email_playload = json.dumps({
            "email": email,
            "confirm_code": confirm_code,
            "meta": meta,
        })
        cache.set(email, email_playload, ex=CONFIRM_CODE_TTL)
        return res_success()

    elif res["msg"] != None:
        return res_err(msg=res["msg"])

    else:
        email_playload = json.dumps({
            "region": res["region"],
            "role": res["role"],
        })
        cache.set(email, email_playload)
        return res_err(msg="email registered")


@router.post("/signup/conform")
def confirm_signup(region: str = Header(...), email: EmailStr = Body(...), pubkey: str = Body(...), confirm_code: str = Body(...)):
    region = region.lower()
    auth_host = region_auth_hosts[region]
    user = json.loads(cache.get(email))
    print("\n\nuser: ", user, type(user))
    if user == None:
        return res_err(msg="no signup data")

    if user == {}:
        return res_err(msg="registering")

    if confirm_code != str(user["confirm_code"]):
        return res_err(msg="wrong confirm_code")

    # "registering": empty data, but TTL=30sec
    cache.set(email, "{}", ex=30)
    payload = {
        "email": email,
        "meta": user["meta"],
        "pubkey": pubkey,
    }

    res = requests.post(f"{auth_host}/signup", json=payload)
    res = res.json()
    cache.set(email, json.dumps(res["data"]), ex=LOGIN_TTL)

    return res


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
@router.post("/login")
def login(
    current_region: str = Header(...),
    email: EmailStr = Body(...),
    meta: str = Body(...),
    pubkey: str = Body(...)
):
    current_region = current_region.lower()
    auth_host = region_auth_hosts[current_region]
    match_host = region_match_hosts[current_region]
    payload = {
        "email": email,
        "meta": meta,
        "pubkey": pubkey,
    }

    auth_res = requests.post(f"{auth_host}/login", json=payload)
    auth_res = auth_res.json()
    auth_data = auth_res["data"]

    # found in DB
    if auth_res["msg"] == "error_pass":
        return res_err(msg="error_pass")

    # not found in DB and S3
    if auth_res["msg"] == "not_registered":
        return res_err(msg="user not found")  # 沒註冊過

    # found in S3, and region == "current_region"(在 meta, 解密後才會知道)(S3記錄:註冊在該auth_service卻找不到)
    if auth_res["msg"] == "register_fail":
        print("\n\nhas record in S3, but no record in DB\n\n")
        return res_err(msg="register fail")  # {log_level:嚴重問題}

    # found in S3, and region != "current_region"(在 meta, 解密後才會知道)(找錯地方)
    # S3 有記錄但該地區的 auth-service 沒記錄，auth 從 S3 找 region 後回傳
    data = auth_res["data"]
    if data["token"] == None:
        region = data["region"]  # 換其他 region 再請求一次
        auth_host = region_auth_hosts[region]
        match_host = region_match_hosts[region]
        auth_res = requests.post(f"{auth_host}/login", json=payload)
        auth_res = auth_res.json()
        auth_data = auth_res["data"]

    # 驗證合法, save into cache
    auth_data.update({
        "current_region": current_region,
        "socketid": "xxx",  # TODO: socketid???
        "online": True,
    })
    auth_payload = json.dumps(auth_data)
    cache.set(email, auth_payload, ex=LOGIN_TTL)

    # 驗證合法 >> 取得 match service 資料
    role = auth_data["role"]
    role_id = auth_data["role_id"]
    print(f"role: {role} role_id: {role_id}")

    match_res = requests.get(f"{match_host}/{role}/{role_id}/matchdata")
    print("\n\nmatch_res: ", match_res)
    match_res = match_res.json()
    match_data = match_res["data"]

    return res_success(data={
        "auth": auth_data,
        "match": match_data,
    })


@router.get("/logout")
def logout(email: EmailStr, token: str = Header(...)):
    user = cache.get(email)
    if not user:
        return res_err(msg="logged out")

    user_payload = json.loads(user)
    if not "token" in user_payload:
        return res_err(msg="logged out")

    if user_payload["token"] != token:
        return res_err(msg="access denied")

    # TODO: 是保留部分資訊，還是需要完全刪除 cache?
    for key in ["token", "socketid", "role_id"]:
        if key in user_payload:
            del user_payload[key]

    user_payload["online"] = False
    cache.set(email, json.dumps(user_payload), ex=LOGIN_TTL)
    return res_success()
