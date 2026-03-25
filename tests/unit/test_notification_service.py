from datetime import datetime, timezone

import pytest

from backend.app.application.exceptions import AuthorizationError, NotFoundError
from backend.app.application.services.notification_service import NotificationService
from backend.app.domain.models.notification import Notification


def make_service(notification_repo):
    return NotificationService(notification_repository=notification_repo)


def make_notification(
    notification_id: int = 1,
    user_id: str = "cust-001",
    event_type: str = "order_created",
    message: str = "Order created",
    is_read: bool = False,
) -> Notification:
    return Notification(
        notification_id=notification_id,
        user_id=user_id,
        event_type=event_type,
        message=message,
        created_at=datetime.now(tz=timezone.utc),
        is_read=is_read,
    )


class TestCreate:

    def test_create_delegates_to_repository(self, mock_notification_repo):
        created = make_notification()
        mock_notification_repo.create_notification.return_value = created
        service = make_service(mock_notification_repo)

        result = service.create("cust-001", "order_created", "Order created")

        assert result == created
        mock_notification_repo.create_notification.assert_called_once_with(
            user_id="cust-001",
            event_type="order_created",
            message="Order created",
        )


class TestRetrieval:

    def test_get_all_for_user_returns_notifications_for_own_account(
        self,
        mock_notification_repo,
        customer_user,
    ):
        notifications = [make_notification(notification_id=1), make_notification(notification_id=2)]
        mock_notification_repo.get_by_user.return_value = notifications
        service = make_service(mock_notification_repo)

        result = service.get_all_for_user(customer_user, customer_user.customer_id)

        assert result == notifications
        mock_notification_repo.get_by_user.assert_called_once_with(customer_user.customer_id)

    def test_get_all_for_user_blocks_customer_from_other_user(
        self,
        mock_notification_repo,
        customer_user,
    ):
        service = make_service(mock_notification_repo)

        with pytest.raises(AuthorizationError):
            service.get_all_for_user(customer_user, "someone-else")

    def test_get_all_for_user_allows_owner_to_read_other_user(
        self,
        mock_notification_repo,
        owner_user,
    ):
        notifications = [make_notification(user_id="cust-001")]
        mock_notification_repo.get_by_user.return_value = notifications
        service = make_service(mock_notification_repo)

        result = service.get_all_for_user(owner_user, "cust-001")

        assert result == notifications

    def test_get_unread_for_user_returns_unread_notifications(
        self,
        mock_notification_repo,
        customer_user,
    ):
        unread = [make_notification(notification_id=3, is_read=False)]
        mock_notification_repo.get_unread_by_user.return_value = unread
        service = make_service(mock_notification_repo)

        result = service.get_unread_for_user(customer_user, customer_user.customer_id)

        assert result == unread
        mock_notification_repo.get_unread_by_user.assert_called_once_with(
            customer_user.customer_id
        )

    def test_get_notification_returns_single_notification(
        self,
        mock_notification_repo,
        customer_user,
    ):
        notification = make_notification(notification_id=10, user_id=customer_user.customer_id)
        mock_notification_repo.get_by_id.return_value = notification
        service = make_service(mock_notification_repo)

        result = service.get_notification(customer_user, 10)

        assert result == notification

    def test_get_notification_raises_for_missing_notification(
        self,
        mock_notification_repo,
        customer_user,
    ):
        mock_notification_repo.get_by_id.return_value = None
        service = make_service(mock_notification_repo)

        with pytest.raises(NotFoundError):
            service.get_notification(customer_user, 999)


class TestMarkRead:

    def test_mark_read_updates_notification(
        self,
        mock_notification_repo,
        customer_user,
    ):
        notification = make_notification(notification_id=7, user_id=customer_user.customer_id)
        updated = make_notification(
            notification_id=7,
            user_id=customer_user.customer_id,
            is_read=True,
        )
        mock_notification_repo.get_by_id.return_value = notification
        mock_notification_repo.mark_as_read.return_value = updated
        service = make_service(mock_notification_repo)

        result = service.mark_read(customer_user, 7)

        assert result == updated
        mock_notification_repo.mark_as_read.assert_called_once_with(7)

    def test_mark_read_rejects_other_users(
        self,
        mock_notification_repo,
        customer_user,
    ):
        mock_notification_repo.get_by_id.return_value = make_notification(
            notification_id=8,
            user_id="someone-else",
        )
        service = make_service(mock_notification_repo)

        with pytest.raises(AuthorizationError):
            service.mark_read(customer_user, 8)

    def test_mark_all_read_returns_updated_count(
        self,
        mock_notification_repo,
        customer_user,
    ):
        mock_notification_repo.mark_all_read_for_user.return_value = 3
        service = make_service(mock_notification_repo)

        result = service.mark_all_read(customer_user, customer_user.customer_id)

        assert result == 3
        mock_notification_repo.mark_all_read_for_user.assert_called_once_with(
            customer_user.customer_id
        )


class TestDelete:

    def test_delete_notification_deletes_existing_record(
        self,
        mock_notification_repo,
        customer_user,
    ):
        notification = make_notification(notification_id=11, user_id=customer_user.customer_id)
        mock_notification_repo.get_by_id.return_value = notification
        service = make_service(mock_notification_repo)

        service.delete_notification(customer_user, 11)

        mock_notification_repo.delete.assert_called_once_with(11)

    def test_delete_notification_raises_for_missing_record(
        self,
        mock_notification_repo,
        customer_user,
    ):
        mock_notification_repo.get_by_id.return_value = None
        service = make_service(mock_notification_repo)

        with pytest.raises(NotFoundError):
            service.delete_notification(customer_user, 12)
