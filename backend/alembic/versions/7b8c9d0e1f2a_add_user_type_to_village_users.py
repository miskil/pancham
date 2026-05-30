"""add user_type to village_users

Revision ID: 7b8c9d0e1f2a
Revises: 6a7b8c9d0e1f
Create Date: 2026-05-30

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "7b8c9d0e1f2a"
down_revision: Union[str, None] = "6a7b8c9d0e1f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("village_users", sa.Column("user_type", sa.String(), nullable=True))
    op.execute("UPDATE village_users SET user_type = 'VILLAGE' WHERE user_type IS NULL")
    op.alter_column("village_users", "user_type", nullable=False)


def downgrade() -> None:
    op.drop_column("village_users", "user_type")
