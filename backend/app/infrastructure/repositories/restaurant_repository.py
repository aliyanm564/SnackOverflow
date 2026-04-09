from typing import List, Optional
from sqlalchemy.orm import Session 
from backend.app.domain.models.restaurant import Restaurant
from backend.app.infrastructure.orm_models import RestaurantORM
from backend.app.infrastructure.repositories.base_repository import BaseRepository

class RestaurantRepository(BaseRepository[Restaurant, str]):

    def __init__(self, db_session: Session) -> None:
        self._db = db_session

    def get_by_id(self, entity_id: str) -> Optional[Restaurant]:
        orm_obj = self._db.get(RestaurantORM, entity_id) 
        return self._to_domain(orm_obj) if orm_obj else None

    def get_all(self) -> List[Restaurant]:
        return [self._to_domain(r) for r in self._db.query(RestaurantORM).all()]
    
    def save(self, entity: Restaurant) -> Restaurant:
        orm_obj = self._to_orm(entity)
        merged = self._db.merge(orm_obj)
        self._db.flush()
        return self._to_domain(merged)
    
    def delete(self, entity_id: str) -> bool:
        orm_obj = self._db.get(RestaurantORM, entity_id)
        if orm_obj is None: 
            return False
        self._db.delete(orm_obj)
        self._db.flush()
        return True

    def get_by_owner(self, owner_id: str) -> List[Restaurant]:
        rows = ( 
            self._db.query(RestaurantORM)
            .filter(RestaurantORM.owner_id == owner_id)
            .all()
        )
        return [self._to_domain(r) for r in rows]
    
    def get_by_location(self, location: str) -> List[Restaurant]:
        rows = ( 
            self._db.query(RestaurantORM)
            .filter(RestaurantORM.location == location)
            .all()
        )
        return [self._to_domain(r) for r in rows]
    
    def search_by_name(self, query: str) -> List[Restaurant]:
        rows = ( 
            self._db.query(RestaurantORM)
            .filter(RestaurantORM.name.ilike(f"%{query}%"))
            .all()
        )
        return [self._to_domain(r) for r in rows]
    
    def get_paginated(self, offset: int = 0, limit: int = 20) -> List[Restaurant]:
        rows = ( 
            self._db.query(RestaurantORM)
            .offset(offset)
            .limit(limit)
            .all()
        )
        return [self._to_domain(r) for r in rows]
    
    @staticmethod
    def _to_domain(orm_obj: RestaurantORM) -> Restaurant:
        return Restaurant(
            restaurant_id=orm_obj.restaurant_id,
            owner_id=orm_obj.owner_id,
            name=orm_obj.name,
            location=orm_obj.location,
            description=orm_obj.description,
            avg_rating=orm_obj.avg_rating,
            review_count=orm_obj.review_count or 0,
        )

    @staticmethod
    def _to_orm(domain_obj: Restaurant) -> RestaurantORM:
        return RestaurantORM(
            restaurant_id=domain_obj.restaurant_id,
            owner_id=domain_obj.owner_id or None,
            name=domain_obj.name,
            location=domain_obj.location,
            description=domain_obj.description,
            avg_rating=domain_obj.avg_rating,
            review_count=domain_obj.review_count,
        )
