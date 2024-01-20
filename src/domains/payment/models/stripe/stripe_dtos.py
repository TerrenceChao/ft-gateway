from typing import Optional
from pydantic import BaseModel
from ..dtos import *


class StripePaymentDTO(BaseModel):
    payment_method_id: Optional[str]


class StripeUserPaymentRequestDTO(UserDTO, StripePaymentDTO):
    pass


class StripeSubscribeRequestDTO(UnsubscribeRequestDTO, StripePaymentDTO):
    plan_id: Optional[str]

    def subscription(self, payment_type: str, merchant: str) -> (SubscriptionDTO):
        subscription_dto = super().subscription(payment_type, merchant)
        subscription_dto.plan_id = self.plan_id
        return subscription_dto
