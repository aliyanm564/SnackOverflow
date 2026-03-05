import pytest
from backend.app.domain.models.user import User, UserRole
from backend.app.domain.rules.role_rules import can_access_feature


# -----------------------------
# Positive Access Cases
# -----------------------------

def test_customer_can_access_customer_feature():
    user = User(customer_id="1", role=UserRole.CUSTOMER)
    assert can_access_feature(user, UserRole.CUSTOMER) is True


def test_restaurant_owner_can_access_owner_feature():
    user = User(customer_id="2", role=UserRole.RESTAURANT_OWNER)
    assert can_access_feature(user, UserRole.RESTAURANT_OWNER) is True


def test_delivery_person_can_access_delivery_feature():
    user = User(customer_id="3", role=UserRole.DELIVERY_PERSON)
    assert can_access_feature(user, UserRole.DELIVERY_PERSON) is True


# -----------------------------
# Negative Access Cases
# -----------------------------

def test_customer_cannot_access_owner_feature():
    user = User(customer_id="4", role=UserRole.CUSTOMER)
    assert can_access_feature(user, UserRole.RESTAURANT_OWNER) is False


def test_owner_cannot_access_delivery_feature():
    user = User(customer_id="5", role=UserRole.RESTAURANT_OWNER)
    assert can_access_feature(user, UserRole.DELIVERY_PERSON) is False


def test_delivery_person_cannot_access_customer_feature():
    user = User(customer_id="6", role=UserRole.DELIVERY_PERSON)
    assert can_access_feature(user, UserRole.CUSTOMER) is False
