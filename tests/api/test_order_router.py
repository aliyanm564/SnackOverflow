from unittest.mock import MagicMock

from backend.app.application.exceptions import (
    AuthorizationError,
    BusinessRuleError,
    NotFoundError,
)
from backend.app.domain.models.enums import OrderStatus
from backend.app.presentation.dependencies import get_order_service


ORDER_URL = "/api/v1/orders"


class TestPlaceOrder:

    def test_place_order_returns_201(
        self, client, customer, customer_headers, sample_order, override
    ):
        mock_svc = MagicMock()
        mock_svc.place_order.return_value = sample_order

        with override(get_order_service, mock_svc, current_user=customer):
            resp = client.post(
                ORDER_URL,
                json={
                    "restaurant_id": sample_order.restaurant_id,
                    "food_item_ids": sample_order.items,
                },
                headers=customer_headers,
            )

        assert resp.status_code == 201
        assert resp.json()["order_id"] == sample_order.order_id

    def test_place_order_returns_403_for_non_customer_error(
        self, client, owner, owner_headers, override
    ):
        mock_svc = MagicMock()
        mock_svc.place_order.side_effect = AuthorizationError(
            "Only customers can place orders."
        )

        with override(get_order_service, mock_svc, current_user=owner):
            resp = client.post(
                ORDER_URL,
                json={
                    "restaurant_id": "rest-api-001",
                    "food_item_ids": ["item-api-001"],
                },
                headers=owner_headers,
            )

        assert resp.status_code == 403

    def test_place_order_returns_404_for_missing_restaurant(
        self, client, customer, customer_headers, override
    ):
        mock_svc = MagicMock()
        mock_svc.place_order.side_effect = NotFoundError("Restaurant not found.")

        with override(get_order_service, mock_svc, current_user=customer):
            resp = client.post(
                ORDER_URL,
                json={
                    "restaurant_id": "missing-rest",
                    "food_item_ids": ["item-api-001"],
                },
                headers=customer_headers,
            )

        assert resp.status_code == 404


class TestListOrders:

    def test_customer_list_orders_uses_paginated_customer_scope(
        self, client, customer, customer_headers, sample_order, override
    ):
        mock_svc = MagicMock()
        mock_svc.get_paginated_orders.return_value = [sample_order]

        with override(get_order_service, mock_svc, current_user=customer):
            resp = client.get(f"{ORDER_URL}?offset=0&limit=10", headers=customer_headers)

        assert resp.status_code == 200
        assert len(resp.json()) == 1
        mock_svc.get_paginated_orders.assert_called_once_with(
            customer_id=customer.customer_id,
            offset=0,
            limit=10,
        )

    def test_owner_list_orders_uses_global_scope(
        self, client, owner, owner_headers, sample_order, override
    ):
        mock_svc = MagicMock()
        mock_svc.get_paginated_orders.return_value = [sample_order]

        with override(get_order_service, mock_svc, current_user=owner):
            resp = client.get(f"{ORDER_URL}?offset=5&limit=15", headers=owner_headers)

        assert resp.status_code == 200
        mock_svc.get_paginated_orders.assert_called_once_with(
            customer_id=None,
            offset=5,
            limit=15,
        )

    def test_list_orders_with_status_filter(
        self, client, customer, customer_headers, sample_order, override
    ):
        mock_svc = MagicMock()
        mock_svc.get_orders_by_status.return_value = [sample_order]

        with override(get_order_service, mock_svc, current_user=customer):
            resp = client.get(f"{ORDER_URL}?status=pending", headers=customer_headers)

        assert resp.status_code == 200
        mock_svc.get_orders_by_status.assert_called_once_with(
            customer, OrderStatus.PENDING
        )

    def test_list_orders_rejects_invalid_status(
        self, client, customer, customer_headers, override
    ):
        mock_svc = MagicMock()

        with override(get_order_service, mock_svc, current_user=customer):
            resp = client.get(f"{ORDER_URL}?status=bad-status", headers=customer_headers)

        assert resp.status_code == 400


class TestRestaurantOrders:

    def test_get_restaurant_orders_returns_200(
        self, client, owner, owner_headers, sample_order, override
    ):
        mock_svc = MagicMock()
        mock_svc.get_orders_for_restaurant.return_value = [sample_order]

        with override(get_order_service, mock_svc, current_user=owner):
            resp = client.get(
                f"{ORDER_URL}/restaurant/{sample_order.restaurant_id}",
                headers=owner_headers,
            )

        assert resp.status_code == 200
        mock_svc.get_orders_for_restaurant.assert_called_once_with(
            owner, sample_order.restaurant_id
        )

    def test_get_restaurant_orders_returns_403(
        self, client, customer, customer_headers, override
    ):
        mock_svc = MagicMock()
        mock_svc.get_orders_for_restaurant.side_effect = AuthorizationError("Forbidden.")

        with override(get_order_service, mock_svc, current_user=customer):
            resp = client.get(
                f"{ORDER_URL}/restaurant/rest-api-001",
                headers=customer_headers,
            )

        assert resp.status_code == 403


class TestGetOrder:

    def test_get_order_returns_200(
        self, client, customer, customer_headers, sample_order, override
    ):
        mock_svc = MagicMock()
        mock_svc.get_order.return_value = sample_order

        with override(get_order_service, mock_svc, current_user=customer):
            resp = client.get(
                f"{ORDER_URL}/{sample_order.order_id}",
                headers=customer_headers,
            )

        assert resp.status_code == 200
        assert resp.json()["order_id"] == sample_order.order_id

    def test_get_order_blocks_customer_from_other_order(
        self, client, customer, customer_headers, sample_order, override
    ):
        mock_svc = MagicMock()
        other_order = sample_order.model_copy(update={"customer_id": "someone-else"})
        mock_svc.get_order.return_value = other_order

        with override(get_order_service, mock_svc, current_user=customer):
            resp = client.get(
                f"{ORDER_URL}/{sample_order.order_id}",
                headers=customer_headers,
            )

        assert resp.status_code == 403

    def test_get_order_returns_404(
        self, client, customer, customer_headers, override
    ):
        mock_svc = MagicMock()
        mock_svc.get_order.side_effect = NotFoundError("Order not found.")

        with override(get_order_service, mock_svc, current_user=customer):
            resp = client.get(f"{ORDER_URL}/missing", headers=customer_headers)

        assert resp.status_code == 404


class TestCancelOrder:

    def test_cancel_order_returns_200(
        self, client, customer, customer_headers, completed_order, override
    ):
        mock_svc = MagicMock()
        cancelled = completed_order.model_copy(update={"status": OrderStatus.CANCELLED})
        mock_svc.cancel_order.return_value = cancelled

        with override(get_order_service, mock_svc, current_user=customer):
            resp = client.post(
                f"{ORDER_URL}/{completed_order.order_id}/cancel",
                headers=customer_headers,
            )

        assert resp.status_code == 200
        assert resp.json()["status"] == "cancelled"

    def test_cancel_order_returns_422(
        self, client, customer, customer_headers, sample_order, override
    ):
        mock_svc = MagicMock()
        mock_svc.cancel_order.side_effect = BusinessRuleError("Cannot cancel.")

        with override(get_order_service, mock_svc, current_user=customer):
            resp = client.post(
                f"{ORDER_URL}/{sample_order.order_id}/cancel",
                headers=customer_headers,
            )

        assert resp.status_code == 422
