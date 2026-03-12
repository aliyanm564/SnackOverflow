"""
test_payment_flow.py  (integration)
-------------------------------------
End-to-end tests for the payment simulation using real repositories and
in-memory SQLite.

Scenarios covered
-----------------
1. Approved payment → order COMPLETED, notifications auditable in DB.
2. Rejected payment → order stays PENDING, PaymentError raised.
3. Loyalty customer pays → discount applied, correct amount charged.
4. Double-payment attempt on a completed order → BusinessRuleError.
5. Payment for a non-existent order → NotFoundError.
"""

import pytest
from sqlalchemy.orm import Session

from backend.app.infrastructure.orm_models import MenuItemORM, RestaurantORM, UserORM
from backend.app.infrastructure.repositories.menu_repository import MenuRepository
from backend.app.infrastructure.repositories.notification_repository import NotificationRepository
from backend.app.infrastructure.repositories.order_repository import OrderRepository
from backend.app.infrastructure.repositories.restaurant_repository import RestaurantRepository
from backend.app.application.services.notification_service import NotificationService
from backend.app.application.services.order_service import OrderService
from backend.app.application.services.payment_service import PaymentService
from backend.app.application.services.pricing_service import PricingService
from backend.app.application.exceptions import BusinessRuleError, NotFoundError, PaymentError
from backend.app.domain.models.enums import OrderStatus
from backend.app.domain.models.user import User, UserRole


# ---------------------------------------------------------------------------
# Shared helper: build the full service stack for a given DB session
# ---------------------------------------------------------------------------

def _build_stack(db: Session, processor=None):
    order_repo = OrderRepository(db)
    menu_repo = MenuRepository(db)
    restaurant_repo = RestaurantRepository(db)
    notification_repo = NotificationRepository(db)

    notification_svc = NotificationService(notification_repo)
    order_svc = OrderService(
        order_repository=order_repo,
        menu_repository=menu_repo,
        restaurant_repository=restaurant_repo,
        notification_service=notification_svc,
    )
    pricing_svc = PricingService(order_repo, menu_repo)
    payment_svc = PaymentService(
        order_repository=order_repo,
        order_service=order_svc,
        pricing_service=pricing_svc,
        payment_processor=processor or (lambda a: True),
        notification_service=notification_svc,
    )
    return order_svc, pricing_svc, payment_svc, notification_repo


def _seed_db(db: Session, loyalty: bool = False, customer_id: str = "p-cust-001"):
    db.add(UserORM(
        customer_id=customer_id,
        role="customer",
        loyalty_program=loyalty,
        order_history_count=0,
    ))

    db.add(
        RestaurantORM(
            restaurant_id="p-rest-001",
            owner_id="owner-001",
            name="Pay Bistro",
            location="Test City",
            description="Asian"
        )
    )

    db.add(MenuItemORM(
        food_item_id="p-item-001",
        restaurant_id="p-rest-001",
        name="Sushi",
        category="Asian",
        price=16.99,
    ))
    db.commit()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestPaymentFlow:

    def test_approved_payment_marks_order_completed(self, db_session):
        """Happy path: processor approves → order is COMPLETED in DB."""
        _seed_db(db_session)
        customer = User(customer_id="p-cust-001", role=UserRole.CUSTOMER, loyalty_program=False)
        order_svc, _, payment_svc, _ = _build_stack(db_session, processor=lambda a: True)

        order = order_svc.place_order(customer, "p-rest-001", ["p-item-001"])
        result = payment_svc.process_payment(order.order_id, customer)

        assert result.status == "approved"
        persisted = OrderRepository(db_session).get_by_id(order.order_id)
        assert persisted.status == OrderStatus.COMPLETED

    def test_rejected_payment_leaves_order_pending(self, db_session):
        """Equivalence partition: processor rejects → order stays PENDING."""
        _seed_db(db_session)
        customer = User(customer_id="p-cust-001", role=UserRole.CUSTOMER, loyalty_program=False)
        order_svc, _, payment_svc, _ = _build_stack(db_session, processor=lambda a: False)

        order = order_svc.place_order(customer, "p-rest-001", ["p-item-001"])

        with pytest.raises(PaymentError):
            payment_svc.process_payment(order.order_id, customer)

        persisted = OrderRepository(db_session).get_by_id(order.order_id)
        assert persisted.status == OrderStatus.PENDING

    def test_loyalty_customer_charged_less(self, db_session):
        """
        Equivalence partition: loyalty member's grand_total must be less
        than the non-loyalty grand_total for the same order.
        """
        _seed_db(db_session, loyalty=True, customer_id="loyal-cust")
        loyal_customer = User(
            customer_id="loyal-cust", role=UserRole.CUSTOMER, loyalty_program=True
        )
        regular_customer = User(
            customer_id="regular-cust", role=UserRole.CUSTOMER, loyalty_program=False
        )

        order_svc, pricing_svc, _, _ = _build_stack(db_session)

        loyal_order = order_svc.place_order(loyal_customer, "p-rest-001", ["p-item-001"])
        loyal_total = pricing_svc.get_price_breakdown(loyal_order.order_id, loyal_customer).grand_total

        # Place another order for a regular customer (same items).
        # We reuse the same menu item but need a different order.
        regular_order = order_svc.place_order(regular_customer, "p-rest-001", ["p-item-001"])
        regular_total = pricing_svc.get_price_breakdown(regular_order.order_id, regular_customer).grand_total

        assert loyal_total < regular_total

    def test_double_payment_raises_business_rule_error(self, db_session):
        """Fault injection: paying for an already-completed order."""
        _seed_db(db_session)
        customer = User(customer_id="p-cust-001", role=UserRole.CUSTOMER, loyalty_program=False)
        order_svc, _, payment_svc, _ = _build_stack(db_session, processor=lambda a: True)

        order = order_svc.place_order(customer, "p-rest-001", ["p-item-001"])
        payment_svc.process_payment(order.order_id, customer)

        with pytest.raises(BusinessRuleError):
            payment_svc.process_payment(order.order_id, customer)

    def test_payment_for_nonexistent_order_raises_not_found(self, db_session):
        """Fault injection: order_id does not exist."""
        _seed_db(db_session)
        customer = User(customer_id="p-cust-001", role=UserRole.CUSTOMER, loyalty_program=False)
        _, _, payment_svc, _ = _build_stack(db_session, processor=lambda a: True)

        with pytest.raises(NotFoundError):
            payment_svc.process_payment("ghost-order", customer)

    def test_payment_notifications_persisted(self, db_session):
        """
        After a successful payment both 'order_created' and 'payment_approved'
        notifications must be stored for the customer.
        """
        _seed_db(db_session)
        customer = User(customer_id="p-cust-001", role=UserRole.CUSTOMER, loyalty_program=False)
        order_svc, _, payment_svc, notification_repo = _build_stack(
            db_session, processor=lambda a: True
        )

        order = order_svc.place_order(customer, "p-rest-001", ["p-item-001"])
        payment_svc.process_payment(order.order_id, customer)

        notifications = notification_repo.get_by_user("p-cust-001")
        event_types = {n.event_type for n in notifications}

        assert "order_created" in event_types
        assert "payment_approved" in event_types

    def test_rejected_payment_notification_persisted(self, db_session):
        """After rejection, a 'payment_failed' notification must be stored."""
        _seed_db(db_session)
        customer = User(customer_id="p-cust-001", role=UserRole.CUSTOMER, loyalty_program=False)
        order_svc, _, payment_svc, notification_repo = _build_stack(
            db_session, processor=lambda a: False
        )

        order = order_svc.place_order(customer, "p-rest-001", ["p-item-001"])
        with pytest.raises(PaymentError):
            payment_svc.process_payment(order.order_id, customer)

        notifications = notification_repo.get_by_user("p-cust-001")
        event_types = {n.event_type for n in notifications}
        assert "payment_failed" in event_types
