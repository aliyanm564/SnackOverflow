import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock
from backend.app.domain.models.user import User, UserRole
from backend.app.domain.models.restaurant import Restaurant
from backend.app.domain.models.menu_item import MenuItem
from backend.app.domain.models.orders import Order
from backend.app.domain.models.delivery import Delivery
from backend.app.domain.models.enums import OrderStatus, DeliveryMethod

"Shared across all infrastructure layer tests."
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.infrastructure.orm_models import Base

@pytest.fixture(scope="function")
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)

@pytest.fixture
def customer_user():
    return User(customer_id="cust-001", name="Alice", age=30,
                loyalty_program=False, role=UserRole.CUSTOMER)

@pytest.fixture
def loyalty_customer():
    return User(customer_id="cust-loyalty", name="Bob",
                loyalty_program=True, role=UserRole.CUSTOMER)

@pytest.fixture
def owner_user():
    return User(customer_id="owner-001", name="Carlo",
                role=UserRole.RESTAURANT_OWNER)

@pytest.fixture
def delivery_user():
    return User(customer_id="driver-001", name="Dana",
                role=UserRole.DELIVERY_PERSON)

@pytest.fixture
def sample_restaurant(owner_user):
    return Restaurant(restaurant_id="rest-001", owner_id=owner_user.customer_id,
                      name="Test Bistro", location="City_1")

@pytest.fixture
def sample_menu_item(sample_restaurant):
    return MenuItem(food_item_id="item-001",
                    restaurant_id=sample_restaurant.restaurant_id,
                    name="Burger", category="American", price=12.99)

@pytest.fixture
def sample_order(customer_user, sample_restaurant, sample_menu_item):
    return Order(order_id="order-001", customer_id=customer_user.customer_id,
                 restaurant_id=sample_restaurant.restaurant_id,
                 items=[sample_menu_item.food_item_id],
                 order_time=datetime.now(tz=timezone.utc),
                 order_value=12.99, status=OrderStatus.PENDING)

@pytest.fixture
def completed_order(sample_order):
    return sample_order.model_copy(update={"status": OrderStatus.COMPLETED})

# --- Mock fixtures ---
@pytest.fixture
def mock_user_repo():        return MagicMock()

@pytest.fixture
def mock_restaurant_repo():  return MagicMock()

@pytest.fixture
def mock_menu_repo():        return MagicMock()

@pytest.fixture
def mock_order_repo():       return MagicMock()

@pytest.fixture
def mock_delivery_repo():    return MagicMock()

@pytest.fixture
def mock_notification_repo(): return MagicMock()

@pytest.fixture
def mock_notification_service(): return MagicMock()

@pytest.fixture
def mock_order_service():    return MagicMock()

@pytest.fixture
def mock_pricing_service():  return MagicMock()
