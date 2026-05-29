import secrets
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..db import get_db
from ..models.village import Village
from ..models.village_user import VillageUser
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
    ngo_name: str | None = None
    ngo_contact_name: str | None = None
    ngo_contact_phone: str | None = None
    village_lead_name: str | None = None
    village_lead_phone: str | None = None
    bhau_enabled: bool = False


class VillageUserOut(BaseModel):
    id: str
    display_name: str | None
    login_username: str
    is_active: bool
    must_change_password: bool
    temp_password: str | None = None

    class Config:
        from_attributes = True


class VillageOut(BaseModel):
    id: str
    name: str
    district: str
    taluka: str
    population: int | None
    ngo_name: str | None = None
    ngo_contact_name: str | None = None
    ngo_contact_phone: str | None = None
    village_lead_name: str | None = None
    village_lead_phone: str | None = None
    is_active: bool
    bhau_enabled: bool
    internal_status: str
    stage: str
    sub_status: str
    # first user's credentials returned only on creation
    login_username: str | None = None
    temp_password: str | None = None

    class Config:
        from_attributes = True


def village_to_out(v: Village, temp_password: str | None = None, login_username: str | None = None) -> VillageOut:
    stage, sub_status = derive_stage_and_substatus(v.internal_status)
    return VillageOut(
        id=v.id,
        name=v.name,
        district=v.district,
        taluka=v.taluka,
        population=v.population,
        ngo_name=v.ngo_name,
        ngo_contact_name=v.ngo_contact_name,
        ngo_contact_phone=v.ngo_contact_phone,
        village_lead_name=v.village_lead_name,
        village_lead_phone=v.village_lead_phone,
        is_active=v.is_active,
        bhau_enabled=v.bhau_enabled,
        internal_status=v.internal_status,
        stage=stage,
        sub_status=sub_status,
        login_username=login_username,
        temp_password=temp_password,
    )


async def _unique_village_username(db: AsyncSession, base: str) -> str:
    username = base
    counter = 1
    while True:
        existing_user = await db.execute(select(VillageUser).where(VillageUser.login_username == username))
        existing_village = await db.execute(select(Village).where(Village.login_username == username))
        if not existing_user.scalar_one_or_none() and not existing_village.scalar_one_or_none():
            return username
        username = f"{base}_{counter}"
        counter += 1


@router.post("", response_model=VillageOut)
async def onboard_village(body: OnboardRequest, db: AsyncSession = Depends(get_db), _=Depends(admin_only)):
    username = await _unique_village_username(db, body.name.lower().replace(" ", "_"))
    temp_password = secrets.token_urlsafe(8)

    village = Village(
        name=body.name,
        district=body.district,
        taluka=body.taluka,
        population=body.population,
        ngo_name=(body.ngo_name or "").strip() or None,
        ngo_contact_name=(body.ngo_contact_name or "").strip() or None,
        ngo_contact_phone=(body.ngo_contact_phone or "").strip() or None,
        village_lead_name=(body.village_lead_name or "").strip() or None,
        village_lead_phone=(body.village_lead_phone or "").strip() or None,
        bhau_enabled=body.bhau_enabled,
        # Keep legacy credential columns populated until a migration removes them.
        login_username=username,
        login_password_hash=hash_password(temp_password),
        must_change_password=True,
    )
    db.add(village)
    await db.flush()  # get village.id

    vu = VillageUser(
        village_id=village.id,
        login_username=username,
        login_password_hash=hash_password(temp_password),
        must_change_password=True,
    )
    db.add(vu)
    await db.commit()
    await db.refresh(village)
    return village_to_out(village, temp_password=temp_password, login_username=username)


@router.get("", response_model=list[VillageOut])
async def list_villages(db: AsyncSession = Depends(get_db), _=Depends(admin_only)):
    result = await db.execute(select(Village).order_by(Village.created_at.desc()))
    villages = result.scalars().all()
    return [village_to_out(v) for v in villages]


@router.get("/{village_id}/users", response_model=list[VillageUserOut])
async def list_village_users(village_id: str, db: AsyncSession = Depends(get_db), _=Depends(admin_only)):
    result = await db.execute(
        select(VillageUser).where(VillageUser.village_id == village_id).order_by(VillageUser.created_at)
    )
    return result.scalars().all()


class AddVillageUserRequest(BaseModel):
    display_name: str | None = None
    login_username: str | None = None  # auto-generated if omitted


@router.post("/{village_id}/users", response_model=VillageUserOut)
async def add_village_user(village_id: str, body: AddVillageUserRequest, db: AsyncSession = Depends(get_db), _=Depends(admin_only)):
    result = await db.execute(select(Village).where(Village.id == village_id))
    village = result.scalar_one_or_none()
    if not village:
        raise HTTPException(status_code=404, detail="Village not found")

    base = (body.login_username or village.name.lower().replace(" ", "_"))
    username = await _unique_village_username(db, base)
    temp_password = secrets.token_urlsafe(8)

    vu = VillageUser(
        village_id=village_id,
        display_name=body.display_name,
        login_username=username,
        login_password_hash=hash_password(temp_password),
        must_change_password=True,
    )
    db.add(vu)
    await db.commit()
    await db.refresh(vu)
    return VillageUserOut(
        id=vu.id,
        display_name=vu.display_name,
        login_username=vu.login_username,
        is_active=vu.is_active,
        must_change_password=vu.must_change_password,
        temp_password=temp_password,
    )


@router.patch("/{village_id}/users/{user_id}/deactivate")
async def deactivate_village_user(village_id: str, user_id: str, db: AsyncSession = Depends(get_db), _=Depends(admin_only)):
    result = await db.execute(
        select(VillageUser).where(VillageUser.id == user_id, VillageUser.village_id == village_id)
    )
    vu = result.scalar_one_or_none()
    if not vu:
        raise HTTPException(status_code=404, detail="User not found")
    vu.is_active = False
    await db.commit()
    return {"ok": True}


@router.patch("/{village_id}/users/{user_id}/reset-password")
async def reset_village_user_password(village_id: str, user_id: str, db: AsyncSession = Depends(get_db), _=Depends(admin_only)):
    result = await db.execute(
        select(VillageUser).where(VillageUser.id == user_id, VillageUser.village_id == village_id)
    )
    vu = result.scalar_one_or_none()
    if not vu:
        raise HTTPException(status_code=404, detail="User not found")
    temp_password = secrets.token_urlsafe(8)
    vu.login_password_hash = hash_password(temp_password)
    vu.must_change_password = True
    vu.is_active = True
    await db.commit()
    return {"ok": True, "temp_password": temp_password, "login_username": vu.login_username}


@router.post("/{village_id}/preview-token")
async def preview_token(village_id: str, db: AsyncSession = Depends(get_db), _=Depends(admin_only)):
    from ..auth import create_token
    # Use the first active user for this village
    result = await db.execute(
        select(VillageUser).where(VillageUser.village_id == village_id, VillageUser.is_active == True)  # noqa: E712
    )
    vu = result.scalars().first()
    if not vu:
        raise HTTPException(status_code=404, detail="No active users for this village")
    token = create_token(subject=vu.login_username, role="VILLAGE", village_id=village_id)
    return {"access_token": token, "village_id": village_id}


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
