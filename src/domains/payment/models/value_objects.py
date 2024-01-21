from typing import Optional
from pydantic import BaseModel
from .models import *
from ..configs.constants import *
from ....infra.utils.time_util import *


class PaymentStatusVO(BaseModel):
    role_id: int
    status: PaymentStatusEnum
    subscribe_status: SubscribeStatusEnum
    current_period_end: Optional[int]
    valid: bool = False
