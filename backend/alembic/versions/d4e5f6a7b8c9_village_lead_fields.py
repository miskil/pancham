"""add village lead fields to villages

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-05-28

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d4e5f6a7b8c9"
down_revision: Union[str, None] = "c3d4e5f6a7b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("villages", sa.Column("village_lead_name", sa.String(), nullable=True))
    op.add_column("villages", sa.Column("village_lead_phone", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("villages", "village_lead_phone")
    op.drop_column("villages", "village_lead_name")
