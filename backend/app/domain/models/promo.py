from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class PromoCode(BaseModel):
    promo_id: str
    code: str
    discount_type: str  # "percentage" or "flat"
    discount_value: float = Field(ge=0)
    expiry_date: Optional[datetime] = None
    usage_limit: Optional[int] = None
    usage_count: int = 0
    is_active: bool = True
    owner_id: str
    assigned_customer_ids: List[str] = []

    model_config = {"from_attributes": True}
