from backend.app.domain.models.restaurant import Restaurant
from backend.app.infrastructure.orm_models import RestaurantORM
from backend.app.infrastructure.repositories.restaurant_repository import RestaurantRepository


def test_save_and_get_by_id(db_session):
    repository = RestaurantRepository(db_session)
    restaurant = Restaurant(
        restaurant_id="rest_1",
        owner_id="owner_1",
        name="Pizza Pizza",
        location="City_1"
    )

    saved = repository.save(restaurant)
    fetched = repository.get_by_id("rest_1")

    assert saved.restaurant_id == "rest_1"
    assert fetched is not None
    assert fetched.name == "Pizza Pizza"
    assert fetched.location == "City_1"

def test_get_all_returns_all_restaurants(db_session):
    repository = RestaurantRepository(db_session)
    repository.save(Restaurant(restaurant_id="rest_1", owner_id="owner_1", name="Pizza Pizza", location="City_1"))
    repository.save(Restaurant(restaurant_id="rest_2", owner_id="owner_2", name="Burger Joint", location="City_2"))

    restaurants = repository.get_all()
    restaurant_ids = {r.restaurant_id for r in restaurants}

    assert len(restaurants) >= 2
    assert restaurant_ids == {"rest_1", "rest_2"}

def test_delete_missing_restaurant_returns_false(db_session):
    repository = RestaurantRepository(db_session)  # ✅ 4 spaces

    deleted = repository.delete("missing_restaurant")

    assert deleted is False

def test_get_by_owner_filters_restaurants(db_session):
    repository = RestaurantRepository(db_session)
    repository.save(Restaurant(restaurant_id="rest_1", owner_id="owner_1", name="Pizza Pizza"))
    repository.save(Restaurant(restaurant_id="rest_2", owner_id="owner_2", name="Burger Joint"))
    repository.save(Restaurant(restaurant_id="rest_3", owner_id="owner_1", name="Pasta Place")) 

    owner_restaurants = repository.get_by_owner("owner_1")

    assert {r.restaurant_id for r in owner_restaurants} == {"rest_1", "rest_3"}


def test_search_by_name(db_session):
    repository = RestaurantRepository(db_session)
    repository.save(Restaurant(restaurant_id="rest_1", owner_id="owner_1", name="Pizza Pizza"))
    repository.save(Restaurant(restaurant_id="rest_2", owner_id="owner_2", name="Burger Joint"))
        
    results = repository.search_by_name("Pizza")

    assert len(results) >= 1
    assert any(r.name == "Pizza Pizza" for r in results)


