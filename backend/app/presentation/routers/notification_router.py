from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from backend.app.application.exceptions import AuthorizationError, NotFoundError
from backend.app.application.services.notification_service import NotificationService
from backend.app.domain.models.user import User
from backend.app.presentation.dependencies import (
    get_current_user,
    get_notification_service,
)
from backend.app.presentation.schemas.schemas import NotificationResponse

router = APIRouter(prefix="/notifications", tags=["Notifications"])


def _to_response(notification) -> NotificationResponse:
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
def get_my_notifications(
    current_user: User = Depends(get_current_user),
    notification_svc: NotificationService = Depends(get_notification_service),
):
    try:
        notifications = notification_svc.get_all_for_user(
            current_user, current_user.customer_id
        )
    except AuthorizationError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    return [_to_response(notification) for notification in notifications]


@router.get(
    "/unread",
    response_model=List[NotificationResponse],
    summary="Get unread notifications for the current user",
)
def get_unread_notifications(
    current_user: User = Depends(get_current_user),
    notification_svc: NotificationService = Depends(get_notification_service),
):
    try:
        notifications = notification_svc.get_unread_for_user(
            current_user, current_user.customer_id
        )
    except AuthorizationError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    return [_to_response(notification) for notification in notifications]


@router.patch(
    "/{notification_id}/read",
    response_model=NotificationResponse,
    summary="Mark a single notification as read",
)
def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    notification_svc: NotificationService = Depends(get_notification_service),
):
    try:
        updated = notification_svc.mark_read(current_user, notification_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except AuthorizationError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    return _to_response(updated)


@router.patch(
    "/read-all",
    summary="Mark all notifications as read for the current user",
)
def mark_all_read(
    current_user: User = Depends(get_current_user),
    notification_svc: NotificationService = Depends(get_notification_service),
):
    try:
        count = notification_svc.mark_all_read(current_user, current_user.customer_id)
    except AuthorizationError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    return {"marked_read": count}


@router.delete(
    "/{notification_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a notification",
)
def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    notification_svc: NotificationService = Depends(get_notification_service),
):
    try:
        notification_svc.delete_notification(current_user, notification_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except AuthorizationError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
