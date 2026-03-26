from typing import List

from backend.app.application.exceptions import AuthorizationError, NotFoundError
from backend.app.domain.models.notification import Notification
from backend.app.domain.models.user import User
from backend.app.domain.models.user import UserRole
from backend.app.infrastructure.repositories.notification_repository import NotificationRepository

class NotificationService:

    def __init__(self, notification_repository: NotificationRepository) -> None:
        self._notifications = notification_repository

    def create(self, user_id: str, event_type: str, message: str) -> Notification:

        return self._notifications.create_notification(
            user_id=user_id,
            event_type=event_type,
            message=message,
        )

    def get_all_for_user(self, requesting_user: User, user_id: str) -> List[Notification]:
        self._assert_can_read(requesting_user, user_id)
        return self._notifications.get_by_user(user_id)

    def get_unread_for_user(self, requesting_user: User, user_id: str) -> List[Notification]:
        self._assert_can_read(requesting_user, user_id)
        return self._notifications.get_unread_by_user(user_id)

    def get_notification(self, requesting_user: User, notification_id: int) -> Notification:
        return self._get_notification_for_user(requesting_user, notification_id)

    def mark_read(self, requesting_user: User, notification_id: int) -> Notification:
        self._get_notification_for_user(requesting_user, notification_id)
        updated = self._notifications.mark_as_read(notification_id)
        if updated is None:
            raise NotFoundError(f"Notification '{notification_id}' not found.")
        return updated

    def mark_all_read(self, requesting_user: User, user_id: str) -> int:
        self._assert_can_read(requesting_user, user_id)
        return self._notifications.mark_all_read_for_user(user_id)

    def delete_notification(self, requesting_user: User, notification_id: int) -> None:
        """Delete a notification. Users can only delete their own."""
        self._get_notification_for_user(requesting_user, notification_id)
        self._notifications.delete(notification_id)

    def _assert_can_read(self, requesting_user: User, target_user_id: str) -> None:
        if (
            requesting_user.role == UserRole.CUSTOMER
            and requesting_user.customer_id != target_user_id
        ):
            raise AuthorizationError(
                "You can only access your own notifications."
            )

    def _get_notification_for_user(
        self,
        requesting_user: User,
        notification_id: int,
    ) -> Notification:
        notification = self._notifications.get_by_id(notification_id)
        if notification is None:
            raise NotFoundError(f"Notification '{notification_id}' not found.")
        self._assert_can_read(requesting_user, notification.user_id)
        return notification
