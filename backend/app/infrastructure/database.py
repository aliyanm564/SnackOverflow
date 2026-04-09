import csv
import hashlib
import os
import uuid
from contextlib import contextmanager
from datetime import datetime
from typing import Generator, Optional

import bcrypt as _bcrypt

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

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./snackoverflow.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


@contextmanager
def get_db() -> Generator[Session, None, None]:
    db: Session = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def get_db_session() -> Generator[Session, None, None]:
    db: Session = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

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
    raw = f"{restaurant_id}::{food_item}"
    return hashlib.md5(raw.encode()).hexdigest()[:12]


def seed_from_csv(csv_path: str, session: Optional[Session] = None) -> None:
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
        items=item_id,
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

    route_taken_raw = row.get("route_taken", "").strip()
    route_type_normalised = route_taken_raw.lower().replace("-", "_") if route_taken_raw else None

    db.add(DeliveryORM(
        order_id=oid,
        delivery_time=delivery_time,
        delivery_time_actual=float(row["delivery_time_actual"]) if row.get("delivery_time_actual") else None,
        delivery_delay=float(row["delivery_delay"]) if row.get("delivery_delay") else None,
        delivery_distance=float(row["delivery_distance"]) if row.get("delivery_distance") else None,
        delivery_method=row.get("delivery_method", "").strip().lower() or None,
        route_taken=row.get("route_type", "").strip() or None,
        route_type=route_type_normalised,
        route_efficiency=float(row["route_efficiency"]) if row.get("route_efficiency") else None,
        traffic_condition=row.get("traffic_condition", "").strip() or None,
        weather_condition=row.get("weather_condition", "").strip() or None,
        predicted_delivery_mode=row.get("predicted_delivery_mode", "").strip() or None,
        traffic_avoidance=_parse_bool(row.get("traffic_avoidance", "false")),
    ))


def _hash_pw(plain: str) -> str:
    return _bcrypt.hashpw(plain.encode(), _bcrypt.gensalt()).decode()


_DEMO_RESTAURANTS = [
    {
        "name": "The Burger Joint",
        "location": "Los Angeles, CA",
        "description": "Smash burgers and loaded fries made fresh daily.",
        "items": [
            {"name": "Classic Smash Burger",  "category": "Burgers", "price": 12.99},
            {"name": "Double Cheese Burger",  "category": "Burgers", "price": 14.99},
            {"name": "Crispy Chicken Burger", "category": "Burgers", "price": 13.49},
            {"name": "Veggie Burger",         "category": "Burgers", "price": 11.99},
            {"name": "Loaded Fries",          "category": "Sides",   "price": 7.99},
            {"name": "Onion Rings",           "category": "Sides",   "price": 5.99},
            {"name": "Vanilla Milkshake",     "category": "Drinks",  "price": 6.49},
        ],
    },
    {
        "name": "Pizza Palace",
        "location": "Los Angeles, CA",
        "description": "Wood-fired pizza with fresh ingredients.",
        "items": [
            {"name": "Margherita Pizza",      "category": "Pizza",   "price": 14.99},
            {"name": "Pepperoni Pizza",       "category": "Pizza",   "price": 16.99},
            {"name": "BBQ Chicken Pizza",     "category": "Pizza",   "price": 17.99},
            {"name": "Mushroom & Truffle",    "category": "Pizza",   "price": 18.99},
            {"name": "Caesar Salad",          "category": "Salads",  "price": 9.99},
            {"name": "Garlic Bread",          "category": "Sides",   "price": 5.49},
            {"name": "Tiramisu",              "category": "Dessert", "price": 7.99},
        ],
    },
    {
        "name": "Sushi World",
        "location": "Los Angeles, CA",
        "description": "Fresh sushi and Japanese favourites.",
        "items": [
            {"name": "Salmon Roll",           "category": "Sushi",      "price": 12.99},
            {"name": "Tuna Roll",             "category": "Sushi",      "price": 13.99},
            {"name": "Dragon Roll",           "category": "Sushi",      "price": 15.99},
            {"name": "Spicy Tuna Roll",       "category": "Sushi",      "price": 14.49},
            {"name": "Miso Soup",             "category": "Soup",       "price": 4.99},
            {"name": "Edamame",               "category": "Appetiser",  "price": 5.99},
            {"name": "Chicken Teriyaki",      "category": "Mains",      "price": 16.99},
        ],
    },
    {
        "name": "Taco Town",
        "location": "Los Angeles, CA",
        "description": "Authentic street tacos and burritos.",
        "items": [
            {"name": "Beef Taco",             "category": "Tacos",   "price": 4.99},
            {"name": "Chicken Taco",          "category": "Tacos",   "price": 4.49},
            {"name": "Fish Taco",             "category": "Tacos",   "price": 5.49},
            {"name": "Carne Asada Burrito",   "category": "Burritos","price": 13.99},
            {"name": "Veggie Burrito",        "category": "Burritos","price": 11.99},
            {"name": "Guacamole & Chips",     "category": "Sides",   "price": 6.99},
            {"name": "Horchata",              "category": "Drinks",  "price": 4.49},
        ],
    },
    {
        "name": "Pasta & More",
        "location": "Los Angeles, CA",
        "description": "Handmade pasta and classic Italian dishes.",
        "items": [
            {"name": "Spaghetti Bolognese",   "category": "Pasta",   "price": 15.99},
            {"name": "Fettuccine Alfredo",    "category": "Pasta",   "price": 14.99},
            {"name": "Penne Arrabbiata",      "category": "Pasta",   "price": 13.99},
            {"name": "Lasagne",               "category": "Mains",   "price": 16.99},
            {"name": "Caprese Salad",         "category": "Starters","price": 8.99},
            {"name": "Bruschetta",            "category": "Starters","price": 6.99},
            {"name": "Panna Cotta",           "category": "Dessert", "price": 7.49},
        ],
    },
]


def seed_demo_data(session: Optional[Session] = None) -> None:
    def _run(db: Session) -> None:
        existing_emails = {
            email for (email,) in db.query(UserORM.email).filter(UserORM.email.isnot(None))
        }

        owner_email = "owner@snackoverflow.com"
        owner_id: Optional[str] = None

        if owner_email not in existing_emails:
            owner_id = str(uuid.uuid4())
            db.add(UserORM(
                customer_id=owner_id,
                name="Alex Owner",
                role="restaurant_owner",
                email=owner_email,
                hashed_password=_hash_pw("password123"),
                loyalty_program=False,
                order_history_count=0,
            ))
            db.flush()
        else:
            row = db.query(UserORM.customer_id).filter(UserORM.email == owner_email).first()
            if row:
                owner_id = row[0]

        for email, name in [
            ("customer@snackoverflow.com", "Jordan Customer"),
            ("alice@snackoverflow.com",    "Alice Chen"),
            ("bob@snackoverflow.com",      "Bob Martinez"),
        ]:
            if email not in existing_emails:
                db.add(UserORM(
                    customer_id=str(uuid.uuid4()),
                    name=name,
                    role="customer",
                    email=email,
                    hashed_password=_hash_pw("password123"),
                    loyalty_program=False,
                    order_history_count=0,
                ))

        if owner_id is None:
            return

        existing_restaurant_names = {
            name for (name,) in db.query(RestaurantORM.name).filter(
                RestaurantORM.owner_id == owner_id
            )
        }

        for restaurant_def in _DEMO_RESTAURANTS:
            if restaurant_def["name"] in existing_restaurant_names:
                continue

            restaurant_id = str(uuid.uuid4())
            db.add(RestaurantORM(
                restaurant_id=restaurant_id,
                owner_id=owner_id,
                name=restaurant_def["name"],
                location=restaurant_def["location"],
                description=restaurant_def["description"],
                avg_rating=None,
                review_count=0,
            ))
            db.flush()

            for item_def in restaurant_def["items"]:
                db.add(MenuItemORM(
                    food_item_id=str(uuid.uuid4()),
                    restaurant_id=restaurant_id,
                    name=item_def["name"],
                    category=item_def["category"],
                    price=item_def["price"],
                ))

    if session is not None:
        _run(session)
    else:
        with get_db() as db:
            _run(db)
