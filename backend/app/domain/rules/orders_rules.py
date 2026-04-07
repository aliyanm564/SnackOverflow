from datetime import datetime
from typing import List
from backend.app.infrastructure.orm_models import MenuItemORM

from backend.app.domain.models.enums import OrderStatus
from backend.app.domain.models.orders import Order


def can_modify_order(order: Order) -> bool:
    """Orders can only be modified if pending."""
    return order.status == OrderStatus.PENDING


def mark_order_completed(order: Order) -> None:
    """Mark an order as completed."""
    order.status = OrderStatus.COMPLETED


def is_menu_item_available(menu_item: MenuItemORM) -> bool:
    now = datetime.now().time()

    start = menu_item.available_from
    end = menu_item.available_until

    if not start and not end:
        return True
    
    if start <= end:
        return start <= now <= end
    else:
        return now >= start or now <= end

def validate_order_items(order: Order, menu_items: List[MenuItemORM]) -> None:
    """Validate that all items in the order are available."""
    for item_id in order.items:
        item = next((i for i in menu_items if i.food_item_id == item_id), None)
        if item is None:
            raise ValueError(f"Menu item '{item_id}' not found.")
        if not is_menu_item_available(item):
            raise ValueError(f"Menu item '{item.name}' is not currently available.")