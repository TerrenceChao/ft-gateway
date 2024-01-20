from typing import Optional
from pydantic import BaseModel, EmailStr
from .models import *


class UserDTO(BaseModel):
    role_id: int
    email: Optional[EmailStr]


class UnsubscribeRequestDTO(BaseModel):
    role_id: int
    email: Optional[EmailStr]
