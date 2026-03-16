"""008 platform settings

Revision ID: 008_platform_settings
Revises: 007_earnings_payouts
Create Date: 2026-03-16

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "008_platform_settings"
down_revision: Union[str, None] = "007_earnings_payouts"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "platform_settings",
        sa.Column("key", sa.String(100), nullable=False),
        sa.Column("value", sa.Text(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("updated_by", sa.Integer(), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("key"),
        sa.ForeignKeyConstraint(["updated_by"], ["users.id"], ondelete="SET NULL"),
    )

    # Insert default settings
    op.execute("""
        INSERT INTO platform_settings (key, value, description) VALUES
        ('default_commission_rate', '0.10', 'Default commission rate (10%)'),
        ('min_payout_threshold', '500', 'Minimum KES amount for payout requests'),
        ('cookie_days', '30', 'Days referral cookie stays valid'),
        ('require_affiliate_approval', 'true', 'Require admin approval for new affiliates'),
        ('terms_version', '1', 'Current terms and conditions version')
    """)


def downgrade() -> None:
    op.drop_table("platform_settings")
