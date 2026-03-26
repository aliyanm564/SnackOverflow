from typing import List

from fastapi import APIRouter, Depends, status

from backend.app.application.services.notification_service import NotificationService
from backend.app.domain.models.notification import Notification
from backend.app.domain.models.user import User
from backend.app.presentation.dependencies import (
    get_current_user,
    get_notification_service,
    handle_app_errors,
)
from backend.app.presentation.schemas import NotificationResponse

router = APIRouter(prefix="/notifications", tags=["Notifications"])


def _to_response(notification: Notification) -> NotificationResponse:
    return NotificationResponse(
        notification_id=notification.notification_id,
        user_id=notification.user_id,
        event_type=notification.event_type,
        message=notification.message,
        created_at=notification.created_at,
        is_read=notification.is_read,
    )


@router.get(
    "",
    response_model=List[NotificationResponse],
    summary="Get all notifications for the current user",
)
@handle_app_errors
def get_my_notifications(
    current_user: User = Depends(get_current_user),
    notification_svc: NotificationService = Depends(get_notification_service),
):
    notifications = notification_svc.get_all_for_user(
        current_user, current_user.customer_id
    )
    return [_to_response(notification) for notification in notifications]


@router.get(
    "/unread",
    response_model=List[NotificationResponse],
    summary="Get unread notifications for the current user",
)
@handle_app_errors
def get_unread_notifications(
    current_user: User = Depends(get_current_user),
    notification_svc: NotificationService = Depends(get_notification_service),
):
    notifications = notification_svc.get_unread_for_user(
        current_user, current_user.customer_id
    )
    return [_to_response(notification) for notification in notifications]


@router.patch(
    "/{notification_id}/read",
    response_model=NotificationResponse,
    summary="Mark a single notification as read",
)
@handle_app_errors
def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    notification_svc: NotificationService = Depends(get_notification_service),
):
    updated = notification_svc.mark_read(current_user, notification_id)
    return _to_response(updated)


@router.patch(
    "/read-all",
    summary="Mark all notifications as read for the current user",
)
@handle_app_errors
def mark_all_read(
    current_user: User = Depends(get_current_user),
    notification_svc: NotificationService = Depends(get_notification_service),
):
    count = notification_svc.mark_all_read(current_user, current_user.customer_id)
    return {"marked_read": count}


@router.delete(
    "/{notification_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a notification",
)
@handle_app_errors
def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    notification_svc: NotificationService = Depends(get_notification_service),
):
    notification_svc.delete_notification(current_user, notification_id)
