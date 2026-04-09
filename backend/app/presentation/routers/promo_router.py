from typing import List

from fastapi import APIRouter, Depends, status

from backend.app.application.services.promo_service import PromoService
from backend.app.domain.models.promo import PromoCode
from backend.app.domain.models.user import User
from backend.app.presentation.dependencies import (
    get_current_user,
    get_pricing_service,
    get_promo_service,
    handle_app_errors,
)
from backend.app.presentation.schemas import (
    AssignPromoRequest,
    CreatePromoRequest,
    PromoResponse,
    ValidatePromoRequest,
    ValidatePromoResponse,
)

router = APIRouter(prefix="/promos", tags=["Promos"])


def _to_response(promo: PromoCode) -> PromoResponse:
    return PromoResponse(
        promo_id=promo.promo_id,
        code=promo.code,
        discount_type=promo.discount_type,
        discount_value=promo.discount_value,
        expiry_date=promo.expiry_date,
        usage_limit=promo.usage_limit,
        usage_count=promo.usage_count,
        is_active=promo.is_active,
        assigned_customer_ids=promo.assigned_customer_ids,
    )


@router.post("", response_model=PromoResponse, status_code=status.HTTP_201_CREATED)
@handle_app_errors
def create_promo(
    body: CreatePromoRequest,
    current_user: User = Depends(get_current_user),
    svc: PromoService = Depends(get_promo_service),
):
    promo = svc.create_promo(
        requesting_user=current_user,
        code=body.code,
        discount_type=body.discount_type,
        discount_value=body.discount_value,
        expiry_date=body.expiry_date,
        usage_limit=body.usage_limit,
    )
    return _to_response(promo)


@router.get("", response_model=List[PromoResponse])
@handle_app_errors
def list_promos(
    current_user: User = Depends(get_current_user),
    svc: PromoService = Depends(get_promo_service),
):
    return [_to_response(p) for p in svc.list_promos(current_user)]


@router.patch("/{promo_id}/activate", response_model=PromoResponse)
@handle_app_errors
def activate_promo(
    promo_id: str,
    current_user: User = Depends(get_current_user),
    svc: PromoService = Depends(get_promo_service),
):
    return _to_response(svc.set_active(current_user, promo_id, True))


@router.patch("/{promo_id}/deactivate", response_model=PromoResponse)
@handle_app_errors
def deactivate_promo(
    promo_id: str,
    current_user: User = Depends(get_current_user),
    svc: PromoService = Depends(get_promo_service),
):
    return _to_response(svc.set_active(current_user, promo_id, False))


@router.post("/{promo_id}/assign", response_model=PromoResponse)
@handle_app_errors
def assign_promo(
    promo_id: str,
    body: AssignPromoRequest,
    current_user: User = Depends(get_current_user),
    svc: PromoService = Depends(get_promo_service),
):
    return _to_response(svc.assign_to_customers(current_user, promo_id, body.customer_ids))


@router.post("/validate", response_model=ValidatePromoResponse)
@handle_app_errors
def validate_promo(
    body: ValidatePromoRequest,
    current_user: User = Depends(get_current_user),
    svc: PromoService = Depends(get_promo_service),
    pricing_svc=Depends(get_pricing_service),
):
    breakdown = pricing_svc.get_price_breakdown(body.order_id, current_user)
    result = svc.validate(body.code, current_user, breakdown.grand_total)

    if result.promo.discount_type == "percentage":
        label = f"{result.promo.discount_value}% off"
    else:
        label = f"${result.discount_amount:.2f} off"

    return ValidatePromoResponse(
        valid=True,
        discount_amount=result.discount_amount,
        adjusted_total=result.adjusted_total,
        message=f"Promo applied: {label}",
    )
