from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.app.application.services.order_service import OrderService
from backend.app.domain.models.enums import OrderStatus
from backend.app.domain.models.orders import Order
from backend.app.domain.models.user import User, UserRole
from backend.app.presentation.dependencies import (
    get_current_user,
    get_order_service,
    handle_app_errors,
)
from backend.app.presentation.dependencies import get_delivery_service
from backend.app.application.services.delivery_service import DeliveryService
from backend.app.presentation.schemas import OrderResponse, OrderTrackingResponse, PlaceOrderRequest, ReorderRequest

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
@handle_app_errors
def place_order(
    body: PlaceOrderRequest,
    current_user: User = Depends(get_current_user),
    order_svc: OrderService = Depends(get_order_service),
):
    order = order_svc.place_order(
        requesting_user=current_user,
        restaurant_id=body.restaurant_id,
        food_item_ids=body.food_item_ids,
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
@handle_app_errors
def get_restaurant_orders(
    restaurant_id: str,
    current_user: User = Depends(get_current_user),
    order_svc: OrderService = Depends(get_order_service),
):
    orders = order_svc.get_orders_for_restaurant(current_user, restaurant_id)
    return [_to_response(o) for o in orders]


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    summary="Get a single order by ID",
)
@handle_app_errors
def get_order(
    order_id: str,
    current_user: User = Depends(get_current_user),
    order_svc: OrderService = Depends(get_order_service),
):
    order = order_svc.get_order(order_id)

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
@handle_app_errors
def cancel_order(
    order_id: str,
    current_user: User = Depends(get_current_user),
    order_svc: OrderService = Depends(get_order_service),
):
    order = order_svc.cancel_order(current_user, order_id)
    return _to_response(order)


@router.post(
    "/{order_id}/complete",
    response_model=OrderResponse,
    summary="Mark an order as delivered/completed (restaurant owners only)",
)
@handle_app_errors
def complete_order(
    order_id: str,
    current_user: User = Depends(get_current_user),
    order_svc: OrderService = Depends(get_order_service),
):
    order = order_svc.complete_order(current_user, order_id)
    return _to_response(order)


@router.post(
    "/{order_id}/reorder",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Place a new order based on a previous one",
)
@handle_app_errors
def reorder(
    order_id: str,
    body: ReorderRequest,
    current_user: User = Depends(get_current_user),
    order_svc: OrderService = Depends(get_order_service),
):
    order = order_svc.reorder(current_user, order_id, body.food_item_ids)
    return _to_response(order)


@router.get(
    "/{order_id}/track",
    response_model=OrderTrackingResponse,
    summary="Track an order with delivery details",
)
@handle_app_errors
def track_order(
    order_id: str,
    current_user: User = Depends(get_current_user),
    order_svc: OrderService = Depends(get_order_service),
    delivery_svc: DeliveryService = Depends(get_delivery_service),
):
    order = order_svc.get_tracking(current_user, order_id)
    try:
        delivery = delivery_svc.get_delivery(order_id)
    except Exception:
        delivery = None

    return OrderTrackingResponse(
        order_id=order.order_id,
        status=order.status.value,
        order_time=order.order_time,
        order_value=order.order_value,
        restaurant_id=order.restaurant_id,
        items=order.items,
        delivery_method=delivery.delivery_method.value if delivery and delivery.delivery_method else None,
        estimated_delivery_time=delivery.delivery_time if delivery else None,
        delivery_distance=delivery.delivery_distance if delivery else None,
    )
