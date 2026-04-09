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
    avg_rating: Optional[float] = None
    review_count: int = 0

    model_config = {"from_attributes": True}


class CreateMenuItemRequest(BaseModel):
    name: str = Field(min_length=1)
    category: Optional[str] = None
    price: Optional[float] = Field(default=None, ge=0)
    available_from: Optional[time] = None
    available_until: Optional[time] = None


class UpdateMenuItemRequest(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = Field(default=None, ge=0)
    available_from: Optional[time] = None
    available_until: Optional[time] = None


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


class ProcessPaymentRequest(BaseModel):
    promo_code: Optional[str] = None


class PaymentResponse(BaseModel):
    order_id: str
    amount_charged: float
    status: str
    message: str


class CreatePromoRequest(BaseModel):
    code: str = Field(min_length=1, max_length=30)
    discount_type: str
    discount_value: float = Field(gt=0)
    expiry_date: Optional[datetime] = None
    usage_limit: Optional[int] = Field(default=None, ge=1)


class AssignPromoRequest(BaseModel):
    customer_ids: List[str]


class ValidatePromoRequest(BaseModel):
    code: str
    order_id: str


class ValidatePromoResponse(BaseModel):
    valid: bool
    discount_amount: float
    adjusted_total: float
    message: str


class PromoResponse(BaseModel):
    promo_id: str
    code: str
    discount_type: str
    discount_value: float
    expiry_date: Optional[datetime]
    usage_limit: Optional[int]
    usage_count: int
    is_active: bool
    assigned_customer_ids: List[str]


class NotificationResponse(BaseModel):
    notification_id: int
    user_id: str
    event_type: str
    message: str
    created_at: datetime
    is_read: bool


class ReviewCreateRequest(BaseModel):
    order_id: str
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = None


class ReviewUpdateRequest(BaseModel):
    rating: Optional[int] = Field(default=None, ge=1, le=5)
    comment: Optional[str] = None


class ReviewResponse(BaseModel):
    review_id: str
    order_id: str
    customer_id: str
    restaurant_id: str
    rating: int
    comment: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


class OrderTrackingResponse(BaseModel):
    order_id: str
    status: str
    order_time: Optional[datetime]
    order_value: Optional[float]
    restaurant_id: str
    items: List[str]
    delivery_method: Optional[str] = None
    estimated_delivery_time: Optional[datetime] = None
    delivery_distance: Optional[float] = None

    model_config = {"from_attributes": True}


class ErrorResponse(BaseModel):
    detail: str
