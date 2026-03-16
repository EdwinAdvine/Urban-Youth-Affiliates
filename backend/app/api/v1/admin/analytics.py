"""Admin analytics endpoint.

Uses the affiliate_performance and platform_overview PostgreSQL views
created in migration 010 instead of raw aggregate queries.
"""

from typing import Optional
from datetime import date, datetime, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import require_admin
from app.models.affiliate_profile import AffiliateProfile, AffiliateStatus
from app.models.conversion import Conversion, ConversionStatus
from app.models.payout_request import PayoutRequest, PayoutStatus
from app.models.product import Product
from app.models.referral_link import ReferralLink
from app.models.user import User

router = APIRouter()


@router.get("/admin/analytics")
async def platform_analytics(
    date_from: Optional[date] = Query(None, alias="from"),
    date_to: Optional[date] = Query(None, alias="to"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin),
):
    dt_from = (
        datetime(date_from.year, date_from.month, date_from.day, tzinfo=timezone.utc)
        if date_from
        else None
    )
    dt_to = (
        datetime(date_to.year, date_to.month, date_to.day, 23, 59, 59, tzinfo=timezone.utc)
        if date_to
        else None
    )

    # ── Platform overview (from view when no date filter, else raw) ────────────
    if dt_from is None and dt_to is None:
        # Use the pre-built view for max performance
        overview = (await db.execute(text("SELECT * FROM platform_overview"))).mappings().one()
        total_affiliates = overview["total_affiliates"] or 0
        active_affiliates = overview["active_affiliates"] or 0
        total_clicks = overview["total_clicks"] or 0
        total_conversions = overview["total_conversions"] or 0
        total_revenue = float(overview["total_revenue"] or 0)
        total_commissions = float(overview["total_commissions_earned"] or 0)
    else:
        # Date-filtered raw queries
        total_affiliates = (
            await db.execute(select(func.count(AffiliateProfile.id)))
        ).scalar() or 0
        active_affiliates = (
            await db.execute(
                select(func.count(AffiliateProfile.id)).where(
                    AffiliateProfile.status == AffiliateStatus.approved
                )
            )
        ).scalar() or 0

        click_q = select(func.count())
        from app.models.referral_click import ReferralClick
        click_q = select(func.count(ReferralClick.id))
        if dt_from:
            click_q = click_q.where(ReferralClick.clicked_at >= dt_from)
        if dt_to:
            click_q = click_q.where(ReferralClick.clicked_at <= dt_to)
        total_clicks = (await db.execute(click_q)).scalar() or 0

        conv_q = select(
            func.count(Conversion.id),
            func.coalesce(func.sum(Conversion.sale_amount), 0),
            func.coalesce(func.sum(Conversion.commission_earned), 0),
        )
        if dt_from:
            conv_q = conv_q.where(Conversion.created_at >= dt_from)
        if dt_to:
            conv_q = conv_q.where(Conversion.created_at <= dt_to)
        conv_row = (await db.execute(conv_q)).one()
        total_conversions = conv_row[0] or 0
        total_revenue = float(conv_row[1] or 0)
        total_commissions = float(conv_row[2] or 0)

    # ── Derived stats ──────────────────────────────────────────────────────────
    conversion_rate = (
        round(total_conversions / total_clicks * 100, 2) if total_clicks > 0 else 0.0
    )

    pending_approvals = (
        await db.execute(
            select(func.count(AffiliateProfile.id)).where(
                AffiliateProfile.status == AffiliateStatus.pending
            )
        )
    ).scalar() or 0

    pending_payouts = float(
        (
            await db.execute(
                select(func.coalesce(func.sum(PayoutRequest.amount), 0)).where(
                    PayoutRequest.status == PayoutStatus.pending
                )
            )
        ).scalar()
        or 0
    )

    # ── Top affiliates (from view) ─────────────────────────────────────────────
    top_affiliates_rows = (
        await db.execute(
            text(
                """
                SELECT affiliate_id, full_name, total_earned AS earned, total_conversions AS conversions
                FROM affiliate_performance
                WHERE status = 'approved'
                ORDER BY total_earned DESC
                LIMIT 10
                """
            )
        )
    ).mappings().all()

    # ── Top products (raw — view doesn't track per-product) ───────────────────
    top_products_q = (
        select(
            Product.id.label("product_id"),
            Product.name,
            func.count(Conversion.id).label("conversions"),
            func.coalesce(func.sum(Conversion.sale_amount), 0).label("revenue"),
        )
        .join(ReferralLink, Conversion.referral_link_id == ReferralLink.id)
        .join(Product, Product.id == ReferralLink.campaign_id)  # approximate join via campaign
        .where(Conversion.status.in_([ConversionStatus.approved, ConversionStatus.paid]))
        .group_by(Product.id, Product.name)
        .order_by(func.sum(Conversion.sale_amount).desc())
        .limit(10)
    )
    # Simpler fallback: join via store
    top_products_q2 = (
        select(
            Product.id.label("product_id"),
            Product.name,
            func.count(Conversion.id).label("conversions"),
            func.coalesce(func.sum(Conversion.sale_amount), 0).label("revenue"),
        )
        .join(Product, Conversion.store_id == Product.store_id)
        .where(
            Conversion.status.in_([ConversionStatus.approved, ConversionStatus.paid]),
            Product.is_deleted == False,  # noqa: E712
        )
        .group_by(Product.id, Product.name)
        .order_by(func.sum(Conversion.sale_amount).desc())
        .limit(10)
    )
    if dt_from:
        top_products_q2 = top_products_q2.where(Conversion.created_at >= dt_from)
    if dt_to:
        top_products_q2 = top_products_q2.where(Conversion.created_at <= dt_to)
    top_products_rows = (await db.execute(top_products_q2)).all()

    return {
        "total_affiliates": total_affiliates,
        "active_affiliates": active_affiliates,
        "pending_approvals": pending_approvals,
        "total_clicks": total_clicks,
        "total_conversions": total_conversions,
        "conversion_rate": conversion_rate,
        "total_revenue": total_revenue,
        "total_commissions": total_commissions,
        "pending_payouts": pending_payouts,
        "top_affiliates": [
            {
                "affiliate_id": r["affiliate_id"],
                "full_name": r["full_name"] or "Unknown",
                "earned": float(r["earned"] or 0),
                "conversions": int(r["conversions"] or 0),
            }
            for r in top_affiliates_rows
        ],
        "top_products": [
            {
                "product_id": r.product_id,
                "name": r.name,
                "conversions": r.conversions,
                "revenue": float(r.revenue or 0),
            }
            for r in top_products_rows
        ],
    }
