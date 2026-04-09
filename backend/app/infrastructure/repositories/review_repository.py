from typing import List, Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.app.domain.models.review import Review
from backend.app.infrastructure.orm_models import ReviewORM
from backend.app.infrastructure.repositories.base_repository import BaseRepository


class ReviewRepository(BaseRepository[Review, str]):

    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_id(self, review_id: str) -> Optional[Review]:
        orm_obj = self._db.get(ReviewORM, review_id)
        return self._to_domain(orm_obj) if orm_obj else None

    def get_by_order(self, order_id: str) -> Optional[Review]:
        orm_obj = (
            self._db.query(ReviewORM)
            .filter(ReviewORM.order_id == order_id)
            .first()
        )
        return self._to_domain(orm_obj) if orm_obj else None

    def get_by_restaurant(self, restaurant_id: str) -> List[Review]:
        rows = (
            self._db.query(ReviewORM)
            .filter(ReviewORM.restaurant_id == restaurant_id)
            .order_by(ReviewORM.created_at.desc())
            .all()
        )
        return [self._to_domain(r) for r in rows]

    def get_by_customer(self, customer_id: str) -> List[Review]:
        rows = (
            self._db.query(ReviewORM)
            .filter(ReviewORM.customer_id == customer_id)
            .order_by(ReviewORM.created_at.desc())
            .all()
        )
        return [self._to_domain(r) for r in rows]

    def save(self, review: Review) -> Review:
        orm_obj = self._to_orm(review)
        merged = self._db.merge(orm_obj)
        self._db.flush()
        return self._to_domain(merged)

    def get_aggregate(self, restaurant_id: str) -> Tuple[float, int]:
        result = (
            self._db.query(
                func.avg(ReviewORM.rating),
                func.count(ReviewORM.review_id),
            )
            .filter(ReviewORM.restaurant_id == restaurant_id)
            .one()
        )
        avg = float(result[0]) if result[0] is not None else 0.0
        count = int(result[1]) if result[1] is not None else 0
        return avg, count

    def get_all(self) -> List[Review]:
        return [self._to_domain(r) for r in self._db.query(ReviewORM).all()]

    def delete(self, review_id: str) -> bool:
        orm_obj = self._db.get(ReviewORM, review_id)
        if orm_obj is None:
            return False
        self._db.delete(orm_obj)
        self._db.flush()
        return True

    @staticmethod
    def _to_domain(orm_obj: ReviewORM) -> Review:
        return Review(
            review_id=orm_obj.review_id,
            order_id=orm_obj.order_id,
            customer_id=orm_obj.customer_id,
            restaurant_id=orm_obj.restaurant_id,
            rating=orm_obj.rating,
            comment=orm_obj.comment,
            created_at=orm_obj.created_at,
            updated_at=orm_obj.updated_at,
        )

    @staticmethod
    def _to_orm(domain_obj: Review) -> ReviewORM:
        return ReviewORM(
            review_id=domain_obj.review_id,
            order_id=domain_obj.order_id,
            customer_id=domain_obj.customer_id,
            restaurant_id=domain_obj.restaurant_id,
            rating=domain_obj.rating,
            comment=domain_obj.comment,
            created_at=domain_obj.created_at,
            updated_at=domain_obj.updated_at,
        )
