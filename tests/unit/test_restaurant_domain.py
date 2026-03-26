import pytest
from backend.app.domain.models.restaurant import Restaurant

def test_restaurant_model_with_required_fields():

 restaurant = Restaurant(restaurant_id="123", owner_id="owner_456")
                        
 assert restaurant.restaurant_id == "123"
 assert restaurant.owner_id == "owner_456"
 assert restaurant.name is None
 assert restaurant.location is None
 assert restaurant.description is None

def test_restaurant_model_with_all_fields():
    restaurant = Restaurant(
        restaurant_id="123",
        owner_id="owner_456",
        name="Boston Pizza",
        location="123 bernard Street",
        description="Best pizza and sports bar in town!"
    )

    assert restaurant.name == "Boston Pizza"
    assert restaurant.location == "123 bernard Street" 
    assert restaurant.description == "Best pizza and sports bar in town!"

def test_two_restaurants_are_independent():
    restaurant1 = Restaurant(restaurant_id="123", owner_id="owner_456")
    restaurant2 = Restaurant(restaurant_id="222", owner_id="owner_222")

    assert restaurant1.restaurant_id == "123"
    assert restaurant2.restaurant_id == "222"
