import uuid
from datetime import datetime, timezone
from typing import List, Optional

from backend.app.application.exceptions import (
    AuthorizationError,
    BusinessRuleError,
    NotFoundError,
)
from backend.app.domain.models.enums import OrderStatus
from backend.app.domain.models.menu_item import MenuItem
from backend.app.domain.models.orders import Order
from backend.app.domain.models.user import User, UserRole
from backend.app.domain.rules.orders_rules import can_modify_order, mark_order_completed
from backend.app.infrastructure.repositories.menu_repository import MenuRepository
from backend.app.infrastructure.repositories.order_repository import OrderRepository
from backend.app.infrastructure.repositories.restaurant_repository import (
    RestaurantRepository,
)


class OrderService:

    def __init__(
        self,
        order_repository: OrderRepository,
        menu_repository: MenuRepository,
        restaurant_repository: RestaurantRepository,
        notification_service=None,
    ) -> None:
        self._orders = order_repository
        self._menu = menu_repository
        self._restaurants = restaurant_repository
        self._notifications = notification_service

    def place_order(
        self,
        requesting_user: User,
        restaurant_id: str,
        food_item_ids: List[str],
    ) -> Order:

        if requesting_user.role != UserRole.CUSTOMER:
            raise AuthorizationError("Only customers can place orders.")

        if self._restaurants.get_by_id(restaurant_id) is None:
            raise NotFoundError(f"Restaurant '{restaurant_id}' not found.")

        if not food_item_ids:
            raise BusinessRuleError("An order must contain at least one item.")

        items = self._get_restaurant_items(food_item_ids, restaurant_id)
        order_value = self._calculate_order_value(items)

        order = Order(
            order_id=str(uuid.uuid4()),
            customer_id=requesting_user.customer_id,
            restaurant_id=restaurant_id,
            items=food_item_ids,
            order_time=datetime.now(tz=timezone.utc),
            order_value=order_value,
            status=OrderStatus.PENDING,
        )
        saved = self._orders.save(order)
        self._notify(
            requesting_user.customer_id,
            "order_created",
            f"Your order {saved.order_id} has been placed.",
        )
        return saved

    def get_order(self, order_id: str) -> Order:
        return self._get_order_or_raise(order_id)

    def get_orders_for_customer(self, customer_id: str) -> List[Order]:
        return self._orders.get_by_customer(customer_id)

    def get_orders_for_restaurant(
        self, requesting_user: User, restaurant_id: str
    ) -> List[Order]:
        if requesting_user.role == UserRole.CUSTOMER:
            raise AuthorizationError("Customers cannot view restaurant order lists.")
        return self._orders.get_by_restaurant(restaurant_id)

    def get_orders_by_status(
        self, requesting_user: User, status: OrderStatus
    ) -> List[Order]:
        if requesting_user.role == UserRole.CUSTOMER:
            return self._orders.get_by_customer_and_status(
                requesting_user.customer_id, status
            )
        return self._orders.get_by_status(status)

    def get_paginated_orders(
        self,
        customer_id: Optional[str] = None,
        restaurant_id: Optional[str] = None,
        offset: int = 0,
        limit: int = 20,
    ) -> List[Order]:
        return self._orders.get_paginated(
            customer_id=customer_id,
            restaurant_id=restaurant_id,
            offset=offset,
            limit=limit,
        )

    def reorder(
        self,
        requesting_user: User,
        original_order_id: str,
        food_item_ids: Optional[List[str]] = None,
    ) -> Order:
        if requesting_user.role != UserRole.CUSTOMER:
            raise AuthorizationError("Only customers can reorder.")

        original = self._get_order_or_raise(original_order_id)

        if original.customer_id != requesting_user.customer_id:
            raise AuthorizationError("You can only reorder from your own past orders.")

        if original.status != OrderStatus.COMPLETED:
            raise BusinessRuleError(
                f"Order '{original_order_id}' cannot be reordered because it is {original.status.value}."
            )

        items_to_use = food_item_ids if food_item_ids is not None else original.items

        if not items_to_use:
            raise BusinessRuleError("An order must contain at least one item.")

        return self.place_order(requesting_user, original.restaurant_id, items_to_use)

    def cancel_order(self, requesting_user: User, order_id: str) -> Order:
        order = self._get_order_or_raise(order_id)

        if order.customer_id != requesting_user.customer_id:
            raise AuthorizationError("You can only cancel your own orders.")

        if not can_modify_order(order):
            raise BusinessRuleError(
                f"Order '{order_id}' cannot be cancelled because it is {order.status.value}."
            )

        updated = self._orders.update_status(order_id, OrderStatus.CANCELLED)
        self._notify(
            requesting_user.customer_id,
            "order_cancelled",
            f"Your order {order_id} has been cancelled.",
        )
        return updated

    def complete_order(self, order_id: str) -> Order:
        order = self._get_order_or_raise(order_id)

        if not can_modify_order(order):
            raise BusinessRuleError(
                f"Order '{order_id}' is already {order.status.value} and cannot be completed."
            )

        # Update the in-memory domain object and persist via the repository's
        # save method so both unit tests (with mocks) and integration tests
        # (with a real session) observe the completed status.
        mark_order_completed(order)
        saved = self._orders.save(order)
        self._notify(
            order.customer_id,
            "order_completed",
            f"Your order {order_id} has been completed.",
        )
        return saved

    def _get_order_or_raise(self, order_id: str) -> Order:
        order = self._orders.get_by_id(order_id)
        if order is None:
            raise NotFoundError(f"Order '{order_id}' not found.")
        return order

    def _get_restaurant_items(
        self, food_item_ids: List[str], restaurant_id: str
    ) -> List[MenuItem]:
        items: List[MenuItem] = []
        for item_id in food_item_ids:
            item = self._menu.get_by_id(item_id)
            if item is None:
                raise NotFoundError(f"Menu item '{item_id}' not found.")
            if item.restaurant_id != restaurant_id:
                raise BusinessRuleError(
                    f"Item '{item_id}' does not belong to restaurant '{restaurant_id}'."
                )
            items.append(item)
        return items

    def _calculate_order_value(self, items: List[MenuItem]) -> float:
        total = 0.0
        for item in items:
            if item.price is not None:
                total += item.price
        return round(total, 2)

    def _notify(self, user_id: str, event_type: str, message: str) -> None:
        if self._notifications is not None:
            self._notifications.create(user_id, event_type, message)
