import inspect
from functools import wraps
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from backend.app.application.exceptions import (
    AppError,
    AuthenticationError,
    AuthorizationError,
    BusinessRuleError,
    ConflictError,
    NotFoundError,
    PaymentError,
)
from backend.app.application.services.auth_service import AuthService
from backend.app.application.services.delivery_service import DeliveryService
from backend.app.application.services.menu_service import MenuService
from backend.app.application.services.notification_service import NotificationService
from backend.app.application.services.order_service import OrderService
from backend.app.application.services.payment_service import PaymentService
from backend.app.application.services.pricing_service import PricingService
from backend.app.application.services.restaurant_service import RestaurantService
from backend.app.application.services.user_service import UserService
from backend.app.domain.models.user import User, UserRole
from backend.app.infrastructure.database import get_db_session
from backend.app.infrastructure.repositories.delivery_repository import DeliveryRepository
from backend.app.infrastructure.repositories.menu_repository import MenuRepository
from backend.app.infrastructure.repositories.notification_repository import NotificationRepository
from backend.app.infrastructure.repositories.order_repository import OrderRepository
from backend.app.infrastructure.repositories.restaurant_repository import RestaurantRepository
from backend.app.infrastructure.repositories.user_repository import UserRepository

_bearer_scheme = HTTPBearer(auto_error=False)


def get_db(db: Session = Depends(get_db_session)) -> Session:
    return db


def get_user_repo(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


def get_restaurant_repo(db: Session = Depends(get_db)) -> RestaurantRepository:
    return RestaurantRepository(db)


def get_menu_repo(db: Session = Depends(get_db)) -> MenuRepository:
    return MenuRepository(db)


def get_order_repo(db: Session = Depends(get_db)) -> OrderRepository:
    return OrderRepository(db)


def get_delivery_repo(db: Session = Depends(get_db)) -> DeliveryRepository:
    return DeliveryRepository(db)


def get_notification_repo(db: Session = Depends(get_db)) -> NotificationRepository:
    return NotificationRepository(db)


def get_notification_service(
    repo: NotificationRepository = Depends(get_notification_repo),
) -> NotificationService:
    return NotificationService(notification_repository=repo)


def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repo),
) -> AuthService:
    return AuthService(user_repository=user_repo)


def get_user_service(
    user_repo: UserRepository = Depends(get_user_repo),
) -> UserService:
    return UserService(user_repository=user_repo)


def get_restaurant_service(
    restaurant_repo: RestaurantRepository = Depends(get_restaurant_repo),
) -> RestaurantService:
    return RestaurantService(restaurant_repository=restaurant_repo)


def get_menu_service(
    menu_repo: MenuRepository = Depends(get_menu_repo),
    restaurant_repo: RestaurantRepository = Depends(get_restaurant_repo),
) -> MenuService:
    return MenuService(menu_repository=menu_repo, restaurant_repository=restaurant_repo)


def get_order_service(
    order_repo: OrderRepository = Depends(get_order_repo),
    menu_repo: MenuRepository = Depends(get_menu_repo),
    restaurant_repo: RestaurantRepository = Depends(get_restaurant_repo),
    notification_svc: NotificationService = Depends(get_notification_service),
) -> OrderService:
    return OrderService(
        order_repository=order_repo,
        menu_repository=menu_repo,
        restaurant_repository=restaurant_repo,
        notification_service=notification_svc,
    )


def get_delivery_service(
    delivery_repo: DeliveryRepository = Depends(get_delivery_repo),
    order_repo: OrderRepository = Depends(get_order_repo),
) -> DeliveryService:
    return DeliveryService(
        delivery_repository=delivery_repo,
        order_repository=order_repo,
    )


def get_pricing_service(
    order_repo: OrderRepository = Depends(get_order_repo),
    menu_repo: MenuRepository = Depends(get_menu_repo),
) -> PricingService:
    return PricingService(order_repository=order_repo, menu_repository=menu_repo)


def get_payment_service(
    order_repo: OrderRepository = Depends(get_order_repo),
    order_svc: OrderService = Depends(get_order_service),
    pricing_svc: PricingService = Depends(get_pricing_service),
    notification_svc: NotificationService = Depends(get_notification_service),
) -> PaymentService:
    return PaymentService(
        order_repository=order_repo,
        order_service=order_svc,
        pricing_service=pricing_svc,
        notification_service=notification_svc,
    )


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer_scheme)],
    auth_svc: AuthService = Depends(get_auth_service),
    user_svc: UserService = Depends(get_user_service),
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        customer_id, _ = auth_svc.verify_token(credentials.credentials)
        return user_svc.get_user(customer_id)
    except (AuthenticationError, NotFoundError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_role(*allowed_roles: UserRole):
    def _check(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{current_user.role.value}' is not permitted for this action.",
            )
        return current_user
    return _check


def app_error_to_http(exc: AppError) -> HTTPException:
    mapping = {
        NotFoundError: status.HTTP_404_NOT_FOUND,
        ConflictError: status.HTTP_409_CONFLICT,
        AuthenticationError: status.HTTP_401_UNAUTHORIZED,
        AuthorizationError: status.HTTP_403_FORBIDDEN,
        BusinessRuleError: status.HTTP_422_UNPROCESSABLE_CONTENT,
        PaymentError: status.HTTP_402_PAYMENT_REQUIRED,
    }
    code = mapping.get(type(exc), status.HTTP_400_BAD_REQUEST)
    return HTTPException(status_code=code, detail=str(exc))


def handle_app_errors(func):
    if inspect.iscoroutinefunction(func):
        @wraps(func)
        async def _async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except AppError as exc:
                raise app_error_to_http(exc) from exc

        return _async_wrapper

    @wraps(func)
    def _sync_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except AppError as exc:
            raise app_error_to_http(exc) from exc

    return _sync_wrapper
