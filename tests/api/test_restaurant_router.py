import pytest
from unittest.mock import MagicMock

from backend.app.application.exceptions import AuthorizationError, NotFoundError
from backend.app.presentation.dependencies import get_restaurant_service

class TestCreateRestaurant: 

    def test_owner_can_create(self, client, owner, owner_headers, sample_restaurant, override):
        mock_svc = MagicMock()
        mock_svc.create_restaurant.return_value = sample_restaurant
        with override(get_restaurant_service, mock_svc, current_user=owner):
            resp = client.post("/api/v1/restaurants", json={
                "name": "API Bistro", "location": "City_1"
            }, headers=owner_headers)
        assert resp.status_code == 201
        assert resp.json()["name"] == "API Bistro"
     
    def test_customer_gets_403(self, client, customer, customer_headers, override):
        mock_svc = MagicMock()
        mock_svc.create_restaurant.side_effect = AuthorizationError("Not allowed")
        with override(get_restaurant_service, mock_svc, current_user=customer):
            resp = client.post("/api/v1/restaurants", json={
                "name": "Nope"
            }, headers=customer_headers)
        assert resp.status_code == 403

class TestGetRestaurant:

    def test_get_existing_restaurant(self, client, sample_restaurant, override):
        mock_svc = MagicMock()
        mock_svc.get_restaurant.return_value = sample_restaurant
        with override(get_restaurant_service, mock_svc):
            resp = client.get(f"/api/v1/restaurants/{sample_restaurant.restaurant_id}")
        assert resp.status_code == 200
        assert resp.json()["restaurant_id"] == sample_restaurant.restaurant_id

    def test_missing_restaurant_returns_404(self, client, override):
        mock_svc = MagicMock()
        mock_svc.get_restaurant.side_effect = NotFoundError("Not found")
        with override(get_restaurant_service, mock_svc):
            resp = client.get("/api/v1/restaurants/fake-id")
        assert resp.status_code == 404

class TestUpdateRestaurant:

    def test_owner_can_update(self, client, owner, owner_headers, sample_restaurant, override):
        updated = sample_restaurant.model_copy(update={"name": "New Name"})
        mock_svc = MagicMock()
        mock_svc.update_restaurant.return_value = updated
        with override(get_restaurant_service, mock_svc, current_user=owner):
            resp = client.patch(f"/api/v1/restaurants/{sample_restaurant.restaurant_id}", json={
                "name": "New Name"
            }, headers=owner_headers)
        assert resp.status_code == 200
        assert resp.json()["name"] == "New Name"

    def test_wrong_owner_gets_403(self, client, customer, customer_headers, sample_restaurant, override):
        mock_svc = MagicMock()
        mock_svc.update_restaurant.side_effect = AuthorizationError("Not your restaurant")
        with override(get_restaurant_service, mock_svc, current_user=customer):
            resp = client.patch(f"/api/v1/restaurants/{sample_restaurant.restaurant_id}", json={
                "name": "Stolen"
            }, headers=customer_headers)
        assert resp.status_code == 403


class TestDeleteRestaurant:

    def test_owner_can_delete(self, client, owner, owner_headers, sample_restaurant, override):
        mock_svc = MagicMock()
        with override(get_restaurant_service, mock_svc, current_user=owner):
            resp = client.delete(f"/api/v1/restaurants/{sample_restaurant.restaurant_id}", headers=owner_headers)
        assert resp.status_code == 204

    def test_wrong_owner_gets_403(self, client, customer, customer_headers, sample_restaurant, override):
        mock_svc = MagicMock()
        mock_svc.delete_restaurant.side_effect = AuthorizationError("Not yours")
        with override(get_restaurant_service, mock_svc, current_user=customer):
            resp = client.delete(f"/api/v1/restaurants/{sample_restaurant.restaurant_id}", headers=customer_headers)
        assert resp.status_code == 403