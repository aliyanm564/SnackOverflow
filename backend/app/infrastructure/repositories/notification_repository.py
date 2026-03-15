from datetime import datetime, timezone
from typing import List, NamedTuple, Optional

from sqlalchemy.orm import Session

from backend.app.infrastructure.orm_models import NotificationORM
from backend.app.infrastructure.repositories.base_repository import BaseRepository


class Notification(NamedTuple):

    notification_id: int
    user_id: str
    event_type: str
    message: str
    created_at: datetime
    is_read: bool


class NotificationRepository(BaseRepository[Notification, int]):
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_id(self, entity_id: int) -> Optional[Notification]:
        orm_obj = self._db.get(NotificationORM, entity_id)
        return self._to_domain(orm_obj) if orm_obj else None

    def get_all(self) -> List[Notification]:
        return [self._to_domain(n) for n in self._db.query(NotificationORM).all()]

    def save(self, entity: Notification) -> Notification:
        orm_obj = NotificationORM(
            user_id=entity.user_id,
            event_type=entity.event_type,
            message=entity.message,
            created_at=entity.created_at,
            is_read=entity.is_read,
        )
        if entity.notification_id:
            orm_obj.notification_id = entity.notification_id
            orm_obj = self._db.merge(orm_obj)
        else:
            self._db.add(orm_obj)

        self._db.flush()
        return self._to_domain(orm_obj)

    def delete(self, entity_id: int) -> bool:
        orm_obj = self._db.get(NotificationORM, entity_id)
        if orm_obj is None:
            return False
        self._db.delete(orm_obj)
        self._db.flush()
        return True

    def get_by_user(self, user_id: str) -> List[Notification]:
        rows = (
            self._db.query(NotificationORM)
            .filter(NotificationORM.user_id == user_id)
            .order_by(NotificationORM.created_at.desc())
            .all()
        )
        return [self._to_domain(r) for r in rows]

    def get_unread_by_user(self, user_id: str) -> List[Notification]:
        rows = (
            self._db.query(NotificationORM)
            .filter(
                NotificationORM.user_id == user_id,
                NotificationORM.is_read == False,  # noqa: E712
            )
            .order_by(NotificationORM.created_at.desc())
            .all()
        )
        return [self._to_domain(r) for r in rows]

    def get_by_event_type(self, event_type: str) -> List[Notification]:
        rows = (
            self._db.query(NotificationORM)
            .filter(NotificationORM.event_type == event_type)
            .all()
        )
        return [self._to_domain(r) for r in rows]

    def mark_as_read(self, notification_id: int) -> Optional[Notification]:
        orm_obj = self._db.get(NotificationORM, notification_id)
        if orm_obj is None:
            return None
        orm_obj.is_read = True
        self._db.flush()
        return self._to_domain(orm_obj)

    def mark_all_read_for_user(self, user_id: str) -> int:
        updated = (
            self._db.query(NotificationORM)
            .filter(
                NotificationORM.user_id == user_id,
                NotificationORM.is_read == False,  # noqa: E712
            )
            .update({"is_read": True})
        )
        self._db.flush()
        return updated

    def create_notification(
        self,
        user_id: str,
        event_type: str,
        message: str,
    ) -> Notification:
        orm_obj = NotificationORM(
            user_id=user_id,
            event_type=event_type,
            message=message,
            created_at = datetime.now(timezone.utc),
            is_read=False,
        )
        self._db.add(orm_obj)
        self._db.flush()
        return self._to_domain(orm_obj)

    @staticmethod
    def _to_domain(orm_obj: NotificationORM) -> Notification:
        created_at = orm_obj.created_at
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)

        return Notification(
            notification_id=orm_obj.notification_id,
            user_id=orm_obj.user_id,
            event_type=orm_obj.event_type,
            message=orm_obj.message,
            created_at=created_at,
            is_read=orm_obj.is_read,
    )
