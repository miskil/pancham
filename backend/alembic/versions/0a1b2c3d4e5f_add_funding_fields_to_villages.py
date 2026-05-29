"""add funding fields to villages

Revision ID: 0a1b2c3d4e5f
Revises: f6a7b8c9d0e1
Create Date: 2026-05-29

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0a1b2c3d4e5f"
down_revision: Union[str, None] = "f6a7b8c9d0e1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("villages", sa.Column("funding_sent_date", sa.Date(), nullable=True))
    op.add_column("villages", sa.Column("funding_received_date", sa.Date(), nullable=True))
    op.add_column("villages", sa.Column("funding_status_note", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("villages", "funding_status_note")
    op.drop_column("villages", "funding_received_date")
    op.drop_column("villages", "funding_sent_date")
