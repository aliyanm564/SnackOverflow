from backend.app.infrastructure.database import seed_from_csv
from backend.app.infrastructure.orm_models import UserORM, OrderORM, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

CSV_PATH = "backend/data/food_delivery.csv"  # ← fix to your actual path

def test_seed_row_counts():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()

    seed_from_csv(CSV_PATH, session=session)  # ← inject session

    assert session.query(UserORM).count() > 0

def test_seed_is_idempotent():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()

    seed_from_csv(CSV_PATH, session=session)
    count_first = session.query(UserORM).count()

    seed_from_csv(CSV_PATH, session=session)
    count_second = session.query(UserORM).count()

    assert count_first == count_second
