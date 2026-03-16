"""002 affiliate profiles

Revision ID: 002_affiliate_profiles
Revises: 001_users
Create Date: 2026-03-16

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "002_affiliate_profiles"
down_revision: Union[str, None] = "001_users"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "affiliate_profiles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("pending", "approved", "rejected", "suspended", name="affiliatestatus"),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("full_name", sa.String(255), nullable=True),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("tiktok_url", sa.String(500), nullable=True),
        sa.Column("instagram_url", sa.String(500), nullable=True),
        sa.Column("twitter_url", sa.String(500), nullable=True),
        sa.Column("payout_method", sa.String(50), nullable=True, server_default="paystack"),
        sa.Column("bank_name", sa.String(255), nullable=True),
        sa.Column("bank_code", sa.String(50), nullable=True),
        sa.Column("account_number", sa.String(50), nullable=True),
        sa.Column("paystack_recipient_code", sa.String(255), nullable=True),
        sa.Column("last_payout_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("terms_version_accepted", sa.Integer(), nullable=True),
        sa.Column("terms_accepted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("approved_by", sa.Integer(), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["approved_by"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_affiliate_profiles_user_id", "affiliate_profiles", ["user_id"], unique=True)
    op.create_index("ix_affiliate_profiles_status", "affiliate_profiles", ["status"])


def downgrade() -> None:
    op.drop_index("ix_affiliate_profiles_status", table_name="affiliate_profiles")
    op.drop_index("ix_affiliate_profiles_user_id", table_name="affiliate_profiles")
    op.drop_table("affiliate_profiles")
    op.execute("DROP TYPE IF EXISTS affiliatestatus")
