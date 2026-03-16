"""005 referral links and clicks

Revision ID: 005_referrals
Revises: 004_campaigns
Create Date: 2026-03-16

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "005_referrals"
down_revision: Union[str, None] = "004_campaigns"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "referral_links",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("affiliate_id", sa.Integer(), nullable=False),
        sa.Column("campaign_id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(32), nullable=False),
        sa.Column("short_url", sa.String(500), nullable=True),
        sa.Column("is_custom", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["affiliate_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], ondelete="RESTRICT"),
    )
    op.create_index("ix_referral_links_code", "referral_links", ["code"], unique=True)
    op.create_index("ix_referral_links_affiliate_id", "referral_links", ["affiliate_id"])
    op.create_index("ix_referral_links_campaign_id", "referral_links", ["campaign_id"])

    op.create_table(
        "referral_clicks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("link_id", sa.Integer(), nullable=False),
        sa.Column("ip_address", sa.String(50), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("referrer_url", sa.Text(), nullable=True),
        sa.Column("country_code", sa.String(10), nullable=True),
        sa.Column("is_flagged", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("clicked_from_tiktok", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "clicked_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["link_id"], ["referral_links.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_referral_clicks_link_id", "referral_clicks", ["link_id"])
    op.create_index("ix_referral_clicks_clicked_at", "referral_clicks", ["clicked_at"])
    op.create_index("ix_referral_clicks_ip_address", "referral_clicks", ["ip_address"])


def downgrade() -> None:
    op.drop_index("ix_referral_clicks_ip_address", table_name="referral_clicks")
    op.drop_index("ix_referral_clicks_clicked_at", table_name="referral_clicks")
    op.drop_index("ix_referral_clicks_link_id", table_name="referral_clicks")
    op.drop_table("referral_clicks")
    op.drop_index("ix_referral_links_campaign_id", table_name="referral_links")
    op.drop_index("ix_referral_links_affiliate_id", table_name="referral_links")
    op.drop_index("ix_referral_links_code", table_name="referral_links")
    op.drop_table("referral_links")
