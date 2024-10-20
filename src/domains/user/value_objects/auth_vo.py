import json
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, EmailStr, validator
from ....configs.constants import VALID_ROLES
from ....configs.exceptions import *
from ...match.company.value_objects.c_value_objects import CompanyMatchDataVO
from ...match.teacher.value_objects.t_value_objects import TeacherMatchDataVO


def meta_validator(meta: str, pubkey: str = None):
    try:
        # TODO: need pubkey to decrypt meta
        meta_json = json.loads(meta)
        if not 'role' in meta_json:
            raise ClientException(msg=f'role is required')
        
        if not meta_json['role'] in VALID_ROLES:
            raise ClientException(msg=f'role allowed only in {VALID_ROLES}')

        if not 'pass' in meta_json:
            raise ClientException(msg=f'pass is required')

        return meta

    except json.JSONDecodeError as e:
        log.error(
            f'func: meta_validator error [json_decode_error] meta:%s, err:%s', meta, e.__str__())
        raise ClientException(msg='invalid json format of meta')

    except ClientException as e:
        raise ClientException(msg=e.msg)


class SignupVO(BaseModel):
    email: EmailStr
    pubkey: str = None
    meta: str

    @validator('meta')
    def check_meta(cls, v, values, **kwargs):
        return meta_validator(v, values['pubkey'])

    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "pubkey": "the-pubkey",
                "meta": "{\"role\":\"teacher\",\"pass\":\"secret\"}",
            },
            "description": "ignore 'pubkey' in the body",
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
                "pubkey": "the-pubkey",
            },
            "description": "ignore 'pubkey' in the body",
        }


class LoginVO(BaseModel):
    current_region: str = None  # in headers
    email: EmailStr
    pubkey: str = None
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

class ResetPasswordVO(BaseModel):
    register_email: EmailStr
    password1: str
    password2: str

class UpdatePasswordVO(ResetPasswordVO):
    origin_password: str

class BaseAuthDTO(BaseModel):
    role: str
    role_id: int
    
class AuthVO(BaseAuthDTO):
    email: EmailStr
    token: str
    region: str
    current_region: Optional[str] = None
    online: Optional[bool] = False
    created_at: int


class PubkeyVO(BaseModel):
    pubkey: str

class SignupResponseVO(BaseModel):
    auth: AuthVO    
    
class LoginResponseVO(SignupResponseVO):
    match: Union[CompanyMatchDataVO, TeacherMatchDataVO]

class SSOLoginVO(BaseModel):
    code: str
    state: str
    sso_type: Optional[str]

    def fine_dict(self):
        d = super().dict()
        d.pop('sso_type', None)
        return d
