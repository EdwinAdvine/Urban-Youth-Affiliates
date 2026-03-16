"""003 stores and products

Revision ID: 003_stores_products
Revises: 002_affiliate_profiles
Create Date: 2026-03-16

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "003_stores_products"
down_revision: Union[str, None] = "002_affiliate_profiles"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "stores",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("website_url", sa.String(500), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("logo_url", sa.String(500), nullable=True),
        sa.Column("admin_id", sa.Integer(), nullable=True),
        sa.Column("api_key", sa.String(255), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["admin_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_stores_slug", "stores", ["slug"], unique=True)
    op.create_index("ix_stores_active", "stores", ["active"])

    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("store_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("sku", sa.String(100), nullable=True),
        sa.Column("price", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(10), nullable=False, server_default="KES"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("image_url", sa.String(500), nullable=True),
        sa.Column("product_url", sa.String(500), nullable=True),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["store_id"], ["stores.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_products_store_id", "products", ["store_id"])
    op.create_index("ix_products_active", "products", ["active"])
    op.create_index("ix_products_category", "products", ["category"])


def downgrade() -> None:
    op.drop_index("ix_products_category", table_name="products")
    op.drop_index("ix_products_active", table_name="products")
    op.drop_index("ix_products_store_id", table_name="products")
    op.drop_table("products")
    op.drop_index("ix_stores_active", table_name="stores")
    op.drop_index("ix_stores_slug", table_name="stores")
    op.drop_table("stores")
