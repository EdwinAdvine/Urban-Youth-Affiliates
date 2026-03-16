"""009 creative assets

Revision ID: 009_creative_assets
Revises: 008_platform_settings
Create Date: 2026-03-16

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "009_creative_assets"
down_revision: Union[str, None] = "008_platform_settings"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "creative_assets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("campaign_id", sa.Integer(), nullable=True),
        sa.Column(
            "asset_type",
            sa.Enum("banner", "video", "image", "text", name="assettype"),
            nullable=False,
        ),
        sa.Column("title", sa.String(255), nullable=True),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("size", sa.String(50), nullable=True),
        sa.Column("embed_code", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_creative_assets_campaign_id", "creative_assets", ["campaign_id"])


def downgrade() -> None:
    op.drop_index("ix_creative_assets_campaign_id", table_name="creative_assets")
    op.drop_table("creative_assets")
    op.execute("DROP TYPE IF EXISTS assettype")
