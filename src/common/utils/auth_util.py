import os
import json
from datetime import date, datetime
from typing import List
import jwt
from fastapi import Header, Body, HTTPException


# JWT_SECRET = os.getenv("TOKEN_EXPIRE_TIME", "zaq1xsw2")
TOKEN_EXPIRE_TIME = int(os.getenv("TOKEN_EXPIRE_TIME", 60 * 60 * 24 * 7))


def __get_secret(data: dict):
    return str(data["role_id"]) # if "role_id" in data else JWT_SECRET

def gen_token(data: dict, fields: List):
    public_info = {}
    secret = __get_secret(data)
    for field in fields:
        val = str(data[field])
        public_info[field] = val
        
    exp = datetime.now().timestamp() + TOKEN_EXPIRE_TIME
    public_info.update({ "exp": exp })
    return jwt.encode(payload=public_info, key=secret, algorithm="HS256")



def __get_secret_by_header(role_id: str):
    return role_id # if role_id else JWT_SECRET

def verify_token(token: str = Header(...), role_id: str = Header(...)):
    secret = __get_secret_by_header(role_id)
    data = jwt.decode(jwt=token, key=secret, algorithms=["HS256"])
    if not "role_id" in data or int(data["role_id"]) != int(role_id):
        raise HTTPException(status_code=400, detail="invalid user")