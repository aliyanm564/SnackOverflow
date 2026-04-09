from dataclasses import dataclass
from typing import Callable, Optional

from backend.app.application.exceptions import (
    BusinessRuleError,
    NotFoundError,
    PaymentError,
)
from backend.app.domain.models.enums import OrderStatus
from backend.app.infrastructure.repositories.order_repository import OrderRepository

@dataclass(frozen=True)
class PaymentResult:
    order_id: str
    amount_charged: float
    status: str
    message: str

def _default_simulated_processor(amount: float) -> bool:
    return amount > 0

class PaymentService:

    def __init__(
        self,
        order_repository: OrderRepository,
        order_service,
        pricing_service,
        payment_processor: Optional[Callable[[float], bool]] = None,
        notification_service=None,
    ) -> None:
        self._orders = order_repository
        self._order_service = order_service
        self._pricing = pricing_service
        self._processor = payment_processor or _default_simulated_processor
        self._notifications = notification_service

    def process_payment(
        self, order_id: str, customer, promo_discount: float = 0.0
    ) -> PaymentResult:
        order = self._orders.get_by_id(order_id)
        if order is None:
            raise NotFoundError(f"Order '{order_id}' not found.")

        if order.status != OrderStatus.PENDING:
            raise BusinessRuleError(
                f"Cannot charge for order '{order_id}': status is {order.status.value}."
            )

        if order.customer_id != customer.customer_id:
            from backend.app.application.exceptions import AuthorizationError
            raise AuthorizationError("You can only pay for your own orders.")

        breakdown = self._pricing.get_price_breakdown(order_id, customer)
        amount = max(0.0, round(breakdown.grand_total - promo_discount, 2))

        approved = self._processor(amount)

        if not approved:
            self._notify(
                customer.customer_id,
                "payment_failed",
                f"Payment of ${amount:.2f} for order {order_id} was declined.",
            )
            raise PaymentError(
                f"Payment of ${amount:.2f} for order '{order_id}' was declined."
            )

        self._notify(
            customer.customer_id,
            "payment_approved",
            f"Payment of ${amount:.2f} for order {order_id} was approved. Your order is being prepared.",
        )

        return PaymentResult(
            order_id=order_id,
            amount_charged=amount,
            status="approved",
            message=f"Payment of ${amount:.2f} approved. Your order is being prepared.",
        )

    def _notify(self, user_id: str, event_type: str, message: str) -> None:
        if self._notifications is not None:
            self._notifications.create(user_id, event_type, message)
