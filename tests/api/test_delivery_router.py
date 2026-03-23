import pytest
from unittest.mock import MagicMock

from backend.app.application.exceptions import AuthorizationError, BusinessRuleError, NotFoundError
from backend.app.presentation.dependencies import get_delivery_service


class TestAssignDelivery:

    def test_owner_can_assign(self, client, owner, owner_headers, sample_delivery, override):
        mock_svc = MagicMock()
        mock_svc.assign_delivery.return_value = sample_delivery
        with override(get_delivery_service, mock_svc, current_user=owner):
            resp = client.post("/api/v1/deliveries/order-api-001", json={
                "delivery_method": "bike", "delivery_distance": 3.5
            }, headers=owner_headers)
        assert resp.status_code == 201
        assert resp.json()["order_id"] == sample_delivery.order_id

    def test_customer_gets_403(self, client, customer, customer_headers, override):
        mock_svc = MagicMock()
        mock_svc.assign_delivery.side_effect = AuthorizationError("Not allowed")
        with override(get_delivery_service, mock_svc, current_user=customer):
            resp = client.post("/api/v1/deliveries/order-001", json={}, headers=customer_headers)
        assert resp.status_code == 403

    def test_duplicate_delivery_gets_422(self, client, owner, owner_headers, override):
        mock_svc = MagicMock()
        mock_svc.assign_delivery.side_effect = BusinessRuleError("Already exists")
        with override(get_delivery_service, mock_svc, current_user=owner):
            resp = client.post("/api/v1/deliveries/order-001", json={}, headers=owner_headers)
        assert resp.status_code == 422

    def test_order_not_found_gets_404(self, client, owner, owner_headers, override):
        mock_svc = MagicMock()
        mock_svc.assign_delivery.side_effect = NotFoundError("Order not found")
        with override(get_delivery_service, mock_svc, current_user=owner):
            resp = client.post("/api/v1/deliveries/fake-order", json={}, headers=owner_headers)
        assert resp.status_code == 404


class TestGetDelivery:

    def test_get_existing_delivery(self, client, sample_delivery, override):
        mock_svc = MagicMock()
        mock_svc.get_delivery.return_value = sample_delivery
        with override(get_delivery_service, mock_svc):
            resp = client.get(f"/api/v1/deliveries/{sample_delivery.order_id}")
        assert resp.status_code == 200
        assert resp.json()["order_id"] == sample_delivery.order_id

    def test_missing_delivery_returns_404(self, client, override):
        mock_svc = MagicMock()
        mock_svc.get_delivery.side_effect = NotFoundError("Not found")
        with override(get_delivery_service, mock_svc):
            resp = client.get("/api/v1/deliveries/fake-order")
        assert resp.status_code == 404


class TestUpdateDelivery:

    def test_owner_can_update(self, client, owner, owner_headers, sample_delivery, override):
        mock_svc = MagicMock()
        mock_svc.update_delivery.return_value = sample_delivery
        with override(get_delivery_service, mock_svc, current_user=owner):
            resp = client.patch(f"/api/v1/deliveries/{sample_delivery.order_id}", json={
                "traffic_condition": "High"
            }, headers=owner_headers)
        assert resp.status_code == 200

    def test_customer_gets_403(self, client, customer, customer_headers, override):
        mock_svc = MagicMock()
        mock_svc.update_delivery.side_effect = AuthorizationError("Not allowed")
        with override(get_delivery_service, mock_svc, current_user=customer):
            resp = client.patch("/api/v1/deliveries/order-001", json={
                "traffic_condition": "High"
            }, headers=customer_headers)
        assert resp.status_code == 403