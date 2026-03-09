"""
ORM models representing the database schema.

Each ORM model is intentionally kept separate 
from the domain models so that concerns never
leak into the domain layer (Dependency Inversion Principle).

Mapping summary
---------------
UserORM          ←→  domain.User
RestaurantORM    ←→  domain.Restaurant
MenuItemORM      ←→  domain.MenuItem
OrderORM         ←→  domain.Order
DeliveryORM      ←→  domain.Delivery
NotificationORM  ←→  (no domain model, infrastructure-only)
"""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

class UserORM(Base):
    """
    Persists customer/delivery-person/restaurant-owner accounts.
    """

    __tablename__ = "users"

    customer_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)
    location = Column(String, nullable=True)
    loyalty_program = Column(Boolean, default=False, nullable=False)
    # Stored as an integer count sourced from the CSV `order_history` column.
    order_history_count = Column(Integer, default=0, nullable=False)
    preferred_cuisine = Column(String, nullable=True)
    order_frequency = Column(String, nullable=True)
    # Stores the UserRole string value ("customer", "restaurant_owner", etc.)
    role = Column(String, default="customer", nullable=False)
    # Authentication fields (populated on registration, not from CSV)
    email = Column(String, unique=True, nullable=True, index=True)
    hashed_password = Column(String, nullable=True)

    orders = relationship("OrderORM", back_populates="customer", foreign_keys="OrderORM.customer_id")
    notifications = relationship("NotificationORM", back_populates="user")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<UserORM customer_id={self.customer_id} role={self.role}>"


# ---------------------------------------------------------------------------
# Restaurants
# ---------------------------------------------------------------------------

class RestaurantORM(Base):
    """
    Represents a restaurant entity.
    """

    __tablename__ = "restaurants"

    restaurant_id = Column(String, primary_key=True, index=True)
    # Nullable because restaurants are seeded before owners register.
    owner_id = Column(String, ForeignKey("users.customer_id"), nullable=True)
    name = Column(String, nullable=True)
    location = Column(String, nullable=True)
    description = Column(Text, nullable=True)

    menu_items = relationship("MenuItemORM", back_populates="restaurant")
    orders = relationship("OrderORM", back_populates="restaurant")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<RestaurantORM id={self.restaurant_id} name={self.name}>"


# ---------------------------------------------------------------------------
# Menu items
# ---------------------------------------------------------------------------

class MenuItemORM(Base):
    """
    A single item on a restaurant's menu.
    """

    __tablename__ = "menu_items"

    food_item_id = Column(String, primary_key=True, index=True)
    restaurant_id = Column(String, ForeignKey("restaurants.restaurant_id"), nullable=False)
    name = Column(String, nullable=False)
    category = Column(String, nullable=True)
    price = Column(Float, nullable=True)

    restaurant = relationship("RestaurantORM", back_populates="menu_items")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<MenuItemORM id={self.food_item_id} name={self.name}>"


# ---------------------------------------------------------------------------
# Orders
# ---------------------------------------------------------------------------

class OrderORM(Base):
    """
    Represents a placed order.
    """

    __tablename__ = "orders"

    order_id = Column(String, primary_key=True, index=True)
    customer_id = Column(String, ForeignKey("users.customer_id"), nullable=False)
    restaurant_id = Column(String, ForeignKey("restaurants.restaurant_id"), nullable=False)
    # Comma-separated food_item_ids, e.g. "a1b2c3,d4e5f6"
    items = Column(Text, nullable=False, default="")
    order_time = Column(DateTime, nullable=True)
    order_value = Column(Float, nullable=True)
    # Stores OrderStatus string value ("pending", "completed", "cancelled")
    status = Column(String, default="pending", nullable=False)
    customer_rating = Column(Float, nullable=True)
    customer_satisfaction = Column(Integer, nullable=True)

    customer = relationship("UserORM", back_populates="orders", foreign_keys=[customer_id])
    restaurant = relationship("RestaurantORM", back_populates="orders")
    delivery = relationship("DeliveryORM", back_populates="order", uselist=False)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<OrderORM id={self.order_id} status={self.status}>"


# ---------------------------------------------------------------------------
# Deliveries
# ---------------------------------------------------------------------------

class DeliveryORM(Base):
    """
    Delivery metadata associated with a single order (1-to-1 with OrderORM).
    """

    __tablename__ = "deliveries"

    order_id = Column(String, ForeignKey("orders.order_id"), primary_key=True, index=True)
    delivery_time = Column(DateTime, nullable=True)
    # Numeric value from CSV (stored as float minutes/hours in dataset)
    delivery_time_actual = Column(Float, nullable=True)
    delivery_delay = Column(Float, nullable=True)
    delivery_distance = Column(Float, nullable=True)
    # Stores DeliveryMethod string value ("walk", "bike", "car", "mixed")
    delivery_method = Column(String, nullable=True)
    # Human-readable route description, e.g. "Bike-friendly"
    route_taken = Column(String, nullable=True)
    # RouteType enum string, e.g. "route_4"
    route_type = Column(String, nullable=True)
    route_efficiency = Column(Float, nullable=True)
    traffic_condition = Column(String, nullable=True)
    weather_condition = Column(String, nullable=True)
    predicted_delivery_mode = Column(String, nullable=True)
    traffic_avoidance = Column(Boolean, nullable=True)

    order = relationship("OrderORM", back_populates="delivery")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<DeliveryORM order_id={self.order_id} method={self.delivery_method}>"


# ---------------------------------------------------------------------------
# Notifications
# ---------------------------------------------------------------------------

class NotificationORM(Base):
    """
    Persists system-generated notifications for a user.
    """

    __tablename__ = "notifications"

    notification_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(String, ForeignKey("users.customer_id"), nullable=False)
    # Short machine-readable event label, e.g. "order_created"
    event_type = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)

    user = relationship("UserORM", back_populates="notifications")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<NotificationORM id={self.notification_id} event={self.event_type}>"
