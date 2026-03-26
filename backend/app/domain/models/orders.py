from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

from backend.app.domain.models.enums import OrderStatus


class Order(BaseModel):
    order_id: str
    customer_id: str
    restaurant_id: str
    items: List[str] = Field(min_length=1)
    order_time: Optional[datetime] = None
    order_value: Optional[float] = Field(default=None, ge=0)
    status: OrderStatus = OrderStatus.PENDING
    customer_rating: Optional[float] = Field(default=None, ge=0, le=5)
    customer_satisfaction: Optional[int] = Field(default=None, ge=1, le=5)

    @field_validator("items")
    @classmethod
    def _validate_items(cls, items: List[str]) -> List[str]:
        if any(not item.strip() for item in items):
            raise ValueError("Order items must be non-empty strings.")
        return items

    def can_be_cancelled(self) -> bool:
        return self.status == OrderStatus.PENDING

    def can_be_completed(self) -> bool:
        return self.status == OrderStatus.PENDING
