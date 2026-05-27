"""initial

Revision ID: 9c3249a25947
Revises:
Create Date: 2026-05-18

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '9c3249a25947'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('villages',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('district', sa.String(), nullable=False),
        sa.Column('taluka', sa.String(), nullable=False),
        sa.Column('population', sa.Integer(), nullable=True),
        sa.Column('login_username', sa.String(), nullable=False),
        sa.Column('login_password_hash', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('bhau_enabled', sa.Boolean(), nullable=False),
        sa.Column('internal_status', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('login_username'),
    )
    op.create_table('proposals',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('village_id', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('focus_area', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('community_context', sa.Text(), nullable=True),
        sa.Column('key_activities', sa.Text(), nullable=True),
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('reviewer_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['village_id'], ['villages.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table('proposal_amendments',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('proposal_id', sa.String(), nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('reviewer_notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['proposal_id'], ['proposals.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table('project_plans',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('village_id', sa.String(), nullable=False),
        sa.Column('version_type', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('frozen_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_from_plan_id', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['village_id'], ['villages.id']),
        sa.ForeignKeyConstraint(['created_from_plan_id'], ['project_plans.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table('milestones',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('plan_id', sa.String(), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_completed', sa.Boolean(), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['plan_id'], ['project_plans.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table('status_updates',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('village_id', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('submitted_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_published', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['village_id'], ['villages.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table('media_files',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('status_update_id', sa.String(), nullable=False),
        sa.Column('media_type', sa.String(), nullable=False),
        sa.Column('file_url', sa.String(), nullable=False),
        sa.Column('caption', sa.String(), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['status_update_id'], ['status_updates.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table('update_threads',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('status_update_id', sa.String(), nullable=False),
        sa.Column('author_role', sa.String(), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('sent_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['status_update_id'], ['status_updates.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table('village_channels',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('village_id', sa.String(), nullable=False),
        sa.Column('author_role', sa.String(), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('sent_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['village_id'], ['villages.id']),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('village_channels')
    op.drop_table('update_threads')
    op.drop_table('media_files')
    op.drop_table('status_updates')
    op.drop_table('milestones')
    op.drop_table('project_plans')
    op.drop_table('proposal_amendments')
    op.drop_table('proposals')
    op.drop_table('villages')
