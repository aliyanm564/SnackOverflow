from backend.app.domain.models.enums import OrderStatus
from backend.app.domain.models.orders import Order
from backend.app.domain.rules.orders_rules import can_modify_order, mark_order_completed


def test_can_modify_order_returns_true_for_pending_order():
    order = Order(
        order_id="o1",
        customer_id="c1",
        restaurant_id="r1",
        items=["item_1"],
        status=OrderStatus.PENDING,
    )

    assert can_modify_order(order) is True


def test_can_modify_order_returns_false_for_non_pending_order():
    order = Order(
        order_id="o2",
        customer_id="c2",
        restaurant_id="r2",
        items=["item_2"],
        status=OrderStatus.COMPLETED,
    )

    assert can_modify_order(order) is False


def test_mark_order_completed_updates_order_status():
    order = Order(
        order_id="o3",
        customer_id="c3",
        restaurant_id="r3",
        items=["item_3"],
        status=OrderStatus.PENDING,
    )

    mark_order_completed(order)

    assert order.status == OrderStatus.COMPLETED
