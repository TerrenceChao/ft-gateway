from typing import Optional
from pydantic import BaseModel


class BaseEntity(BaseModel):
    created_at: Optional[int] = None
    updated_at: Optional[int] = None

