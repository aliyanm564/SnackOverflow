"""
notification_service.py
-----------------------
Handles notification use-cases (Feature 8).

Responsibilities
----------------
* Create a notification for a user when a domain event occurs.
* Retrieve all notifications for a user (newest first).
* Retrieve only unread notifications.
* Mark a single notification or all notifications for a user as read.
* Delete a notification.

Why notifications live in the application layer
-----------------------------------------------
Notifications are triggered by application events (order placed, payment
approved, etc.) that span multiple domain objects. They have no business
rules of their own, so they don't belong in the domain layer. They do need
persistence, so they live here and delegate to NotificationRepository.
"""

from typing import List

from backend.app.application.exceptions import AuthorizationError, NotFoundError
from backend.app.domain.models.user import User
from backend.app.infrastructure.repositories.notification_repository import (
    Notification,
    NotificationRepository,
)


class NotificationService:

    def __init__(self, notification_repository: NotificationRepository) -> None:
        self._notifications = notification_repository

    # ------------------------------------------------------------------
    # Creation (called by other services, not directly by routers)
    # ------------------------------------------------------------------

    def create(self, user_id: str, event_type: str, message: str) -> Notification:
        """
        Persist a new notification.

        This is the internal entry point used by OrderService, PaymentService,
        etc. It is intentionally simple — no validation needed because callers
        are trusted application services.
        """
        return self._notifications.create_notification(
            user_id=user_id,
            event_type=event_type,
            message=message,
        )

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    def get_all_for_user(self, requesting_user: User, user_id: str) -> List[Notification]:
        """
        Return all notifications for a user, newest first.

        Users may only retrieve their own notifications.
        Restaurant owners and delivery personnel can retrieve any user's
        notifications for operational purposes.
        """
        self._assert_can_read(requesting_user, user_id)
        return self._notifications.get_by_user(user_id)

    def get_unread_for_user(self, requesting_user: User, user_id: str) -> List[Notification]:
        """Return only unread notifications for a user."""
        self._assert_can_read(requesting_user, user_id)
        return self._notifications.get_unread_by_user(user_id)

    def get_notification(self, requesting_user: User, notification_id: int) -> Notification:
        """Fetch a single notification by ID."""
        notification = self._notifications.get_by_id(notification_id)
        if notification is None:
            raise NotFoundError(f"Notification '{notification_id}' not found.")
        self._assert_can_read(requesting_user, notification.user_id)
        return notification

    # ------------------------------------------------------------------
    # Mark as read
    # ------------------------------------------------------------------

    def mark_read(self, requesting_user: User, notification_id: int) -> Notification:
        """Mark a single notification as read."""
        notification = self._notifications.get_by_id(notification_id)
        if notification is None:
            raise NotFoundError(f"Notification '{notification_id}' not found.")

        self._assert_can_read(requesting_user, notification.user_id)

        updated = self._notifications.mark_as_read(notification_id)
        return updated

    def mark_all_read(self, requesting_user: User, user_id: str) -> int:
        """
        Mark all of a user's unread notifications as read.
        Returns the count of notifications updated.
        """
        self._assert_can_read(requesting_user, user_id)
        return self._notifications.mark_all_read_for_user(user_id)

    # ------------------------------------------------------------------
    # Deletion
    # ------------------------------------------------------------------

    def delete_notification(self, requesting_user: User, notification_id: int) -> None:
        """Delete a notification. Users can only delete their own."""
        notification = self._notifications.get_by_id(notification_id)
        if notification is None:
            raise NotFoundError(f"Notification '{notification_id}' not found.")
        self._assert_can_read(requesting_user, notification.user_id)
        self._notifications.delete(notification_id)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _assert_can_read(self, requesting_user: User, target_user_id: str) -> None:
        """
        Users may only read/manage their own notifications.
        Non-customer roles (owners, delivery staff) can read any user's
        notifications for operational oversight.
        """
        from backend.app.domain.models.user import UserRole
        if (
            requesting_user.role == UserRole.CUSTOMER
            and requesting_user.customer_id != target_user_id
        ):
            raise AuthorizationError(
                "You can only access your own notifications."
            )
