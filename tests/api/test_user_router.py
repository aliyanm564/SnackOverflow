import pytest
from unittest.mock import MagicMock

from backend.app.application.exceptions import AuthorizationError, NotFoundError
from backend.app.presentation.dependencies import get_user_service
from backend.app.domain.models.user import UserRole


class TestGetMe:

    def test_get_own_profile_returns_200(
        self, client, customer, customer_headers, override
    ):
        mock_svc = MagicMock()
        with override(get_user_service, mock_svc, current_user=customer):
            resp = client.get("/api/v1/users/me", headers=customer_headers)
        assert resp.status_code == 200
        assert resp.json()["customer_id"] == customer.customer_id

    def test_no_token_returns_401(self, client):
        resp = client.get("/api/v1/users/me")
        assert resp.status_code == 401


class TestUpdateMe:

    def test_update_profile_returns_updated_user(
        self, client, customer, customer_headers, override
    ):
        updated = customer.model_copy(update={"name": "Alice Updated"})
        mock_svc = MagicMock()
        mock_svc.update_profile.return_value = updated

        with override(get_user_service, mock_svc, current_user=customer):
            resp = client.patch(
                "/api/v1/users/me",
                json={"name": "Alice Updated"},
                headers=customer_headers,
            )
        assert resp.status_code == 200
        assert resp.json()["name"] == "Alice Updated"

    def test_age_out_of_range_returns_422(
        self, client, customer, customer_headers, override
    ):
        mock_svc = MagicMock()
        with override(get_user_service, mock_svc, current_user=customer):
            resp = client.patch(
                "/api/v1/users/me",
                json={"age": 999},
                headers=customer_headers,
            )
        assert resp.status_code == 422


class TestGetUserById:

    def test_customer_can_get_own_profile(
        self, client, customer, customer_headers, override
    ):
        mock_svc = MagicMock()
        mock_svc.get_user.return_value = customer
        with override(get_user_service, mock_svc, current_user=customer):
            resp = client.get(
                f"/api/v1/users/{customer.customer_id}",
                headers=customer_headers,
            )
        assert resp.status_code == 200

    def test_customer_cannot_get_other_users_profile(
        self, client, customer, customer_headers, override
    ):
        mock_svc = MagicMock()
        with override(get_user_service, mock_svc, current_user=customer):
            resp = client.get(
                "/api/v1/users/someone-else",
                headers=customer_headers,
            )
        assert resp.status_code == 403

    def test_nonexistent_user_returns_404(
        self, client, owner, owner_headers, override
    ):
        mock_svc = MagicMock()
        mock_svc.get_user.side_effect = NotFoundError("User not found.")
        with override(get_user_service, mock_svc, current_user=owner):
            resp = client.get("/api/v1/users/ghost", headers=owner_headers)
        assert resp.status_code == 404


class TestChangeRole:

    def test_owner_can_change_role(
        self, client, owner, owner_headers, customer, override
    ):
        updated = customer.model_copy(update={"role": UserRole.DELIVERY_PERSON})
        mock_svc = MagicMock()
        mock_svc.change_role.return_value = updated

        with override(get_user_service, mock_svc, current_user=owner):
            resp = client.patch(
                f"/api/v1/users/{customer.customer_id}/role",
                json={"new_role": "delivery_person"},
                headers=owner_headers,
            )
        assert resp.status_code == 200
        assert resp.json()["role"] == "delivery_person"

    def test_invalid_role_string_returns_400(
        self, client, owner, owner_headers, override
    ):
        mock_svc = MagicMock()
        with override(get_user_service, mock_svc, current_user=owner):
            resp = client.patch(
                "/api/v1/users/some-id/role",
                json={"new_role": "wizard"},
                headers=owner_headers,
            )
        assert resp.status_code == 400

    def test_customer_cannot_change_roles(
        self, client, customer, customer_headers, override
    ):
        mock_svc = MagicMock()
        mock_svc.change_role.side_effect = AuthorizationError("Not permitted.")
        with override(get_user_service, mock_svc, current_user=customer):
            resp = client.patch(
                "/api/v1/users/some-id/role",
                json={"new_role": "delivery_person"},
                headers=customer_headers,
            )
        assert resp.status_code == 403


class TestDeleteUser:

    def test_user_can_delete_own_account(
        self, client, customer, customer_headers, override
    ):
        mock_svc = MagicMock()
        with override(get_user_service, mock_svc, current_user=customer):
            resp = client.delete(
                f"/api/v1/users/{customer.customer_id}",
                headers=customer_headers,
            )
        assert resp.status_code == 204

    def test_user_cannot_delete_other_account(
        self, client, customer, customer_headers, override
    ):
        mock_svc = MagicMock()
        with override(get_user_service, mock_svc, current_user=customer):
            resp = client.delete(
                "/api/v1/users/someone-else",
                headers=customer_headers,
            )
        assert resp.status_code == 403
