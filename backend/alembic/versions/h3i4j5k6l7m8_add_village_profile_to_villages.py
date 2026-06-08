"""add village_profile JSONB to villages

Revision ID: h3i4j5k6l7m8
Revises: g2h3i4j5k6l7
Create Date: 2026-06-07

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = "h3i4j5k6l7m8"
down_revision = "g2h3i4j5k6l7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("villages", sa.Column("village_profile", JSONB(), nullable=False, server_default="{}"))


def downgrade() -> None:
    op.drop_column("villages", "village_profile")
