from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

from backend.app.domain.models.enums import OrderStatus


class Order(BaseModel):
    order_id: str
    customer_id: str
    restaurant_id: str
    items: List[str]
    order_time: Optional[datetime] = None
    order_value: Optional[float] = None
    status: OrderStatus = OrderStatus.PENDING
    customer_rating: Optional[float] = None
    customer_satisfaction: Optional[int] = None
