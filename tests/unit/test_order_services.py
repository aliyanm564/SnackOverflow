import pytest

from backend.app.application.exceptions import (
    AuthorizationError,
    BusinessRuleError,
    NotFoundError,
)
from backend.app.application.services.order_service import OrderService
from backend.app.domain.models.enums import OrderStatus


def make_service(
    order_repo,
    menu_repo,
    restaurant_repo,
    notification_service=None,
):
    return OrderService(
        order_repository=order_repo,
        menu_repository=menu_repo,
        restaurant_repository=restaurant_repo,
        notification_service=notification_service,
    )


class TestPlaceOrder:

    def test_place_order_saves_pending_order_and_notifies(
        self,
        mock_order_repo,
        mock_menu_repo,
        mock_restaurant_repo,
        mock_notification_service,
        customer_user,
        sample_restaurant,
        sample_menu_item,
    ):
        mock_restaurant_repo.get_by_id.return_value = sample_restaurant
        mock_menu_repo.get_by_id.return_value = sample_menu_item
        mock_order_repo.save.side_effect = lambda order: order

        service = make_service(
            mock_order_repo,
            mock_menu_repo,
            mock_restaurant_repo,
            mock_notification_service,
        )

        result = service.place_order(
            requesting_user=customer_user,
            restaurant_id=sample_restaurant.restaurant_id,
            food_item_ids=[sample_menu_item.food_item_id],
        )

        assert result.customer_id == customer_user.customer_id
        assert result.restaurant_id == sample_restaurant.restaurant_id
        assert result.items == [sample_menu_item.food_item_id]
        assert result.status == OrderStatus.PENDING
        assert result.order_value == sample_menu_item.price
        mock_order_repo.save.assert_called_once()
        mock_notification_service.create.assert_called_once()

    def test_place_order_rejects_non_customer(
        self,
        mock_order_repo,
        mock_menu_repo,
        mock_restaurant_repo,
        owner_user,
    ):
        service = make_service(mock_order_repo, mock_menu_repo, mock_restaurant_repo)

        with pytest.raises(AuthorizationError):
            service.place_order(owner_user, "rest-001", ["item-001"])

    def test_place_order_raises_not_found_for_missing_restaurant(
        self,
        mock_order_repo,
        mock_menu_repo,
        mock_restaurant_repo,
        customer_user,
    ):
        mock_restaurant_repo.get_by_id.return_value = None
        service = make_service(mock_order_repo, mock_menu_repo, mock_restaurant_repo)

        with pytest.raises(NotFoundError):
            service.place_order(customer_user, "missing-rest", ["item-001"])

    def test_place_order_rejects_empty_items(
        self,
        mock_order_repo,
        mock_menu_repo,
        mock_restaurant_repo,
        customer_user,
        sample_restaurant,
    ):
        mock_restaurant_repo.get_by_id.return_value = sample_restaurant
        service = make_service(mock_order_repo, mock_menu_repo, mock_restaurant_repo)

        with pytest.raises(BusinessRuleError):
            service.place_order(customer_user, sample_restaurant.restaurant_id, [])

    def test_place_order_rejects_item_from_different_restaurant(
        self,
        mock_order_repo,
        mock_menu_repo,
        mock_restaurant_repo,
        customer_user,
        sample_restaurant,
        sample_menu_item,
    ):
        wrong_item = sample_menu_item.model_copy(update={"restaurant_id": "other-rest"})
        mock_restaurant_repo.get_by_id.return_value = sample_restaurant
        mock_menu_repo.get_by_id.return_value = wrong_item
        service = make_service(mock_order_repo, mock_menu_repo, mock_restaurant_repo)

        with pytest.raises(BusinessRuleError):
            service.place_order(
                customer_user,
                sample_restaurant.restaurant_id,
                [wrong_item.food_item_id],
            )


class TestRetrieval:

    def test_get_order_returns_order(
        self,
        mock_order_repo,
        mock_menu_repo,
        mock_restaurant_repo,
        sample_order,
    ):
        mock_order_repo.get_by_id.return_value = sample_order
        service = make_service(mock_order_repo, mock_menu_repo, mock_restaurant_repo)

        result = service.get_order(sample_order.order_id)

        assert result == sample_order

    def test_get_order_raises_for_missing_order(
        self,
        mock_order_repo,
        mock_menu_repo,
        mock_restaurant_repo,
    ):
        mock_order_repo.get_by_id.return_value = None
        service = make_service(mock_order_repo, mock_menu_repo, mock_restaurant_repo)

        with pytest.raises(NotFoundError):
            service.get_order("missing-order")

    def test_get_orders_by_status_filters_customer_scope(
        self,
        mock_order_repo,
        mock_menu_repo,
        mock_restaurant_repo,
        customer_user,
    ):
        mock_order_repo.get_by_customer_and_status.return_value = []
        service = make_service(mock_order_repo, mock_menu_repo, mock_restaurant_repo)

        service.get_orders_by_status(customer_user, OrderStatus.PENDING)

        mock_order_repo.get_by_customer_and_status.assert_called_once_with(
            customer_user.customer_id, OrderStatus.PENDING
        )


class TestCancelOrder:

    def test_cancel_order_updates_status_and_notifies(
        self,
        mock_order_repo,
        mock_menu_repo,
        mock_restaurant_repo,
        mock_notification_service,
        customer_user,
        sample_order,
    ):
        cancelled = sample_order.model_copy(update={"status": OrderStatus.CANCELLED})
        mock_order_repo.get_by_id.return_value = sample_order
        mock_order_repo.update_status.return_value = cancelled
        service = make_service(
            mock_order_repo,
            mock_menu_repo,
            mock_restaurant_repo,
            mock_notification_service,
        )

        result = service.cancel_order(customer_user, sample_order.order_id)

        assert result.status == OrderStatus.CANCELLED
        mock_order_repo.update_status.assert_called_once_with(
            sample_order.order_id, OrderStatus.CANCELLED
        )
        mock_notification_service.create.assert_called_once()

    def test_cancel_order_rejects_other_users(
        self,
        mock_order_repo,
        mock_menu_repo,
        mock_restaurant_repo,
        loyalty_customer,
        sample_order,
    ):
        mock_order_repo.get_by_id.return_value = sample_order
        service = make_service(mock_order_repo, mock_menu_repo, mock_restaurant_repo)

        with pytest.raises(AuthorizationError):
            service.cancel_order(loyalty_customer, sample_order.order_id)

    def test_cancel_order_rejects_non_pending_order(
        self,
        mock_order_repo,
        mock_menu_repo,
        mock_restaurant_repo,
        customer_user,
        completed_order,
    ):
        mock_order_repo.get_by_id.return_value = completed_order
        service = make_service(mock_order_repo, mock_menu_repo, mock_restaurant_repo)

        with pytest.raises(BusinessRuleError):
            service.cancel_order(customer_user, completed_order.order_id)


class TestCompleteOrder:

    def test_complete_order_marks_completed_and_notifies(
        self,
        mock_order_repo,
        mock_menu_repo,
        mock_restaurant_repo,
        mock_notification_service,
        sample_order,
    ):
        mock_order_repo.get_by_id.return_value = sample_order
        mock_order_repo.save.side_effect = lambda order: order
        service = make_service(
            mock_order_repo,
            mock_menu_repo,
            mock_restaurant_repo,
            mock_notification_service,
        )

        result = service.complete_order(sample_order.order_id)

        assert result.status == OrderStatus.COMPLETED
        mock_order_repo.save.assert_called_once()
        mock_notification_service.create.assert_called_once()

    def test_complete_order_rejects_non_pending_order(
        self,
        mock_order_repo,
        mock_menu_repo,
        mock_restaurant_repo,
        completed_order,
    ):
        mock_order_repo.get_by_id.return_value = completed_order
        service = make_service(mock_order_repo, mock_menu_repo, mock_restaurant_repo)

        with pytest.raises(BusinessRuleError):
            service.complete_order(completed_order.order_id)


class TestReorder:

    def test_reorder_uses_original_items_when_no_override_is_provided(
        self,
        mock_order_repo,
        mock_menu_repo,
        mock_restaurant_repo,
        mock_notification_service,
        customer_user,
        completed_order,
        sample_restaurant,
        sample_menu_item,
    ):
        mock_order_repo.get_by_id.return_value = completed_order
        mock_restaurant_repo.get_by_id.return_value = sample_restaurant
        mock_menu_repo.get_by_id.return_value = sample_menu_item
        mock_order_repo.save.side_effect = lambda order: order
        service = make_service(
            mock_order_repo,
            mock_menu_repo,
            mock_restaurant_repo,
            mock_notification_service,
        )

        result = service.reorder(customer_user, completed_order.order_id)

        assert result.order_id != completed_order.order_id
        assert result.items == completed_order.items
        assert result.customer_id == completed_order.customer_id
        assert result.restaurant_id == completed_order.restaurant_id
        assert result.status == OrderStatus.PENDING
        assert completed_order.status == OrderStatus.COMPLETED

    def test_reorder_uses_override_items_when_provided(
        self,
        mock_order_repo,
        mock_menu_repo,
        mock_restaurant_repo,
        customer_user,
        completed_order,
        sample_restaurant,
        sample_menu_item,
    ):
        updated_item = sample_menu_item.model_copy(update={"food_item_id": "item-002"})
        mock_order_repo.get_by_id.return_value = completed_order
        mock_restaurant_repo.get_by_id.return_value = sample_restaurant
        mock_menu_repo.get_by_id.return_value = updated_item
        mock_order_repo.save.side_effect = lambda order: order
        service = make_service(mock_order_repo, mock_menu_repo, mock_restaurant_repo)

        result = service.reorder(
            customer_user,
            completed_order.order_id,
            [updated_item.food_item_id],
        )

        assert result.items == [updated_item.food_item_id]

    def test_reorder_rejects_orders_owned_by_another_customer(
        self,
        mock_order_repo,
        mock_menu_repo,
        mock_restaurant_repo,
        loyalty_customer,
        completed_order,
    ):
        mock_order_repo.get_by_id.return_value = completed_order
        service = make_service(mock_order_repo, mock_menu_repo, mock_restaurant_repo)

        with pytest.raises(AuthorizationError):
            service.reorder(loyalty_customer, completed_order.order_id)

    def test_reorder_rejects_non_completed_orders(
        self,
        mock_order_repo,
        mock_menu_repo,
        mock_restaurant_repo,
        customer_user,
        sample_order,
    ):
        mock_order_repo.get_by_id.return_value = sample_order
        service = make_service(mock_order_repo, mock_menu_repo, mock_restaurant_repo)

        with pytest.raises(BusinessRuleError):
            service.reorder(customer_user, sample_order.order_id)

    def test_reorder_rejects_empty_override_items(
        self,
        mock_order_repo,
        mock_menu_repo,
        mock_restaurant_repo,
        customer_user,
        completed_order,
    ):
        mock_order_repo.get_by_id.return_value = completed_order
        service = make_service(mock_order_repo, mock_menu_repo, mock_restaurant_repo)

        with pytest.raises(BusinessRuleError):
            service.reorder(customer_user, completed_order.order_id, [])
