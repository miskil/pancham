import asyncio
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from alembic import command
from alembic.config import Config

from ..auth import require_role
from ..config import settings
from ..db import engine

router = APIRouter(prefix="/admin/maintenance", tags=["admin-maintenance"])
admin_only = require_role("ADMIN")


class ResetTablesRequest(BaseModel):
    confirm_phrase: str


class ResetTablesResponse(BaseModel):
    ok: bool
    message: str


def _run_alembic_upgrade_head() -> None:
    backend_dir = Path(__file__).resolve().parents[1]
    alembic_ini = backend_dir / "alembic.ini"
    cfg = Config(str(alembic_ini))
    command.upgrade(cfg, "head")


@router.post("/reset-tables", response_model=ResetTablesResponse)
async def reset_tables(body: ResetTablesRequest, _=Depends(admin_only)):
    if not settings.enable_reset_tables_endpoint:
        raise HTTPException(status_code=403, detail="Reset endpoint is disabled")

    if body.confirm_phrase != "RESET ALL TABLES":
        raise HTTPException(status_code=400, detail="Invalid confirmation phrase")

    # Wipe the schema, then re-run all migrations to recreate tables.
    async with engine.begin() as conn:
        await conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
        await conn.execute(text("CREATE SCHEMA public"))
        await conn.execute(text("GRANT ALL ON SCHEMA public TO public"))

    await engine.dispose()
    await asyncio.to_thread(_run_alembic_upgrade_head)

    return ResetTablesResponse(
        ok=True,
        message="All tables were reset and recreated from migrations.",
    )
