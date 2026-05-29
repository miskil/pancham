"""create funding rounds table

Revision ID: 2c3d4e5f6a7b
Revises: 1b2c3d4e5f6a
Create Date: 2026-05-29

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "2c3d4e5f6a7b"
down_revision: Union[str, None] = "1b2c3d4e5f6a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "funding_rounds",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("village_id", sa.String(), nullable=False),
        sa.Column("round_number", sa.Integer(), nullable=False),
        sa.Column("funding_amount", sa.Float(), nullable=True),
        sa.Column("funding_sent_date", sa.Date(), nullable=True),
        sa.Column("funding_received_date", sa.Date(), nullable=True),
        sa.Column("funding_status_note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["village_id"], ["villages.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("village_id", "round_number", name="uq_funding_rounds_village_round_number"),
    )


def downgrade() -> None:
    op.drop_table("funding_rounds")
