import pytest
from backend.app.domain.models.menu_item import MenuItem

def test_menu_item_model_with_required_fields():
    """test for required fields only"""
    item = MenuItem(food_item_id="123", restaurant_id="456", name="Pizza")

    assert item.food_item_id == "123"
    assert item.restaurant_id == "456"
    assert item.name == "Pizza"
    assert item.category is None
    assert item.price is None

def test_menu_item_model_with_all_fields():
    """test for all fields"""
    item = MenuItem(
        food_item_id="123",
        restaurant_id="456",
        name="Pizza",
        category="Main Course",
        price=9.99
    )

    assert item.name == "Pizza"
    assert item.category == "Main Course"
    assert item.price == 9.99

def test_menu_item_belongs_to_restaurant():
    """test menu item is linked to restaurant."""
    item = MenuItem(food_item_id="123", restaurant_id="456", name="Pizza")

    assert item.restaurant_id == "456"