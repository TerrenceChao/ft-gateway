from typing import List, Optional
from pydantic import BaseModel, EmailStr
from .base_schemas import BaseEntity


class BaseAuth(BaseEntity):
    email: EmailStr
    aid: Optional[int] = None


class FTAuth(BaseAuth):
    pass_hash: Optional[str] = None
    pass_salt: Optional[str] = None


# TODO:
class FacebookAuth(BaseAuth):
    pass


# TODO:
class GoogleAuth(BaseAuth):
    pass


class Account(BaseEntity):
    aid: Optional[int] = None
    region: str
    email: EmailStr
    email2: Optional[EmailStr] = None
    in_active: bool = True
    role: str
    role_id: Optional[int] = None
    auth: BaseAuth
