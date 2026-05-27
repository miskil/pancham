import secrets
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..db import get_db
from ..models.village import Village
from ..models.evidence import SupportEvidence
from ..auth import hash_password, require_role
from ..utils.stage import derive_stage_and_substatus

router = APIRouter(prefix="/admin/villages", tags=["admin-onboard"])
admin_only = require_role("ADMIN")


class OnboardRequest(BaseModel):
    name: str
    district: str
    taluka: str
    population: int | None = None
    bhau_enabled: bool = False


class VillageOut(BaseModel):
    id: str
    name: str
    district: str
    taluka: str
    population: int | None
    login_username: str
    is_active: bool
    bhau_enabled: bool
    internal_status: str
    stage: str
    sub_status: str
    temp_password: str | None = None

    class Config:
        from_attributes = True


def village_to_out(v: Village, temp_password: str | None = None) -> VillageOut:
    stage, sub_status = derive_stage_and_substatus(v.internal_status)
    return VillageOut(
        id=v.id,
        name=v.name,
        district=v.district,
        taluka=v.taluka,
        population=v.population,
        login_username=v.login_username,
        is_active=v.is_active,
        bhau_enabled=v.bhau_enabled,
        internal_status=v.internal_status,
        stage=stage,
        sub_status=sub_status,
        temp_password=temp_password,
    )


@router.post("", response_model=VillageOut)
async def onboard_village(body: OnboardRequest, db: AsyncSession = Depends(get_db), _=Depends(admin_only)):
    username = body.name.lower().replace(" ", "_") + "_" + secrets.token_hex(3)
    temp_password = secrets.token_urlsafe(8)

    village = Village(
        name=body.name,
        district=body.district,
        taluka=body.taluka,
        population=body.population,
        bhau_enabled=body.bhau_enabled,
        login_username=username,
        login_password_hash=hash_password(temp_password),
    )
    db.add(village)
    await db.commit()
    await db.refresh(village)
    return village_to_out(village, temp_password=temp_password)


@router.get("", response_model=list[VillageOut])
async def list_villages(db: AsyncSession = Depends(get_db), _=Depends(admin_only)):
    result = await db.execute(select(Village).order_by(Village.created_at.desc()))
    villages = result.scalars().all()
    return [village_to_out(v) for v in villages]


@router.post("/{village_id}/preview-token")
async def preview_token(village_id: str, db: AsyncSession = Depends(get_db), _=Depends(admin_only)):
    from ..auth import create_token
    result = await db.execute(select(Village).where(Village.id == village_id))
    village = result.scalar_one_or_none()
    if not village:
        raise HTTPException(status_code=404, detail="Village not found")
    token = create_token(subject=village.login_username, role="VILLAGE", village_id=village.id)
    return {"access_token": token, "village_id": village.id, "village_name": village.name}


@router.get("/{village_id}/evidence")
async def list_village_evidence(village_id: str, db: AsyncSession = Depends(get_db), _=Depends(admin_only)):
    result = await db.execute(
        select(SupportEvidence)
        .where(SupportEvidence.village_id == village_id)
        .order_by(SupportEvidence.uploaded_at.desc())
    )
    docs = result.scalars().all()
    return [
        {
            "id": d.id,
            "doc_type": d.doc_type,
            "filename": d.filename,
            "file_url": d.file_url,
            "notes": d.notes,
            "uploaded_at": d.uploaded_at.isoformat(),
        }
        for d in docs
    ]


@router.patch("/{village_id}/deactivate")
async def deactivate_village(village_id: str, db: AsyncSession = Depends(get_db), _=Depends(admin_only)):
    result = await db.execute(select(Village).where(Village.id == village_id))
    village = result.scalar_one_or_none()
    if not village:
        raise HTTPException(status_code=404, detail="Village not found")
    village.is_active = False
    await db.commit()
    return {"ok": True}
