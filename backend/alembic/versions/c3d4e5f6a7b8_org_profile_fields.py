"""add org profile fields to villages

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-05-28

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "c3d4e5f6a7b8"
down_revision: Union[str, None] = "b2c3d4e5f6a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("villages", sa.Column("ngo_name", sa.String(), nullable=True))
    op.add_column("villages", sa.Column("ngo_contact_name", sa.String(), nullable=True))
    op.add_column("villages", sa.Column("ngo_contact_phone", sa.String(), nullable=True))
    op.add_column("villages", sa.Column("ngo_whatsapp_phone", sa.String(), nullable=True))
    op.add_column(
        "villages",
        sa.Column(
            "vdc_members",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
    )


def downgrade() -> None:
    op.drop_column("villages", "vdc_members")
    op.drop_column("villages", "ngo_whatsapp_phone")
    op.drop_column("villages", "ngo_contact_phone")
    op.drop_column("villages", "ngo_contact_name")
    op.drop_column("villages", "ngo_name")
