from backend.app.domain.models.user import User, UserRole
from backend.app.infrastructure.orm_models import UserORM
from backend.app.infrastructure.repositories.user_repository import UserRepository


def test_save_and_get_by_id(db_session):
    repository = UserRepository(db_session)
    user = User(
        customer_id="user_1",
        name="Aman",
        location="City_1",
        role=UserRole.CUSTOMER,
    )

    saved_user = repository.save(user)
    fetched_user = repository.get_by_id("user_1")

    assert saved_user.customer_id == "user_1"
    assert fetched_user is not None
    assert fetched_user.customer_id == "user_1"
    assert fetched_user.name == "Aman"
    assert fetched_user.location == "City_1"
    assert fetched_user.role == UserRole.CUSTOMER


def test_get_all_returns_all_users(db_session):
    repository = UserRepository(db_session)
    repository.save(User(customer_id="user_1", name="Ali"))
    repository.save(User(customer_id="user_2", name="Sara", role=UserRole.DELIVERY_PERSON))

    users = repository.get_all()
    user_ids = {user.customer_id for user in users}

    assert len(users) == 2
    assert user_ids == {"user_1", "user_2"}


def test_delete_existing_user(db_session):
    repository = UserRepository(db_session)
    repository.save(User(customer_id="user_1", name="Delete Me"))

    deleted = repository.delete("user_1")
    fetched_user = repository.get_by_id("user_1")

    assert deleted is True
    assert fetched_user is None


def test_delete_missing_user_returns_false(db_session):
    repository = UserRepository(db_session)

    deleted = repository.delete("missing_user")

    assert deleted is False


def test_get_by_role_filters_users(db_session):
    repository = UserRepository(db_session)
    repository.save(User(customer_id="user_1", role=UserRole.CUSTOMER))
    repository.save(User(customer_id="user_2", role=UserRole.RESTAURANT_OWNER))
    repository.save(User(customer_id="user_3", role=UserRole.RESTAURANT_OWNER))

    owners = repository.get_by_role(UserRole.RESTAURANT_OWNER)

    assert {user.customer_id for user in owners} == {"user_2", "user_3"}


def test_get_by_location_filters_users(db_session):
    repository = UserRepository(db_session)
    repository.save(User(customer_id="user_1", location="City_5"))
    repository.save(User(customer_id="user_2", location="City_5"))
    repository.save(User(customer_id="user_3", location="City_6"))

    city_users = repository.get_by_location("City_5")

    assert {user.customer_id for user in city_users} == {"user_1", "user_2"}


def test_get_by_email_and_password_helpers(db_session):
    repository = UserRepository(db_session)
    repository.save(User(customer_id="user_1", name="Auth User"))

    orm_user = repository._db.get(UserORM, "user_1")  # noqa: SLF001 - test setup for persistence-only fields
    orm_user.email = "user@example.com"
    db_session.flush()

    repository.set_hashed_password("user_1", "hashed-secret")

    fetched_user = repository.get_by_email("user@example.com")
    hashed_password = repository.get_hashed_password("user_1")

    assert fetched_user is not None
    assert fetched_user.customer_id == "user_1"
    assert hashed_password == "hashed-secret"
