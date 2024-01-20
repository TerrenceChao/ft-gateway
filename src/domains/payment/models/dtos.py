from pydantic import BaseModel
from .models import *


class UserDTO(BaseModel):
    role_id: int


class UnsubscribeRequestDTO(BaseModel):
    role_id: int
