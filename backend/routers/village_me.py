from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..db import get_db
from ..models.village import Village
from ..models.village_user import VillageUser
from ..auth import require_role
from ..utils.stage import derive_stage_and_substatus

router = APIRouter(prefix="/village", tags=["village"])
village_only = require_role("VILLAGE")


class VillageMe(BaseModel):
    id: str
    name: str
    district: str
    taluka: str
    ngo_name: str | None = None
    fcra_number: str | None = None
    fcra_expiry_date: date | None = None
    ngo_contact_name: str | None = None
    ngo_contact_phone: str | None = None
    village_lead_name: str | None = None
    village_lead_phone: str | None = None
    current_user_username: str | None = None
    current_user_display_name: str | None = None
    current_user_type: str | None = None
    internal_status: str
    stage: str
    sub_status: str
    bhau_enabled: bool


@router.get("/me", response_model=VillageMe)
async def get_me(db: AsyncSession = Depends(get_db), user=Depends(village_only)):
    result = await db.execute(select(Village).where(Village.id == user["village_id"]))
    village = result.scalar_one_or_none()
    if not village:
        raise HTTPException(status_code=404, detail="Village not found")
    user_result = await db.execute(
        select(VillageUser).where(
            VillageUser.village_id == user["village_id"],
            VillageUser.login_username == user.get("sub"),
        )
    )
    village_user = user_result.scalar_one_or_none()
    stage, sub_status = derive_stage_and_substatus(village.internal_status)
    return VillageMe(
        id=village.id, name=village.name, district=village.district, taluka=village.taluka,
        ngo_name=village.ngo_name,
        fcra_number=village.fcra_number or village.ngo_name,
        fcra_expiry_date=village.fcra_expiry_date,
        ngo_contact_name=village.ngo_contact_name,
        ngo_contact_phone=village.ngo_contact_phone,
        village_lead_name=village.village_lead_name, village_lead_phone=village.village_lead_phone,
        current_user_username=user.get("sub"), current_user_display_name=village_user.display_name if village_user else None,
        current_user_type=village_user.user_type if village_user else None,
        internal_status=village.internal_status, stage=stage, sub_status=sub_status,
        bhau_enabled=village.bhau_enabled,
    )
