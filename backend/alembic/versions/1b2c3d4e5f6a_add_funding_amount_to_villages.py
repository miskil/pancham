"""add funding amount to villages

Revision ID: 1b2c3d4e5f6a
Revises: 0a1b2c3d4e5f
Create Date: 2026-05-29

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "1b2c3d4e5f6a"
down_revision: Union[str, None] = "0a1b2c3d4e5f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("villages", sa.Column("funding_amount", sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column("villages", "funding_amount")
