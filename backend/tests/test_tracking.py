"""
Tracking API endpoints: track_click.
"""

import pytest

pytestmark = pytest.mark.integration


async def get_admin_token(client):
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@yuaffiliates.co.ke", "password": "Admin@1234!"}
    )
    assert resp.status_code == 200
    return resp.json()["access_token"]


def auth(token):
    return {"Authorization": f"Bearer {token}"}


async def create_approved_affiliate_campaign_link(client):
    """Setup approved affiliate with campaign link."""
    admin_token = await get_admin_token(client)

    # Register affiliate
    reg_resp = await client.post("/api/v1/auth/register", json={
        "email": "track_aff@example.com",
        "password": "Track@1234!",
        "full_name": "Tracking Affiliate",
        "terms_accepted": True,
    })
    assert reg_resp.status_code == 201
    profile_id = reg_resp.json()["profile"]["id"]

    # Approve
    await client.post(
        f"/api/v1/admin/affiliates/{profile_id}/approve",
        json={"notes": "Test approve"},
        headers=auth(admin_token)
    )

    # Create store
    store_resp = await client.post("/api/v1/admin/stores", json={
        "name": "Track Store",
        "slug": "track-store"
    }, headers=auth(admin_token))
    assert store_resp.status_code == 201
    store_id = store_resp.json()["id"]

    # Create product
    product_resp = await client.post("/api/v1/admin/products", json={
        "store_id": store_id,
        "name": "Track Product",
        "price": 1000,
        "currency": "KES",
        "product_url": "https://example.com/track-product"
    }, headers=auth(admin_token))
    assert product_resp.status_code == 201
    product_id = product_resp.json()["id"]

    # Create campaign
    campaign_resp = await client.post("/api/v1/admin/campaigns", json={
        "name": "Track Campaign",
        "store_id": store_id,
        "product_id": product_id,
        "commission_type": "percent",
        "rate": "0.10",
        "cookie_days": 30
    }, headers=auth(admin_token))
    assert campaign_resp.status_code == 201
    campaign_id = campaign_resp.json()["id"]

    # Affiliate login & link
    aff_login = await client.post("/api/v1/auth/login", json={
        "email": "track_aff@example.com",
        "password": "Track@1234!"
    })
    aff_token = aff_login.json()["access_token"]
    link_resp = await client.post("/api/v1/affiliate/links", json={
        "campaign_id": campaign_id
    }, headers=auth(aff_token))
    assert link_resp.status_code == 201
    ref_code = link_resp.json()["code"]

    expected_redirect = "https://example.com/track-product?ref=" + ref_code

    return ref_code, expected_redirect


@pytest.mark.asyncio
async def test_track_click_valid(client):
    ref_code, expected_redirect = await create_approved_affiliate_campaign_link(client)
    resp = await client.get(f"/track/{ref_code}")
    assert resp.status_code == 302
    assert resp.next.url == expected_redirect
    assert resp.cookies["yu_aff_ref"] == ref_code


@pytest.mark.asyncio
async def test_track_click_invalid(client):
    resp = await client.get("/track/invalid123")
    assert resp.status_code == 302
    assert resp.next.url == "/"
    assert "yu_aff_ref" not in resp.cookies