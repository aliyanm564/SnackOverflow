import pytest
from datetime import datetime

from backend.app.domain.models.enums import OrderStatus
from backend.app.domain.models.orders import Order


def test_create_order_with_required_fields():
    order = Order(
        order_id="o1",
        customer_id="c1",
        restaurant_id="r1",
        items=["food_1", "food_2"]
    )

    assert order.order_id == "o1"
    assert order.customer_id == "c1"
    assert order.restaurant_id == "r1"
    assert order.items == ["food_1", "food_2"]
    assert order.status == OrderStatus.PENDING
    assert order.order_time is None
    assert order.order_value is None
    assert order.customer_rating is None
    assert order.customer_satisfaction is None


def test_order_with_all_fields():
    now = datetime.now()
    order = Order(
        order_id="o2",
        customer_id="c2",
        restaurant_id="r2",
        items=["food_3"],
        order_time=now,
        order_value=24.75,
        status=OrderStatus.COMPLETED,
        customer_rating=4.5,
        customer_satisfaction=5
    )

    assert order.order_time == now
    assert order.order_value == 24.75
    assert order.status == OrderStatus.COMPLETED
    assert order.customer_rating == 4.5
    assert order.customer_satisfaction == 5


def test_order_status_from_string():
    order = Order(
        order_id="o3",
        customer_id="c3",
        restaurant_id="r3",
        items=["food_4"],
        status="cancelled"
    )

    assert order.status == OrderStatus.CANCELLED


def test_invalid_order_status_raises_error():
    with pytest.raises(ValueError):
        Order(
            order_id="o4",
            customer_id="c4",
            restaurant_id="r4",
            items=["food_5"],
            status="invalid_status"
        )


def test_order_requires_at_least_one_item():
    with pytest.raises(ValueError):
        Order(
            order_id="o5",
            customer_id="c5",
            restaurant_id="r5",
            items=[],
        )


def test_order_rejects_blank_item_ids():
    with pytest.raises(ValueError):
        Order(
            order_id="o6",
            customer_id="c6",
            restaurant_id="r6",
            items=["food_1", "   "],
        )


def test_order_rejects_negative_order_value():
    with pytest.raises(ValueError):
        Order(
            order_id="o7",
            customer_id="c7",
            restaurant_id="r7",
            items=["food_1"],
            order_value=-1.0,
        )


def test_order_rejects_rating_out_of_range():
    with pytest.raises(ValueError):
        Order(
            order_id="o8",
            customer_id="c8",
            restaurant_id="r8",
            items=["food_1"],
            customer_rating=5.5,
        )


def test_order_rejects_satisfaction_out_of_range():
    with pytest.raises(ValueError):
        Order(
            order_id="o9",
            customer_id="c9",
            restaurant_id="r9",
            items=["food_1"],
            customer_satisfaction=0,
        )


def test_pending_order_can_be_cancelled_and_completed():
    order = Order(
        order_id="o10",
        customer_id="c10",
        restaurant_id="r10",
        items=["food_1"],
    )

    assert order.can_be_cancelled() is True
    assert order.can_be_completed() is True


def test_non_pending_order_cannot_be_cancelled_or_completed():
    order = Order(
        order_id="o11",
        customer_id="c11",
        restaurant_id="r11",
        items=["food_1"],
        status=OrderStatus.COMPLETED,
    )

    assert order.can_be_cancelled() is False
    assert order.can_be_completed() is False
