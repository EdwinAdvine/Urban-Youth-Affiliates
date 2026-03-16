"""
Paystack payment gateway service.
Handles Transfer Recipient creation and Transfer initiation for affiliate payouts.
"""

import logging
from typing import Optional
import httpx

from app.config import settings
from app.exceptions import PaymentError

logger = logging.getLogger(__name__)

PAYSTACK_BASE_URL = "https://api.paystack.co"


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {settings.paystack_secret_key}",
        "Content-Type": "application/json",
    }


async def create_transfer_recipient(
    name: str,
    bank_code: str,
    account_number: str,
    currency: str = "KES",
) -> str:
    """Create a Paystack Transfer Recipient and return recipient_code."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{PAYSTACK_BASE_URL}/transferrecipient",
            headers=_headers(),
            json={
                "type": "nuban",
                "name": name,
                "bank_code": bank_code,
                "account_number": account_number,
                "currency": currency,
            },
            timeout=30,
        )

    data = response.json()
    if not data.get("status"):
        raise PaymentError(f"Paystack error: {data.get('message', 'Unknown error')}")

    recipient_code = data["data"]["recipient_code"]
    logger.info(f"Created Paystack recipient: {recipient_code} for {name}")
    return recipient_code


async def initiate_transfer(
    recipient_code: str,
    amount_kes: float,
    reason: str = "Affiliate commission payout",
) -> str:
    """Initiate a Paystack transfer and return transfer_code. Amount in KES (kobo for NGN)."""
    # Paystack amount in smallest currency unit (cents for KES = 100x)
    amount_in_units = int(amount_kes * 100)

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{PAYSTACK_BASE_URL}/transfer",
            headers=_headers(),
            json={
                "source": "balance",
                "amount": amount_in_units,
                "recipient": recipient_code,
                "reason": reason,
            },
            timeout=30,
        )

    data = response.json()
    if not data.get("status"):
        raise PaymentError(f"Paystack transfer failed: {data.get('message', 'Unknown error')}")

    transfer_code = data["data"]["transfer_code"]
    logger.info(f"Initiated Paystack transfer: {transfer_code} amount={amount_kes}")
    return transfer_code


async def verify_transfer(transfer_code: str) -> dict:
    """Verify a transfer status."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{PAYSTACK_BASE_URL}/transfer/{transfer_code}",
            headers=_headers(),
            timeout=30,
        )

    data = response.json()
    if not data.get("status"):
        raise PaymentError(f"Paystack verify failed: {data.get('message', 'Unknown error')}")

    return data["data"]


async def verify_webhook_signature(body: bytes, signature: str) -> bool:
    """Verify Paystack webhook signature using HMAC-SHA512."""
    import hmac
    import hashlib

    expected = hmac.new(
        settings.paystack_webhook_secret.encode(),
        body,
        hashlib.sha512,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


async def list_banks(country: str = "kenya") -> list:
    """List supported banks for a country."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{PAYSTACK_BASE_URL}/bank",
            headers=_headers(),
            params={"country": country, "use_cursor": "true", "perPage": "100"},
            timeout=30,
        )

    data = response.json()
    if not data.get("status"):
        return []
    return data.get("data", [])
