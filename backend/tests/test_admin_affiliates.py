"""
Admin affiliates API endpoints.

Tests list, update, approve/reject/suspend.
"""

import pytest
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import patch

pytestmark = pytest.mark.integration


async def create_pending_affiliate(client):
    """Helper: Register a pending affiliate."""
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test_aff@example.com",
            "password": "Test@1234!",
            "full_name": "Test Affiliate",
            "phone": "0712345678",
            "terms_accepted": True,
        },
    )
    assert resp.status_code == 201
    return resp.json()["profile"]["id"]


async def get_admin_token(client):
    """Helper: Login as admin."""
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@yuaffiliates.co.ke", "password": "Admin@1234!"}
    )
    assert resp.status_code == 200
    return resp.json()["access_token"]


def auth_headers(token: str):
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_list_admin_affiliates(client):
    admin_token = await get_admin_token(client)
    resp = await client.get("/api/v1/admin/affiliates/", headers=auth_headers(admin_token))
    assert resp.status_code == 200
    affiliates = resp.json()
    assert isinstance(affiliates, list)


@pytest.mark.asyncio
async def test_list_admin_affiliates_filter_status(client):
    admin_token = await get_admin_token(client)
    # Create pending
    profile_id = await create_pending_affiliate(client)
    resp = await client.get(
        "/api/v1/admin/affiliates/?status=pending",
        headers=auth_headers(admin_token)
    )
    assert resp.status_code == 200
    affiliates = resp.json()
    assert len(affiliates) > 0
    assert all(a["status"] == "pending" for a in affiliates)


@pytest.mark.asyncio
async def test_update_admin_affiliate(client):
    admin_token = await get_admin_token(client)
    profile_id = await create_pending_affiliate(client)
    update_data = {"phone": "0720000000", "website": "https://test.com"}
    resp = await client.patch(
        f"/api/v1/admin/affiliates/{profile_id}",
        json=update_data,
        headers=auth_headers(admin_token)
    )
    assert resp.status_code == 200
    updated = resp.json()
    assert updated["phone"] == "0720000000"
    assert updated["website"] == "https://test.com"
    assert updated["updated_at"]  # Should be set


@pytest.mark.asyncio
async def test_approve_admin_affiliate(client):
    admin_token = await get_admin_token(client)
    profile_id = await create_pending_affiliate(client)
    resp = await client.post(
        f"/api/v1/admin/affiliates/{profile_id}/approve",
        json={"notes": "Approved after review"},
        headers=auth_headers(admin_token)
    )
    assert resp.status_code == 200
    result = resp.json()
    assert result["message"] == "Affiliate approved"
    assert result["profile"]["status"] == "approved"
    assert result["profile"]["notes"] == "Approved after review"


@pytest.mark.asyncio
async def test_reject_admin_affiliate(client):
    admin_token = await get_admin_token(client)
    profile_id = await create_pending_affiliate(client)
    resp = await client.post(
        f"/api/v1/admin/affiliates/{profile_id}/reject",
        json={"notes": "Insufficient details"},
        headers=auth_headers(admin_token)
    )
    assert resp.status_code == 200
    result = resp.json()
    assert result["message"] == "Affiliate rejected"
    assert result["profile"]["status"] == "rejected"


@pytest.mark.asyncio
async def test_suspend_admin_affiliate(client):
    admin_token = await get_admin_token(client)
    profile_id = await create_pending_affiliate(client)
    # First approve
    await client.post(
        f"/api/v1/admin/affiliates/{profile_id}/approve",
        json={"notes": "Temp approve"},
        headers=auth_headers(admin_token)
    )
    # Then suspend
    resp = await client.post(
        f"/api/v1/admin/affiliates/{profile_id}/suspend",
        json={"notes": "Violated TOS"},
        headers=auth_headers(admin_token)
    )
    assert resp.status_code == 200
    result = resp.json()
    assert result["message"] == "Affiliate suspended"
    assert result["profile"]["status"] == "suspended"


@pytest.mark.asyncio
async def test_admin_affiliates_auth_required(client):
    resp = await client.get("/api/v1/admin/affiliates/")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_non_admin_cannot_list_affiliates(client):
    # Register affiliate
    await create_pending_affiliate(client)
    aff_token_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "test_aff@example.com", "password": "Test@1234!"}
    )
    aff_token = aff_token_resp.json()["access_token"]
    resp = await client.get("/api/v1/admin/affiliates/", headers=auth_headers(aff_token))
    assert resp.status_code == 403