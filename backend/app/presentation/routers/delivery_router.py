from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status

from backend.app.application.services.delivery_service import DeliveryService
from backend.app.domain.models.user import User
from backend.app.presentation.dependencies import (
    get_current_user,
    get_delivery_service,
    handle_app_errors,
)
from backend.app.presentation.schemas import (
    AssignDeliveryRequest,
    UpdateDeliveryRequest,
    DeliveryResponse,
)

router = APIRouter(prefix="/deliveries", tags=["Deliveries"])

def _to_response(delivery) -> DeliveryResponse:
    return DeliveryResponse(
        order_id=delivery.order_id,
        delivery_time=delivery.delivery_time,
        delivery_time_actual=delivery.delivery_time_actual,
        delivery_delay=delivery.delivery_delay,
        delivery_distance=delivery.delivery_distance,
        delivery_method=delivery.delivery_method.value if delivery.delivery_method else None,
        route_taken=delivery.route_taken,
        route_type=delivery.route_type.value if delivery.route_type else None,
        route_efficiency=delivery.route_efficiency,
        traffic_condition=delivery.traffic_condition,
        weather_condition=delivery.weather_condition,
        predicted_delivery_mode=delivery.predicted_delivery_mode,
        traffic_avoidance=delivery.traffic_avoidance,
    )

@router.post("/{order_id}", response_model=DeliveryResponse, status_code=status.HTTP_201_CREATED)
@handle_app_errors
def assign_delivery(
    order_id: str,
    body: AssignDeliveryRequest,
    current_user: User = Depends(get_current_user),
    svc: DeliveryService = Depends(get_delivery_service),
):
    delivery = svc.assign_delivery(
        requesting_user=current_user,
        order_id=order_id,
        delivery_method=body.delivery_method,
        delivery_distance=body.delivery_distance,
        estimated_delivery_time=body.estimated_delivery_time,
    )
    return _to_response(delivery)

@router.get("/{order_id}", response_model=DeliveryResponse)
@handle_app_errors
def get_delivery(
    order_id: str,
    svc: DeliveryService = Depends(get_delivery_service),
):
    delivery = svc.get_delivery(order_id)
    return _to_response(delivery)

@router.get("", response_model=List[DeliveryResponse])
def list_deliveries(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    svc: DeliveryService = Depends(get_delivery_service),
):
    return [_to_response(d) for d in svc.list_deliveries(offset=offset, limit=limit)]

@router.patch("/{order_id}", response_model=DeliveryResponse)
@handle_app_errors
def update_delivery(
    order_id: str,
    body: UpdateDeliveryRequest,
    current_user: User = Depends(get_current_user),
    svc: DeliveryService = Depends(get_delivery_service),
):
    updated = svc.update_delivery(
        requesting_user=current_user,
        order_id=order_id,
        delivery_time_actual=body.delivery_time_actual,
        delivery_delay=body.delivery_delay,
        delivery_method=body.delivery_method,
        route_taken=body.route_taken,
        route_type=body.route_type,
        route_efficiency=body.route_efficiency,
        traffic_condition=body.traffic_condition,
        weather_condition=body.weather_condition,
        predicted_delivery_mode=body.predicted_delivery_mode,
        traffic_avoidance=body.traffic_avoidance,
    )
    return _to_response(updated)
