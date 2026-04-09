import uuid
from datetime import time
from typing import List, Optional

from backend.app.application.exceptions import AuthorizationError, NotFoundError
from backend.app.domain.models.menu_item import MenuItem
from backend.app.domain.models.user import User, UserRole
from backend.app.infrastructure.repositories.menu_repository import MenuRepository
from backend.app.infrastructure.repositories.restaurant_repository import (
    RestaurantRepository,
)

_UNSET = object()


class MenuService:

    def __init__(
        self,
        menu_repository: MenuRepository,
        restaurant_repository: RestaurantRepository,
    ) -> None:
        self._menu = menu_repository
        self._restaurants = restaurant_repository

    def add_item(
        self,
        requesting_user: User,
        restaurant_id: str,
        name: str,
        category: Optional[str] = None,
        price: Optional[float] = None,
        available_from: Optional[time] = None,
        available_until: Optional[time] = None,
    ) -> MenuItem:
        restaurant = self._restaurants.get_by_id(restaurant_id)
        if restaurant is None:
            raise NotFoundError(f"Restaurant '{restaurant_id}' not found.")

        if requesting_user.role != UserRole.RESTAURANT_OWNER:
            raise AuthorizationError("Only restaurant owners can manage menu items.")

        if restaurant.owner_id != requesting_user.customer_id:
            raise AuthorizationError(
                f"User '{requesting_user.customer_id}' does not own restaurant '{restaurant_id}'."
            )

        if price is not None and price < 0:
            raise ValueError("Item price cannot be negative.")

        item = MenuItem(
            food_item_id=str(uuid.uuid4()),
            restaurant_id=restaurant_id,
            name=name,
            category=category,
            price=price,
            available_from=available_from,
            available_until=available_until,
        )
        return self._menu.save(item)

    def get_item(self, food_item_id: str) -> MenuItem:
        item = self._menu.get_by_id(food_item_id)
        if item is None:
            raise NotFoundError(f"Menu item '{food_item_id}' not found.")
        return item

    def get_menu_for_restaurant(self, restaurant_id: str) -> List[MenuItem]:
        if self._restaurants.get_by_id(restaurant_id) is None:
            raise NotFoundError(f"Restaurant '{restaurant_id}' not found.")
        return self._menu.get_by_restaurant(restaurant_id)

    def search_items(self, query: str) -> List[MenuItem]:
        return self._menu.search_by_name(query)

    def filter_by_category(self, category: str) -> List[MenuItem]:
        return self._menu.get_by_category(category)

    def filter_by_price_range(self, min_price: float, max_price: float) -> List[MenuItem]:
        if min_price > max_price:
            raise ValueError("min_price cannot exceed max_price.")
        return self._menu.get_by_price_range(min_price, max_price)

    def list_items_paginated(
        self,
        restaurant_id: Optional[str] = None,
        offset: int = 0,
        limit: int = 20,
    ) -> List[MenuItem]:
        return self._menu.get_paginated(restaurant_id=restaurant_id, offset=offset, limit=limit)

    def update_item(
        self,
        requesting_user: User,
        food_item_id: str,
        name: Optional[str] = None,
        category: Optional[str] = None,
        price: Optional[float] = None,
        available_from=_UNSET,
        available_until=_UNSET,
    ) -> MenuItem:
        item = self.get_item(food_item_id)
        self._assert_item_owner(requesting_user, item)

        if price is not None and price < 0:
            raise ValueError("Item price cannot be negative.")

        changes = {}
        if name is not None:
            changes["name"] = name
        if category is not None:
            changes["category"] = category
        if price is not None:
            changes["price"] = price
        if available_from is not _UNSET:
            changes["available_from"] = available_from
        if available_until is not _UNSET:
            changes["available_until"] = available_until

        if changes:
            item = item.model_copy(update=changes)
        return self._menu.save(item)

    def delete_item(self, requesting_user: User, food_item_id: str) -> None:
        item = self.get_item(food_item_id)
        self._assert_item_owner(requesting_user, item)
        self._menu.delete(food_item_id)

    def _assert_item_owner(self, user: User, item: MenuItem) -> None:
        restaurant = self._restaurants.get_by_id(item.restaurant_id)
        if restaurant is None or restaurant.owner_id != user.customer_id:
            raise AuthorizationError(
                f"User '{user.customer_id}' does not own the restaurant for item '{item.food_item_id}'."
            )
