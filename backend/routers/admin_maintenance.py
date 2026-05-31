import asyncio
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import text
from alembic import command
from alembic.config import Config

from ..auth import require_role
from ..config import settings
from ..db import engine

router = APIRouter(tags=["admin-maintenance"])
admin_only = require_role("ADMIN")


class ResetTablesResponse(BaseModel):
    ok: bool
    message: str


def _run_alembic_upgrade_head() -> None:
    backend_dir = Path(__file__).resolve().parents[1]
    alembic_ini = backend_dir / "alembic.ini"
    cfg = Config(str(alembic_ini))
    command.upgrade(cfg, "head")


def _validate_admin_password(admin_password: str) -> None:
    if admin_password != settings.admin_password:
        raise HTTPException(status_code=401, detail="Invalid admin password")


async def _reset_schema_and_migrate() -> None:
    async with engine.begin() as conn:
        await conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
        await conn.execute(text("CREATE SCHEMA public"))
        await conn.execute(text("GRANT ALL ON SCHEMA public TO public"))

    await engine.dispose()
    await asyncio.to_thread(_run_alembic_upgrade_head)


@router.post("/admin/maintenance/reset-tables", response_model=ResetTablesResponse)
@router.post("/reset-tables", response_model=ResetTablesResponse)
async def reset_tables(_=Depends(admin_only)):
    if not settings.enable_reset_tables_endpoint:
        raise HTTPException(status_code=403, detail="Reset endpoint is disabled")

    await _reset_schema_and_migrate()

    return ResetTablesResponse(
        ok=True,
        message="All tables were reset and recreated from migrations.",
    )


@router.get("/admin/maintenance/reset-tables", response_model=ResetTablesResponse)
@router.get("/reset-tables", response_model=ResetTablesResponse)
async def reset_tables_browser(
    admin_password: str = Query(...),
):
    if not settings.enable_reset_tables_endpoint:
        raise HTTPException(status_code=403, detail="Reset endpoint is disabled")

    _validate_admin_password(admin_password)
    await _reset_schema_and_migrate()

    return ResetTablesResponse(
        ok=True,
        message="All tables were reset and recreated from migrations.",
    )
