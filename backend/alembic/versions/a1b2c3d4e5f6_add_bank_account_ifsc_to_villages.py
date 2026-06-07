"""add bank_account_number and ifsc_code to villages

Revision ID: a1b2c3d4e5f6
Revises: f6a7b8c9d0e1
Create Date: 2026-06-07

"""
from alembic import op
import sqlalchemy as sa

revision = "a1b2c3d4e5f6"
down_revision = "f6a7b8c9d0e1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("villages", sa.Column("bank_account_number", sa.String(), nullable=True))
    op.add_column("villages", sa.Column("ifsc_code", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("villages", "ifsc_code")
    op.drop_column("villages", "bank_account_number")
