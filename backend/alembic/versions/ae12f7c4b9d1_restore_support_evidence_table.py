"""restore support_evidence table

Revision ID: ae12f7c4b9d1
Revises: 9d0e1f2a3b4c
Create Date: 2026-05-31 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'ae12f7c4b9d1'
down_revision: Union[str, None] = '9d0e1f2a3b4c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if inspector.has_table('support_evidence'):
        return

    op.create_table(
        'support_evidence',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('village_id', sa.String(), nullable=False),
        sa.Column('doc_type', sa.String(), nullable=False),
        sa.Column('filename', sa.String(), nullable=False),
        sa.Column('file_url', sa.String(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['village_id'], ['villages.id'], name=op.f('support_evidence_village_id_fkey')),
        sa.PrimaryKeyConstraint('id', name=op.f('support_evidence_pkey')),
    )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if inspector.has_table('support_evidence'):
        op.drop_table('support_evidence')