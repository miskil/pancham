"""add receipt_content to funding_rounds

Revision ID: j5k6l7m8n9o0
Revises: i4j5k6l7m8n9
Create Date: 2026-06-08

"""
from alembic import op
import sqlalchemy as sa

revision = "j5k6l7m8n9o0"
down_revision = "i4j5k6l7m8n9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("funding_rounds", sa.Column("receipt_content", sa.LargeBinary(), nullable=True))


def downgrade() -> None:
    op.drop_column("funding_rounds", "receipt_content")
