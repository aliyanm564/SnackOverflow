import pytest

from backend.app.application.services.pricing_service import PricingService
from backend.app.domain.models.user import User
from backend.app.domain.models.orders import Order
from backend.app.domain.models.enums import OrderStatus


class FakeMenuItem:
    def __init__(self, food_item_id, price):
        self.food_item_id = food_item_id
        self.restaurant_id = "rest1"
        self.name = food_item_id
        self.category = "test"
        self.price = price


class FakeMenuRepository:
    def __init__(self):   
        self.items = {
            "burger": FakeMenuItem("burger", 10.0),
            "fries": FakeMenuItem("fries", 5.0),
        }

    def get_by_id(self, entity_id):
        return self.items.get(entity_id)


class FakeOrderRepository:
    def __init__(self, order):
        self.order = order

    def get_by_id(self, order_id):
        if order_id == self.order.order_id:
            return self.order
        return None


@pytest.fixture
def customer():
    return User(
        customer_id="cust1",
        loyalty_program=True,
    )


@pytest.fixture
def order():
    return Order(
        order_id="order1",
        customer_id="cust1",
        restaurant_id="rest1",
        items=["burger", "fries"],
        order_value=None,
        status=OrderStatus.PENDING,
    )


@pytest.fixture
def pricing_service(order):
    menu_repo = FakeMenuRepository()
    order_repo = FakeOrderRepository(order)

    return PricingService(
        order_repository=order_repo,
        menu_repository=menu_repo,
    )


def test_get_price_breakdown(pricing_service, customer):
    breakdown = pricing_service.get_price_breakdown("order1", customer)

    assert breakdown.subtotal == 15.0
    assert breakdown.taxes == round(15.0 * 0.13, 2)
    assert breakdown.loyalty_discount == round(15.0 * 0.05, 2)
    assert breakdown.grand_total > 0


def test_quote_order(pricing_service, customer):
    breakdown = pricing_service.quote_order(
        food_item_ids=["burger", "fries"],
        customer=customer,
        delivery_distance=3.0,
    )

    assert breakdown.subtotal == 15.0
    assert breakdown.taxes == round(15.0 * 0.13, 2)
    assert breakdown.loyalty_discount == round(15.0 * 0.05, 2)
    assert breakdown.grand_total > 0