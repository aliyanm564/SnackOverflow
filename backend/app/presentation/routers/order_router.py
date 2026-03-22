from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.app.application.exceptions import (
    AuthorizationError,
    BusinessRuleError,
    NotFoundError,
)
from backend.app.application.services.order_service import OrderService
from backend.app.domain.models.enums import OrderStatus
from backend.app.domain.models.orders import Order
from backend.app.domain.models.user import User, UserRole
from backend.app.presentation.dependencies import get_current_user, get_order_service
from backend.app.presentation.schemas.schemas import OrderResponse, PlaceOrderRequest

router = APIRouter(prefix="/orders", tags=["Orders"])


def _to_response(order: Order) -> OrderResponse:
    return OrderResponse(
        order_id=order.order_id,
        customer_id=order.customer_id,
        restaurant_id=order.restaurant_id,
        items=order.items,
        order_time=order.order_time,
        order_value=order.order_value,
        status=order.status.value,
        customer_rating=order.customer_rating,
        customer_satisfaction=order.customer_satisfaction,
    )


@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Place a new order (customers only)",
)
def place_order(
    body: PlaceOrderRequest,
    current_user: User = Depends(get_current_user),
    order_svc: OrderService = Depends(get_order_service),
):
    try:
        order = order_svc.place_order(
            requesting_user=current_user,
            restaurant_id=body.restaurant_id,
            food_item_ids=body.food_item_ids,
        )
    except AuthorizationError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except BusinessRuleError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )
    return _to_response(order)


@router.get(
    "",
    response_model=List[OrderResponse],
    summary="List orders for the current user",
)
def list_my_orders(
    status_filter: Optional[str] = Query(default=None, alias="status"),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    order_svc: OrderService = Depends(get_order_service),
):
    if status_filter:
        try:
            parsed_status = OrderStatus(status_filter)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status '{status_filter}'.",
            )
        orders = order_svc.get_orders_by_status(current_user, parsed_status)
    else:
        customer_id = (
            current_user.customer_id
            if current_user.role == UserRole.CUSTOMER
            else None
        )
        orders = order_svc.get_paginated_orders(
            customer_id=customer_id,
            offset=offset,
            limit=limit,
        )
    return [_to_response(o) for o in orders]


@router.get(
    "/restaurant/{restaurant_id}",
    response_model=List[OrderResponse],
    summary="Get all orders for a restaurant (owners only)",
)
def get_restaurant_orders(
    restaurant_id: str,
    current_user: User = Depends(get_current_user),
    order_svc: OrderService = Depends(get_order_service),
):
    try:
        orders = order_svc.get_orders_for_restaurant(current_user, restaurant_id)
    except AuthorizationError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    return [_to_response(o) for o in orders]


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    summary="Get a single order by ID",
)
def get_order(
    order_id: str,
    current_user: User = Depends(get_current_user),
    order_svc: OrderService = Depends(get_order_service),
):
    try:
        order = order_svc.get_order(order_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

    if (
        current_user.role == UserRole.CUSTOMER
        and order.customer_id != current_user.customer_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied.",
        )

    return _to_response(order)


@router.post(
    "/{order_id}/cancel",
    response_model=OrderResponse,
    summary="Cancel a pending order",
)
def cancel_order(
    order_id: str,
    current_user: User = Depends(get_current_user),
    order_svc: OrderService = Depends(get_order_service),
):
    try:
        order = order_svc.cancel_order(current_user, order_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except AuthorizationError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except BusinessRuleError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )
    return _to_response(order)
