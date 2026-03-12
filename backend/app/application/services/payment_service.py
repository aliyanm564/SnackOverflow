"""
payment_service.py
------------------
Simulates payment processing (Feature 7).

No real payment gateway is used. The service follows the correct workflow:
  1. Validate the order exists and is PENDING.
  2. Compute the expected total via PricingService.
  3. Simulate approval/rejection (configurable strategy for testability).
  4. On approval  → call OrderService.complete_order() to mark it COMPLETED.
  5. On rejection → raise PaymentError; order stays PENDING for retry.

Why a separate service?
-----------------------
Mixing payment logic into OrderService would violate SRP. Payment has its
own failure modes, retry semantics, and audit trail that are distinct from
order management.

Testability
-----------
`payment_processor` is an injected callable with signature:
    (amount: float) -> bool

In tests you inject `lambda amount: True` (always approve) or
`lambda amount: False` (always reject). In production you swap in a
real gateway call.
"""

from dataclasses import dataclass
from typing import Callable, Optional

from backend.app.application.exceptions import (
    BusinessRuleError,
    NotFoundError,
    PaymentError,
)
from backend.app.domain.models.enums import OrderStatus
from backend.app.infrastructure.repositories.order_repository import OrderRepository


# ---------------------------------------------------------------------------
# Value object returned to the caller
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PaymentResult:
    order_id: str
    amount_charged: float
    status: str          # "approved" | "rejected"
    message: str


# ---------------------------------------------------------------------------
# Default simulated processor
# ---------------------------------------------------------------------------

def _default_simulated_processor(amount: float) -> bool:
    """
    Deterministic simulation: approve all payments above $0.
    In a real system this would call a payment gateway SDK.
    """
    return amount > 0


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------

class PaymentService:

    def __init__(
        self,
        order_repository: OrderRepository,
        order_service,          # OrderService — type hint omitted to avoid circular import
        pricing_service,        # PricingService
        payment_processor: Optional[Callable[[float], bool]] = None,
        notification_service=None,
    ) -> None:
        self._orders = order_repository
        self._order_service = order_service
        self._pricing = pricing_service
        self._processor = payment_processor or _default_simulated_processor
        self._notifications = notification_service

    # ------------------------------------------------------------------
    # Process payment
    # ------------------------------------------------------------------

    def process_payment(self, order_id: str, customer) -> PaymentResult:
        """
        Attempt to charge the customer for the given order.

        Workflow
        --------
        1. Fetch order, assert it is PENDING.
        2. Compute total via PricingService.
        3. Call the payment processor.
        4a. Approved → complete the order, return PaymentResult(approved).
        4b. Rejected → raise PaymentError (order remains PENDING for retry).

        Parameters
        ----------
        order_id : str
        customer : User domain object of the paying customer.
        """
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

        # Compute total using the pricing service.
        breakdown = self._pricing.get_price_breakdown(order_id, customer)
        amount = breakdown.grand_total

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

        # Payment approved — complete the order.
        self._order_service.complete_order(order_id)
        self._notify(
            customer.customer_id,
            "payment_approved",
            f"Payment of ${amount:.2f} for order {order_id} was approved.",
        )

        return PaymentResult(
            order_id=order_id,
            amount_charged=amount,
            status="approved",
            message=f"Payment of ${amount:.2f} approved. Order is now complete.",
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _notify(self, user_id: str, event_type: str, message: str) -> None:
        if self._notifications is not None:
            self._notifications.create(user_id, event_type, message)
