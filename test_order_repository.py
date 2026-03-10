import pytest
from datetime import datetime
from unittest.mock import MagicMock

from backend.app.domain.models.enums import OrderStatus
from backend.app.domain.models.orders import Order
from backend.app.infrastructure.repositories.order_repository import OrderRepository


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def repo(mock_db):
    return OrderRepository(mock_db)


def test_get_by_id_returns_order(repo, mock_db):
    orm_order = MagicMock()
    orm_order.order_id = "1"
    orm_order.customer_id = "cust1"
    orm_order.restaurant_id = "rest1"
    orm_order.items = "burger,fries"
    orm_order.order_time = datetime.now()
    orm_order.order_value = 20.0
    orm_order.status = OrderStatus.PENDING.value
    orm_order.customer_rating = None
    orm_order.customer_satisfaction = None

    mock_db.get.return_value = orm_order

    result = repo.get_by_id("1")

    assert result is not None
    assert result.order_id == "1"
    assert result.customer_id == "cust1"
    mock_db.get.assert_called_once()


def test_get_by_id_returns_none_if_not_found(repo, mock_db):
    mock_db.get.return_value = None

    result = repo.get_by_id("999")

    assert result is None


def test_delete_existing_order(repo, mock_db):
    orm_order = MagicMock()
    mock_db.get.return_value = orm_order

    result = repo.delete("1")

    assert result is True
    mock_db.delete.assert_called_once_with(orm_order)
    mock_db.flush.assert_called_once()


def test_delete_nonexistent_order(repo, mock_db):
    mock_db.get.return_value = None

    result = repo.delete("1")

    assert result is False


def test_update_status(repo, mock_db):
    orm_order = MagicMock()
    orm_order.status = OrderStatus.PENDING.value
    orm_order.order_id = "1"
    orm_order.customer_id = "cust1"
    orm_order.restaurant_id = "rest1"
    orm_order.items = "pizza"
    orm_order.order_time = datetime.now()
    orm_order.order_value = 15.0
    orm_order.customer_rating = None
    orm_order.customer_satisfaction = None

    mock_db.get.return_value = orm_order

    result = repo.update_status("1", OrderStatus.COMPLETED)

    assert result.status == OrderStatus.COMPLETED
    assert orm_order.status == OrderStatus.COMPLETED.value
    mock_db.flush.assert_called_once()