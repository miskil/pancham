"""add receipt fields to funding_rounds

Revision ID: i4j5k6l7m8n9
Revises: h3i4j5k6l7m8
Create Date: 2026-06-07

"""
from alembic import op
import sqlalchemy as sa

revision = "i4j5k6l7m8n9"
down_revision = "h3i4j5k6l7m8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("funding_rounds", sa.Column("receipt_filename", sa.String(), nullable=True))
    op.add_column("funding_rounds", sa.Column("receipt_url", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("funding_rounds", "receipt_url")
    op.drop_column("funding_rounds", "receipt_filename")
