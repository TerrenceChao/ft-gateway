from typing import Optional
from pydantic import BaseModel
from ..dtos import *


class StripePaymentDTO(BaseModel):
    payment_method_id: Optional[str]


class StripeUserPaymentRequestDTO(UserDTO, StripePaymentDTO):
    pass


class StripeSubscribeRequestDTO(UnsubscribeRequestDTO, StripePaymentDTO):
    plan_id: Optional[str]
