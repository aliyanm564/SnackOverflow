# backend/app/domain/models/delivery.py
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from backend.app.domain.models.enums import DeliveryMethod, RouteType


class Delivery(BaseModel):
    order_id: str
    delivery_time: Optional[datetime] = None
    delivery_time_actual: Optional[datetime] = None
    delivery_delay: Optional[float] = None
    delivery_distance: Optional[float] = None
    delivery_method: Optional[DeliveryMethod] = None
    route_taken: Optional[str] = None
    route_type: Optional[RouteType] = None
    route_efficiency: Optional[float] = None
    traffic_condition: Optional[str] = None
    weather_condition: Optional[str] = None
    predicted_delivery_mode: Optional[str] = None
    traffic_avoidance: Optional[bool] = None
