from pydantic import BaseModel, EmailStr
from typing import Optional


class EmailVO(BaseModel):
    sender_id: int
    recipient_id: int
    subject: str
    body: str


class EmailAuthVO(EmailVO):
    sender_role: Optional[str]
    recipient_role: Optional[str]
    recipient_email: Optional[EmailStr]
