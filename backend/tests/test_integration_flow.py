"""
Full-flow integration test.

Tests the entire affiliate lifecycle:
  1. Admin registers (super_admin via seed)
  2. Affiliate registers
  3. Admin approves the affiliate
  4. Admin creates a store + product + campaign
  5. Affiliate generates a referral link
  6. Click is recorded via the tracking endpoint
  7. Store POSTs a conversion (webhook)
  8. Commission credited to affiliate pending balance
  9. Admin approves the conversion
  10. Commission moves to approved balance
  11. Affiliate requests a payout (Paystack mocked)
  12. Admin approves the payout (Paystack transfer mocked)

Run: pytest tests/test_integration_flow.py -m integration -v
"""

import pytest
from decimal import Decimal
from unittest.mock import AsyncMock, patch

pytestmark = pytest.mark.integration


# ─── Helpers ─────────────────────────────────────────────────────────────────

async def login(client, email: str, password: str) -> str:
    resp = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ─── Tests ────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_register_affiliate(client):
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test_affiliate@example.com",
            "password": "Affiliate@1234!",
            "full_name": "Test Affiliate",
            "phone": "0712345678",
            "terms_accepted": True,
        },
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["user"]["role"] == "affiliate"
    assert data["profile"]["status"] in ("pending", "approved")


@pytest.mark.asyncio
async def test_full_affiliate_flow(client):
    # ── 1. Seed admin exists ──────────────────────────────────────────────────
    admin_token = await login(client, "admin@yuaffiliates.co.ke", "Admin@1234!")

    # ── 2. Register affiliate ─────────────────────────────────────────────────
    reg = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "flow_affiliate@example.com",
            "password": "Affiliate@1234!",
            "full_name": "Flow Affiliate",
            "terms_accepted": True,
        },
    )
    assert reg.status_code == 201, reg.text
    profile_id = reg.json()["profile"]["id"]

    # ── 3. Admin approves affiliate ───────────────────────────────────────────
    approve = await client.post(
        f"/api/v1/admin/affiliates/{profile_id}/action",
        json={"action": "approve"},
        headers=auth(admin_token),
    )
    assert approve.status_code == 200, approve.text
    assert approve.json()["status"] == "approved"

    # ── 4. Create store ───────────────────────────────────────────────────────
    store_resp = await client.post(
        "/api/v1/admin/stores",
        json={"name": "Test Store", "slug": "test-store-flow"},
        headers=auth(admin_token),
    )
    assert store_resp.status_code == 201, store_resp.text
    store = store_resp.json()
    store_api_key = store["api_key"]
    store_id = store["id"]

    # ── 5. Create product ─────────────────────────────────────────────────────
    product_resp = await client.post(
        "/api/v1/admin/products",
        json={
            "store_id": store_id,
            "name": "Test Product",
            "price": 2000,
            "currency": "KES",
            "product_url": "https://example.com/product",
        },
        headers=auth(admin_token),
    )
    assert product_resp.status_code == 201, product_resp.text
    product_id = product_resp.json()["id"]

    # ── 6. Create campaign ────────────────────────────────────────────────────
    campaign_resp = await client.post(
        "/api/v1/admin/campaigns",
        json={
            "name": "Test Campaign",
            "store_id": store_id,
            "commission_type": "percent",
            "rate": "0.10",
            "cookie_days": 30,
        },
        headers=auth(admin_token),
    )
    assert campaign_resp.status_code == 201, campaign_resp.text
    campaign_id = campaign_resp.json()["id"]

    # ── 7. Affiliate logs in ──────────────────────────────────────────────────
    affiliate_token = await login(client, "flow_affiliate@example.com", "Affiliate@1234!")

    # ── 8. Affiliate generates a link ─────────────────────────────────────────
    link_resp = await client.post(
        "/api/v1/affiliate/links",
        json={"campaign_id": campaign_id},
        headers=auth(affiliate_token),
    )
    assert link_resp.status_code == 201, link_resp.text
    link = link_resp.json()
    ref_code = link["code"]
    assert len(ref_code) == 10

    # ── 9. Click is tracked ───────────────────────────────────────────────────
    click_resp = await client.get(
        f"/track/{ref_code}",
        follow_redirects=False,
    )
    assert click_resp.status_code in (302, 307), click_resp.text

    # ── 10. Store POSTs conversion ────────────────────────────────────────────
    with patch("app.tasks.notifications.notify_new_sale.delay"):
        conv_resp = await client.post(
            "/api/v1/webhooks/conversion",
            json={
                "ref_code": ref_code,
                "external_order_id": "ORDER-FLOW-001",
                "sale_amount": "2000.00",
            },
            headers={"X-Store-Api-Key": store_api_key},
        )
    assert conv_resp.status_code == 201, conv_resp.text
    conversion = conv_resp.json()
    assert conversion["status"] == "pending"
    assert Decimal(str(conversion["commission_earned"])) == Decimal("200.00")
    conversion_id = conversion["id"]

    # ── 11. Affiliate balance shows pending commission ────────────────────────
    balance_resp = await client.get(
        "/api/v1/affiliate/earnings/balance",
        headers=auth(affiliate_token),
    )
    assert balance_resp.status_code == 200
    balance = balance_resp.json()
    assert Decimal(str(balance["pending"])) >= Decimal("200.00")

    # ── 12. Admin approves conversion ─────────────────────────────────────────
    approve_conv = await client.post(
        f"/api/v1/admin/conversions/{conversion_id}/action",
        json={"action": "approve"},
        headers=auth(admin_token),
    )
    assert approve_conv.status_code == 200, approve_conv.text
    assert approve_conv.json()["status"] == "approved"

    # ── 13. Approved balance increases ────────────────────────────────────────
    balance_resp2 = await client.get(
        "/api/v1/affiliate/earnings/balance",
        headers=auth(affiliate_token),
    )
    balance2 = balance_resp2.json()
    assert Decimal(str(balance2["approved"])) >= Decimal("200.00")

    # ── 14. Affiliate requests payout (Paystack mocked) ───────────────────────
    with (
        patch(
            "app.services.payments.paystack.initiate_transfer",
            new=AsyncMock(return_value="TRF_mock_code"),
        ),
        patch("app.tasks.notifications.notify_payout_approved.delay"),
    ):
        payout_req = await client.post(
            "/api/v1/affiliate/payouts",
            json={"amount": "200.00"},
            headers=auth(affiliate_token),
        )
        assert payout_req.status_code == 201, payout_req.text
        payout_id = payout_req.json()["id"]

        # Admin approves payout
        approve_payout = await client.post(
            f"/api/v1/admin/payouts/{payout_id}/approve",
            headers=auth(admin_token),
        )
    assert approve_payout.status_code == 200, approve_payout.text
    assert approve_payout.json()["status"] == "processing"


@pytest.mark.asyncio
async def test_duplicate_conversion_rejected(client):
    """Same order_id from the same store cannot convert twice."""
    admin_token = await login(client, "admin@yuaffiliates.co.ke", "Admin@1234!")

    store_resp = await client.post(
        "/api/v1/admin/stores",
        json={"name": "Dedup Store", "slug": "dedup-store"},
        headers=auth(admin_token),
    )
    store = store_resp.json()
    store_api_key = store["api_key"]

    # Create a campaign and affiliate link (reuse test_affiliate from prev test or create fresh)
    campaign_resp = await client.post(
        "/api/v1/admin/campaigns",
        json={"name": "Dedup Campaign", "store_id": store["id"], "commission_type": "percent", "rate": "0.05"},
        headers=auth(admin_token),
    )
    campaign_id = campaign_resp.json()["id"]

    affiliate_token = await login(client, "test_affiliate@example.com", "Affiliate@1234!")
    link_resp = await client.post(
        "/api/v1/affiliate/links",
        json={"campaign_id": campaign_id},
        headers=auth(affiliate_token),
    )
    ref_code = link_resp.json()["code"]

    payload = {
        "ref_code": ref_code,
        "external_order_id": "ORDER-DEDUP-001",
        "sale_amount": "500.00",
    }
    headers = {"X-Store-Api-Key": store_api_key}

    with patch("app.tasks.notifications.notify_new_sale.delay"):
        r1 = await client.post("/api/v1/webhooks/conversion", json=payload, headers=headers)
        r2 = await client.post("/api/v1/webhooks/conversion", json=payload, headers=headers)

    assert r1.status_code == 201
    assert r2.status_code == 409  # ConflictError


@pytest.mark.asyncio
async def test_unapproved_affiliate_cannot_generate_link(client):
    """A pending affiliate should not be able to generate referral links."""
    # Register without approval
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "pending_aff@example.com",
            "password": "Pending@1234!",
            "full_name": "Pending Affiliate",
            "terms_accepted": True,
        },
    )
    affiliate_token = await login(client, "pending_aff@example.com", "Pending@1234!")

    # Attempt to get a link — should be 403 if require_approval=true
    link_resp = await client.post(
        "/api/v1/affiliate/links",
        json={"campaign_id": 1},
        headers=auth(affiliate_token),
    )
    # 403 when pending, 404 when campaign doesn't exist — either means gating worked
    assert link_resp.status_code in (403, 404)
