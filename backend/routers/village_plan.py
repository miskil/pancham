from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..db import get_db
from ..models.plan import ProjectPlan, empty_plan_data
from ..models.village import Village
from ..auth import require_role

router = APIRouter(prefix="/village/plan", tags=["village-plan"])
village_only = require_role("VILLAGE")


class PlanBody(BaseModel):
    plan_data: dict | None = None
    submit: bool = False


class PlanOut(BaseModel):
    id: str
    version_type: str
    status: str
    plan_data: dict
    frozen_at: str | None
    updated_at: str | None

    class Config:
        from_attributes = True


@router.post("", response_model=PlanOut)
async def create_plan(body: PlanBody, db: AsyncSession = Depends(get_db), user=Depends(village_only)):
    result = await db.execute(select(Village).where(Village.id == user["village_id"]))
    village = result.scalar_one_or_none()
    if not village or village.internal_status not in ("ACCEPTED", "PLAN_SUBMITTED"):
        raise HTTPException(status_code=403, detail="Proposal must be accepted before submitting a plan")

    existing = await db.execute(
        select(ProjectPlan).where(ProjectPlan.village_id == user["village_id"], ProjectPlan.version_type == "BASELINE")
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Plan already exists — use PATCH to update")

    plan = ProjectPlan(
        village_id=user["village_id"],
        version_type="BASELINE",
        status="SUBMITTED" if body.submit else "DRAFT",
        plan_data=body.plan_data or empty_plan_data(),
    )
    db.add(plan)

    if body.submit:
        village.internal_status = "PLAN_SUBMITTED"

    await db.commit()
    await db.refresh(plan)
    return _out(plan)


@router.patch("/baseline", response_model=PlanOut)
async def update_baseline(body: PlanBody, db: AsyncSession = Depends(get_db), user=Depends(village_only)):
    plan = await _get(db, user["village_id"], "BASELINE")
    if not plan:
        raise HTTPException(status_code=404, detail="No baseline plan yet")
    if plan.status == "FROZEN":
        raise HTTPException(status_code=400, detail="Baseline is frozen and cannot be edited")

    result = await db.execute(select(Village).where(Village.id == user["village_id"]))
    village = result.scalar_one_or_none()
    if not village:
        raise HTTPException(status_code=404, detail="Village not found")

    if body.plan_data is not None:
        plan.plan_data = body.plan_data

    if body.submit:
        plan.status = "SUBMITTED"
        village.internal_status = "PLAN_SUBMITTED"
    elif plan.status != "SUBMITTED":
        plan.status = "DRAFT"

    await db.commit()
    await db.refresh(plan)
    return _out(plan)


@router.get("/baseline", response_model=PlanOut)
async def get_baseline(db: AsyncSession = Depends(get_db), user=Depends(village_only)):
    plan = await _get(db, user["village_id"], "BASELINE")
    if not plan:
        raise HTTPException(status_code=404, detail="No plan yet")
    return _out(plan)


@router.get("/wip", response_model=PlanOut)
async def get_wip(db: AsyncSession = Depends(get_db), user=Depends(village_only)):
    plan = await _get(db, user["village_id"], "WIP")
    if not plan:
        raise HTTPException(status_code=404, detail="No WIP plan yet")
    return _out(plan)


@router.patch("/wip", response_model=PlanOut)
async def update_wip(body: PlanBody, db: AsyncSession = Depends(get_db), user=Depends(village_only)):
    plan = await _get(db, user["village_id"], "WIP")
    if not plan:
        raise HTTPException(status_code=404, detail="No WIP plan yet")
    if body.plan_data is not None:
        plan.plan_data = body.plan_data
    await db.commit()
    await db.refresh(plan)
    return _out(plan)


def _out(p: ProjectPlan) -> PlanOut:
    return PlanOut(
        id=p.id,
        version_type=p.version_type,
        status=p.status,
        plan_data=p.plan_data or empty_plan_data(),
        frozen_at=p.frozen_at.isoformat() if p.frozen_at else None,
        updated_at=p.updated_at.isoformat() if p.updated_at else None,
    )


async def _get(db: AsyncSession, village_id: str, version_type: str) -> ProjectPlan | None:
    result = await db.execute(
        select(ProjectPlan).where(
            ProjectPlan.village_id == village_id,
            ProjectPlan.version_type == version_type,
        )
    )
    return result.scalar_one_or_none()
