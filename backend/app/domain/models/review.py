from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Review(BaseModel):
    review_id: str
    order_id: str
    customer_id: str
    restaurant_id: str
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
