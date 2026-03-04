import pytest
from backend.app.domain.models.enums import OrderStatus, DeliveryMethod, RouteType


# -----------------------------
# OrderStatus Tests
# -----------------------------

def test_order_status_values():
    assert OrderStatus.PENDING.value == "pending"
    assert OrderStatus.COMPLETED.value == "completed"
    assert OrderStatus.CANCELLED.value == "cancelled"


def test_order_status_from_string():
    status = OrderStatus("pending")
    assert status == OrderStatus.PENDING


def test_invalid_order_status():
    with pytest.raises(ValueError):
        OrderStatus("invalid_status")


# -----------------------------
# DeliveryMethod Tests
# -----------------------------

def test_delivery_method_values():
    assert DeliveryMethod.WALK.value == "walk"
    assert DeliveryMethod.BIKE.value == "bike"
    assert DeliveryMethod.CAR.value == "car"
    assert DeliveryMethod.MIXED.value == "mixed"


def test_delivery_method_from_string():
    method = DeliveryMethod("bike")
    assert method == DeliveryMethod.BIKE


def test_invalid_delivery_method():
    with pytest.raises(ValueError):
        DeliveryMethod("plane")


# -----------------------------
# RouteType Tests
# -----------------------------

def test_route_type_values():
    assert RouteType.ROUTE_1.value == "route_1"
    assert RouteType.ROUTE_2.value == "route_2"
    assert RouteType.ROUTE_3.value == "route_3"
    assert RouteType.ROUTE_4.value == "route_4"
    assert RouteType.ROUTE_5.value == "route_5"


def test_route_type_from_string():
    route = RouteType("route_3")
    assert route == RouteType.ROUTE_3


def test_invalid_route_type():
    with pytest.raises(ValueError):
        RouteType("route_99")
