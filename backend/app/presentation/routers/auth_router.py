from fastapi import APIRouter, Depends, HTTPException, status

from backend.app.application.services.auth_service import AuthService
from backend.app.domain.models.user import UserRole
from backend.app.presentation.dependencies import get_auth_service, handle_app_errors
from backend.app.presentation.schemas import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
@handle_app_errors
def register(
    body: RegisterRequest,
    auth_svc: AuthService = Depends(get_auth_service),
):
    try:
        role = UserRole(body.role)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role '{body.role}'. Must be one of: {[r.value for r in UserRole]}",
        )
    user = auth_svc.register(
        email=body.email,
        password=body.password,
        role=role,
        name=body.name,
        age=body.age,
        gender=body.gender,
        location=body.location,
        preferred_cuisine=body.preferred_cuisine,
        order_frequency=body.order_frequency,
        loyalty_program=body.loyalty_program,
    )

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


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Log in and receive a JWT access token",
)
@handle_app_errors
def login(
    body: LoginRequest,
    auth_svc: AuthService = Depends(get_auth_service),
):
    token = auth_svc.login(body.email, body.password)

    return TokenResponse(access_token=token)
