"""
delivery_repository.py
----------------------
Concrete repository for Delivery persistence.

Responsibilities
----------------
* CRUD on the `deliveries` table.
* Domain-specific queries: filter by delivery method, route type,
  weather/traffic condition, and delayed deliveries.
* ORM ↔ domain mapping.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from backend.app.domain.models.delivery import Delivery
from backend.app.domain.models.enums import DeliveryMethod, RouteType
from backend.app.infrastructure.orm_models import DeliveryORM
from backend.app.infrastructure.repositories.base_repository import BaseRepository

class DeliveryRepository(BaseRepository[Delivery, str]):
    def __init__(self, db_session: Session):
        self._db = db_session

    # ------------------------------------------------------------------
    # BaseRepository contract
    # ------------------------------------------------------------------

    def get_by_id(self, entity_id: str) -> Optional[Delivery]:
        """Fetch a Delivery by its ID."""
        orm_obj = self._db.get(DeliveryORM, entity_id)
        return self._to_domain(orm_obj) if orm_obj else None

    def get_all(self) -> List[Delivery]:
        return [self._to_domain(d) for d in self._db.query(DeliveryORM).all()]

    def save(self, entity: Delivery) -> Delivery:
        orm_obj = self._to_orm(entity)
        merged = self._db.merge(orm_obj)
        self._db.flush()
        return self._to_domain(merged)

    def delete(self, entity_id: str) -> bool:
        orm_obj = self._db.get(DeliveryORM, entity_id)
        if orm_obj is None:
            return False 
        self._db.delete(orm_obj)
        self._db.flush()
        return True

    # ------------------------------------------------------------------
    # Domain-specific queries
    # ------------------------------------------------------------------
            
    def get_by_delivery_method(self, method: DeliveryMethod) -> List[Delivery]:
        """return all delieveries with the specified delivery method."""
        rows = (
            self._db.query(DeliveryORM)
            .filter(DeliveryORM.delivery_method == method.value)
            .all()
        )
        return [self._to_domain(r) for r in rows]

    def get_by_route_type(self, route_type: RouteType) -> List[Delivery]:
        """return all delieveries with the specified route type."""
        rows = (
            self._db.query(DeliveryORM)
            .filter(DeliveryORM.route_type == route_type.value)
            .all()
        )
        return [self._to_domain(r) for r in rows]

    def get_delayed(self, min_delay_minutes: float = 0.0) -> List[Delivery]:
        """return deliveries whose delay exceeds the given threshold."""
        rows = (
            self._db.query(DeliveryORM)
            .filter(DeliveryORM.delivery_delay > min_delay_minutes)
            .order_by(DeliveryORM.delivery_delay.desc())
            .all() 
        )
        return [self._to_domain(r) for r in rows]

    def get_by_traffic_condition(self, condition:str) -> List[Delivery]:
        """Filter deliveries by traffic condition."""
        rows = (
            self._db.query(DeliveryORM)
            .filter(DeliveryORM.traffic_condition == condition)
            .all()
        )
        return [self._to_domain(r) for r in rows]

    def get_by_weather_condition(self, condition:str) -> List[Delivery]:
        """Filter deliveries by weather condition."""
        rows = (
            self._db.query(DeliveryORM)
            .filter(DeliveryORM.weather_condition == condition)
            .all()
        )
        return [self._to_domain(r) for r in rows]

    def get_paginated(self, offset: int = 0, limit: int = 20) -> List[Delivery]:
        rows = (
            self._db.query(DeliveryORM)
            .offset(offset)
            .limit(limit)
            .all()
        )
        return [self._to_domain(r) for r in rows]

    # ------------------------------------------------------------------
    # Mapping helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _to_domain(orm_obj: DeliveryORM) -> Delivery:
        method = None
        if orm_obj.delivery_method:
            try:
                method = DeliveryMethod(orm_obj.delivery_method.lower())
            except ValueError:
                pass

        route_type = None
        if orm_obj.route_type:
            try:
                route_type = RouteType(orm_obj.route_type.lower())
            except ValueError:
                pass

        return Delivery(
            order_id=orm_obj.order_id,
            delivery_time =orm_obj.delivery_time,
            delivery_time_actual=orm_obj.delivery_time_actual,
            delivery_delay = orm_obj.delivery_delay,
            delivery_distance = orm_obj.delivery_distance,
            delivery_method=method,
            route_taken =orm_obj.route_taken,
            route_type = route_type,
            route_efficiency=orm_obj.route_efficiency,
                traffic_condition=orm_obj.traffic_condition,
                weather_condition=orm_obj.weather_condition,
                predicted_delivery_mode=orm_obj.predicted_delivery_mode,
                traffic_avoidance=orm_obj.traffic_avoidance,
            )

    @staticmethod
    def _to_orm(domain_obj: Delivery) -> DeliveryORM:
            return DeliveryORM(
                order_id=domain_obj.order_id,
                delivery_time=domain_obj.delivery_time,
                delivery_time_actual=domain_obj.delivery_time_actual,
                delivery_delay=domain_obj.delivery_delay,
                delivery_distance=domain_obj.delivery_distance,
                delivery_method=domain_obj.delivery_method.value if domain_obj.delivery_method else None,
                route_taken=domain_obj.route_taken,
                route_type=domain_obj.route_type.value if domain_obj.route_type else None,
                route_efficiency=domain_obj.route_efficiency,
                traffic_condition=domain_obj.traffic_condition,
                weather_condition=domain_obj.weather_condition,
                predicted_delivery_mode=domain_obj.predicted_delivery_mode,
                traffic_avoidance=domain_obj.traffic_avoidance,
            )
        