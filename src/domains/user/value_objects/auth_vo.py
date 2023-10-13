import json
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, EmailStr, validator
from ....configs.constants import VALID_ROLES, REGION_MAPPING
from ....configs.exceptions import *
from ...match.company.value_objects.c_value_objects import CompanyMatchDataVO
from ...match.teacher.value_objects.t_value_objects import TeacherMatchDataVO

REGION_CODES = set(REGION_MAPPING.values())


def meta_validator(meta: str):
    try:
        meta_json = json.loads(meta)
        if not meta_json['role'] in VALID_ROLES:
            raise ClientException(msg=f'role allowed only in {VALID_ROLES}')

        if not meta_json['region'] in REGION_CODES:
            raise ClientException(msg=f'region is not allowed')

        return meta

    except json.JSONDecodeError as e:
        log.error(
            f'func: meta_validator error [json_decode_error] meta:%s, err:%s', meta, e.__str__())
        raise ClientException(msg=f'invalid json format, meta:{meta}')

    except ClientException as e:
        raise ClientException(msg=e.msg)


class SignupVO(BaseModel):
    email: EmailStr
    meta: str

    @validator('meta')
    def check_meta(cls, v):
        return meta_validator(v)

    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "meta": "{\"region\":\"jp\",\"role\":\"teacher\",\"pass\":\"secret\"}",
            }
        }


class SignupConfirmVO(BaseModel):
    email: EmailStr
    confirm_code: str
    pubkey: str = None

    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "confirm_code": "106E7B",
                "pubkey": "the-pubkey"
            }
        }


class LoginVO(BaseModel):
    current_region: str = None,  # this.header, auth-service.body
    email: EmailStr
    meta: str
    prefetch: int = None
    pubkey: str = None

    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "meta": "{\"pass\":\"secret\"}",
                "prefetch": None,
                "pubkey": "the-pubkey"
            }
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


class PubkeyVO(BaseModel):
    pubkey: str
