from typing import Optional
from pydantic import BaseModel

class Restaurant(BaseModel):
    restaurant_id: str
    name: Optional[str] = None
    location: Optional[str] = None
    cuisine_type: Optional[str] = None
    rating: Optional[float] = None