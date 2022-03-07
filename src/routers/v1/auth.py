import os, time, json
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
from ...db.nosql import schemas
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


cache_host = os.getenv("CACHE_HOST", "localhost")
cache_port = int(os.getenv("CACHE_PORT", "6379"))
cache_user = os.getenv("CACHE_USERNAME", "myuser")
cache_pass = os.getenv("CACHE_PASSWORD", "qwer1234")


cache = Redis(
  host=cache_host, 
  port=cache_port, 
  decode_responses=True, 
  # ssl=True, 
  # username=cache_user, 
  # password=cache_pass,
)

log.basicConfig(level=log.INFO)
if cache.ping():
    log.info("Connected to Redis")


def gen_confirm_code():
  code = int(time.time() ** 6 % 1000000)
  return code if (code > 100000) else code + 100000


router = APIRouter(
  prefix="/auth",
  tags=["auth"],
  responses={404: {"description": "Not found"}},
)


@router.get("/welcome")
def get_public_key(region: str = Header(...), timestamp: int = 0):
  auth_host = region_auth_hosts[region]

  slot = timestamp % 100
  pubkey = cache.get(f"pubkey_{slot}")
  if pubkey == None:
    res = requests.get(f"{auth_host}/security/pubkey", params={ "ts": timestamp })
    pubkey = res["data"]
    cache.set(f"pubkey_{slot}", pubkey)
  
  return res_success(data=pubkey)


@router.post("/signup")
def signup(region: str = Header(...), email: str = Body(...), meta: str = Body(...)):
  auth_host = region_auth_hosts[region]
  user = cache.get(email)
  if user != None:
    return res_err(msg="registered or registering")

  confirm_code = gen_confirm_code()
  res = requests.post(f"{auth_host}/sendcode/email", json={
    "email": email,
    "confirm_code": confirm_code,
    "sendby": "no_exist", # email 不存在時寄送
  })

  if res["msg"] and res["msg"] == "email_sent":
    cache.set(email, {
      "email": email,
      "confirm_code": confirm_code,
      "meta": meta,
    })
    return res_success()

  else:
    cache.set(email, {
      "region": res["region"],
      "role": res["role"],
    })
    return res_err(msg="email registered")


@router.post("/signup/conform")
def confirm_signup(region: str = Header(...), email: str = Body(...), pubkey: str = Body(...), confirm_code: str = Body(...)):
  auth_host = region_auth_hosts[region]
  user = cache.get(email)
  if user == None:
    return res_err(msg="no signup data")
  
  if user == {}:
    return res_err(msg="registering")
  
  if confirm_code != user["confirm_code"]:
    return res_err(msg="wrong confirm_code")

  # "registering": empty data, but TTL=30sec
  cache.set(email, {}, ex=30) 
  payload = {
    "email": email,
    "meta": user["meta"],
    "pubkey": pubkey,
  }

  res = requests.post(f"{auth_host}/signup", json=payload)
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
            socketId: ??????(for region)
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
            socketId: ??????(for region)
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
  region: str = Header(...),
  email: str = Body(...),
  meta: str = Body(...),
  pubkey: str = Body(...)
):
  auth_host = region_auth_hosts[region]
  match_host = region_match_hosts[region]
  payload = {
    "email": email,
    "meta": meta,
    "pubkey": pubkey,
  }

  auth_res = requests.post(f"{auth_host}/login", json=payload)

  # found in DB
  if auth_res["msg"] == "error_pass":
    return res_err(msg="error_pass")

  # not found in DB and S3
  if auth_res["msg"] == "not_registered":
    return res_err(msg="user not found") # 沒註冊過
  
  # found in S3, and region == "current_region"(在 meta, 解密後才會知道)(S3記錄:註冊在該auth_service卻找不到)
  if auth_res["msg"] == "register_fail":
    return res_err(msg="register fail") # {log_level:嚴重問題}
  
  # found in S3, and region != "current_region"(在 meta, 解密後才會知道)(找錯地方)
  # S3 有記錄但該地區的 auth-service 沒記錄，auth 從 S3 找 region 後回傳
  data = auth_res["data"]
  if data["token"] == None:
    region = data["region"] # 換其他 region 再請求一次
    auth_host = region_auth_hosts[region]
    match_host = region_match_hosts[region]
    auth_res = requests.post(f"{auth_host}/login", json=payload)
    
  # 驗證合法, save into cache
  auth_res.update({ 
    "current_region": current_region,
    "socketid": "xxx", # TODO: socketId???
    "online": True,
  })
  cache.set(email, auth_res)
  
  # 驗證合法 >> 取得 match service 資料
  role_id = auth_res["role_id"]
  match_res = requests.get(f"{match_host}/matchdata/{role_id}")

  return res_success(data={
    "auth": auth_res,
    "match": match_res,
  })


@router.get("/logout")
def logout(email: str = Body(...), token: str = Body(...)):
  user = cache.get(email)
  if not user["token"]:
    return res_err(msg="logged out")

  if user["token"] != token:
    return res_err(msg="access denied")

  for key in ["token", "socketId"]:
    if user[key]:
      del user[key]

  user["online"] = False
    
  cache.set(email, user)
  return res_success()
    