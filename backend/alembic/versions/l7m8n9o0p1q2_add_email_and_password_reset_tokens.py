"""add email to users and password_reset_tokens table

Revision ID: l7m8n9o0p1q2
Revises: k6l7m8n9o0p1
Create Date: 2026-08-16

"""
from alembic import op
import sqlalchemy as sa

revision = "l7m8n9o0p1q2"
down_revision = "k6l7m8n9o0p1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("admin_users", sa.Column("email", sa.String(), nullable=True))
    op.create_unique_constraint("uq_admin_users_email", "admin_users", ["email"])

    op.add_column("village_users", sa.Column("email", sa.String(), nullable=True))
    op.create_unique_constraint("uq_village_users_email", "village_users", ["email"])

    op.create_table(
        "password_reset_tokens",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("user_type", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("token_hash", sa.String(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_unique_constraint("uq_password_reset_tokens_token_hash", "password_reset_tokens", ["token_hash"])
    op.create_index("ix_password_reset_tokens_token_hash", "password_reset_tokens", ["token_hash"])


def downgrade() -> None:
    op.drop_index("ix_password_reset_tokens_token_hash", table_name="password_reset_tokens")
    op.drop_table("password_reset_tokens")
    op.drop_constraint("uq_village_users_email", "village_users", type_="unique")
    op.drop_column("village_users", "email")
    op.drop_constraint("uq_admin_users_email", "admin_users", type_="unique")
    op.drop_column("admin_users", "email")
