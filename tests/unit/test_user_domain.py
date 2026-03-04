import pytest
from backend.app.domain.models.user import User, UserRole


def test_create_user_with_required_fields():
    user = User(customer_id="123")

    assert user.customer_id == "123"
    assert user.loyalty_program is False
    assert user.order_history == []
    assert user.role == UserRole.CUSTOMER


def test_user_with_all_fields():
    user = User(
        customer_id="abc",
        name="Aliyan",
        age=22,
        gender="Male",
        location="Kelowna",
        loyalty_program=True,
        preferred_cuisine="Asian",
        order_frequency="Weekly",
        role=UserRole.RESTAURANT_OWNER
    )

    assert user.name == "Aliyan"
    assert user.age == 22
    assert user.loyalty_program is True
    assert user.role == UserRole.RESTAURANT_OWNER


def test_order_history_is_not_shared_between_instances():
    user1 = User(customer_id="1")
    user2 = User(customer_id="2")

    user1.order_history.append("order_1")

    assert user1.order_history == ["order_1"]
    assert user2.order_history == []  # should NOT contain order_1


def test_invalid_role_raises_error():
    with pytest.raises(ValueError):
        User(customer_id="x", role="invalid_role")
