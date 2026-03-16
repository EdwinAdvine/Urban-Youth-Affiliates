"""
Unit tests for commission calculation logic.
"""

import pytest
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

from app.models.campaign import Campaign, CommissionType
from app.services.commission_service import calculate_commission


@pytest.mark.asyncio
async def test_percent_commission():
    campaign = Campaign(commission_type=CommissionType.percent, rate=Decimal("0.10"))
    result = await calculate_commission(None, campaign, Decimal("1000"))
    assert result == Decimal("100.00")


@pytest.mark.asyncio
async def test_fixed_commission():
    campaign = Campaign(commission_type=CommissionType.fixed, rate=Decimal("50"))
    result = await calculate_commission(None, campaign, Decimal("1000"))
    assert result == Decimal("50.00")


@pytest.mark.asyncio
async def test_no_campaign_uses_default():
    from unittest.mock import patch
    with patch("app.services.commission_service.settings") as mock_settings:
        mock_settings.default_commission_rate = 0.10
        result = await calculate_commission(None, None, Decimal("1000"))
        assert result == Decimal("100.00")


@pytest.mark.asyncio
async def test_min_sale_threshold_not_met():
    campaign = Campaign(
        commission_type=CommissionType.percent,
        rate=Decimal("0.10"),
        min_sale_amount=Decimal("500"),
    )
    result = await calculate_commission(None, campaign, Decimal("100"))
    assert result == Decimal("0.00")


@pytest.mark.asyncio
async def test_min_sale_threshold_met():
    campaign = Campaign(
        commission_type=CommissionType.percent,
        rate=Decimal("0.10"),
        min_sale_amount=Decimal("500"),
    )
    result = await calculate_commission(None, campaign, Decimal("1000"))
    assert result == Decimal("100.00")


def test_link_code_uniqueness():
    """Generated referral codes must be unique across many calls."""
    from app.services.tracking_service import generate_code

    codes = {generate_code() for _ in range(1000)}
    # All 1000 generated codes should be distinct
    assert len(codes) == 1000


def test_link_code_format():
    """Generated referral codes must be exactly 10 alphanumeric characters."""
    from app.services.tracking_service import generate_code
    import re

    for _ in range(20):
        code = generate_code()
        assert len(code) == 10
        assert re.match(r"^[A-Za-z0-9]+$", code), f"Non-alphanumeric code: {code}"
