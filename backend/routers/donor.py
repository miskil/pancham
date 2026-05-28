from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from ..db import get_db
from ..models.village import Village
from ..models.status_update import StatusUpdate, MediaFile
from ..auth import require_role
from ..utils.stage import derive_stage_and_substatus

router = APIRouter(prefix="/donor", tags=["donor"])
donor_access = require_role("ADMIN", "DONOR")


class VillageOut(BaseModel):
    id: str
    name: str
    district: str
    ngo_name: str | None = None
    ngo_contact_name: str | None = None
    ngo_contact_phone: str | None = None
    stage: str
    sub_status: str


class MediaOut(BaseModel):
    id: str
    media_type: str
    file_url: str
    caption: str | None

    class Config:
        from_attributes = True


class UpdateOut(BaseModel):
    id: str
    description: str
    submitted_at: str
    media_files: list[MediaOut]

    class Config:
        from_attributes = True


@router.get("/villages", response_model=list[VillageOut])
async def list_villages(db: AsyncSession = Depends(get_db), _=Depends(donor_access)):
    result = await db.execute(
        select(Village)
        .join(StatusUpdate, StatusUpdate.village_id == Village.id)
        .where(StatusUpdate.is_published == True, Village.is_active == True)  # noqa: E712
        .distinct()
    )
    villages = result.scalars().all()
    out = []
    for v in villages:
        stage, sub_status = derive_stage_and_substatus(v.internal_status)
        out.append(
            VillageOut(
                id=v.id,
                name=v.name,
                district=v.district,
                ngo_name=v.ngo_name,
                ngo_contact_name=v.ngo_contact_name,
                ngo_contact_phone=v.ngo_contact_phone,
                stage=stage,
                sub_status=sub_status,
            )
        )
    return out


@router.get("/villages/{village_id}/updates", response_model=list[UpdateOut])
async def get_updates(village_id: str, db: AsyncSession = Depends(get_db), _=Depends(donor_access)):
    result = await db.execute(
        select(StatusUpdate)
        .options(selectinload(StatusUpdate.media_files))
        .where(StatusUpdate.village_id == village_id, StatusUpdate.is_published == True)  # noqa: E712
        .order_by(StatusUpdate.submitted_at.desc())
    )
    updates = result.scalars().all()
    return [
        UpdateOut(
            id=u.id, description=u.description, submitted_at=u.submitted_at.isoformat(),
            media_files=[MediaOut.model_validate(m) for m in u.media_files],
        )
        for u in updates
    ]
