"""restrict village user types to ADMIN NGO VDC

Revision ID: 8c9d0e1f2a3b
Revises: 7b8c9d0e1f2a
Create Date: 2026-05-29

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "8c9d0e1f2a3b"
down_revision: Union[str, None] = "7b8c9d0e1f2a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("UPDATE village_users SET user_type = 'VDC' WHERE user_type IS NULL OR user_type = 'VILLAGE'")
    op.create_check_constraint(
        "ck_village_users_user_type_allowed",
        "village_users",
        "user_type IN ('ADMIN', 'NGO', 'VDC')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_village_users_user_type_allowed", "village_users", type_="check")
