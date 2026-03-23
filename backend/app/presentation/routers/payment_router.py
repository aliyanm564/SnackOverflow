from fastapi import APIRouter, Depends, HTTPException, status

from backend.app.application.exceptions import (
    AuthorizationError,
    BusinessRuleError,
    NotFoundError,
    PaymentError,
)
from backend.app.application.services.payment_service import PaymentService
from backend.app.domain.models.user import User
from backend.app.presentation.dependencies import get_current_user, get_payment_service
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
def process_payment(
    order_id: str,
    current_user: User = Depends(get_current_user),
    payment_svc: PaymentService = Depends(get_payment_service),
):
    try:
        result = payment_svc.process_payment(order_id, current_user)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except AuthorizationError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except BusinessRuleError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc))
    except PaymentError as exc:
        raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail=str(exc))

    return PaymentResponse(
        order_id=result.order_id,
        amount_charged=result.amount_charged,
        status=result.status,
        message=result.message,
    )