from typing import Optional
from pydantic import BaseModel

class MenuItem(BaseModel):
    food_item_id: str
    restaurant_id: str
    name: str
    category: Optional[str] = None
    price: Optional[float] = None