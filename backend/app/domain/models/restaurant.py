from typing import Optional
from pydantic import BaseModel

class Restaurant(BaseModel):
    restaurant_id: str
    owner_id: str
    name: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None