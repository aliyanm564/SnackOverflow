import pytest
from datetime import datetime
from backend.app.domain.models.delivery import Delivery
from backend.app.domain.models.enums import DeliveryMethod, RouteType


def test_create_delivery_with_required_field():
    delivery = Delivery(order_id="order123")

    assert delivery.order_id == "order123"
    assert delivery.delivery_time is None
    assert delivery.delivery_distance is None
    assert delivery.delivery_method is None


def test_delivery_with_all_fields():
    now = datetime.now()

    delivery = Delivery(
        order_id="order456",
        delivery_time=now,
        delivery_time_actual=now,
        delivery_delay=5.0,
        delivery_distance=10.5,
        delivery_method=DeliveryMethod.BIKE,
        route_taken="Main St",
        route_type=RouteType.ROUTE_2,
        route_efficiency=0.9,
        traffic_condition="Moderate",
        weather_condition="Clear",
        predicted_delivery_mode="bike",
        traffic_avoidance=True
    )

    assert delivery.delivery_method == DeliveryMethod.BIKE
    assert delivery.route_type == RouteType.ROUTE_2
    assert delivery.delivery_distance == 10.5
    assert delivery.traffic_avoidance is True


def test_delivery_method_from_string():
    delivery = Delivery(order_id="1", delivery_method="car")

    assert delivery.delivery_method == DeliveryMethod.CAR


def test_route_type_from_string():
    delivery = Delivery(order_id="2", route_type="route_3")

    assert delivery.route_type == RouteType.ROUTE_3


def test_invalid_delivery_method():
    with pytest.raises(ValueError):
        Delivery(order_id="3", delivery_method="plane")


def test_invalid_route_type():
    with pytest.raises(ValueError):
        Delivery(order_id="4", route_type="route_99")
