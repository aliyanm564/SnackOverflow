import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.app.presentation.routers.payment_router import router
from backend.app.presentation.dependencies import get_current_user, get_payment_service
from backend.app.application.exceptions import (
    AuthorizationError,
    BusinessRuleError,
    NotFoundError,
    PaymentError,
)


class MockUser:
    def __init__(self, user_id="user-1"):
        self.id = user_id


class MockPaymentResult:
    def __init__(self, order_id, amount_charged, status, message):
        self.order_id = order_id
        self.amount_charged = amount_charged
        self.status = status
        self.message = message


class MockPaymentService:
    def __init__(self, behavior="success"):
        self.behavior = behavior

    def process_payment(self, order_id, user, promo_discount=0):
        if self.behavior == "not_found":
            raise NotFoundError("Order not found")
        if self.behavior == "unauthorized":
            raise AuthorizationError("Forbidden")
        if self.behavior == "invalid_state":
            raise BusinessRuleError("Invalid order state")
        if self.behavior == "payment_fail":
            raise PaymentError("Payment declined")

        return MockPaymentResult(
            order_id=order_id,
            amount_charged=25.0,
            status="approved",
            message="Payment successful",
        )


@pytest.fixture
def app():
    app = FastAPI()
    app.include_router(router)
    return app


def override_user():
    return MockUser()


def override_service(behavior):
    def _override():
        return MockPaymentService(behavior)
    return _override


def test_process_payment_success(app):
    app.dependency_overrides[get_current_user] = override_user
    app.dependency_overrides[get_payment_service] = override_service("success")

    client = TestClient(app)
    response = client.post("/payments/order-123")

    assert response.status_code == 200
    data = response.json()
    assert data["order_id"] == "order-123"
    assert data["status"] == "approved"


def test_process_payment_not_found(app):
    app.dependency_overrides[get_current_user] = override_user
    app.dependency_overrides[get_payment_service] = override_service("not_found")

    client = TestClient(app)
    response = client.post("/payments/order-123")

    assert response.status_code == 404


def test_process_payment_unauthorized(app):
    app.dependency_overrides[get_current_user] = override_user
    app.dependency_overrides[get_payment_service] = override_service("unauthorized")

    client = TestClient(app)
    response = client.post("/payments/order-123")

    assert response.status_code == 403


def test_process_payment_invalid_state(app):
    app.dependency_overrides[get_current_user] = override_user
    app.dependency_overrides[get_payment_service] = override_service("invalid_state")

    client = TestClient(app)
    response = client.post("/payments/order-123")

    assert response.status_code == 422


def test_process_payment_declined(app):
    app.dependency_overrides[get_current_user] = override_user
    app.dependency_overrides[get_payment_service] = override_service("payment_fail")

    client = TestClient(app)
    response = client.post("/payments/order-123")

    assert response.status_code == 402