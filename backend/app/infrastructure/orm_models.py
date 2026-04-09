from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    Time,
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""

class UserORM(Base):

    __tablename__ = "users"

    customer_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)
    location = Column(String, nullable=True)
    loyalty_program = Column(Boolean, default=False, nullable=False)
    order_history_count = Column(Integer, default=0, nullable=False)
    preferred_cuisine = Column(String, nullable=True)
    order_frequency = Column(String, nullable=True)
    role = Column(String, default="customer", nullable=False)
    email = Column(String, unique=True, nullable=True, index=True)
    hashed_password = Column(String, nullable=True)

    orders = relationship("OrderORM", back_populates="customer", foreign_keys="OrderORM.customer_id")
    notifications = relationship("NotificationORM", back_populates="user")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<UserORM customer_id={self.customer_id} role={self.role}>"

class RestaurantORM(Base):
    __tablename__ = "restaurants"

    restaurant_id = Column(String, primary_key=True, index=True)
    owner_id = Column(String, ForeignKey("users.customer_id"), nullable=True)
    name = Column(String, nullable=True)
    location = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    avg_rating = Column(Float, nullable=True)
    review_count = Column(Integer, default=0, nullable=False)

    menu_items = relationship("MenuItemORM", back_populates="restaurant")
    orders = relationship("OrderORM", back_populates="restaurant")
    reviews = relationship("ReviewORM", back_populates="restaurant")

    def __repr__(self) -> str:
        return f"<RestaurantORM id={self.restaurant_id} name={self.name}>"

class MenuItemORM(Base):

    __tablename__ = "menu_items"

    food_item_id = Column(String, primary_key=True, index=True)
    restaurant_id = Column(String, ForeignKey("restaurants.restaurant_id"), nullable=False)
    name = Column(String, nullable=False)
    category = Column(String, nullable=True)
    price = Column(Float, nullable=True)
    available_from = Column(Time, nullable=True)
    available_until = Column(Time, nullable=True)

    restaurant = relationship("RestaurantORM", back_populates="menu_items")

    def __repr__(self) -> str:
        return f"<MenuItemORM id={self.food_item_id} name={self.name}>"

class OrderORM(Base):

    __tablename__ = "orders"

    order_id = Column(String, primary_key=True, index=True)
    customer_id = Column(String, ForeignKey("users.customer_id"), nullable=False)
    restaurant_id = Column(String, ForeignKey("restaurants.restaurant_id"), nullable=False)
    items = Column(Text, nullable=False, default="")
    order_time = Column(DateTime, nullable=True)
    order_value = Column(Float, nullable=True)
    status = Column(String, default="pending", nullable=False)
    customer_rating = Column(Float, nullable=True)
    customer_satisfaction = Column(Integer, nullable=True)

    customer = relationship("UserORM", back_populates="orders", foreign_keys=[customer_id])
    restaurant = relationship("RestaurantORM", back_populates="orders")
    delivery = relationship("DeliveryORM", back_populates="order", uselist=False)

    def __repr__(self) -> str:
        return f"<OrderORM id={self.order_id} status={self.status}>"

class DeliveryORM(Base):

    __tablename__ = "deliveries"

    order_id = Column(String, ForeignKey("orders.order_id"), primary_key=True, index=True)
    delivery_time = Column(DateTime, nullable=True)
    delivery_time_actual = Column(Float, nullable=True)
    delivery_delay = Column(Float, nullable=True)
    delivery_distance = Column(Float, nullable=True)
    delivery_method = Column(String, nullable=True)
    route_taken = Column(String, nullable=True)
    route_type = Column(String, nullable=True)
    route_efficiency = Column(Float, nullable=True)
    traffic_condition = Column(String, nullable=True)
    weather_condition = Column(String, nullable=True)
    predicted_delivery_mode = Column(String, nullable=True)
    traffic_avoidance = Column(Boolean, nullable=True)

    order = relationship("OrderORM", back_populates="delivery")

    def __repr__(self) -> str:
        return f"<DeliveryORM order_id={self.order_id} method={self.delivery_method}>"

class PromoCodeORM(Base):

    __tablename__ = "promo_codes"

    promo_id = Column(String, primary_key=True, index=True)
    code = Column(String, unique=True, nullable=False, index=True)
    discount_type = Column(String, nullable=False)
    discount_value = Column(Float, nullable=False)
    expiry_date = Column(DateTime, nullable=True)
    usage_limit = Column(Integer, nullable=True)
    usage_count = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    owner_id = Column(String, ForeignKey("users.customer_id"), nullable=False)

    assignments = relationship(
        "PromoAssignmentORM", back_populates="promo", cascade="all, delete-orphan"
    )


class PromoAssignmentORM(Base):

    __tablename__ = "promo_assignments"

    promo_id = Column(String, ForeignKey("promo_codes.promo_id"), primary_key=True)
    customer_id = Column(String, ForeignKey("users.customer_id"), primary_key=True)

    promo = relationship("PromoCodeORM", back_populates="assignments")


class ReviewORM(Base):

    __tablename__ = "reviews"

    review_id = Column(String, primary_key=True, index=True)
    order_id = Column(String, ForeignKey("orders.order_id"), unique=True, nullable=False)
    customer_id = Column(String, ForeignKey("users.customer_id"), nullable=False)
    restaurant_id = Column(String, ForeignKey("restaurants.restaurant_id"), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, nullable=True)

    restaurant = relationship("RestaurantORM", back_populates="reviews")

    def __repr__(self) -> str:
        return f"<ReviewORM id={self.review_id} rating={self.rating}>"


class NotificationORM(Base):

    __tablename__ = "notifications"

    notification_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(String, ForeignKey("users.customer_id"), nullable=False)
    event_type = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)

    user = relationship("UserORM", back_populates="notifications")

    def __repr__(self) -> str:
        return f"<NotificationORM id={self.notification_id} event={self.event_type}>"
