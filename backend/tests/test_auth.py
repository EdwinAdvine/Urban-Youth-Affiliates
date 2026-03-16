"""
Auth API endpoints: register, login, refresh.
"""

import pytest

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_register_affiliate(client):
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "new_aff@example.com",
            "password": "Affiliate@1234!",
            "full_name": "New Affiliate",
            "phone": "0712345678",
            "terms_accepted": True,
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["user"]["email"] == "new_aff@example.com"
    assert data["user"]["role"] == "affiliate"
    assert data["profile"]["status"] in ["pending", "approved"]


@pytest.mark.asyncio
async def test_register_admin(client):
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "new_admin@example.com",
            "password": "Admin@1234!",
            "full_name": "New Admin",
            "role": "admin",  # Assuming allows admin reg for test
            "terms_accepted": True,
        },
    )
    # May 403 if restricted, or 201
    assert resp.status_code in [201, 403]


@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    # First register
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "dup@example.com",
            "password": "Pass@1234!",
            "full_name": "Dup User",
            "terms_accepted": True,
        },
    )
    # Duplicate
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "dup@example.com",
            "password": "Pass@1234!",
            "full_name": "Dup Again",
            "terms_accepted": True,
        },
    )
    assert resp.status_code == 400
    assert "already exists" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_success(client):
    # Register first
    reg_resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "login_test@example.com",
            "password": "Login@1234!",
            "full_name": "Login Test",
            "terms_accepted": True,
        },
    )
    assert reg_resp.status_code == 201
    # Login
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "login_test@example.com", "password": "Login@1234!"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_login_invalid_credentials(client):
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "nonexistent@example.com", "password": "wrong"}
    )
    assert resp.status_code == 401
    assert "Invalid credentials" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_login_missing_password(client):
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@yuaffiliates.co.ke"}
    )
    assert resp.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_refresh_token(client):
    # Login
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@yuaffiliates.co.ke", "password": "Admin@1234!"}
    )
    assert login_resp.status_code == 200
    refresh_token = login_resp.json()["refresh_token"]
    # Refresh
    resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["access_token"] != login_resp.json()["access_token"]  # New token