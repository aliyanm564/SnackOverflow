from backend.app.domain.models.enums import OrderStatus
from backend.app.domain.models.orders import Order


def can_modify_order(order: Order) -> bool:
    """Orders can only be modified if pending."""
    return order.status == OrderStatus.PENDING


def mark_order_completed(order: Order) -> None:
    """Mark an order as completed."""
    order.status = OrderStatus.COMPLETED
