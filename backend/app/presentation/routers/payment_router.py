from typing import Optional

from fastapi import APIRouter, Depends, status

from backend.app.application.services.payment_service import PaymentService
from backend.app.application.services.promo_service import PromoService
from backend.app.domain.models.user import User
from backend.app.presentation.dependencies import (
    get_current_user,
    get_payment_service,
    get_pricing_service,
    get_promo_service,
    handle_app_errors,
)
from backend.app.presentation.schemas import PaymentResponse, ProcessPaymentRequest

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post(
    "/{order_id}",
    response_model=PaymentResponse,
    summary="Process payment for a pending order",
    responses={
        402: {"description": "Payment declined"},
        404: {"description": "Order not found"},
        422: {"description": "Order is not in a payable state"},
    },
)
@handle_app_errors
def process_payment(
    order_id: str,
    body: Optional[ProcessPaymentRequest] = None,
    current_user: User = Depends(get_current_user),
    payment_svc: PaymentService = Depends(get_payment_service),
    promo_svc: PromoService = Depends(get_promo_service),
    pricing_svc=Depends(get_pricing_service),
):
    promo_discount = 0.0
    promo_code = body.promo_code if body else None

    if promo_code:
        breakdown = pricing_svc.get_price_breakdown(order_id, current_user)
        validation = promo_svc.validate(promo_code, current_user, breakdown.grand_total)
        promo_discount = validation.discount_amount

    result = payment_svc.process_payment(order_id, current_user, promo_discount=promo_discount)

    if promo_code and promo_discount > 0:
        promo_svc.increment_usage(promo_code)

    return PaymentResponse(
        order_id=result.order_id,
        amount_charged=result.amount_charged,
        status=result.status,
        message=result.message,
    )
