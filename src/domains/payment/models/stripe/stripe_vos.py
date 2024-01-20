from pydantic import BaseModel
from typing import Optional


class StripePlanVO(BaseModel):
    id: str
    amount: float
    currency: str
    interval: str
    interval_count: int
    nickname: Optional[str]
    trial_period_days: Optional[int]
    product: Optional[str]
