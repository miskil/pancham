from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from ..db import get_db
from ..models.proposal import Proposal
from ..models.village import Village
from ..auth import require_role

router = APIRouter(prefix="/admin/proposals", tags=["admin-proposals"])
admin_only = require_role("ADMIN")

VALID_TRANSITIONS = {
    "SUBMITTED": ["UNDER_REVIEW"],
    "UNDER_REVIEW": ["AMENDMENT_REQUESTED", "ACCEPTED", "DECLINED"],
    "AMENDED": ["UNDER_REVIEW", "AMENDMENT_REQUESTED", "ACCEPTED", "DECLINED"],
}


class ReviewRequest(BaseModel):
    notes: str | None = None


class ProposalOut(BaseModel):
    id: str
    village_id: str
    village_name: str
    status: str
    focus_area: str | None
    description: str | None
    community_context: str | None
    key_activities: str | None
    reviewer_notes: str | None

    class Config:
        from_attributes = True


@router.get("", response_model=list[ProposalOut])
async def list_proposals(db: AsyncSession = Depends(get_db), _=Depends(admin_only)):
    result = await db.execute(
        select(Proposal).options(selectinload(Proposal.village)).order_by(Proposal.submitted_at.desc())
    )
    proposals = result.scalars().all()
    return [
        ProposalOut(
            id=p.id, village_id=p.village_id, village_name=p.village.name,
            status=p.status, focus_area=p.focus_area, description=p.description,
            community_context=p.community_context, key_activities=p.key_activities,
            reviewer_notes=p.reviewer_notes,
        )
        for p in proposals
    ]


@router.get("/{proposal_id}", response_model=ProposalOut)
async def get_proposal(proposal_id: str, db: AsyncSession = Depends(get_db), _=Depends(admin_only)):
    result = await db.execute(
        select(Proposal).options(selectinload(Proposal.village)).where(Proposal.id == proposal_id)
    )
    p = result.scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=404, detail="Proposal not found")
    return ProposalOut(
        id=p.id, village_id=p.village_id, village_name=p.village.name,
        status=p.status, focus_area=p.focus_area, description=p.description,
        community_context=p.community_context, key_activities=p.key_activities,
        reviewer_notes=p.reviewer_notes,
    )


async def _transition_proposal(proposal_id: str, new_status: str, notes: str | None, db: AsyncSession):
    result = await db.execute(
        select(Proposal).options(selectinload(Proposal.village)).where(Proposal.id == proposal_id)
    )
    p = result.scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=404, detail="Proposal not found")
    allowed = VALID_TRANSITIONS.get(p.status, [])
    if new_status not in allowed:
        raise HTTPException(status_code=400, detail=f"Cannot move from {p.status} to {new_status}")
    p.status = new_status
    if notes is not None:
        p.reviewer_notes = notes
    if new_status == "ACCEPTED":
        p.village.internal_status = "ACCEPTED"
    elif new_status == "UNDER_REVIEW":
        p.village.internal_status = "UNDER_REVIEW"
    elif new_status == "AMENDMENT_REQUESTED":
        p.village.internal_status = "AMENDMENT_REQUESTED"
    await db.commit()
    return {"ok": True, "status": new_status}


@router.patch("/{proposal_id}/review")
async def review_proposal(proposal_id: str, body: ReviewRequest, db: AsyncSession = Depends(get_db), _=Depends(admin_only)):
    return await _transition_proposal(proposal_id, "UNDER_REVIEW", body.notes, db)


@router.patch("/{proposal_id}/accept")
async def accept_proposal(proposal_id: str, body: ReviewRequest, db: AsyncSession = Depends(get_db), _=Depends(admin_only)):
    return await _transition_proposal(proposal_id, "ACCEPTED", body.notes, db)


@router.patch("/{proposal_id}/request-amendment")
async def request_amendment(proposal_id: str, body: ReviewRequest, db: AsyncSession = Depends(get_db), _=Depends(admin_only)):
    return await _transition_proposal(proposal_id, "AMENDMENT_REQUESTED", body.notes, db)


@router.patch("/{proposal_id}/decline")
async def decline_proposal(proposal_id: str, body: ReviewRequest, db: AsyncSession = Depends(get_db), _=Depends(admin_only)):
    return await _transition_proposal(proposal_id, "DECLINED", body.notes, db)
