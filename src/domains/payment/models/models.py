from decimal import Decimal
from typing import Optional, Dict, Union
from pydantic import BaseModel
from ..configs.constants import PaymentStatusEnum
from ....infra.utils.time_util import gen_timestamp

class BasePaymentChannel(BaseModel):
    merchant: str
    customer_id: str # binding with role_id
    payout_id: Optional[str] # one-time payment
    subscription_id: Optional[str] # recurring payment
    current_period_end: int = -1 # in seconds
    

class BaseUserPayment(BaseModel):
    role_id: int
    payment_type: str
    merchant: str


class PaymentStatusModel(BasePaymentChannel, BaseUserPayment):
    # role_id: int # partition key
    # payment_type: str # order key
    status: PaymentStatusEnum = PaymentStatusEnum.UNPAID


class PaymentRecordModel(PaymentStatusModel):
    # customer_id: str # partition key
    created_at: Optional[int] # order key
    plan_id: str
    plan: Optional[Dict]
    amount: Optional[str]
    currency: Optional[str]
    
    def __init__(self, **data):
        super().__init__(**data)
        if self.created_at is None:
            self.created_at = gen_timestamp()
        
    def base_user_payment(self) -> (BaseUserPayment):
        return BaseUserPayment(
            role_id=self.role_id,
            payment_type=self.payment_type,
            merchant=self.merchant,
        )
