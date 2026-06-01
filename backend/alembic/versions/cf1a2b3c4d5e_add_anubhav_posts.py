"""add anubhav_posts table

Revision ID: cf1a2b3c4d5e
Revises: ae12f7c4b9d1
Create Date: 2026-05-31 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'cf1a2b3c4d5e'
down_revision: Union[str, None] = 'ae12f7c4b9d1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'anubhav_posts',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('author_role', sa.String(), nullable=False),
        sa.Column('author_village_id', sa.String(), nullable=True),
        sa.Column('author_admin_id', sa.String(), nullable=True),
        sa.Column('author_display_name', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['author_village_id'], ['villages.id'], name=op.f('anubhav_posts_author_village_id_fkey')),
        sa.ForeignKeyConstraint(['author_admin_id'], ['admin_users.id'], name=op.f('anubhav_posts_author_admin_id_fkey')),
        sa.PrimaryKeyConstraint('id', name=op.f('anubhav_posts_pkey')),
    )


def downgrade() -> None:
    op.drop_table('anubhav_posts')
