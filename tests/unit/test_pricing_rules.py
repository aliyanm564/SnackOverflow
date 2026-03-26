import pytest

from backend.app.domain.models.orders import Order
from backend.app.domain.rules.pricing_rules import (
    calculate_delivery_fee,
    calculate_subtotal,
    calculate_total,
)


def test_calculate_subtotal_basic():
    order = Order(
        order_id="1",
        customer_id="cust1",
        restaurant_id="rest1",
        items=["burger", "fries"],
    )

    prices = {
        "burger": 10.0,
        "fries": 5.0,
    }

    subtotal = calculate_subtotal(order, prices)

    assert subtotal == 15.0


def test_calculate_subtotal_missing_price():
    order = Order(
        order_id="2",
        customer_id="cust1",
        restaurant_id="rest1",
        items=["burger", "unknown_item"],
    )

    prices = {
        "burger": 10.0,
    }

    subtotal = calculate_subtotal(order, prices)

    assert subtotal == 10.0


def test_delivery_fee_with_no_order_value():
    order = Order(
        order_id="3",
        customer_id="cust1",
        restaurant_id="rest1",
        items=["placeholder-item"],
    )

    fee = calculate_delivery_fee(order)

    assert fee == 5.0


def test_delivery_fee_with_distance():
    order = Order(
        order_id="4",
        customer_id="cust1",
        restaurant_id="rest1",
        items=["placeholder-item"],
    )

    order.order_value = 20

    fee = calculate_delivery_fee(order)

    assert fee == 5.0


def test_calculate_total():
    order = Order(
        order_id="5",
        customer_id="cust1",
        restaurant_id="rest1",
        items=["pizza"],
    )

    prices = {"pizza": 20.0}

    order.order_value = 20

    total = calculate_total(order, prices)

    expected_total = 20 + 5 + 2.6

    assert total == pytest.approx(expected_total)
