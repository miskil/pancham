from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..db import get_db
from ..models.proposal import Proposal
from ..models.village import Village
from ..auth import require_role

router = APIRouter(prefix="/village/proposal", tags=["village-proposal"])
village_only = require_role("VILLAGE")


class ProposalBody(BaseModel):
    focus_areas: list[str] | None = None
    focus_area: str | None = None
    per_capita_income: str | None = None
    description: str | None = None
    community_context: str | None = None
    key_activities: str | None = None
    submit: bool = False


class ProposalOut(BaseModel):
    id: str
    status: str
    focus_areas: list[str]
    focus_area: str | None
    per_capita_income: str | None
    description: str | None
    community_context: str | None
    key_activities: str | None
    reviewer_notes: str | None

    class Config:
        from_attributes = True


def _parse_focus_areas(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [item.strip() for item in raw.split(",") if item.strip()]


def _serialize_focus_areas(body: ProposalBody) -> str | None:
    if body.focus_areas is not None:
        cleaned = [item.strip() for item in body.focus_areas if item and item.strip()]
        return ",".join(dict.fromkeys(cleaned)) if cleaned else None
    if body.focus_area is not None:
        return body.focus_area.strip() or None
    return None


def _to_out(proposal: Proposal) -> ProposalOut:
    focus_areas = _parse_focus_areas(proposal.focus_area)
    return ProposalOut(
        id=proposal.id,
        status=proposal.status,
        focus_areas=focus_areas,
        focus_area=proposal.focus_area,
        per_capita_income=proposal.per_capita_income,
        description=proposal.description,
        community_context=proposal.community_context,
        key_activities=proposal.key_activities,
        reviewer_notes=proposal.reviewer_notes,
    )


@router.post("", response_model=ProposalOut)
async def create_proposal(body: ProposalBody, db: AsyncSession = Depends(get_db), user=Depends(village_only)):
    existing = await db.execute(select(Proposal).where(Proposal.village_id == user["village_id"]))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Proposal already exists — use PATCH to update")

    status = "SUBMITTED" if body.submit else "DRAFT"
    proposal = Proposal(
        village_id=user["village_id"],
        status=status,
        focus_area=_serialize_focus_areas(body),
        per_capita_income=body.per_capita_income,
        description=body.description,
        community_context=body.community_context,
        key_activities=body.key_activities,
    )
    db.add(proposal)

    if body.submit:
        result = await db.execute(select(Village).where(Village.id == user["village_id"]))
        village = result.scalar_one()
        village.internal_status = "PROPOSAL_SUBMITTED"

    await db.commit()
    await db.refresh(proposal)
    return _to_out(proposal)


@router.get("", response_model=ProposalOut)
async def get_proposal(db: AsyncSession = Depends(get_db), user=Depends(village_only)):
    result = await db.execute(select(Proposal).where(Proposal.village_id == user["village_id"]))
    proposal = result.scalar_one_or_none()
    if not proposal:
        raise HTTPException(status_code=404, detail="No proposal yet")
    return _to_out(proposal)


@router.patch("", response_model=ProposalOut)
async def update_proposal(body: ProposalBody, db: AsyncSession = Depends(get_db), user=Depends(village_only)):
    result = await db.execute(select(Proposal).where(Proposal.village_id == user["village_id"]))
    proposal = result.scalar_one_or_none()
    if not proposal:
        raise HTTPException(status_code=404, detail="No proposal yet")
    if proposal.status == "ACCEPTED":
        raise HTTPException(status_code=400, detail="Accepted proposal is read-only")

    serialized_focus_areas = _serialize_focus_areas(body)
    if serialized_focus_areas is not None:
        proposal.focus_area = serialized_focus_areas
    if body.per_capita_income is not None:
        proposal.per_capita_income = body.per_capita_income
    if body.description is not None:
        proposal.description = body.description
    if body.community_context is not None:
        proposal.community_context = body.community_context
    if body.key_activities is not None:
        proposal.key_activities = body.key_activities

    if body.submit:
        was_amendment = proposal.status == "AMENDMENT_REQUESTED"
        proposal.status = "AMENDED" if was_amendment else "SUBMITTED"
        result2 = await db.execute(select(Village).where(Village.id == user["village_id"]))
        village = result2.scalar_one()
        village.internal_status = "AMENDED" if was_amendment else "PROPOSAL_SUBMITTED"

    await db.commit()
    await db.refresh(proposal)
    return _to_out(proposal)
