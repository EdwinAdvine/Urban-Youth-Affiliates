"""010 notifications

Revision ID: 010_notifications
Revises: 009_creative_assets
Create Date: 2026-03-16

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "010_notifications"
down_revision: Union[str, None] = "009_creative_assets"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column(
            "notification_type",
            sa.String(50),
            nullable=False,
            server_default="info",
        ),
        sa.Column("read", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("action_url", sa.String(500), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"])
    op.create_index("ix_notifications_read", "notifications", ["read"])
    op.create_index("ix_notifications_created_at", "notifications", ["created_at"])

    # Analytics views
    op.execute("""
        CREATE OR REPLACE VIEW affiliate_performance AS
        SELECT
            u.id AS affiliate_id,
            u.email,
            ap.full_name,
            ap.status,
            COUNT(DISTINCT rl.id) AS total_links,
            COUNT(DISTINCT rc.id) AS total_clicks,
            COUNT(DISTINCT CASE WHEN c.status IN ('approved', 'paid') THEN c.id END) AS total_conversions,
            COALESCE(SUM(CASE WHEN c.status IN ('approved', 'paid') THEN c.commission_earned END), 0) AS total_earned,
            COALESCE(SUM(CASE WHEN c.status = 'pending' THEN c.commission_earned END), 0) AS pending_earnings,
            CASE
                WHEN COUNT(DISTINCT rc.id) > 0
                THEN ROUND(
                    COUNT(DISTINCT CASE WHEN c.status IN ('approved','paid') THEN c.id END)::numeric
                    / COUNT(DISTINCT rc.id)::numeric * 100, 2
                )
                ELSE 0
            END AS conversion_rate
        FROM users u
        JOIN affiliate_profiles ap ON ap.user_id = u.id
        LEFT JOIN referral_links rl ON rl.affiliate_id = u.id
        LEFT JOIN referral_clicks rc ON rc.link_id = rl.id
        LEFT JOIN conversions c ON c.referral_link_id = rl.id
        WHERE u.role = 'affiliate'
        GROUP BY u.id, u.email, ap.full_name, ap.status
    """)

    op.execute("""
        CREATE OR REPLACE VIEW platform_overview AS
        SELECT
            (SELECT COUNT(*) FROM users
             WHERE role = 'affiliate' AND is_deleted = false) AS total_affiliates,
            (SELECT COUNT(*) FROM users u2
             JOIN affiliate_profiles ap2 ON ap2.user_id = u2.id
             WHERE u2.role = 'affiliate' AND ap2.status = 'approved') AS active_affiliates,
            (SELECT COUNT(*) FROM stores WHERE active = true) AS total_stores,
            (SELECT COUNT(*) FROM products WHERE active = true AND is_deleted = false) AS total_products,
            (SELECT COUNT(*) FROM referral_links) AS total_links,
            (SELECT COUNT(*) FROM referral_clicks) AS total_clicks,
            (SELECT COUNT(*) FROM conversions) AS total_conversions,
            (SELECT COALESCE(SUM(sale_amount), 0) FROM conversions) AS total_revenue,
            (SELECT COALESCE(SUM(commission_earned), 0) FROM conversions) AS total_commissions_earned,
            (SELECT COALESCE(SUM(commission_earned), 0) FROM conversions
             WHERE status = 'paid') AS total_commissions_paid
    """)


def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS platform_overview")
    op.execute("DROP VIEW IF EXISTS affiliate_performance")
    op.drop_index("ix_notifications_created_at", table_name="notifications")
    op.drop_index("ix_notifications_read", table_name="notifications")
    op.drop_index("ix_notifications_user_id", table_name="notifications")
    op.drop_table("notifications")
