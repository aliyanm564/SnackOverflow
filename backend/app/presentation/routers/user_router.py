from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.app.application.exceptions import AuthorizationError, NotFoundError
from backend.app.application.services.user_service import UserService
from backend.app.domain.models.user import User, UserRole
from backend.app.presentation.dependencies import get_current_user, get_user_service
from backend.app.presentation.schemas.schemas import (
    ChangeRoleRequest,
    UpdateProfileRequest,
    UserResponse,
)

router = APIRouter(prefix="/users", tags=["Users"])


def _to_response(user: User) -> UserResponse:
    return UserResponse(
        customer_id=user.customer_id,
        name=user.name,
        age=user.age,
        gender=user.gender,
        location=user.location,
        loyalty_program=user.loyalty_program,
        preferred_cuisine=user.preferred_cuisine,
        order_frequency=user.order_frequency,
        role=user.role.value,
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get the currently authenticated user's profile",
)
def get_me(current_user: User = Depends(get_current_user)):
    return _to_response(current_user)


@router.patch(
    "/me",
    response_model=UserResponse,
    summary="Update the currently authenticated user's profile",
)
def update_me(
    body: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    user_svc: UserService = Depends(get_user_service),
):
    updated = user_svc.update_profile(
        customer_id=current_user.customer_id,
        name=body.name,
        age=body.age,
        gender=body.gender,
        location=body.location,
        preferred_cuisine=body.preferred_cuisine,
        order_frequency=body.order_frequency,
        loyalty_program=body.loyalty_program,
    )
    return _to_response(updated)


@router.get(
    "",
    response_model=List[UserResponse],
    summary="List all users (restaurant owners only)",
)
def list_users(
    role: Optional[str] = Query(default=None, description="Filter by role"),
    location: Optional[str] = Query(default=None, description="Filter by location"),
    current_user: User = Depends(get_current_user),
    user_svc: UserService = Depends(get_user_service),
):
    if current_user.role != UserRole.RESTAURANT_OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only restaurant owners can list users.",
        )
    role_filter = UserRole(role) if role else None
    users = user_svc.list_users(role=role_filter, location=location)
    return [_to_response(u) for u in users]


@router.get(
    "/{customer_id}",
    response_model=UserResponse,
    summary="Get a user by ID",
)
def get_user(
    customer_id: str,
    current_user: User = Depends(get_current_user),
    user_svc: UserService = Depends(get_user_service),
):
    if (
        current_user.role == UserRole.CUSTOMER
        and current_user.customer_id != customer_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own profile.",
        )
    try:
        user = user_svc.get_user(customer_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    return _to_response(user)


@router.patch(
    "/{customer_id}/role",
    response_model=UserResponse,
    summary="Change a user's role (restaurant owners only)",
)
def change_role(
    customer_id: str,
    body: ChangeRoleRequest,
    current_user: User = Depends(get_current_user),
    user_svc: UserService = Depends(get_user_service),
):
    try:
        new_role = UserRole(body.new_role)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role '{body.new_role}'.",
        )
    try:
        updated = user_svc.change_role(current_user, customer_id, new_role)
    except (AuthorizationError, NotFoundError) as exc:
        code = (
            status.HTTP_403_FORBIDDEN
            if isinstance(exc, AuthorizationError)
            else status.HTTP_404_NOT_FOUND
        )
        raise HTTPException(status_code=code, detail=str(exc))
    return _to_response(updated)


@router.delete(
    "/{customer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user account",
)
def delete_user(
    customer_id: str,
    current_user: User = Depends(get_current_user),
    user_svc: UserService = Depends(get_user_service),
):
    if current_user.customer_id != customer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own account.",
        )
    try:
        user_svc.delete_user(customer_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
