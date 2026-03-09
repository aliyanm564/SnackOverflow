import csv
import hashlib
import os
from contextlib import contextmanager
from datetime import datetime
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.app.infrastructure.orm_models import (
    Base,
    DeliveryORM,
    MenuItemORM,
    NotificationORM,
    OrderORM,
    RestaurantORM,
    UserORM,
)

# ---------------------------------------------------------------------------
# Engine & session factory
# ---------------------------------------------------------------------------

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./snackoverflow.db")

engine = create_engine(
    DATABASE_URL,
    # Required for SQLite to work across threads in FastAPI
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Create all tables (no-op if they already exist)."""
    Base.metadata.create_all(bind=engine)


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """
    Context-manager that yields a SQLAlchemy session and guarantees
    commit-on-success / rollback-on-error behaviour.

    Usage (in repositories / services):
        with get_db() as db:
            db.add(some_orm_object)
    """
    db: Session = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# ---------------------------------------------------------------------------
# FastAPI dependency (used by routers via Depends)
# ---------------------------------------------------------------------------

def get_db_session() -> Generator[Session, None, None]:
    """Yield a session for FastAPI Depends injection."""
    db: Session = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# ---------------------------------------------------------------------------
# CSV seeding helpers
# ---------------------------------------------------------------------------

# Maps the food item name to a rough cuisine category derived from the dataset.
_ITEM_CATEGORY: dict[str, str] = {
    "Taccos": "Mexican",
    "Burritos": "Mexican",
    "Briyani rice": "Asian",
    "Chicken rice": "Asian",
    "Dumplings": "Asian",
    "Sushi": "Asian",
    "Pasta": "Italian",
    "Whole cake": "Bakery",
    "Cup cake": "Bakery",
    "Cookie": "Bakery",
    "Beef pie": "Bakery",
    "Chicken pie": "Bakery",
    "PastrySmoothie": "Bakery",
    "CoffeeBoba tea": "Drinks",
    "Burger": "American",
    "Fried chicken": "American",
    "Chicken wings": "American",
    "Pizza": "Italian",
    "Shawarma": "Middle Eastern",
    "Salad": "Healthy",
    "Soup": "Comfort",
}

# Approximate per-item prices inferred from dataset order_value ranges.
_ITEM_PRICE: dict[str, float] = {
    "Taccos": 12.99,
    "Burritos": 13.99,
    "Briyani rice": 14.99,
    "Chicken rice": 11.99,
    "Dumplings": 10.99,
    "Sushi": 16.99,
    "Pasta": 13.49,
    "Whole cake": 29.99,
    "Cup cake": 5.99,
    "Cookie": 3.99,
    "Beef pie": 11.49,
    "Chicken pie": 10.99,
    "PastrySmoothie": 8.99,
    "CoffeeBoba tea": 6.49,
    "Burger": 12.49,
    "Fried chicken": 13.99,
    "Chicken wings": 11.99,
    "Pizza": 15.99,
    "Shawarma": 12.99,
    "Salad": 9.99,
    "Soup": 8.99,
}


def _parse_bool(value: str) -> bool:
    return value.strip().lower() in ("yes", "true", "1")


def _stable_menu_item_id(restaurant_id: str, food_item: str) -> str:
    """
    Deterministic food_item_id so repeated seeding won't create duplicates.
    Uses a short hex digest of restaurant + item name.
    """
    raw = f"{restaurant_id}::{food_item}"
    return hashlib.md5(raw.encode()).hexdigest()[:12]


def seed_from_csv(csv_path: str, session: Session | None = None) -> None:
    """
    Reads food_delivery.csv and populates the database.

    Strategy (idempotent):
      * Users    – keyed on customer_id
      * Restaurants – keyed on restaurant_id (numeric string)
      * MenuItems   – keyed on (restaurant_id, food_item)
      * Orders      – keyed on order_id
      * Deliveries  – keyed on order_id (one delivery per order)

    Rows whose primary key already exists are silently skipped so this
    function is safe to call on every application startup.
    """
    def _run(db: Session) -> None:
        existing_users = {u for (u,) in db.query(UserORM.customer_id)}
        existing_restaurants = {r for (r,) in db.query(RestaurantORM.restaurant_id)}
        existing_menu_items = {m for (m,) in db.query(MenuItemORM.food_item_id)}
        existing_orders = {o for (o,) in db.query(OrderORM.order_id)}
        existing_deliveries = {d for (d,) in db.query(DeliveryORM.order_id)}

        with open(csv_path, newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                _seed_user(db, row, existing_users)
                _seed_restaurant(db, row, existing_restaurants)
                _seed_menu_item(db, row, existing_menu_items)
                _seed_order(db, row, existing_orders)
                _seed_delivery(db, row, existing_deliveries)

    if session is not None:
        _run(session)
    else:
        with get_db() as db:
            _run(db)


def _seed_user(db: Session, row: dict, seen: set) -> None:
    cid = row["customer_id"].strip()
    if cid in seen:
        return
    seen.add(cid)
    db.add(UserORM(
        customer_id=cid,
        age=int(row["age"]) if row["age"] else None,
        gender=row["gender"] or None,
        location=row["location"] or None,
        loyalty_program=_parse_bool(row["loyalty_program"]),
        order_history_count=int(row["order_history"]) if row["order_history"] else 0,
        preferred_cuisine=row["preferred_cuisine"] or None,
        order_frequency=row["order_frequency"] or None,
        role="customer",
    ))


def _seed_restaurant(db: Session, row: dict, seen: set) -> None:
    rid = row["restaurant_id"].strip()
    if rid in seen:
        return
    seen.add(rid)
    db.add(RestaurantORM(
        restaurant_id=rid,
        # No owner yet – will be assigned when restaurant owners register.
        owner_id=None,
        name=f"Restaurant {rid}",
        location=row["location"] or None,
        description=None,
    ))


def _seed_menu_item(db: Session, row: dict, seen: set) -> None:
    food_name = row["food_item"].strip()
    rid = row["restaurant_id"].strip()
    item_id = _stable_menu_item_id(rid, food_name)
    if item_id in seen:
        return
    seen.add(item_id)
    db.add(MenuItemORM(
        food_item_id=item_id,
        restaurant_id=rid,
        name=food_name,
        category=_ITEM_CATEGORY.get(food_name, "Other"),
        price=_ITEM_PRICE.get(food_name, 9.99),
    ))


def _seed_order(db: Session, row: dict, seen: set) -> None:
    oid = row["order_id"].strip()
    if oid in seen:
        return
    seen.add(oid)

    food_name = row["food_item"].strip()
    rid = row["restaurant_id"].strip()
    item_id = _stable_menu_item_id(rid, food_name)

    order_time = None
    if row.get("order_time"):
        try:
            order_time = datetime.strptime(row["order_time"].strip(), "%Y-%m-%d")
        except ValueError:
            pass

    rating_raw = row.get("customer_rating", "").strip()
    satisfaction_raw = row.get("customer_satisfaction", "").strip()

    db.add(OrderORM(
        order_id=oid,
        customer_id=row["customer_id"].strip(),
        restaurant_id=rid,
        items=item_id,          # stored as comma-separated item IDs
        order_time=order_time,
        order_value=float(row["order_value"]) if row.get("order_value") else None,
        status="completed",     # historical data is all completed
        customer_rating=float(rating_raw) if rating_raw else None,
        customer_satisfaction=int(satisfaction_raw) if satisfaction_raw else None,
    ))


def _seed_delivery(db: Session, row: dict, seen: set) -> None:
    oid = row["order_id"].strip()
    if oid in seen:
        return
    seen.add(oid)

    delivery_time = None
    if row.get("delivery_time"):
        try:
            delivery_time = datetime.strptime(row["delivery_time"].strip(), "%Y-%m-%d")
        except ValueError:
            pass

    # CSV `route_taken` holds "Route_4" style values → maps to RouteType enum.
    # CSV `route_type` holds "Bike-friendly" / "Car-only" → stored as a plain string.
    route_taken_raw = row.get("route_taken", "").strip()
    route_type_normalised = route_taken_raw.lower().replace("-", "_") if route_taken_raw else None

    db.add(DeliveryORM(
        order_id=oid,
        delivery_time=delivery_time,
        delivery_time_actual=float(row["delivery_time_actual"]) if row.get("delivery_time_actual") else None,
        delivery_delay=float(row["delivery_delay"]) if row.get("delivery_delay") else None,
        delivery_distance=float(row["delivery_distance"]) if row.get("delivery_distance") else None,
        delivery_method=row.get("delivery_method", "").strip().lower() or None,
        route_taken=row.get("route_type", "").strip() or None,   # "Bike-friendly" etc.
        route_type=route_type_normalised,                         # "route_4" etc.
        route_efficiency=float(row["route_efficiency"]) if row.get("route_efficiency") else None,
        traffic_condition=row.get("traffic_condition", "").strip() or None,
        weather_condition=row.get("weather_condition", "").strip() or None,
        predicted_delivery_mode=row.get("predicted_delivery_mode", "").strip() or None,
        traffic_avoidance=_parse_bool(row.get("traffic_avoidance", "false")),
    ))
