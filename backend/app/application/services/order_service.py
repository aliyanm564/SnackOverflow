"""
order_service.py
----------------
Coordinates order lifecycle use-cases.

Responsibilities
----------------
* Place a new order (validates items belong to the restaurant).
* Retrieve orders by customer, restaurant, or status.
* Cancel an order (only if PENDING — enforced by domain rule can_modify_order).
* Mark an order complete (called internally after payment succeeds).
* Emit a notification after every status transition (via NotificationService).

Domain rules used
-----------------
  order_rules.can_modify_order  → guards cancel / item-update
  order_rules.mark_order_completed → transitions status to COMPLETED
"""

import uuid
from datetime import datetime, timezone
from typing import List, Optional

from backend.app.application.exceptions import (
    AuthorizationError,
    BusinessRuleError,
    NotFoundError,
)
from backend.app.domain.models.enums import OrderStatus
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
        # NotificationService is injected lazily to avoid circular imports;
        # see _notify() for usage.
        notification_service=None,
    ) -> None:
        self._orders = order_repository
        self._menu = menu_repository
        self._restaurants = restaurant_repository
        self._notifications = notification_service

    # ------------------------------------------------------------------
    # Place order
    # ------------------------------------------------------------------

    def place_order(
        self,
        requesting_user: User,
        restaurant_id: str,
        food_item_ids: List[str],
    ) -> Order:
        """
        Create and persist a new PENDING order.

        Validation performed:
        * The restaurant must exist.
        * Every item in food_item_ids must exist and belong to that restaurant.
        * Only customers may place orders.
        """
        if requesting_user.role != UserRole.CUSTOMER:
            raise AuthorizationError("Only customers can place orders.")

        if self._restaurants.get_by_id(restaurant_id) is None:
            raise NotFoundError(f"Restaurant '{restaurant_id}' not found.")

        if not food_item_ids:
            raise BusinessRuleError("An order must contain at least one item.")

        self._validate_items_belong_to_restaurant(food_item_ids, restaurant_id)

        order_value = self._calculate_order_value(food_item_ids)

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

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    def get_order(self, order_id: str) -> Order:
        order = self._orders.get_by_id(order_id)
        if order is None:
            raise NotFoundError(f"Order '{order_id}' not found.")
        return order

    def get_orders_for_customer(self, customer_id: str) -> List[Order]:
        return self._orders.get_by_customer(customer_id)

    def get_orders_for_restaurant(
        self, requesting_user: User, restaurant_id: str
    ) -> List[Order]:
        """Restaurant owners can see their restaurant's orders."""
        if requesting_user.role == UserRole.CUSTOMER:
            raise AuthorizationError("Customers cannot view restaurant order lists.")
        return self._orders.get_by_restaurant(restaurant_id)

    def get_orders_by_status(
        self, requesting_user: User, status: OrderStatus
    ) -> List[Order]:
        """
        Return all orders in a given status.
        Customers see only their own; owners see all for their restaurant
        (filtering is done at the router level using the customer/restaurant
        scoped methods above — this method is for admin-style views).
        """
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

    # ------------------------------------------------------------------
    # Cancellation
    # ------------------------------------------------------------------

    def cancel_order(self, requesting_user: User, order_id: str) -> Order:
        """
        Cancel a PENDING order.

        Rules:
        * The order must belong to the requesting customer.
        * can_modify_order (domain rule) must return True (order is PENDING).
        """
        order = self.get_order(order_id)

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

    # ------------------------------------------------------------------
    # Complete order (called by PaymentService after payment success)
    # ------------------------------------------------------------------

    def complete_order(self, order_id: str) -> Order:
        """
        Transition an order from PENDING → COMPLETED.

        Uses the domain rule mark_order_completed which mutates the model,
        then persists the updated status via the repository.

        This method is intentionally package-internal; it is only called
        by PaymentService, not directly by routers.
        """
        order = self.get_order(order_id)

        if not can_modify_order(order):
            raise BusinessRuleError(
                f"Order '{order_id}' is already {order.status.value} and cannot be completed."
            )

        # Apply the domain rule mutation, then persist.
        mark_order_completed(order)
        saved = self._orders.save(order)
        self._notify(
            order.customer_id,
            "order_completed",
            f"Your order {order_id} has been completed.",
        )
        return saved

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _validate_items_belong_to_restaurant(
        self, food_item_ids: List[str], restaurant_id: str
    ) -> None:
        """
        Raise BusinessRuleError if any item does not exist or belongs to
        a different restaurant.
        """
        for item_id in food_item_ids:
            item = self._menu.get_by_id(item_id)
            if item is None:
                raise NotFoundError(f"Menu item '{item_id}' not found.")
            if item.restaurant_id != restaurant_id:
                raise BusinessRuleError(
                    f"Item '{item_id}' does not belong to restaurant '{restaurant_id}'."
                )

    def _calculate_order_value(self, food_item_ids: List[str]) -> float:
        """Sum the prices of all items in the order."""
        total = 0.0
        for item_id in food_item_ids:
            item = self._menu.get_by_id(item_id)
            if item and item.price is not None:
                total += item.price
        return round(total, 2)

    def _notify(self, user_id: str, event_type: str, message: str) -> None:
        """Fire a notification if the notification service is wired in."""
        if self._notifications is not None:
            self._notifications.create(user_id, event_type, message)
