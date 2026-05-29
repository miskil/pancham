"""add proposal per capita income

Revision ID: a7a5a4f2912a
Revises: 9dcebcc034cd
Create Date: 2026-05-29 12:01:43.839236

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'a7a5a4f2912a'
down_revision: Union[str, None] = '9dcebcc034cd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('proposals', sa.Column('per_capita_income', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('proposals', 'per_capita_income')
