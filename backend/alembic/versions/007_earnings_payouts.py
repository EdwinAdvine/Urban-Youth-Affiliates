"""007 earnings and payout requests

Revision ID: 007_earnings_payouts
Revises: 006_conversions
Create Date: 2026-03-16

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "007_earnings_payouts"
down_revision: Union[str, None] = "006_conversions"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "affiliate_balances",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("affiliate_id", sa.Integer(), nullable=False),
        sa.Column("pending", sa.Numeric(12, 2), nullable=False, server_default="0.00"),
        sa.Column("approved", sa.Numeric(12, 2), nullable=False, server_default="0.00"),
        sa.Column("paid_out", sa.Numeric(12, 2), nullable=False, server_default="0.00"),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["affiliate_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index(
        "ix_affiliate_balances_affiliate_id",
        "affiliate_balances",
        ["affiliate_id"],
        unique=True,
    )

    op.create_table(
        "payout_requests",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("affiliate_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column(
            "status",
            sa.Enum("pending", "processing", "paid", "failed", name="payoutstatus"),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("paystack_transfer_code", sa.String(255), nullable=True),
        sa.Column("paystack_recipient_code", sa.String(255), nullable=True),
        sa.Column("failure_reason", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "requested_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("processed_by", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["affiliate_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["processed_by"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_payout_requests_affiliate_id", "payout_requests", ["affiliate_id"])
    op.create_index("ix_payout_requests_status", "payout_requests", ["status"])
    op.create_index("ix_payout_requests_requested_at", "payout_requests", ["requested_at"])


def downgrade() -> None:
    op.drop_index("ix_payout_requests_requested_at", table_name="payout_requests")
    op.drop_index("ix_payout_requests_status", table_name="payout_requests")
    op.drop_index("ix_payout_requests_affiliate_id", table_name="payout_requests")
    op.drop_table("payout_requests")
    op.drop_index("ix_affiliate_balances_affiliate_id", table_name="affiliate_balances")
    op.drop_table("affiliate_balances")
    op.execute("DROP TYPE IF EXISTS payoutstatus")
