
from datetime import datetime
from typing import List, Optional

from backend.app.application.exceptions import (
    AuthorizationError,
    BusinessRuleError,
    NotFoundError,
)
from backend.app.domain.models.delivery import Delivery
from backend.app.domain.models.enums import DeliveryMethod, OrderStatus, RouteType
from backend.app.domain.models.user import User, UserRole
from backend.app.infrastructure.repositories.delivery_repository import (
    DeliveryRepository,
)
from backend.app.infrastructure.repositories.order_repository import OrderRepository
from backend.app.infrastructure.repositories.restaurant_repository import RestaurantRepository

class DeliveryService:

    def __init__(
        self,
        delivery_repository: DeliveryRepository,
        order_repository: OrderRepository,
        restaurant_repository: Optional[RestaurantRepository] = None,
        notification_service=None,
    ) -> None:
        self._deliveries = delivery_repository
        self._orders = order_repository
        self._restaurants = restaurant_repository
        self._notifications = notification_service

    def assign_delivery(
        self,
        requesting_user: User,
        order_id: str,
        delivery_method: Optional[DeliveryMethod] = None,
        delivery_distance: Optional[float] = None,
        estimated_delivery_time: Optional[datetime] = None,
    ) -> Delivery:

        if requesting_user.role != UserRole.RESTAURANT_OWNER:
            raise AuthorizationError("Only restaurant owners can assign deliveries.")

        order = self._orders.get_by_id(order_id)
        if order is None:
            raise NotFoundError(f"Order '{order_id}' not found.")

        if self._restaurants is not None:
            restaurant = self._restaurants.get_by_id(order.restaurant_id)
            if restaurant is None or restaurant.owner_id != requesting_user.customer_id:
                raise AuthorizationError(
                    "You can only assign deliveries for your own restaurant's orders."
                )

        if order.status != OrderStatus.PENDING:
            raise BusinessRuleError(
                f"Order '{order_id}' is {order.status.value} and cannot be assigned a delivery."
            )

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
        saved = self._deliveries.save(delivery)

        self._orders.update_status(order_id, OrderStatus.OUT_FOR_DELIVERY)

        self._notify(
            order.customer_id,
            "order_out_for_delivery",
            f"Your order {order_id} is out for delivery!",
        )

        return saved

    def get_delivery(self, order_id: str) -> Delivery:
        delivery = self._deliveries.get_by_id(order_id)
        if delivery is None:
            raise NotFoundError(f"No delivery found for order '{order_id}'.")
        return delivery

    def list_deliveries(self, offset: int = 0, limit: int = 20) -> List[Delivery]:
        return self._deliveries.get_paginated(offset=offset, limit=limit)

    def update_delivery(self, requesting_user: User, order_id: str, updates: dict) -> Delivery:
        if requesting_user.role == UserRole.CUSTOMER:
            raise AuthorizationError("Customers cannot perform this action.")

        delivery = self.get_delivery(order_id)

        valid_fields = {k: v for k, v in updates.items() if v is not None}

        updated_delivery = delivery.model_copy(update=valid_fields)
        return self._deliveries.save(updated_delivery)

    def _notify(self, user_id: str, event_type: str, message: str) -> None:
        if self._notifications is not None:
            self._notifications.create(user_id, event_type, message)

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
    
    