"""006 conversions

Revision ID: 006_conversions
Revises: 005_referrals
Create Date: 2026-03-16

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "006_conversions"
down_revision: Union[str, None] = "005_referrals"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "conversions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("referral_link_id", sa.Integer(), nullable=False),
        sa.Column("store_id", sa.Integer(), nullable=False),
        sa.Column("external_order_id", sa.String(255), nullable=False),
        sa.Column("sale_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("commission_earned", sa.Numeric(12, 2), nullable=False),
        sa.Column(
            "status",
            sa.Enum("pending", "approved", "rejected", "paid", name="conversionstatus"),
            nullable=False,
            server_default="pending",
        ),
        sa.Column(
            "conversion_source",
            sa.Enum("api", "webhook", "manual", name="conversionsource"),
            nullable=False,
            server_default="api",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("approved_by", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["referral_link_id"], ["referral_links.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["store_id"], ["stores.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["approved_by"], ["users.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("store_id", "external_order_id", name="uq_conversion_order"),
    )
    op.create_index("ix_conversions_referral_link_id", "conversions", ["referral_link_id"])
    op.create_index("ix_conversions_status", "conversions", ["status"])
    op.create_index("ix_conversions_store_id", "conversions", ["store_id"])
    op.create_index("ix_conversions_created_at", "conversions", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_conversions_created_at", table_name="conversions")
    op.drop_index("ix_conversions_store_id", table_name="conversions")
    op.drop_index("ix_conversions_status", table_name="conversions")
    op.drop_index("ix_conversions_referral_link_id", table_name="conversions")
    op.drop_table("conversions")
    op.execute("DROP TYPE IF EXISTS conversionstatus")
    op.execute("DROP TYPE IF EXISTS conversionsource")
