"""004 campaigns

Revision ID: 004_campaigns
Revises: 003_stores_products
Create Date: 2026-03-16

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "004_campaigns"
down_revision: Union[str, None] = "003_stores_products"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "campaigns",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=True),
        sa.Column("store_id", sa.Integer(), nullable=True),
        sa.Column(
            "commission_type",
            sa.Enum("percent", "fixed", name="commissiontype"),
            nullable=False,
            server_default="percent",
        ),
        sa.Column("rate", sa.Numeric(10, 4), nullable=False),
        sa.Column("min_sale_amount", sa.Numeric(12, 2), nullable=True),
        sa.Column("cookie_days", sa.Integer(), nullable=False, server_default="30"),
        sa.Column("active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["store_id"], ["stores.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_campaigns_active", "campaigns", ["active"])
    op.create_index("ix_campaigns_product_id", "campaigns", ["product_id"])
    op.create_index("ix_campaigns_store_id", "campaigns", ["store_id"])


def downgrade() -> None:
    op.drop_index("ix_campaigns_store_id", table_name="campaigns")
    op.drop_index("ix_campaigns_product_id", table_name="campaigns")
    op.drop_index("ix_campaigns_active", table_name="campaigns")
    op.drop_table("campaigns")
    op.execute("DROP TYPE IF EXISTS commissiontype")
