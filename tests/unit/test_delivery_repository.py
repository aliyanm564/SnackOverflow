from backend.app.domain.models.delivery import Delivery
from backend.app.domain.models.enums import DeliveryMethod, RouteType
from backend.app.infrastructure.repositories.delivery_repository import DeliveryRepository

def test_save_and_get_by_id(db_session):
    repository = DeliveryRepository(db_session)
    delivery = Delivery(
        order_id = "order_1",
        delivery_distance =5.5,
        delivery_method = DeliveryMethod.CAR, 
        traffic_condition="Low"
    )
    saved = repository.save(delivery)
    fetched = repository.get_by_id("order_1")

    assert saved.order_id == "order_1"
    assert fetched is not None
    assert fetched.delivery_distance == 5.5

def test_get_all_returns_all_deliveries(db_session):
    repository = DeliveryRepository(db_session)
    repository.save(Delivery(order_id="order_1", delivery_distance=3.0))
    repository.save(Delivery(order_id="order_2", delivery_distance=7.0))

    deliveries = repository.get_all()
    order_ids = {d.order_id for d in deliveries}

    assert len(deliveries) >= 2
    assert "order_1" in order_ids
    assert "order_2" in order_ids

def test_delete_existing_delivery(db_session):
    repository = DeliveryRepository(db_session)
    repository.save(Delivery(order_id="order_1", delivery_distance=5.0))

    deleted = repository.delete("order_1")
    fetched = repository.get_by_id("order_1")

    assert deleted is True
    assert fetched is None

def test_delete_missing_delivery_returns_false(db_session):
    repository = DeliveryRepository(db_session)

    deleted = repository.delete("missing_order")

    assert deleted is False

def test_get_by_traffic_condition(db_session):
    repository = DeliveryRepository(db_session)
    repository.save(Delivery(order_id="order_1", traffic_condition="High"))
    repository.save(Delivery(order_id="order_2", traffic_condition="Low"))
    repository.save(Delivery(order_id="order_3", traffic_condition="High"))

    high_traffic_deliveries = repository.get_by_traffic_condition("High")

    assert {d.order_id for d in high_traffic_deliveries} == {"order_1", "order_3"}

def test_get_by_weather_condition(db_session):
    repository = DeliveryRepository(db_session)
    repository.save(Delivery(order_id="order_1", weather_condition="Sunny"))
    repository.save(Delivery(order_id="order_2", weather_condition="Rainy"))

    sunny = repository.get_by_weather_condition("Sunny")

    assert len(sunny) >= 1
    assert any(d.order_id == "order_1" for d in sunny)


