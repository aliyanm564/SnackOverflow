from fastapi import APIRouter, Depends, status

from backend.app.application.services.payment_service import PaymentService
from backend.app.domain.models.user import User
from backend.app.presentation.dependencies import (
    get_current_user,
    get_payment_service,
    handle_app_errors,
)
from backend.app.presentation.schemas import PaymentResponse

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
    current_user: User = Depends(get_current_user),
    payment_svc: PaymentService = Depends(get_payment_service),
):
    result = payment_svc.process_payment(order_id, current_user)

    return PaymentResponse(
        order_id=result.order_id,
        amount_charged=result.amount_charged,
        status=result.status,
        message=result.message,
    )
