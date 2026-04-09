from typing import List, Optional

from sqlalchemy.orm import Session

from backend.app.domain.models.promo import PromoCode
from backend.app.infrastructure.orm_models import PromoAssignmentORM, PromoCodeORM
from backend.app.infrastructure.repositories.base_repository import BaseRepository


class PromoRepository(BaseRepository[PromoCode, str]):

    def __init__(self, db_session: Session):
        self._db = db_session

    def get_by_id(self, promo_id: str) -> Optional[PromoCode]:
        orm = self._db.get(PromoCodeORM, promo_id)
        return self._to_domain(orm) if orm else None

    def get_by_code(self, code: str) -> Optional[PromoCode]:
        orm = (
            self._db.query(PromoCodeORM)
            .filter(PromoCodeORM.code == code)
            .first()
        )
        return self._to_domain(orm) if orm else None

    def get_by_owner(self, owner_id: str) -> List[PromoCode]:
        rows = (
            self._db.query(PromoCodeORM)
            .filter(PromoCodeORM.owner_id == owner_id)
            .all()
        )
        return [self._to_domain(r) for r in rows]

    def get_all(self) -> List[PromoCode]:
        return [self._to_domain(r) for r in self._db.query(PromoCodeORM).all()]

    def save(self, entity: PromoCode) -> PromoCode:
        orm = self._to_orm(entity)
        merged = self._db.merge(orm)
        self._db.flush()
        return self._to_domain(merged)

    def delete(self, promo_id: str) -> bool:
        orm = self._db.get(PromoCodeORM, promo_id)
        if orm is None:
            return False
        self._db.delete(orm)
        self._db.flush()
        return True

    def add_assignment(self, promo_id: str, customer_id: str) -> None:
        existing = self._db.get(PromoAssignmentORM, (promo_id, customer_id))
        if existing is None:
            self._db.add(PromoAssignmentORM(promo_id=promo_id, customer_id=customer_id))
            self._db.flush()

    def remove_assignment(self, promo_id: str, customer_id: str) -> None:
        existing = self._db.get(PromoAssignmentORM, (promo_id, customer_id))
        if existing is not None:
            self._db.delete(existing)
            self._db.flush()

    def _get_assigned_ids(self, promo_id: str) -> List[str]:
        rows = (
            self._db.query(PromoAssignmentORM)
            .filter(PromoAssignmentORM.promo_id == promo_id)
            .all()
        )
        return [r.customer_id for r in rows]

    def _to_domain(self, orm: PromoCodeORM) -> PromoCode:
        return PromoCode(
            promo_id=orm.promo_id,
            code=orm.code,
            discount_type=orm.discount_type,
            discount_value=orm.discount_value,
            expiry_date=orm.expiry_date,
            usage_limit=orm.usage_limit,
            usage_count=orm.usage_count,
            is_active=orm.is_active,
            owner_id=orm.owner_id,
            assigned_customer_ids=self._get_assigned_ids(orm.promo_id),
        )

    def _to_orm(self, domain: PromoCode) -> PromoCodeORM:
        return PromoCodeORM(
            promo_id=domain.promo_id,
            code=domain.code,
            discount_type=domain.discount_type,
            discount_value=domain.discount_value,
            expiry_date=domain.expiry_date,
            usage_limit=domain.usage_limit,
            usage_count=domain.usage_count,
            is_active=domain.is_active,
            owner_id=domain.owner_id,
        )
