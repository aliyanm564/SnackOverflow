
from datetime import datetime
from typing import List, Optional

from backend.app.application.exceptions import (
    AuthorizationError,
    BusinessRuleError,
    NotFoundError,
)
from backend.app.domain.models.delivery import Delivery
from backend.app.domain.models.enums import DeliveryMethod, RouteType
from backend.app.domain.models.user import User, UserRole
from backend.app.infrastructure.repositories.delivery_repository import (
    DeliveryRepository,
)
from backend.app.infrastructure.repositories.order_repository import OrderRepository

class DeliveryService:

    def __init__(
        self,
        delivery_repository: DeliveryRepository,
        order_repository: OrderRepository,
    ) -> None:
        self._deliveries = delivery_repository
        self._orders = order_repository

    def assign_delivery(
        self,
        requesting_user: User,
        order_id: str,
        delivery_method: Optional[DeliveryMethod] = None,
        delivery_distance: Optional[float] = None,
        estimated_delivery_time: Optional[datetime] = None,
    ) -> Delivery:
      
        self._check_not_customer(requesting_user)

        order = self._orders.get_by_id(order_id)
        if order is None:
            raise NotFoundError(f"Order '{order_id}' not found.")

        existing = self._deliveries.get_by_id(order_id)
        if existing is not None:
            raise BusinessRuleError(
                f"Delivery already exists for order '{order_id}'."
            )

        delivery = Delivery(
            order_id=order_id,
            delivery_method=delivery_method,
            delivery_distance=delivery_distance,
            delivery_time=estimated_delivery_time,
        )
        return self._deliveries.save(delivery)

    def get_delivery(self, order_id: str) -> Delivery:
        delivery = self._deliveries.get_by_id(order_id)
        if delivery is None:
            raise NotFoundError(f"No delivery found for order '{order_id}'.")
        return delivery

    def list_deliveries(self, offset: int = 0, limit: int = 20) -> List[Delivery]:
        return self._deliveries.get_paginated(offset=offset, limit=limit)

    def update_delivery(
        self,
        requesting_user: User,
        order_id: str,
        delivery_time_actual: Optional[float] = None,
        delivery_delay: Optional[float] = None,
        delivery_method: Optional[DeliveryMethod] = None,
        route_taken: Optional[str] = None,
        route_type: Optional[RouteType] = None,
        route_efficiency: Optional[float] = None,
        traffic_condition: Optional[str] = None,
        weather_condition: Optional[str] = None,
        predicted_delivery_mode: Optional[str] = None,
        traffic_avoidance: Optional[bool] = None,
    ) -> Delivery:
        self._check_not_customer(requesting_user)

        delivery = self.get_delivery(order_id)

        updates = {}
        if delivery_time_actual is not None:
            updates["delivery_time_actual"] = delivery_time_actual
        if delivery_delay is not None:
            updates["delivery_delay"] = delivery_delay
        if delivery_method is not None:
            updates["delivery_method"] = delivery_method
        if route_taken is not None:
            updates["route_taken"] = route_taken
        if route_type is not None:
            updates["route_type"] = route_type
        if route_efficiency is not None:
            updates["route_efficiency"] = route_efficiency
        if traffic_condition is not None:
            updates["traffic_condition"] = traffic_condition
        if weather_condition is not None:
            updates["weather_condition"] = weather_condition
        if predicted_delivery_mode is not None:
            updates["predicted_delivery_mode"] = predicted_delivery_mode
        if traffic_avoidance is not None:
            updates["traffic_avoidance"] = traffic_avoidance

        updated_delivery = delivery.model_copy(update=updates)
        return self._deliveries.save(updated_delivery)
    
    def _check_not_customer(self, user: User) -> None:
        if user.role == UserRole.CUSTOMER:
            raise AuthorizationError("Customers cannot perform this action.")

    def get_by_method(self, method: DeliveryMethod) -> List[Delivery]:
        return self._deliveries.get_by_delivery_method(method)

    def get_by_route_type(self, route_type: RouteType) -> List[Delivery]:
        return self._deliveries.get_by_route_type(route_type)

    def get_delayed_deliveries(self, min_delay: float = 0.0) -> List[Delivery]:
        if min_delay < 0:
            raise ValueError("Delay cant be negative.")
        return self._deliveries.get_delayed(min_delay)

    def get_by_traffic(self, condition: str) -> List[Delivery]:
        return self._deliveries.get_by_traffic_condition(condition)

    def get_by_weather(self, condition: str) -> List[Delivery]:
        return self._deliveries.get_by_weather_condition(condition)
    
    