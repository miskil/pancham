"""add mous table

Revision ID: m8n9o0p1q2r3
Revises: l7m8n9o0p1q2
Create Date: 2026-08-17

"""
from alembic import op
import sqlalchemy as sa

revision = "m8n9o0p1q2r3"
down_revision = "l7m8n9o0p1q2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "mous",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("village_id", sa.String(), sa.ForeignKey("villages.id"), nullable=False),
        sa.Column("status", sa.String(), nullable=False, server_default="DRAFT"),
        sa.Column("terms", sa.Text(), nullable=True),
        sa.Column("admin_notes", sa.Text(), nullable=True),
        sa.Column("village_notes", sa.Text(), nullable=True),
        sa.Column("sent_date", sa.Date(), nullable=True),
        sa.Column("signed_date", sa.Date(), nullable=True),
        sa.Column("expiry_date", sa.Date(), nullable=True),
        sa.Column("draft_document_filename", sa.String(), nullable=True),
        sa.Column("draft_document_content", sa.LargeBinary(), nullable=True),
        sa.Column("signed_document_filename", sa.String(), nullable=True),
        sa.Column("signed_document_content", sa.LargeBinary(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_mous_village_id", "mous", ["village_id"])


def downgrade() -> None:
    op.drop_index("ix_mous_village_id", table_name="mous")
    op.drop_table("mous")
