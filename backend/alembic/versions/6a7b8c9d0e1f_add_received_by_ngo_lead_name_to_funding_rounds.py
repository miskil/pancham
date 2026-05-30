"""add received by ngo lead name to funding rounds

Revision ID: 6a7b8c9d0e1f
Revises: 5f6a7b8c9d0e
Create Date: 2026-05-30

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "6a7b8c9d0e1f"
down_revision: Union[str, None] = "5f6a7b8c9d0e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("funding_rounds", sa.Column("funding_received_by_ngo_lead_name", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("funding_rounds", "funding_received_by_ngo_lead_name")
