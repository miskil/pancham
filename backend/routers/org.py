from fastapi import APIRouter, Depends, HTTPException
from datetime import date
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import require_role
from ..db import get_db
from ..models.village import Village
from ..models.village_user import VillageUser

router = APIRouter(tags=["org"])
admin_only = require_role("ADMIN")
village_only = require_role("VILLAGE")


class VdcMember(BaseModel):
    name: str
    role: str | None = None
    phone: str | None = None


class OrgProfileIn(BaseModel):
    ngo_name: str | None = None
    ngo_contact_name: str | None = None
    ngo_contact_phone: str | None = None
    village_lead_name: str | None = None
    village_lead_phone: str | None = None
    ngo_whatsapp_phone: str | None = None
    vdc_members: list[VdcMember] | None = None


class OrgProfileOut(BaseModel):
    village_id: str
    ngo_name: str | None = None
    ngo_contact_name: str | None = None
    ngo_contact_phone: str | None = None
    village_lead_name: str | None = None
    village_lead_phone: str | None = None
    ngo_whatsapp_phone: str | None = None
    vdc_members: list[VdcMember]


class FundingProfileIn(BaseModel):
    funding_sent_date: date | None = None
    funding_received_date: date | None = None
    funding_amount: float | None = None
    funding_status_note: str | None = None


class FundingProfileOut(BaseModel):
    village_id: str
    funding_sent_date: date | None = None
    funding_received_date: date | None = None
    funding_amount: float | None = None
    funding_status_note: str | None = None


def _serialize_org(village: Village) -> OrgProfileOut:
    members = village.vdc_members or []
    return OrgProfileOut(
        village_id=village.id,
        ngo_name=village.ngo_name,
        ngo_contact_name=village.ngo_contact_name,
        ngo_contact_phone=village.ngo_contact_phone,
        village_lead_name=village.village_lead_name,
        village_lead_phone=village.village_lead_phone,
        ngo_whatsapp_phone=village.ngo_whatsapp_phone,
        vdc_members=members,
    )


def _validate_members_limit(members: list[VdcMember] | None) -> None:
    if members is not None and len(members) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 VDC members are allowed")


def _norm_name(value: str | None) -> str:
    if not value:
        return ""
    return " ".join(value.strip().lower().split())


async def _ensure_ngo_lead_user(db: AsyncSession, village_id: str, username: str | None) -> None:
    if not username:
        raise HTTPException(status_code=403, detail="Only NGO lead can update funding")
    village_result = await db.execute(select(Village).where(Village.id == village_id))
    village = village_result.scalar_one_or_none()
    if not village:
        raise HTTPException(status_code=404, detail="Village not found")
    user_result = await db.execute(
        select(VillageUser).where(
            VillageUser.village_id == village_id,
            VillageUser.login_username == username,
            VillageUser.is_active == True,  # noqa: E712
        )
    )
    village_user = user_result.scalar_one_or_none()
    if not village_user:
        raise HTTPException(status_code=403, detail="Only NGO lead can update funding")
    if (village_user.user_type or "").upper() != "NGO":
        raise HTTPException(status_code=403, detail="Only NGO lead can update funding")


def _serialize_funding(village: Village) -> FundingProfileOut:
    return FundingProfileOut(
        village_id=village.id,
        funding_sent_date=village.funding_sent_date,
        funding_received_date=village.funding_received_date,
        funding_amount=village.funding_amount,
        funding_status_note=village.funding_status_note,
    )


@router.get("/village/org", response_model=OrgProfileOut)
async def get_village_org(
    db: AsyncSession = Depends(get_db),
    user=Depends(village_only),
):
    result = await db.execute(select(Village).where(Village.id == user["village_id"]))
    village = result.scalar_one_or_none()
    if not village:
        raise HTTPException(status_code=404, detail="Village not found")
    return _serialize_org(village)


@router.patch("/village/org", response_model=OrgProfileOut)
async def update_village_org(
    body: OrgProfileIn,
    db: AsyncSession = Depends(get_db),
    user=Depends(village_only),
):
    _validate_members_limit(body.vdc_members)

    result = await db.execute(select(Village).where(Village.id == user["village_id"]))
    village = result.scalar_one_or_none()
    if not village:
        raise HTTPException(status_code=404, detail="Village not found")

    if body.ngo_name is not None:
        village.ngo_name = body.ngo_name.strip() or None
    if body.ngo_contact_name is not None:
        village.ngo_contact_name = body.ngo_contact_name.strip() or None
    if body.ngo_contact_phone is not None:
        village.ngo_contact_phone = body.ngo_contact_phone.strip() or None
    if body.village_lead_name is not None:
        village.village_lead_name = body.village_lead_name.strip() or None
    if body.village_lead_phone is not None:
        village.village_lead_phone = body.village_lead_phone.strip() or None
    if body.ngo_whatsapp_phone is not None:
        village.ngo_whatsapp_phone = body.ngo_whatsapp_phone.strip() or None
    if body.vdc_members is not None:
        village.vdc_members = [
            {
                "name": m.name.strip(),
                "role": (m.role or "").strip() or None,
                "phone": (m.phone or "").strip() or None,
            }
            for m in body.vdc_members
            if m.name.strip()
        ]

    await db.commit()
    await db.refresh(village)
    return _serialize_org(village)


@router.get("/admin/villages/{village_id}/org", response_model=OrgProfileOut)
async def get_admin_village_org(
    village_id: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(admin_only),
):
    result = await db.execute(select(Village).where(Village.id == village_id))
    village = result.scalar_one_or_none()
    if not village:
        raise HTTPException(status_code=404, detail="Village not found")
    return _serialize_org(village)


@router.patch("/admin/villages/{village_id}/org", response_model=OrgProfileOut)
async def update_admin_village_org(
    village_id: str,
    body: OrgProfileIn,
    db: AsyncSession = Depends(get_db),
    _=Depends(admin_only),
):
    _validate_members_limit(body.vdc_members)

    result = await db.execute(select(Village).where(Village.id == village_id))
    village = result.scalar_one_or_none()
    if not village:
        raise HTTPException(status_code=404, detail="Village not found")

    if body.ngo_name is not None:
        village.ngo_name = body.ngo_name.strip() or None
    if body.ngo_contact_name is not None:
        village.ngo_contact_name = body.ngo_contact_name.strip() or None
    if body.ngo_contact_phone is not None:
        village.ngo_contact_phone = body.ngo_contact_phone.strip() or None
    if body.village_lead_name is not None:
        village.village_lead_name = body.village_lead_name.strip() or None
    if body.village_lead_phone is not None:
        village.village_lead_phone = body.village_lead_phone.strip() or None
    if body.ngo_whatsapp_phone is not None:
        village.ngo_whatsapp_phone = body.ngo_whatsapp_phone.strip() or None
    if body.vdc_members is not None:
        village.vdc_members = [
            {
                "name": m.name.strip(),
                "role": (m.role or "").strip() or None,
                "phone": (m.phone or "").strip() or None,
            }
            for m in body.vdc_members
            if m.name.strip()
        ]

    await db.commit()
    await db.refresh(village)
    return _serialize_org(village)


@router.get("/village/funding", response_model=FundingProfileOut)
async def get_village_funding(
    db: AsyncSession = Depends(get_db),
    user=Depends(village_only),
):
    result = await db.execute(select(Village).where(Village.id == user["village_id"]))
    village = result.scalar_one_or_none()
    if not village:
        raise HTTPException(status_code=404, detail="Village not found")
    return _serialize_funding(village)


@router.patch("/village/funding", response_model=FundingProfileOut)
async def update_village_funding(
    body: FundingProfileIn,
    db: AsyncSession = Depends(get_db),
    user=Depends(village_only),
):
    await _ensure_ngo_lead_user(db, user["village_id"], user.get("sub"))
    result = await db.execute(select(Village).where(Village.id == user["village_id"]))
    village = result.scalar_one_or_none()
    if not village:
        raise HTTPException(status_code=404, detail="Village not found")

    payload = body.model_dump(exclude_unset=True)
    if "funding_received_date" in payload:
        village.funding_received_date = payload["funding_received_date"]
    if "funding_status_note" in payload:
        note = payload["funding_status_note"]
        village.funding_status_note = note.strip() if isinstance(note, str) and note.strip() else None

    await db.commit()
    await db.refresh(village)
    return _serialize_funding(village)


@router.get("/admin/villages/{village_id}/funding", response_model=FundingProfileOut)
async def get_admin_village_funding(
    village_id: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(admin_only),
):
    result = await db.execute(select(Village).where(Village.id == village_id))
    village = result.scalar_one_or_none()
    if not village:
        raise HTTPException(status_code=404, detail="Village not found")
    return _serialize_funding(village)


@router.patch("/admin/villages/{village_id}/funding", response_model=FundingProfileOut)
async def update_admin_village_funding(
    village_id: str,
    body: FundingProfileIn,
    db: AsyncSession = Depends(get_db),
    _=Depends(admin_only),
):
    result = await db.execute(select(Village).where(Village.id == village_id))
    village = result.scalar_one_or_none()
    if not village:
        raise HTTPException(status_code=404, detail="Village not found")

    payload = body.model_dump(exclude_unset=True)
    if "funding_sent_date" in payload:
        village.funding_sent_date = payload["funding_sent_date"]
    if "funding_amount" in payload:
        village.funding_amount = payload["funding_amount"]
    if "funding_status_note" in payload:
        note = payload["funding_status_note"]
        village.funding_status_note = note.strip() if isinstance(note, str) and note.strip() else None

    await db.commit()
    await db.refresh(village)
    return _serialize_funding(village)
