import json
from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr
from .models import *


class UserDTO(BaseModel):
    role_id: int
    email: Optional[EmailStr]

    def model(self, payment_type: str, merchant: str) -> (BaseUserPayment):
        return BaseUserPayment(
            role_id=self.role_id,
            payment_type=payment_type,
            merchant=merchant,
        )


# TODO: deprecated
class UserPaymentDTO(BaseModel):
    user: UserDTO
    payment_type: Optional[str]
    merchant: Optional[str]

    def model(self) -> (BaseUserPayment):
        return BaseUserPayment(
            role_id=self.user.role_id,
            payment_type=self.payment_type,
            merchant=self.merchant,
        )


class SubscriptionDTO(BaseModel):
    user: UserDTO
    payment_type: Optional[str]
    merchant: Optional[str]
    plan_id: Optional[str]

    def user_model(self) -> (BaseUserPayment):
        return BaseUserPayment(
            role_id=self.user.role_id,
            payment_type=self.payment_type,
            merchant=self.merchant,
        )


class UnsubscribeRequestDTO(BaseModel):
    role_id: int
    email: Optional[EmailStr]

    def subscription(self, payment_type: str, merchant: str) -> (SubscriptionDTO):
        return SubscriptionDTO(
            user=UserDTO(
                role_id=self.role_id,
                email=self.email,
            ),
            payment_type=payment_type,
            merchant=merchant,
        )


class WebhookRequestDTO(BaseModel):
    signature: str
    body: bytes

    def __str__(self) -> (str):
        try:
            dao = {
                'signature': self.signature,
                'body': json.loads(self.body.decode('utf-8')),
            }

        except Exception as e:
            dao = {
                'signature': self.signature,
                'body': self.body.decode('utf-8'),
            }

        finally:
            return json.dumps(dao, indent=4)
