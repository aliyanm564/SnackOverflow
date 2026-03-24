from unittest.mock import MagicMock

from backend.app.application.exceptions import AuthorizationError, NotFoundError
from backend.app.presentation.dependencies import get_menu_service

MENU_URL = "/api/v1/menu"
RESTAURANT_MENU_URL = "/api/v1/restaurants/test-restaurant/menu"


class TestCreateMenuItem:

    def test_create_menu_item_returns_201(
        self, client, owner, owner_headers, sample_menu_item, override
    ):
        mock_svc = MagicMock()
        mock_svc.add_item.return_value = sample_menu_item

        with override(get_menu_service, mock_svc, current_user=owner):
            resp = client.post(
                RESTAURANT_MENU_URL,
                json={
                    "name": sample_menu_item.name,
                    "category": sample_menu_item.category,
                    "price": sample_menu_item.price,
                },
                headers=owner_headers,
            )

        assert resp.status_code == 201
        assert resp.json()["name"] == sample_menu_item.name

    def test_create_menu_item_unauthorized(
        self, client, customer, customer_headers, override
    ):
        mock_svc = MagicMock()
        mock_svc.add_item.side_effect = AuthorizationError("Forbidden")

        with override(get_menu_service, mock_svc, current_user=customer):
            resp = client.post(
                RESTAURANT_MENU_URL,
                json={"name": "Burger", "category": "Fast Food", "price": 10},
                headers=customer_headers,
            )

        assert resp.status_code == 403


class TestGetMenuItem:

    def test_get_menu_item_returns_200(
        self, client, customer, customer_headers, sample_menu_item, override
    ):
        mock_svc = MagicMock()
        mock_svc.get_item.return_value = sample_menu_item

        with override(get_menu_service, mock_svc, current_user=customer):
            resp = client.get(
                f"{MENU_URL}/{sample_menu_item.food_item_id}",
                headers=customer_headers,
            )

        assert resp.status_code == 200
        assert resp.json()["food_item_id"] == sample_menu_item.food_item_id

    def test_get_menu_item_not_found(
        self, client, customer, customer_headers, override
    ):
        mock_svc = MagicMock()
        mock_svc.get_item.side_effect = NotFoundError("Not found")

        with override(get_menu_service, mock_svc, current_user=customer):
            resp = client.get(f"{MENU_URL}/missing", headers=customer_headers)

        assert resp.status_code == 404


class TestRestaurantMenu:

    def test_get_restaurant_menu_returns_200(
        self, client, customer, customer_headers, sample_menu_item, override
    ):
        mock_svc = MagicMock()
        mock_svc.list_items_paginated.return_value = [sample_menu_item]

        with override(get_menu_service, mock_svc, current_user=customer):
            resp = client.get(RESTAURANT_MENU_URL, headers=customer_headers)

        assert resp.status_code == 200
        assert len(resp.json()) == 1


class TestUpdateMenuItem:

    def test_update_menu_item_returns_200(
        self, client, owner, owner_headers, sample_menu_item, override
    ):
        mock_svc = MagicMock()
        updated = sample_menu_item.model_copy(update={"name": "Updated"})
        mock_svc.update_item.return_value = updated

        with override(get_menu_service, mock_svc, current_user=owner):
            resp = client.patch(
                f"{MENU_URL}/{sample_menu_item.food_item_id}",
                json={"name": "Updated"},
                headers=owner_headers,
            )

        assert resp.status_code == 200
        assert resp.json()["name"] == "Updated"


class TestDeleteMenuItem:

    def test_delete_menu_item_returns_204(
        self, client, owner, owner_headers, sample_menu_item, override
    ):
        mock_svc = MagicMock()
        mock_svc.delete_item.return_value = None

        with override(get_menu_service, mock_svc, current_user=owner):
            resp = client.delete(
                f"{MENU_URL}/{sample_menu_item.food_item_id}",
                headers=owner_headers,
            )

        assert resp.status_code == 204


class TestSearchAndFilter:

    def test_search_menu_items_returns_200(
        self, client, customer, customer_headers, sample_menu_item, override
    ):
        mock_svc = MagicMock()
        mock_svc.search_items.return_value = [sample_menu_item]

        with override(get_menu_service, mock_svc, current_user=customer):
            resp = client.get(
                f"{MENU_URL}/search?q=Burger",
                headers=customer_headers,
            )

        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_filter_menu_items_returns_200(
        self, client, customer, customer_headers, sample_menu_item, override
    ):
        mock_svc = MagicMock()
        mock_svc.filter_by_category.return_value = [sample_menu_item]

        with override(get_menu_service, mock_svc, current_user=customer):
            resp = client.get(
                f"{MENU_URL}/filter?category=Fast Food",
                headers=customer_headers,
            )

        assert resp.status_code == 200
        assert len(resp.json()) == 1
