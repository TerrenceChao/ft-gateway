import json
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, EmailStr, validator
from ....configs.constants import VALID_ROLES
from ....configs.exceptions import *


class PubkeyVO(BaseModel):
    pubkey: str = None


class SignupVO(BaseModel):
    email: EmailStr
    meta: str

    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "meta": "{\"role\":\"teacher\",\"pass\":\"secret\"}",
            },
        }


class SignupConfirmVO(PubkeyVO):
    email: EmailStr
    confirm_code: str

    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "confirm_code": "106E7B",
                "pubkey": "the-pubkey",
            },
            "description": "ignore 'pubkey' in the body",
        }


class LoginVO(PubkeyVO):
    current_region: str = None  # in headers
    email: EmailStr
    meta: str
    prefetch: int = None

    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "pubkey": "the-pubkey",
                "meta": "{\"pass\":\"secret\"}",
                "prefetch": 3,
            },
            "description": "ignore 'current_region' in the body, it will be set in headers; ignore 'pubkey' in the body",
        }

class ResetPasswordVO(PubkeyVO):
    register_email: EmailStr
    meta: str
    
    class Config:
        schema_extra = {
            "example": {
                "register_email": "user@example.com",
                "pubkey": "the-pubkey",
                "meta": "{\"password1\":\"new_pass\",\"password2\":\"new_pass\"}",
            },
            "description": "ignore 'pubkey' in the body",
        }
    
class UpdatePasswordVO(ResetPasswordVO):
    pass

    class Config:
        schema_extra = {
            "example": {
                "register_email": "user@example.com",
                "pubkey": "the-pubkey",
                "meta": "{\"password1\":\"new_pass\",\"password2\":\"new_pass\",\"origin_password\":\"password\"}",
            },
            "description": "ignore 'pubkey' in the body",
        }


class AuthVO(BaseModel):
    email: EmailStr
    role: str
    role_id: int
    token: str
    region: str
    current_region: Optional[str] = None
    socketid: Optional[str] = None
    online: Optional[bool] = False
    created_at: int


