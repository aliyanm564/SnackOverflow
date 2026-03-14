import pytest
from backend.app.application.exceptions import AuthorizationError, NotFoundError
from backend.app.application.services.restaurant_service import RestaurantService
from backend.app.domain.models.restaurant import Restaurant
from backend.app.domain.models.user import User, UserRole


def test_create_restaurant_as_owner(mock_restaurant_repo, owner_user):
    mock_restaurant_repo.save.return_value = Restaurant(
        restaurant_id="rest-new", owner_id="owner-001", name="Sukhi's Place"
    )
    service = RestaurantService(mock_restaurant_repo)
    result = service.create_restaurant(owner_user, name="Sukhi's Place")
    assert result.name == "Sukhi's Place"


def test_create_restaurant_as_customer_fails(mock_restaurant_repo, customer_user):
    service = RestaurantService(mock_restaurant_repo)

    with pytest.raises(AuthorizationError):
        service.create_restaurant(customer_user, name="Nope")


def test_get_restaurant_not_found(mock_restaurant_repo):
    mock_restaurant_repo.get_by_id.return_value = None
    service = RestaurantService(mock_restaurant_repo)

    with pytest.raises(NotFoundError):
        service.get_restaurant("doesnt-exist")


def test_update_restaurant_as_owner(mock_restaurant_repo, owner_user, sample_restaurant):
    mock_restaurant_repo.get_by_id.return_value = sample_restaurant
    mock_restaurant_repo.save.return_value = sample_restaurant.model_copy(update={"name": "New Name"})
    service = RestaurantService(mock_restaurant_repo)

    result = service.update_restaurant(owner_user, "rest-001", name="New Name")
    assert result.name == "New Name"


def test_update_restaurant_wrong_owner(mock_restaurant_repo, sample_restaurant):
    other_user = User(customer_id="other-guy", name="Hacker", role=UserRole.RESTAURANT_OWNER)
    mock_restaurant_repo.get_by_id.return_value = sample_restaurant
    service = RestaurantService(mock_restaurant_repo)

    with pytest.raises(AuthorizationError):
        service.update_restaurant(other_user, "rest-001", name="Stolen")


def test_delete_restaurant_wrong_owner(mock_restaurant_repo, sample_restaurant):
    other_user = User(customer_id="other-guy", name="Hacker", role=UserRole.RESTAURANT_OWNER)
    mock_restaurant_repo.get_by_id.return_value = sample_restaurant
    service = RestaurantService(mock_restaurant_repo)

    with pytest.raises(AuthorizationError):
        service.delete_restaurant(other_user, "rest-001")