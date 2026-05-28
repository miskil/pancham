from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import require_role
from ..db import get_db
from ..models.village import Village

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
