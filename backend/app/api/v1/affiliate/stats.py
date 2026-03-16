"""Affiliate personal stats with optional date-range filter.

GET /api/v1/affiliate/stats?from=2026-01-01&to=2026-03-31
"""

from datetime import date, datetime, timezone, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import require_affiliate
from app.models.affiliate_balance import AffiliateBalance
from app.models.conversion import Conversion, ConversionStatus
from app.models.referral_click import ReferralClick
from app.models.referral_link import ReferralLink
from app.models.user import User

router = APIRouter()


@router.get("/affiliate/stats")
async def affiliate_stats(
    date_from: Optional[date] = Query(None, alias="from", description="Start date (YYYY-MM-DD)"),
    date_to: Optional[date] = Query(None, alias="to", description="End date (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_affiliate),
):
    # Convert dates to datetimes (UTC)
    dt_from = datetime(date_from.year, date_from.month, date_from.day, tzinfo=timezone.utc) if date_from else None
    dt_to = datetime(date_to.year, date_to.month, date_to.day, 23, 59, 59, tzinfo=timezone.utc) if date_to else None

    # ── Clicks ────────────────────────────────────────────────────────────────
    click_q = (
        select(func.count(ReferralClick.id))
        .join(ReferralLink, ReferralClick.link_id == ReferralLink.id)
        .where(ReferralLink.affiliate_id == user.id)
    )
    if dt_from:
        click_q = click_q.where(ReferralClick.clicked_at >= dt_from)
    if dt_to:
        click_q = click_q.where(ReferralClick.clicked_at <= dt_to)
    total_clicks = (await db.execute(click_q)).scalar() or 0

    # ── Conversions ───────────────────────────────────────────────────────────
    conv_base = (
        select(Conversion)
        .join(ReferralLink, Conversion.referral_link_id == ReferralLink.id)
        .where(ReferralLink.affiliate_id == user.id)
    )
    if dt_from:
        conv_base = conv_base.where(Conversion.created_at >= dt_from)
    if dt_to:
        conv_base = conv_base.where(Conversion.created_at <= dt_to)

    total_conversions_q = select(func.count()).select_from(conv_base.subquery())
    total_conversions = (await db.execute(total_conversions_q)).scalar() or 0

    approved_conv_q = (
        select(func.count(), func.sum(Conversion.commission_earned))
        .join(ReferralLink, Conversion.referral_link_id == ReferralLink.id)
        .where(
            ReferralLink.affiliate_id == user.id,
            Conversion.status.in_([ConversionStatus.approved, ConversionStatus.paid]),
        )
    )
    if dt_from:
        approved_conv_q = approved_conv_q.where(Conversion.created_at >= dt_from)
    if dt_to:
        approved_conv_q = approved_conv_q.where(Conversion.created_at <= dt_to)
    approved_row = (await db.execute(approved_conv_q)).one()
    approved_conversions = approved_row[0] or 0
    total_earned = float(approved_row[1] or 0)

    # ── Links ─────────────────────────────────────────────────────────────────
    link_q = select(func.count(ReferralLink.id)).where(ReferralLink.affiliate_id == user.id)
    if dt_from:
        link_q = link_q.where(ReferralLink.created_at >= dt_from)
    if dt_to:
        link_q = link_q.where(ReferralLink.created_at <= dt_to)
    total_links = (await db.execute(link_q)).scalar() or 0

    # ── Conversion rate ───────────────────────────────────────────────────────
    conversion_rate = round((total_conversions / total_clicks * 100), 2) if total_clicks > 0 else 0.0

    # ── Current balance (not date-filtered — always current snapshot) ─────────
    bal_result = await db.execute(
        select(AffiliateBalance).where(AffiliateBalance.affiliate_id == user.id)
    )
    balance = bal_result.scalar_one_or_none()

    # ── Top performing links in the period ────────────────────────────────────
    top_links_q = (
        select(
            ReferralLink.id,
            ReferralLink.code,
            ReferralLink.short_url,
            func.count(ReferralClick.id).label("clicks"),
            func.count(Conversion.id).label("conversions"),
            func.coalesce(func.sum(Conversion.commission_earned), 0).label("earned"),
        )
        .outerjoin(ReferralClick, ReferralClick.link_id == ReferralLink.id)
        .outerjoin(
            Conversion,
            (Conversion.referral_link_id == ReferralLink.id)
            & Conversion.status.in_([ConversionStatus.approved, ConversionStatus.paid]),
        )
        .where(ReferralLink.affiliate_id == user.id)
        .group_by(ReferralLink.id, ReferralLink.code, ReferralLink.short_url)
        .order_by(func.count(ReferralClick.id).desc())
        .limit(5)
    )
    top_links_rows = (await db.execute(top_links_q)).all()

    return {
        "period": {
            "from": date_from.isoformat() if date_from else None,
            "to": date_to.isoformat() if date_to else None,
        },
        "summary": {
            "total_links": total_links,
            "total_clicks": total_clicks,
            "total_conversions": total_conversions,
            "approved_conversions": approved_conversions,
            "conversion_rate": conversion_rate,
            "total_earned": total_earned,
        },
        "balance": {
            "pending": float(balance.pending or 0) if balance else 0,
            "approved": float(balance.approved or 0) if balance else 0,
            "paid_out": float(balance.paid_out or 0) if balance else 0,
        },
        "top_links": [
            {
                "id": r.id,
                "code": r.code,
                "short_url": r.short_url,
                "clicks": r.clicks,
                "conversions": r.conversions,
                "earned": float(r.earned),
            }
            for r in top_links_rows
        ],
    }


@router.get("/affiliate/stats/daily")
async def affiliate_stats_daily(
    days: int = Query(30, ge=7, le=90, description="Number of days to include"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_affiliate),
):
    """Return daily click and conversion counts for the last N days (chart data)."""
    rows = (
        await db.execute(
            text("""
                WITH date_series AS (
                    SELECT generate_series(
                        CURRENT_DATE - CAST(:days AS INT) * INTERVAL '1 day',
                        CURRENT_DATE,
                        INTERVAL '1 day'
                    )::date AS day
                ),
                daily_clicks AS (
                    SELECT DATE(rc.clicked_at AT TIME ZONE 'UTC') AS day,
                           COUNT(*) AS clicks
                    FROM referral_clicks rc
                    JOIN referral_links rl ON rc.link_id = rl.id
                    WHERE rl.affiliate_id = :uid
                      AND rc.clicked_at >= CURRENT_DATE - CAST(:days AS INT) * INTERVAL '1 day'
                    GROUP BY DATE(rc.clicked_at AT TIME ZONE 'UTC')
                ),
                daily_conv AS (
                    SELECT DATE(c.created_at AT TIME ZONE 'UTC') AS day,
                           COUNT(*) AS conversions
                    FROM conversions c
                    JOIN referral_links rl ON c.referral_link_id = rl.id
                    WHERE rl.affiliate_id = :uid
                      AND c.status IN ('approved', 'paid')
                      AND c.created_at >= CURRENT_DATE - CAST(:days AS INT) * INTERVAL '1 day'
                    GROUP BY DATE(c.created_at AT TIME ZONE 'UTC')
                )
                SELECT ds.day::text AS date,
                       COALESCE(dc.clicks, 0)      AS clicks,
                       COALESCE(dconv.conversions, 0) AS conversions
                FROM date_series ds
                LEFT JOIN daily_clicks dc    ON dc.day    = ds.day
                LEFT JOIN daily_conv   dconv ON dconv.day = ds.day
                ORDER BY ds.day
            """),
            {"uid": user.id, "days": days},
        )
    ).mappings().all()

    return {
        "days": days,
        "series": [
            {"date": r["date"], "clicks": r["clicks"], "conversions": r["conversions"]}
            for r in rows
        ],
    }
