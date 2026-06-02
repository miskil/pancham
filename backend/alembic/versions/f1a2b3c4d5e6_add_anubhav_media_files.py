"""add anubhav media files table

Revision ID: f1a2b3c4d5e6
Revises: cf1a2b3c4d5e
Create Date: 2026-06-02 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f1a2b3c4d5e6"
down_revision: Union[str, None] = "cf1a2b3c4d5e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "anubhav_media_files",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("anubhav_post_id", sa.String(), nullable=False),
        sa.Column("media_type", sa.String(), nullable=False),
        sa.Column("file_url", sa.String(), nullable=False),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["anubhav_post_id"], ["anubhav_posts.id"], ondelete="CASCADE", name=op.f("anubhav_media_files_anubhav_post_id_fkey")),
        sa.PrimaryKeyConstraint("id", name=op.f("anubhav_media_files_pkey")),
    )
    op.create_index(op.f("ix_anubhav_media_files_anubhav_post_id"), "anubhav_media_files", ["anubhav_post_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_anubhav_media_files_anubhav_post_id"), table_name="anubhav_media_files")
    op.drop_table("anubhav_media_files")
