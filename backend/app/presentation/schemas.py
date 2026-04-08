from datetime import datetime, time
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    name: Optional[str] = None
    age: Optional[int] = Field(default=None, ge=0, le=120)
    gender: Optional[str] = None
    location: Optional[str] = None
    preferred_cuisine: Optional[str] = None
    order_frequency: Optional[str] = None
    loyalty_program: bool = False
    role: str = "customer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    customer_id: str
    name: Optional[str]
    age: Optional[int]
    gender: Optional[str]
    location: Optional[str]
    loyalty_program: bool
    preferred_cuisine: Optional[str]
    order_frequency: Optional[str]
    role: str

    model_config = {"from_attributes": True}


class UpdateProfileRequest(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = Field(default=None, ge=0, le=120)
    gender: Optional[str] = None
    location: Optional[str] = None
    preferred_cuisine: Optional[str] = None
    order_frequency: Optional[str] = None
    loyalty_program: Optional[bool] = None


class ChangeRoleRequest(BaseModel):
    new_role: str


class CreateRestaurantRequest(BaseModel):
    name: str = Field(min_length=1)
    location: Optional[str] = None
    description: Optional[str] = None


class UpdateRestaurantRequest(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None


class RestaurantResponse(BaseModel):
    restaurant_id: str
    owner_id: str
    name: Optional[str]
    location: Optional[str]
    description: Optional[str]

    model_config = {"from_attributes": True}


class CreateMenuItemRequest(BaseModel):
    name: str = Field(min_length=1)
    category: Optional[str] = None
    price: Optional[float] = Field(default=None, ge=0)


class UpdateMenuItemRequest(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = Field(default=None, ge=0)


class MenuItemResponse(BaseModel):
    food_item_id: str
    restaurant_id: str
    name: str
    category: Optional[str]
    price: Optional[float]
    available_from: Optional[time] = None
    available_until: Optional[time] = None


    model_config = {"from_attributes": True}


class PlaceOrderRequest(BaseModel):
    restaurant_id: str
    food_item_ids: List[str] = Field(min_length=1)


class OrderResponse(BaseModel):
    order_id: str
    customer_id: str
    restaurant_id: str
    items: List[str]
    order_time: Optional[datetime]
    order_value: Optional[float]
    status: str
    customer_rating: Optional[float]
    customer_satisfaction: Optional[int]

    model_config = {"from_attributes": True}


class AssignDeliveryRequest(BaseModel):
    delivery_method: Optional[str] = None
    delivery_distance: Optional[float] = Field(default=None, ge=0)
    estimated_delivery_time: Optional[datetime] = None


class UpdateDeliveryRequest(BaseModel):
    delivery_time_actual: Optional[float] = None
    delivery_delay: Optional[float] = None
    delivery_method: Optional[str] = None
    route_taken: Optional[str] = None
    route_type: Optional[str] = None
    route_efficiency: Optional[float] = None
    traffic_condition: Optional[str] = None
    weather_condition: Optional[str] = None
    predicted_delivery_mode: Optional[str] = None
    traffic_avoidance: Optional[bool] = None


class DeliveryResponse(BaseModel):
    order_id: str
    delivery_time: Optional[datetime]
    delivery_time_actual: Optional[float]
    delivery_delay: Optional[float]
    delivery_distance: Optional[float]
    delivery_method: Optional[str]
    route_taken: Optional[str]
    route_type: Optional[str]
    route_efficiency: Optional[float]
    traffic_condition: Optional[str]
    weather_condition: Optional[str]
    predicted_delivery_mode: Optional[str]
    traffic_avoidance: Optional[bool]

    model_config = {"from_attributes": True}


class QuoteRequest(BaseModel):
    food_item_ids: List[str] = Field(min_length=1)
    delivery_distance: float = Field(default=0.0, ge=0)


class PriceBreakdownResponse(BaseModel):
    subtotal: float
    delivery_fee: float
    taxes: float
    loyalty_discount: float
    grand_total: float


class PaymentResponse(BaseModel):
    order_id: str
    amount_charged: float
    status: str
    message: str


class NotificationResponse(BaseModel):
    notification_id: int
    user_id: str
    event_type: str
    message: str
    created_at: datetime
    is_read: bool


class ErrorResponse(BaseModel):
    detail: str
