from typing import List, Optional

from sqlalchemy.orm import Session

from backend.app.domain.models.menu_item import MenuItem
from backend.app.infrastructure.orm_models import MenuItemORM
from backend.app.infrastructure.repositories.base_repository import BaseRepository


class MenuRepository(BaseRepository[MenuItem, str]):
    """SQLAlchemy-backed repository for MenuItem entities."""

    def __init__(self, db: Session) -> None:
        self._db = db


# ------------------------------------------------------------------
    # BaseRepository contract
    # ------------------------------------------------------------------

    def get_by_id(self, entity_id: str) -> Optional[MenuItem]:
        orm_obj = self._db.get(MenuItemORM, entity_id)
        return self._to_domain(orm_obj) if orm_obj else None

    def get_all(self) -> List[MenuItem]:
        return [self._to_domain(m) for m in self._db.query(MenuItemORM).all()]

    def save(self, entity: MenuItem) -> MenuItem:
        orm_obj = self._to_orm(entity)
        merged = self._db.merge(orm_obj)
        self._db.flush()
        return self._to_domain(merged)

    def delete(self, entity_id: str) -> bool:
        orm_obj = self._db.get(MenuItemORM, entity_id)
        if orm_obj is None:
            return False
        self._db.delete(orm_obj)
        self._db.flush()
        return True

    # ------------------------------------------------------------------
    # Domain-specific queries
    # ------------------------------------------------------------------

    def get_by_restaurant(self, restaurant_id: str) -> List[MenuItem]:
        """Return all menu items for a given restaurant."""
        rows = (
            self._db.query(MenuItemORM)
            .filter(MenuItemORM.restaurant_id == restaurant_id)
            .all()
        )
        return [self._to_domain(r) for r in rows]

    def get_by_category(self, category: str) -> List[MenuItem]:
        """Return all menu items in a given cuisine category."""
        rows = (
            self._db.query(MenuItemORM)
            .filter(MenuItemORM.category == category)
            .all()
        )
        return [self._to_domain(r) for r in rows]

    def search_by_name(self, query: str) -> List[MenuItem]:
        """Case-insensitive partial name match across all restaurants."""
        rows = (
            self._db.query(MenuItemORM)
            .filter(MenuItemORM.name.ilike(f"%{query}%"))
            .all()
        )
        return [self._to_domain(r) for r in rows]

    def get_by_price_range(self, min_price: float, max_price: float) -> List[MenuItem]:
        """Return items whose price falls within the inclusive range."""
        rows = (
            self._db.query(MenuItemORM)
            .filter(MenuItemORM.price >= min_price, MenuItemORM.price <= max_price)
            .all()
        )
        return [self._to_domain(r) for r in rows]

    def get_paginated(
        self,
        restaurant_id: Optional[str] = None,
        offset: int = 0,
        limit: int = 20,
    ) -> List[MenuItem]:
        """
        Paginated item listing.
        Optionally scoped to a single restaurant if restaurant_id is provided.
        """
        q = self._db.query(MenuItemORM)
        if restaurant_id:
            q = q.filter(MenuItemORM.restaurant_id == restaurant_id)
        return [self._to_domain(r) for r in q.offset(offset).limit(limit).all()]

    # ------------------------------------------------------------------
    # Mapping helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _to_domain(orm_obj: MenuItemORM) -> MenuItem:
        return MenuItem(
            food_item_id=orm_obj.food_item_id,
            restaurant_id=orm_obj.restaurant_id,
            name=orm_obj.name,
            category=orm_obj.category,
            price=orm_obj.price,
        )

    @staticmethod
    def _to_orm(domain_obj: MenuItem) -> MenuItemORM:
        return MenuItemORM(
            food_item_id=domain_obj.food_item_id,
            restaurant_id=domain_obj.restaurant_id,
            name=domain_obj.name,
            category=domain_obj.category,
            price=domain_obj.price,
        )
