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
    focus_area: str | None = None
    description: str | None = None
    community_context: str | None = None
    key_activities: str | None = None
    submit: bool = False


class ProposalOut(BaseModel):
    id: str
    status: str
    focus_area: str | None
    description: str | None
    community_context: str | None
    key_activities: str | None
    reviewer_notes: str | None

    class Config:
        from_attributes = True


@router.post("", response_model=ProposalOut)
async def create_proposal(body: ProposalBody, db: AsyncSession = Depends(get_db), user=Depends(village_only)):
    existing = await db.execute(select(Proposal).where(Proposal.village_id == user["village_id"]))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Proposal already exists — use PATCH to update")

    status = "SUBMITTED" if body.submit else "DRAFT"
    proposal = Proposal(
        village_id=user["village_id"],
        status=status,
        focus_area=body.focus_area,
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
    return proposal


@router.get("", response_model=ProposalOut)
async def get_proposal(db: AsyncSession = Depends(get_db), user=Depends(village_only)):
    result = await db.execute(select(Proposal).where(Proposal.village_id == user["village_id"]))
    proposal = result.scalar_one_or_none()
    if not proposal:
        raise HTTPException(status_code=404, detail="No proposal yet")
    return proposal


@router.patch("", response_model=ProposalOut)
async def update_proposal(body: ProposalBody, db: AsyncSession = Depends(get_db), user=Depends(village_only)):
    result = await db.execute(select(Proposal).where(Proposal.village_id == user["village_id"]))
    proposal = result.scalar_one_or_none()
    if not proposal:
        raise HTTPException(status_code=404, detail="No proposal yet")
    if proposal.status == "ACCEPTED":
        raise HTTPException(status_code=400, detail="Accepted proposal is read-only")

    if body.focus_area is not None:
        proposal.focus_area = body.focus_area
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
    return proposal
