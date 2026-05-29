"""village_users_and_admin_users

Revision ID: 9dcebcc034cd
Revises: 60354633785d
Create Date: 2026-05-29 08:30:41.396121

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '9dcebcc034cd'
down_revision: Union[str, None] = '60354633785d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- village_users -------------------------------------------------
    op.create_table(
        "village_users",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("village_id", sa.String(), sa.ForeignKey("villages.id"), nullable=False),
        sa.Column("display_name", sa.String(), nullable=True),
        sa.Column("login_username", sa.String(), nullable=False),
        sa.Column("login_password_hash", sa.String(), nullable=False),
        sa.Column("must_change_password", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("login_username"),
    )

    # Migrate existing village credentials into village_users
    conn = op.get_bind()
    villages = conn.execute(
        sa.text("SELECT id, login_username, login_password_hash, must_change_password FROM villages WHERE login_username IS NOT NULL")
    ).fetchall()
    for v in villages:
        import uuid as _uuid
        conn.execute(
            sa.text(
                "INSERT INTO village_users (id, village_id, login_username, login_password_hash, must_change_password, is_active) "
                "VALUES (:id, :village_id, :username, :pw_hash, :mcp, true)"
            ),
            {"id": str(_uuid.uuid4()), "village_id": v[0], "username": v[1], "pw_hash": v[2], "mcp": v[3]},
        )

    # --- admin_users ---------------------------------------------------
    op.create_table(
        "admin_users",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("display_name", sa.String(), nullable=True),
        sa.Column("login_username", sa.String(), nullable=False),
        sa.Column("login_password_hash", sa.String(), nullable=False),
        sa.Column("must_change_password", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("login_username"),
    )

    # Seed initial admin from env / hardcoded fallback
    # The password hash will be bcrypt of settings.admin_password.
    # We import bcrypt directly here so the migration is self-contained.
    import os
    import bcrypt as _bcrypt
    admin_username = os.environ.get("ADMIN_USERNAME", "admin")
    admin_password = os.environ.get("ADMIN_PASSWORD", "changeme")
    pw_hash = _bcrypt.hashpw(admin_password.encode(), _bcrypt.gensalt()).decode()
    import uuid as _uuid2
    conn.execute(
        sa.text(
            "INSERT INTO admin_users (id, login_username, login_password_hash, must_change_password, is_active) "
            "VALUES (:id, :username, :pw_hash, false, true) "
            "ON CONFLICT (login_username) DO NOTHING"
        ),
        {"id": str(_uuid2.uuid4()), "username": admin_username, "pw_hash": pw_hash},
    )


def downgrade() -> None:
    op.drop_table("admin_users")
    op.drop_table("village_users")
