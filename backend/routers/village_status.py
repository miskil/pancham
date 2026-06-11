from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from ..db import get_db
from ..models.status_update import StatusUpdate, MediaFile
from ..auth import require_role
from ..utils.storage import save_upload

router = APIRouter(prefix="/village/status", tags=["village-status"])
village_only = require_role("VILLAGE")


class StatusBody(BaseModel):
    milestone_ref: str | None = None
    description: str = ""


class MediaOut(BaseModel):
    id: str
    media_type: str
    file_url: str
    caption: str | None

    class Config:
        from_attributes = True


class StatusUpdateOut(BaseModel):
    id: str
    milestone_ref: str | None
    description: str
    submitted_at: str
    is_published: bool
    media_files: list[MediaOut]

    class Config:
        from_attributes = True


@router.post("", response_model=StatusUpdateOut)
async def create_update(body: StatusBody, db: AsyncSession = Depends(get_db), user=Depends(village_only)):
    update = StatusUpdate(
        village_id=user["village_id"],
        milestone_ref=body.milestone_ref or None,
        description=body.description or "",
    )
    db.add(update)
    await db.commit()
    await db.refresh(update)
    return StatusUpdateOut(
        id=update.id, milestone_ref=update.milestone_ref, description=update.description,
        submitted_at=update.submitted_at.isoformat(),
        is_published=update.is_published, media_files=[],
    )


@router.get("", response_model=list[StatusUpdateOut])
async def list_updates(db: AsyncSession = Depends(get_db), user=Depends(village_only)):
    result = await db.execute(
        select(StatusUpdate)
        .options(selectinload(StatusUpdate.media_files))
        .where(StatusUpdate.village_id == user["village_id"])
        .order_by(StatusUpdate.submitted_at.desc())
    )
    updates = result.scalars().all()
    return [
        StatusUpdateOut(
            id=u.id, milestone_ref=u.milestone_ref, description=u.description,
            submitted_at=u.submitted_at.isoformat(),
            is_published=u.is_published,
            media_files=[MediaOut.model_validate(m) for m in u.media_files],
        )
        for u in updates
    ]


@router.post("/{update_id}/media", response_model=MediaOut)
async def upload_media(
    update_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user=Depends(village_only),
):
    result = await db.execute(select(StatusUpdate).where(StatusUpdate.id == update_id))
    update = result.scalar_one_or_none()
    if not update or update.village_id != user["village_id"]:
        raise HTTPException(status_code=404, detail="Update not found")

    media_type = "VIDEO" if file.content_type and file.content_type.startswith("video") else "PHOTO"
    file_url = save_upload(file.file, file.filename, "media")
    media = MediaFile(status_update_id=update_id, media_type=media_type, file_url=file_url)
    db.add(media)
    await db.commit()
    await db.refresh(media)
    return media
