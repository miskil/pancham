"""add milestone_ref to status_updates

Revision ID: k6l7m8n9o0p1
Revises: j5k6l7m8n9o0
Create Date: 2026-06-08

"""
from alembic import op
import sqlalchemy as sa

revision = "k6l7m8n9o0p1"
down_revision = "j5k6l7m8n9o0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("status_updates", sa.Column("milestone_ref", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("status_updates", "milestone_ref")
