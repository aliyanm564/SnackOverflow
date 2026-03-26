import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.application.services.menu_service import MenuService
from backend.app.domain.models.user import User, UserRole
from backend.app.infrastructure.repositories.menu_repository import MenuRepository
from backend.app.infrastructure.repositories.restaurant_repository import RestaurantRepository
from backend.app.domain.models.restaurant import Restaurant
from backend.app.infrastructure.database import Base


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    SessionLocal = sessionmaker(bind=engine)

    Base.metadata.create_all(engine)

    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def menu_service(db):
    menu_repo = MenuRepository(db)
    restaurant_repo = RestaurantRepository(db)
    return MenuService(menu_repo, restaurant_repo)


@pytest.fixture
def owner():
    return User(
        customer_id="owner-1",
        name="Test Owner",
        role=UserRole.RESTAURANT_OWNER
    )


@pytest.fixture
def restaurant(db, owner):
    repo = RestaurantRepository(db)

    restaurant = Restaurant(
        restaurant_id="rest-1",
        name="Pizza Place",
        owner_id=owner.customer_id
    )

    repo.save(restaurant)
    return restaurant


def test_add_menu_item(menu_service, owner, restaurant):
    item = menu_service.add_item(
        requesting_user=owner,
        restaurant_id=restaurant.restaurant_id,
        name="Pepperoni Pizza",
        category="Pizza",
        price=12.99
    )

    assert item.name == "Pepperoni Pizza"
    assert item.price == 12.99


def test_get_menu_for_restaurant(menu_service, owner, restaurant):
    menu_service.add_item(
        requesting_user=owner,
        restaurant_id=restaurant.restaurant_id,
        name="Burger",
        category="Fast Food",
        price=9.99
    )

    items = menu_service.get_menu_for_restaurant(restaurant.restaurant_id)

    assert len(items) == 1
    assert items[0].name == "Burger"


def test_update_menu_item(menu_service, owner, restaurant):
    item = menu_service.add_item(
        requesting_user=owner,
        restaurant_id=restaurant.restaurant_id,
        name="Fries",
        category="Sides",
        price=4.99
    )

    updated = menu_service.update_item(
        requesting_user=owner,
        food_item_id=item.food_item_id,
        price=5.99
    )

    assert updated.price == 5.99


def test_delete_menu_item(menu_service, owner, restaurant):
    item = menu_service.add_item(
        requesting_user=owner,
        restaurant_id=restaurant.restaurant_id,
        name="Salad",
        category="Healthy",
        price=7.99
    )

    menu_service.delete_item(owner, item.food_item_id)

    with pytest.raises(Exception):
        menu_service.get_item(item.food_item_id)