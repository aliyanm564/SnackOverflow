import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Optional

from backend.app.application.exceptions import (
    AuthorizationError,
    BusinessRuleError,
    ConflictError,
    NotFoundError,
)
from backend.app.domain.models.promo import PromoCode
from backend.app.domain.models.user import User, UserRole
from backend.app.infrastructure.repositories.promo_repository import PromoRepository


@dataclass(frozen=True)
class PromoValidationResult:
    promo: PromoCode
    discount_amount: float
    adjusted_total: float


class PromoService:

    def __init__(self, promo_repository: PromoRepository) -> None:
        self._promos = promo_repository

    def create_promo(
        self,
        requesting_user: User,
        code: str,
        discount_type: str,
        discount_value: float,
        expiry_date: Optional[datetime] = None,
        usage_limit: Optional[int] = None,
    ) -> PromoCode:
        if requesting_user.role != UserRole.RESTAURANT_OWNER:
            raise AuthorizationError("Only restaurant owners can create promo codes.")

        if discount_type not in ("percentage", "flat"):
            raise BusinessRuleError("discount_type must be 'percentage' or 'flat'.")

        if discount_value <= 0:
            raise BusinessRuleError("discount_value must be greater than zero.")

        if discount_type == "percentage" and discount_value > 100:
            raise BusinessRuleError("Percentage discount cannot exceed 100.")

        normalised = code.upper().strip()
        if self._promos.get_by_code(normalised) is not None:
            raise ConflictError(f"Promo code '{normalised}' already exists.")

        promo = PromoCode(
            promo_id=str(uuid.uuid4()),
            code=normalised,
            discount_type=discount_type,
            discount_value=discount_value,
            expiry_date=expiry_date,
            usage_limit=usage_limit,
            usage_count=0,
            is_active=True,
            owner_id=requesting_user.customer_id,
        )
        return self._promos.save(promo)

    def list_promos(self, requesting_user: User) -> List[PromoCode]:
        if requesting_user.role != UserRole.RESTAURANT_OWNER:
            raise AuthorizationError("Only restaurant owners can list promo codes.")
        return self._promos.get_by_owner(requesting_user.customer_id)

    def set_active(self, requesting_user: User, promo_id: str, is_active: bool) -> PromoCode:
        promo = self._get_or_raise(promo_id)
        self._check_owner(requesting_user, promo)
        updated = promo.model_copy(update={"is_active": is_active})
        return self._promos.save(updated)

    def assign_to_customers(
        self,
        requesting_user: User,
        promo_id: str,
        customer_ids: List[str],
    ) -> PromoCode:
        promo = self._get_or_raise(promo_id)
        self._check_owner(requesting_user, promo)
        for cid in customer_ids:
            self._promos.add_assignment(promo_id, cid)
        return self._get_or_raise(promo_id)

    def validate(
        self,
        code: str,
        customer: User,
        order_total: float,
    ) -> PromoValidationResult:
        normalised = code.upper().strip()
        promo = self._promos.get_by_code(normalised)
        if promo is None:
            raise NotFoundError(f"Promo code '{code}' not found.")

        if not promo.is_active:
            raise BusinessRuleError("This promo code is not active.")

        if promo.expiry_date is not None:
            expiry = promo.expiry_date
            if expiry.tzinfo is None:
                expiry = expiry.replace(tzinfo=timezone.utc)
            if datetime.now(tz=timezone.utc) > expiry:
                raise BusinessRuleError("This promo code has expired.")

        if promo.usage_limit is not None and promo.usage_count >= promo.usage_limit:
            raise BusinessRuleError("This promo code has reached its usage limit.")

        if (
            promo.assigned_customer_ids
            and customer.customer_id not in promo.assigned_customer_ids
        ):
            raise BusinessRuleError("This promo code is not available for your account.")

        discount = self._compute_discount(promo, order_total)
        adjusted = max(0.0, round(order_total - discount, 2))

        return PromoValidationResult(
            promo=promo,
            discount_amount=round(discount, 2),
            adjusted_total=adjusted,
        )

    def increment_usage(self, code: str) -> None:
        promo = self._promos.get_by_code(code.upper().strip())
        if promo is not None:
            self._promos.save(promo.model_copy(update={"usage_count": promo.usage_count + 1}))

    def _compute_discount(self, promo: PromoCode, total: float) -> float:
        if promo.discount_type == "percentage":
            return round(total * promo.discount_value / 100, 2)
        return min(promo.discount_value, total)

    def _get_or_raise(self, promo_id: str) -> PromoCode:
        promo = self._promos.get_by_id(promo_id)
        if promo is None:
            raise NotFoundError(f"Promo '{promo_id}' not found.")
        return promo

    def _check_owner(self, user: User, promo: PromoCode) -> None:
        if user.role != UserRole.RESTAURANT_OWNER or user.customer_id != promo.owner_id:
            raise AuthorizationError("You do not own this promo code.")
