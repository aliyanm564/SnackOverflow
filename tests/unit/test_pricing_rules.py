import pytest
from backend.app.domain.models.orders import Order
from backend.app.domain.rules.pricing_rules import (
    calculate_subtotal,
    calculate_delivery_fee,
    calculate_total
)


# --------------------------------
# Subtotal Tests
# --------------------------------

def test_calculate_subtotal_basic():
    order = Order(
        order_id="1",
        customer_id="cust1",
        restaurant_id="rest1",
        items=["burger", "fries"]
    )

    prices = {
        "burger": 10.0,
        "fries": 5.0
    }

    subtotal = calculate_subtotal(order, prices)

    assert subtotal == 15.0


def test_calculate_subtotal_missing_price():
    order = Order(
        order_id="2",
        customer_id="cust1",
        restaurant_id="rest1",
        items=["burger", "unknown_item"]
    )

    prices = {
        "burger": 10.0
    }

    subtotal = calculate_subtotal(order, prices)

    # unknown_item should default to 0
    assert subtotal == 10.0


# --------------------------------
# Delivery Fee Tests
# --------------------------------

def test_delivery_fee_with_no_order_value():
    order = Order(
        order_id="3",
        customer_id="cust1",
        restaurant_id="rest1",
        items=[]
    )

    fee = calculate_delivery_fee(order)

    assert fee == 5.0


def test_delivery_fee_with_distance():
    orders = Order(
    order_id="4",
    customer_id="cust1",
    restaurant_id="rest1",
    items=[]
    )

    orders.order_value = 20

    fee = calculate_delivery_fee(orders)

    # distance defaults to 0
    assert fee == 5.0



# --------------------------------
# Total Cost Tests
# --------------------------------

def test_calculate_total():
    order = Order(
        order_id="5",
        customer_id="cust1",
        restaurant_id="rest1",
        items=["pizza"]
    )

    prices = {"pizza": 20.0}

    order.order_value = 20

    total = calculate_total(order, prices)

    # subtotal = 20
    # delivery = 5
    # tax = 20 * 0.13 = 2.6
    expected_total = 20 + 5 + 2.6

    assert total == pytest.approx(expected_total)



import pytest
from backend.app.domain.models.orders import Order
from backend.app.domain.rules.pricing_rules import (
    calculate_subtotal,
    calculate_delivery_fee,
    calculate_total
)


# --------------------------------
# Subtotal Tests
# --------------------------------

def test_calculate_subtotal_basic():
    order = Order(
        order_id="1",
        customer_id="cust1",
        restaurant_id="rest1",
        items=["burger", "fries"]
    )

    prices = {
        "burger": 10.0,
        "fries": 5.0
    }

    subtotal = calculate_subtotal(order, prices)

    assert subtotal == 15.0


def test_calculate_subtotal_missing_price():
    order = Order(
        order_id="2",
        customer_id="cust1",
        restaurant_id="rest1",
        items=["burger", "unknown_item"]
    )

    prices = {
        "burger": 10.0
    }

    subtotal = calculate_subtotal(order, prices)

    # unknown_item should default to 0
    assert subtotal == 10.0


# --------------------------------
# Delivery Fee Tests
# --------------------------------

def test_delivery_fee_with_no_order_value():
    order = Order(
        order_id="3",
        customer_id="cust1",
        restaurant_id="rest1",
        items=[]
    )

    fee = calculate_delivery_fee(order)

    assert fee == 5.0


def test_delivery_fee_with_distance():
    orders = Order(
    order_id="4",
    customer_id="cust1",
    restaurant_id="rest1",
    items=[]
    )

    orders.order_value = 20

    fee = calculate_delivery_fee(orders)

    # distance defaults to 0
    assert fee == 5.0



# --------------------------------
# Total Cost Tests
# --------------------------------

def test_calculate_total():
    order = Order(
        order_id="5",
        customer_id="cust1",
        restaurant_id="rest1",
        items=["pizza"]
    )

    prices = {"pizza": 20.0}

    order.order_value = 20

    total = calculate_total(order, prices)

    # subtotal = 20
    # delivery = 5
    # tax = 20 * 0.13 = 2.6
    expected_total = 20 + 5 + 2.6

    assert total == pytest.approx(expected_total)


