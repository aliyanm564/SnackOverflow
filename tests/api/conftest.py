import pytest
from contextlib import contextmanager
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.presentation.dependencies import (
    get_auth_service,
    get_user_service,
    get_restaurant_service,
    get_menu_service,
    get_order_service,
    get_delivery_service,
    get_pricing_service,
    get_payment_service,
    get_notification_service,
    get_current_user,
)
from backend.app.domain.models.user import User, UserRole
from backend.app.domain.models.restaurant import Restaurant
from backend.app.domain.models.menu_item import MenuItem
from backend.app.domain.models.orders import Order
from backend.app.domain.models.delivery import Delivery
from backend.app.domain.models.enums import OrderStatus, DeliveryMethod


@pytest.fixture(scope="module")
def client():
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


@pytest.fixture
def customer():
    return User(
        customer_id="api-cust-001",
        name="Alice",
        loyalty_program=False,
        role=UserRole.CUSTOMER,
    )


@pytest.fixture
def owner():
    return User(
        customer_id="api-owner-001",
        name="Carlo",
        role=UserRole.RESTAURANT_OWNER,
    )


@pytest.fixture
def delivery_person():
    return User(
        customer_id="api-driver-001",
        name="Dana",
        role=UserRole.DELIVERY_PERSON,
    )


def make_auth_headers(user: User) -> dict:
    from backend.app.application.services.auth_service import AuthService
    from unittest.mock import MagicMock
    fake_repo = MagicMock()
    svc = AuthService(user_repository=fake_repo)
    token = svc._create_token(user.customer_id, user.role)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def customer_headers(customer):
    return make_auth_headers(customer)


@pytest.fixture
def owner_headers(owner):
    return make_auth_headers(owner)


@pytest.fixture
def driver_headers(delivery_person):
    return make_auth_headers(delivery_person)


@pytest.fixture
def override(client):
    @contextmanager
    def _override(service_dep, mock_service, current_user: User = None):
        overrides = {service_dep: lambda: mock_service}
        if current_user is not None:
            overrides[get_current_user] = lambda: current_user
        app.dependency_overrides.update(overrides)
        try:
            yield
        finally:
            for key in overrides:
                app.dependency_overrides.pop(key, None)

    return _override


@pytest.fixture
def sample_restaurant(owner):
    return Restaurant(
        restaurant_id="rest-api-001",
        owner_id=owner.customer_id,
        name="API Bistro",
        location="City_1",
        description="Test restaurant",
    )


@pytest.fixture
def sample_menu_item(sample_restaurant):
    return MenuItem(
        food_item_id="item-api-001",
        restaurant_id=sample_restaurant.restaurant_id,
        name="Burger",
        category="American",
        price=12.99,
    )


@pytest.fixture
def sample_order(customer, sample_restaurant, sample_menu_item):
    from datetime import datetime, timezone
    return Order(
        order_id="order-api-001",
        customer_id=customer.customer_id,
        restaurant_id=sample_restaurant.restaurant_id,
        items=[sample_menu_item.food_item_id],
        order_time=datetime.now(tz=timezone.utc),
        order_value=12.99,
        status=OrderStatus.PENDING,
    )


@pytest.fixture
def completed_order(sample_order):
    return sample_order.model_copy(update={"status": OrderStatus.COMPLETED})


@pytest.fixture
def sample_delivery(sample_order):
    return Delivery(
        order_id=sample_order.order_id,
        delivery_method=DeliveryMethod.BIKE,
        delivery_distance=3.5,
    )
