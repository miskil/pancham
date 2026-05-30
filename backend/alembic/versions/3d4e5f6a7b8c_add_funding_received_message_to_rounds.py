"""split funding notes and add funding received message to funding rounds

Revision ID: 3d4e5f6a7b8c
Revises: 2c3d4e5f6a7b
Create Date: 2026-05-29

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "3d4e5f6a7b8c"
down_revision: Union[str, None] = "2c3d4e5f6a7b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("funding_rounds", sa.Column("admin_funding_note", sa.Text(), nullable=True))
    op.add_column("funding_rounds", sa.Column("village_funding_note", sa.Text(), nullable=True))
    op.add_column("funding_rounds", sa.Column("funding_received_message", sa.Text(), nullable=True))
    op.execute("UPDATE funding_rounds SET admin_funding_note = funding_status_note, village_funding_note = funding_status_note WHERE funding_status_note IS NOT NULL")


def downgrade() -> None:
    op.drop_column("funding_rounds", "admin_funding_note")
    op.drop_column("funding_rounds", "village_funding_note")
    op.drop_column("funding_rounds", "funding_received_message")
