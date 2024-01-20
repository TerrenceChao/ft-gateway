from typing import Optional, Dict, Any
from pydantic import BaseModel
from .models import *
from ..configs.constants import *
from ....infra.utils.time_util import *


class PaymentStatusVO(BaseModel):
    role_id: int
    status: PaymentStatusEnum
    current_period_end: Optional[int]
    valid: bool = False

    def __init__(self, **data):
        super().__init__(**data)
        if data.get('current_period_end', -1) > 0:
            self.valid = \
                self.status in PAYMENT_PERIOD or \
                self.current_period_end > current_seconds()

        elif data.get('payout_id') != None:
            self.valid = True
