import pytest
from unittest.mock import MagicMock

from backend.app.infrastructure.repositories.menu_repository import MenuRepository
from backend.app.domain.models.menu_item import MenuItem


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def repo(mock_db):
    return MenuRepository(mock_db)


def test_get_by_id_returns_menu_item(repo, mock_db):
    orm_item = MagicMock()
    orm_item.food_item_id = "1"
    orm_item.restaurant_id = "r1"
    orm_item.name = "Burger"
    orm_item.category = "Fast Food"
    orm_item.price = 10.0

    mock_db.get.return_value = orm_item

    result = repo.get_by_id("1")

    assert result is not None
    assert result.food_item_id == "1"
    assert result.name == "Burger"
    mock_db.get.assert_called_once()


def test_get_by_id_returns_none_if_not_found(repo, mock_db):
    mock_db.get.return_value = None

    result = repo.get_by_id("999")

    assert result is None


def test_delete_existing_menu_item(repo, mock_db):
    orm_item = MagicMock()
    mock_db.get.return_value = orm_item

    result = repo.delete("1")

    assert result is True
    mock_db.delete.assert_called_once_with(orm_item)
    mock_db.flush.assert_called_once()


def test_delete_nonexistent_menu_item(repo, mock_db):
    mock_db.get.return_value = None

    result = repo.delete("1")

    assert result is False


def test_save_menu_item(repo, mock_db):
    menu_item = MenuItem(
        food_item_id="1",
        restaurant_id="r1",
        name="Pizza",
        category="Italian",
        price=15.0
    )

    orm_item = MagicMock()
    orm_item.food_item_id = "1"
    orm_item.restaurant_id = "r1"
    orm_item.name = "Pizza"
    orm_item.category = "Italian"
    orm_item.price = 15.0

    mock_db.merge.return_value = orm_item

    result = repo.save(menu_item)

    assert result.food_item_id == "1"
    assert result.name == "Pizza"
    mock_db.merge.assert_called_once()
    mock_db.flush.assert_called_once()