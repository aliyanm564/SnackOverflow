from typing import List, Optional

from sqlalchemy.orm import Session

from backend.app.domain.models.user import User, UserRole
from backend.app.infrastructure.orm_models import UserORM
from backend.app.infrastructure.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User, str]):

    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_id(self, entity_id: str) -> Optional[User]:
        orm_obj = self._db.get(UserORM, entity_id)
        return self._to_domain(orm_obj) if orm_obj else None

    def get_all(self) -> List[User]:
        return [self._to_domain(user) for user in self._db.query(UserORM).all()]

    def save(self, entity: User) -> User:
        orm_obj = self._to_orm(entity)
        merged = self._db.merge(orm_obj)
        self._db.flush()
        return self._to_domain(merged)

    def delete(self, entity_id: str) -> bool:
        orm_obj = self._db.get(UserORM, entity_id)
        if orm_obj is None:
            return False
        self._db.delete(orm_obj)
        self._db.flush()
        return True

    def get_by_email(self, email: str) -> Optional[User]:
        orm_obj = self._db.query(UserORM).filter(UserORM.email == email).first()
        return self._to_domain(orm_obj) if orm_obj else None

    def get_by_role(self, role: UserRole) -> List[User]:
        rows = self._db.query(UserORM).filter(UserORM.role == role.value).all()
        return [self._to_domain(row) for row in rows]

    def get_by_location(self, location: str) -> List[User]:
        rows = self._db.query(UserORM).filter(UserORM.location == location).all()
        return [self._to_domain(row) for row in rows]

    def get_hashed_password(self, customer_id: str) -> Optional[str]:
        row = self._db.get(UserORM, customer_id)
        return row.hashed_password if row else None

    def set_hashed_password(self, customer_id: str, hashed_password: str) -> None:
        row = self._db.get(UserORM, customer_id)
        if row:
            row.hashed_password = hashed_password
            self._db.flush()

    @staticmethod
    def _to_domain(orm_obj: UserORM) -> User:
        return User(
            customer_id=orm_obj.customer_id,
            name=orm_obj.name,
            age=orm_obj.age,
            gender=orm_obj.gender,
            location=orm_obj.location,
            loyalty_program=orm_obj.loyalty_program,
            order_history=[],
            preferred_cuisine=orm_obj.preferred_cuisine,
            order_frequency=orm_obj.order_frequency,
            role=UserRole(orm_obj.role),
        )

    @staticmethod
    def _to_orm(domain_obj: User) -> UserORM:
        return UserORM(
            customer_id=domain_obj.customer_id,
            name=domain_obj.name,
            age=domain_obj.age,
            gender=domain_obj.gender,
            location=domain_obj.location,
            loyalty_program=domain_obj.loyalty_program,
            order_history_count=len(domain_obj.order_history),
            preferred_cuisine=domain_obj.preferred_cuisine,
            order_frequency=domain_obj.order_frequency,
            role=domain_obj.role.value,
        )
