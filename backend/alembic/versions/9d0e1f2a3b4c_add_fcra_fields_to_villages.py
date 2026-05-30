"""add fcra fields to villages

Revision ID: 9d0e1f2a3b4c
Revises: 8c9d0e1f2a3b
Create Date: 2026-05-29

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9d0e1f2a3b4c"
down_revision: Union[str, None] = "8c9d0e1f2a3b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("villages", sa.Column("fcra_number", sa.String(), nullable=True))
    op.add_column("villages", sa.Column("fcra_expiry_date", sa.Date(), nullable=True))
    op.execute("UPDATE villages SET fcra_number = ngo_name WHERE fcra_number IS NULL AND ngo_name IS NOT NULL")


def downgrade() -> None:
    op.drop_column("villages", "fcra_expiry_date")
    op.drop_column("villages", "fcra_number")
