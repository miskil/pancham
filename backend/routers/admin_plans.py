from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from ..db import get_db
from ..models.plan import ProjectPlan, empty_plan_data
from ..models.village import Village
from ..auth import require_role

router = APIRouter(prefix="/admin/plans", tags=["admin-plans"])
admin_only = require_role("ADMIN")


class PlanOut(BaseModel):
    id: str
    village_id: str
    village_name: str
    version_type: str
    status: str
    plan_data: dict
    frozen_at: str | None

    class Config:
        from_attributes = True


@router.get("", response_model=list[PlanOut])
async def list_plans(db: AsyncSession = Depends(get_db), _=Depends(admin_only)):
    result = await db.execute(
        select(ProjectPlan)
        .options(selectinload(ProjectPlan.village))
        .where(ProjectPlan.version_type == "BASELINE")
        .order_by(ProjectPlan.created_at.desc())
    )
    return [_out(p) for p in result.scalars().all()]


@router.get("/{plan_id}", response_model=PlanOut)
async def get_plan(plan_id: str, db: AsyncSession = Depends(get_db), _=Depends(admin_only)):
    return _out(await _load(plan_id, db))


@router.get("/{plan_id}/wip", response_model=PlanOut)
async def get_wip(plan_id: str, db: AsyncSession = Depends(get_db), _=Depends(admin_only)):
    result = await db.execute(
        select(ProjectPlan)
        .options(selectinload(ProjectPlan.village))
        .where(ProjectPlan.created_from_plan_id == plan_id, ProjectPlan.version_type == "WIP")
    )
    wip = result.scalar_one_or_none()
    if not wip:
        raise HTTPException(status_code=404, detail="WIP not found")
    return _out(wip)


class PlanDataIn(BaseModel):
    plan_data: dict


@router.patch("/{plan_id}", response_model=PlanOut)
async def update_plan(plan_id: str, body: PlanDataIn, db: AsyncSession = Depends(get_db), _=Depends(admin_only)):
    p = await _load(plan_id, db)
    if p.status == "FROZEN":
        raise HTTPException(status_code=400, detail="Cannot edit a frozen plan")
    p.plan_data = body.plan_data
    await db.commit()
    await db.refresh(p)
    return _out(p)


@router.patch("/{plan_id}/accept")
async def accept_plan(plan_id: str, db: AsyncSession = Depends(get_db), _=Depends(admin_only)):
    p = await _load(plan_id, db)
    if p.status != "SUBMITTED":
        raise HTTPException(status_code=400, detail="Plan must be SUBMITTED to accept")

    now = datetime.now(timezone.utc)
    p.status = "FROZEN"
    p.frozen_at = now

    wip = ProjectPlan(
        village_id=p.village_id,
        version_type="WIP",
        status="DRAFT",
        plan_data=dict(p.plan_data),
        created_from_plan_id=p.id,
    )
    db.add(wip)

    result = await db.execute(select(Village).where(Village.id == p.village_id))
    village = result.scalar_one()
    village.internal_status = "BASELINE_FROZEN"

    await db.commit()
    return {"ok": True, "wip_plan_id": wip.id}


def _out(p: ProjectPlan) -> PlanOut:
    return PlanOut(
        id=p.id,
        village_id=p.village_id,
        village_name=p.village.name,
        version_type=p.version_type,
        status=p.status,
        plan_data=p.plan_data or empty_plan_data(),
        frozen_at=p.frozen_at.isoformat() if p.frozen_at else None,
    )


async def _load(plan_id: str, db: AsyncSession) -> ProjectPlan:
    result = await db.execute(
        select(ProjectPlan).options(selectinload(ProjectPlan.village)).where(ProjectPlan.id == plan_id)
    )
    p = result.scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=404, detail="Plan not found")
    return p
