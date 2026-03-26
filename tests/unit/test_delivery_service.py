import pytest
from backend.app.application.exceptions import AuthorizationError, BusinessRuleError, NotFoundError
from backend.app.application.services.delivery_service import DeliveryService
from backend.app.domain.models.delivery import Delivery
from backend.app.domain.models.enums import DeliveryMethod, OrderStatus
from backend.app.domain.models.orders import Order
 
def test_assign_delivery_as_owner(mock_delivery_repo, mock_order_repo, owner_user):
    mock_order_repo.get_by_id.return_value = Order(
        order_id="order-001", customer_id="cust-001", restaurant_id="rest-001",
        items=["item-001"], order_value=12.99, status=OrderStatus.PENDING
    )
    mock_delivery_repo.get_by_id.return_value = None
    mock_delivery_repo.save.return_value = Delivery(order_id="order-001")
    service = DeliveryService(mock_delivery_repo, mock_order_repo)
 
    result = service.assign_delivery(owner_user, "order-001")
 
    assert result.order_id == "order-001"
 
def test_assign_delivery_as_customer_fails(mock_delivery_repo, mock_order_repo, customer_user):
    service = DeliveryService(mock_delivery_repo, mock_order_repo)
 
    with pytest.raises(AuthorizationError):
        service.assign_delivery(customer_user, "order-001")
 
 
def test_assign_delivery_order_not_found(mock_delivery_repo, mock_order_repo, owner_user):
    mock_order_repo.get_by_id.return_value = None
    service = DeliveryService(mock_delivery_repo, mock_order_repo)
 
    with pytest.raises(NotFoundError):
        service.assign_delivery(owner_user, "fake-order")
 
def test_assign_delivery_already_exists(mock_delivery_repo, mock_order_repo, owner_user):
    mock_order_repo.get_by_id.return_value = Order(
        order_id="order-001", customer_id="cust-001", restaurant_id="rest-001",
        items=["item-001"], order_value=12.99, status=OrderStatus.PENDING
    )
    mock_delivery_repo.get_by_id.return_value = Delivery(order_id="order-001")
    service = DeliveryService(mock_delivery_repo, mock_order_repo)
 
    with pytest.raises(BusinessRuleError):
        service.assign_delivery(owner_user, "order-001") 
 
def test_get_delivery_not_found(mock_delivery_repo, mock_order_repo):
    mock_delivery_repo.get_by_id.return_value = None
    service = DeliveryService(mock_delivery_repo, mock_order_repo)
 
    with pytest.raises(NotFoundError):
        service.get_delivery("fake-order")
 
 
def test_update_delivery_as_customer_fails(mock_delivery_repo, mock_order_repo, customer_user):
    service = DeliveryService(mock_delivery_repo, mock_order_repo)
 
    with pytest.raises(AuthorizationError):
         service.update_delivery(customer_user, "order-001", {"traffic_condition": "High"})
 
def test_negative_delay_threshold(mock_delivery_repo, mock_order_repo):
    service = DeliveryService(mock_delivery_repo, mock_order_repo)

    with pytest.raises(ValueError):
        service.get_delayed_deliveries(min_delay=-5.0)