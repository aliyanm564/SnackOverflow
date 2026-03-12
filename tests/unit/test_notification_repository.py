from datetime import datetime, timedelta, timezone

from backend.app.infrastructure.repositories.notification_repository import (
    Notification,
    NotificationRepository,
)


def test_save_and_get_by_id(db_session):
    repo = NotificationRepository(db_session)
    created_at = datetime.now(timezone.utc)

    saved = repo.save(
        Notification(
            notification_id=0,
            user_id="user-1",
            event_type="order_created",
            message="Order created",
            created_at=created_at,
            is_read=False,
        )
    )

    fetched = repo.get_by_id(saved.notification_id)

    assert saved.notification_id > 0
    assert fetched == saved


def test_get_all_returns_all_notifications(db_session):
    repo = NotificationRepository(db_session)

    repo.create_notification("user-1", "order_created", "First")
    repo.create_notification("user-2", "payment_received", "Second")

    all_notifications = repo.get_all()

    assert len(all_notifications) == 2


def test_delete_existing_and_missing_notification(db_session):
    repo = NotificationRepository(db_session)
    saved = repo.create_notification("user-1", "order_completed", "Done")

    assert repo.delete(saved.notification_id) is True
    assert repo.get_by_id(saved.notification_id) is None
    assert repo.delete(999999) is False


def test_get_by_user_returns_newest_first(db_session):
    repo = NotificationRepository(db_session)
    older = datetime.now(timezone.utc) - timedelta(hours=1)
    newer = datetime.now(timezone.utc)

    repo.save(
        Notification(0, "user-1", "order_created", "Older", older, False)
    )
    repo.save(
        Notification(0, "user-1", "order_completed", "Newer", newer, False)
    )
    repo.create_notification("user-2", "payment_received", "Other user")

    notifications = repo.get_by_user("user-1")

    assert len(notifications) == 2
    assert notifications[0].message == "Newer"
    assert notifications[1].message == "Older"


def test_get_unread_by_user_filters_read_notifications(db_session):
    repo = NotificationRepository(db_session)
    unread = repo.create_notification("user-1", "order_created", "Unread")
    read = repo.create_notification("user-1", "order_completed", "Read")
    repo.mark_as_read(read.notification_id)

    notifications = repo.get_unread_by_user("user-1")

    assert [n.notification_id for n in notifications] == [unread.notification_id]


def test_get_by_event_type_filters_notifications(db_session):
    repo = NotificationRepository(db_session)

    repo.create_notification("user-1", "order_created", "Created")
    repo.create_notification("user-2", "payment_received", "Paid")
    repo.create_notification("user-3", "order_created", "Created again")

    notifications = repo.get_by_event_type("order_created")

    assert len(notifications) == 2
    assert all(n.event_type == "order_created" for n in notifications)


def test_mark_as_read_updates_notification(db_session):
    repo = NotificationRepository(db_session)
    saved = repo.create_notification("user-1", "order_created", "Unread")

    updated = repo.mark_as_read(saved.notification_id)

    assert updated is not None
    assert updated.is_read is True
    assert repo.get_by_id(saved.notification_id).is_read is True


def test_mark_all_read_for_user_returns_updated_count(db_session):
    repo = NotificationRepository(db_session)
    repo.create_notification("user-1", "order_created", "First")
    second = repo.create_notification("user-1", "order_completed", "Second")
    repo.create_notification("user-2", "payment_received", "Other")
    repo.mark_as_read(second.notification_id)

    updated_count = repo.mark_all_read_for_user("user-1")

    assert updated_count == 1
    assert repo.get_unread_by_user("user-1") == []


def test_save_with_existing_id_updates_notification(db_session):
    repo = NotificationRepository(db_session)
    saved = repo.create_notification("user-1", "order_created", "Original")

    updated = repo.save(
        Notification(
            notification_id=saved.notification_id,
            user_id=saved.user_id,
            event_type=saved.event_type,
            message="Updated",
            created_at=saved.created_at,
            is_read=True,
        )
    )

    assert updated.notification_id == saved.notification_id
    assert updated.message == "Updated"
    assert updated.is_read is True
