from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from ..db import get_db
from ..models.status_update import StatusUpdate, MediaFile
from ..auth import require_role

router = APIRouter(prefix="/admin/status-updates", tags=["admin-status"])
admin_only = require_role("ADMIN")


class MediaOut(BaseModel):
    id: str
    media_type: str
    file_url: str

    class Config:
        from_attributes = True


class StatusUpdateOut(BaseModel):
    id: str
    village_id: str
    village_name: str
    description: str
    submitted_at: str
    is_published: bool
    media_files: list[MediaOut] = []

    class Config:
        from_attributes = True


@router.get("", response_model=list[StatusUpdateOut])
async def list_updates(village_id: str | None = None, db: AsyncSession = Depends(get_db), _=Depends(admin_only)):
    q = (
        select(StatusUpdate)
        .options(selectinload(StatusUpdate.village), selectinload(StatusUpdate.media_files))
        .order_by(StatusUpdate.submitted_at.desc())
    )
    if village_id:
        q = q.where(StatusUpdate.village_id == village_id)
    result = await db.execute(q)
    updates = result.scalars().all()
    return [
        StatusUpdateOut(
            id=u.id, village_id=u.village_id, village_name=u.village.name,
            description=u.description, submitted_at=u.submitted_at.isoformat(),
            is_published=u.is_published,
            media_files=[MediaOut(id=m.id, media_type=m.media_type, file_url=m.file_url) for m in u.media_files],
        )
        for u in updates
    ]


@router.patch("/{update_id}/publish")
async def publish_update(update_id: str, db: AsyncSession = Depends(get_db), _=Depends(admin_only)):
    u = await _load(update_id, db)
    u.is_published = True
    await db.commit()
    return {"ok": True}


@router.patch("/{update_id}/unpublish")
async def unpublish_update(update_id: str, db: AsyncSession = Depends(get_db), _=Depends(admin_only)):
    u = await _load(update_id, db)
    u.is_published = False
    await db.commit()
    return {"ok": True}


async def _load(update_id: str, db: AsyncSession) -> StatusUpdate:
    result = await db.execute(
        select(StatusUpdate).options(selectinload(StatusUpdate.village)).where(StatusUpdate.id == update_id)
    )
    u = result.scalar_one_or_none()
    if not u:
        raise HTTPException(status_code=404, detail="Update not found")
    return u
