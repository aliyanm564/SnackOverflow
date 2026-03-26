from datetime import datetime, timezone
from unittest.mock import MagicMock

from backend.app.application.exceptions import AuthorizationError, NotFoundError
from backend.app.domain.models.notification import Notification
from backend.app.presentation.dependencies import get_notification_service


NOTIFICATION_URL = "/api/v1/notifications"


def make_notification(
    notification_id: int = 1,
    user_id: str = "api-cust-001",
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


class TestGetNotifications:

    def test_get_my_notifications_returns_200(
        self, client, customer, customer_headers, override
    ):
        notifications = [make_notification(notification_id=1, user_id=customer.customer_id)]
        mock_svc = MagicMock()
        mock_svc.get_all_for_user.return_value = notifications

        with override(get_notification_service, mock_svc, current_user=customer):
            resp = client.get(NOTIFICATION_URL, headers=customer_headers)

        assert resp.status_code == 200
        assert len(resp.json()) == 1
        mock_svc.get_all_for_user.assert_called_once_with(
            customer, customer.customer_id
        )

    def test_get_unread_notifications_returns_200(
        self, client, customer, customer_headers, override
    ):
        notifications = [make_notification(notification_id=2, user_id=customer.customer_id)]
        mock_svc = MagicMock()
        mock_svc.get_unread_for_user.return_value = notifications

        with override(get_notification_service, mock_svc, current_user=customer):
            resp = client.get(f"{NOTIFICATION_URL}/unread", headers=customer_headers)

        assert resp.status_code == 200
        assert len(resp.json()) == 1
        mock_svc.get_unread_for_user.assert_called_once_with(
            customer, customer.customer_id
        )


class TestMarkRead:

    def test_mark_notification_read_returns_200(
        self, client, customer, customer_headers, override
    ):
        updated = make_notification(
            notification_id=3,
            user_id=customer.customer_id,
            is_read=True,
        )
        mock_svc = MagicMock()
        mock_svc.mark_read.return_value = updated

        with override(get_notification_service, mock_svc, current_user=customer):
            resp = client.patch(f"{NOTIFICATION_URL}/3/read", headers=customer_headers)

        assert resp.status_code == 200
        assert resp.json()["is_read"] is True
        mock_svc.mark_read.assert_called_once_with(customer, 3)

    def test_mark_notification_read_returns_404(
        self, client, customer, customer_headers, override
    ):
        mock_svc = MagicMock()
        mock_svc.mark_read.side_effect = NotFoundError("Notification not found.")

        with override(get_notification_service, mock_svc, current_user=customer):
            resp = client.patch(f"{NOTIFICATION_URL}/9/read", headers=customer_headers)

        assert resp.status_code == 404

    def test_mark_notification_read_returns_403(
        self, client, customer, customer_headers, override
    ):
        mock_svc = MagicMock()
        mock_svc.mark_read.side_effect = AuthorizationError("Forbidden.")

        with override(get_notification_service, mock_svc, current_user=customer):
            resp = client.patch(f"{NOTIFICATION_URL}/9/read", headers=customer_headers)

        assert resp.status_code == 403


class TestMarkAllRead:

    def test_mark_all_read_returns_count(
        self, client, customer, customer_headers, override
    ):
        mock_svc = MagicMock()
        mock_svc.mark_all_read.return_value = 3

        with override(get_notification_service, mock_svc, current_user=customer):
            resp = client.patch(f"{NOTIFICATION_URL}/read-all", headers=customer_headers)

        assert resp.status_code == 200
        assert resp.json() == {"marked_read": 3}
        mock_svc.mark_all_read.assert_called_once_with(customer, customer.customer_id)


class TestDeleteNotification:

    def test_delete_notification_returns_204(
        self, client, customer, customer_headers, override
    ):
        mock_svc = MagicMock()

        with override(get_notification_service, mock_svc, current_user=customer):
            resp = client.delete(f"{NOTIFICATION_URL}/12", headers=customer_headers)

        assert resp.status_code == 204
        mock_svc.delete_notification.assert_called_once_with(customer, 12)

    def test_delete_notification_returns_404(
        self, client, customer, customer_headers, override
    ):
        mock_svc = MagicMock()
        mock_svc.delete_notification.side_effect = NotFoundError("Notification not found.")

        with override(get_notification_service, mock_svc, current_user=customer):
            resp = client.delete(f"{NOTIFICATION_URL}/12", headers=customer_headers)

        assert resp.status_code == 404

    def test_delete_notification_returns_403(
        self, client, customer, customer_headers, override
    ):
        mock_svc = MagicMock()
        mock_svc.delete_notification.side_effect = AuthorizationError("Forbidden.")

        with override(get_notification_service, mock_svc, current_user=customer):
            resp = client.delete(f"{NOTIFICATION_URL}/12", headers=customer_headers)

        assert resp.status_code == 403
