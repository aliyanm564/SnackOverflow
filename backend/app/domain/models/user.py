from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class UserRole(str, Enum):
    CUSTOMER = "customer"
    RESTAURANT_OWNER = "restaurant_owner"
    DELIVERY_PERSON = "delivery_person"


class User(BaseModel):
    customer_id: str
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    location: Optional[str] = None
    loyalty_program: bool = False
    order_history: List[str] = Field(default_factory=list)
    preferred_cuisine: Optional[str] = None
    order_frequency: Optional[str] = None
    role: UserRole = UserRole.CUSTOMER
    
