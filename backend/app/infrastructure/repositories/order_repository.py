from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from backend.app.domain.models.enums import OrderStatus
from backend.app.domain.models.orders import Order
from backend.app.infrastructure.orm_models import OrderORM
from backend.app.infrastructure.repositories.base_repository import BaseRepository

_ITEMS_SEP = ","


class OrderRepository(BaseRepository[Order, str]):
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_id(self, entity_id: str) -> Optional[Order]:
        orm_obj = self._db.get(OrderORM, entity_id)
        return self._to_domain(orm_obj) if orm_obj else None

    def get_all(self) -> List[Order]:
        return [self._to_domain(o) for o in self._db.query(OrderORM).all()]

    def save(self, entity: Order) -> Order:
        orm_obj = self._to_orm(entity)
        merged = self._db.merge(orm_obj)
        self._db.flush()
        return self._to_domain(merged)

    def delete(self, entity_id: str) -> bool:
        orm_obj = self._db.get(OrderORM, entity_id)
        if orm_obj is None:
            return False
        self._db.delete(orm_obj)
        self._db.flush()
        return True

    def get_by_customer(self, customer_id: str) -> List[Order]:
        rows = (
            self._db.query(OrderORM)
            .filter(OrderORM.customer_id == customer_id)
            .order_by(OrderORM.order_time.desc())
            .all()
        )
        return [self._to_domain(r) for r in rows]

    def get_by_restaurant(self, restaurant_id: str) -> List[Order]:
        rows = (
            self._db.query(OrderORM)
            .filter(OrderORM.restaurant_id == restaurant_id)
            .order_by(OrderORM.order_time.desc())
            .all()
        )
        return [self._to_domain(r) for r in rows]

    def get_by_status(self, status: OrderStatus) -> List[Order]:
        rows = (
            self._db.query(OrderORM)
            .filter(OrderORM.status == status.value)
            .all()
        )
        return [self._to_domain(r) for r in rows]

    def get_by_customer_and_status(
        self, customer_id: str, status: OrderStatus
    ) -> List[Order]:
        rows = (
            self._db.query(OrderORM)
            .filter(
                OrderORM.customer_id == customer_id,
                OrderORM.status == status.value,
            )
            .all()
        )
        return [self._to_domain(r) for r in rows]

    def update_status(self, order_id: str, new_status: OrderStatus) -> Optional[Order]:
        orm_obj = self._db.get(OrderORM, order_id)
        if orm_obj is None:
            return None
        orm_obj.status = new_status.value
        self._db.flush()
        return self._to_domain(orm_obj)

    def get_paginated(
        self,
        customer_id: Optional[str] = None,
        restaurant_id: Optional[str] = None,
        offset: int = 0,
        limit: int = 20,
    ) -> List[Order]:
        q = self._db.query(OrderORM)
        if customer_id:
            q = q.filter(OrderORM.customer_id == customer_id)
        if restaurant_id:
            q = q.filter(OrderORM.restaurant_id == restaurant_id)
        q = q.order_by(OrderORM.order_time.desc()).offset(offset).limit(limit)
        return [self._to_domain(r) for r in q.all()]

    @staticmethod
    def _to_domain(orm_obj: OrderORM) -> Order:
        items = (
            [i for i in orm_obj.items.split(_ITEMS_SEP) if i]
            if orm_obj.items
            else []
        )
        return Order(
            order_id=orm_obj.order_id,
            customer_id=orm_obj.customer_id,
            restaurant_id=orm_obj.restaurant_id,
            items=items,
            order_time=orm_obj.order_time,
            order_value=orm_obj.order_value,
            status=OrderStatus(orm_obj.status),
            customer_rating=orm_obj.customer_rating,
            customer_satisfaction=orm_obj.customer_satisfaction,
        )

    @staticmethod
    def _to_orm(domain_obj: Order) -> OrderORM:
        return OrderORM(
            order_id=domain_obj.order_id,
            customer_id=domain_obj.customer_id,
            restaurant_id=domain_obj.restaurant_id,
            items=_ITEMS_SEP.join(domain_obj.items),
            order_time=domain_obj.order_time,
            order_value=domain_obj.order_value,
            status=domain_obj.status.value,
            customer_rating=domain_obj.customer_rating,
            customer_satisfaction=domain_obj.customer_satisfaction,
        )
