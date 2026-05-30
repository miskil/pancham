from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import require_role
from ..db import get_db
from ..models.funding import FundingRound
from ..models.village import Village

router = APIRouter(tags=["funding"])
admin_only = require_role("ADMIN")
village_only = require_role("VILLAGE")


class FundingRoundCreateIn(BaseModel):
    funding_amount: float | None = None
    funding_sent_date: date | None = None
    funding_status_note: str | None = None


class FundingRoundUpdateIn(BaseModel):
    funding_amount: float | None = None
    funding_sent_date: date | None = None
    funding_received_date: date | None = None
    funding_status_note: str | None = None
    funding_received_message: str | None = None


class FundingRoundOut(BaseModel):
    id: str
    village_id: str
    round_number: int
    funding_amount: float | None = None
    funding_sent_date: date | None = None
    funding_received_date: date | None = None
    funding_status_note: str | None = None
    funding_received_message: str | None = None
    created_at: str | None = None
    updated_at: str | None = None

    class Config:
        from_attributes = True


async def _load_round_for_admin(db: AsyncSession, village_id: str, round_id: str) -> FundingRound:
    result = await db.execute(select(FundingRound).where(FundingRound.id == round_id, FundingRound.village_id == village_id))
    funding_round = result.scalar_one_or_none()
    if not funding_round:
        raise HTTPException(status_code=404, detail="Funding round not found")
    return funding_round


async def _load_round_for_village(db: AsyncSession, village_id: str, round_id: str) -> FundingRound:
    result = await db.execute(select(FundingRound).where(FundingRound.id == round_id, FundingRound.village_id == village_id))
    funding_round = result.scalar_one_or_none()
    if not funding_round:
        raise HTTPException(status_code=404, detail="Funding round not found")
    return funding_round


def _serialize_round(funding_round: FundingRound) -> FundingRoundOut:
    return FundingRoundOut(
        id=funding_round.id,
        village_id=funding_round.village_id,
        round_number=funding_round.round_number,
        funding_amount=funding_round.funding_amount,
        funding_sent_date=funding_round.funding_sent_date,
        funding_received_date=funding_round.funding_received_date,
        funding_status_note=funding_round.funding_status_note,
        funding_received_message=funding_round.funding_received_message,
        created_at=funding_round.created_at.isoformat() if funding_round.created_at else None,
        updated_at=funding_round.updated_at.isoformat() if funding_round.updated_at else None,
    )


def _has_received_information(funding_round: FundingRound) -> bool:
    if funding_round.funding_received_date is not None:
        return True
    if isinstance(funding_round.funding_received_message, str) and funding_round.funding_received_message.strip():
        return True
    return False


@router.get("/admin/villages/{village_id}/funding-rounds", response_model=list[FundingRoundOut])
async def list_admin_funding_rounds(village_id: str, db: AsyncSession = Depends(get_db), _=Depends(admin_only)):
    result = await db.execute(
        select(FundingRound)
        .where(FundingRound.village_id == village_id)
        .order_by(FundingRound.round_number.asc())
    )
    return [_serialize_round(item) for item in result.scalars().all()]


@router.post("/admin/villages/{village_id}/funding-rounds", response_model=FundingRoundOut)
async def create_admin_funding_round(
    village_id: str,
    body: FundingRoundCreateIn,
    db: AsyncSession = Depends(get_db),
    _=Depends(admin_only),
):
    village_result = await db.execute(select(Village).where(Village.id == village_id))
    village = village_result.scalar_one_or_none()
    if not village:
        raise HTTPException(status_code=404, detail="Village not found")

    max_round_result = await db.execute(select(func.max(FundingRound.round_number)).where(FundingRound.village_id == village_id))
    next_round_number = (max_round_result.scalar_one() or 0) + 1

    funding_round = FundingRound(
        village_id=village_id,
        round_number=next_round_number,
        funding_amount=body.funding_amount,
        funding_sent_date=body.funding_sent_date,
        funding_status_note=(body.funding_status_note or "").strip() or None,
    )
    db.add(funding_round)
    await db.commit()
    await db.refresh(funding_round)
    return _serialize_round(funding_round)


@router.patch("/admin/villages/{village_id}/funding-rounds/{round_id}", response_model=FundingRoundOut)
async def update_admin_funding_round(
    village_id: str,
    round_id: str,
    body: FundingRoundUpdateIn,
    db: AsyncSession = Depends(get_db),
    _=Depends(admin_only),
):
    funding_round = await _load_round_for_admin(db, village_id, round_id)
    payload = body.model_dump(exclude_unset=True)
    if "funding_amount" in payload:
        funding_round.funding_amount = payload["funding_amount"]
    if "funding_sent_date" in payload:
        funding_round.funding_sent_date = payload["funding_sent_date"]
    if "funding_status_note" in payload:
        note = payload["funding_status_note"]
        funding_round.funding_status_note = note.strip() if isinstance(note, str) and note.strip() else None
    await db.commit()
    await db.refresh(funding_round)
    return _serialize_round(funding_round)


@router.delete("/admin/villages/{village_id}/funding-rounds/{round_id}")
async def delete_admin_funding_round(
    village_id: str,
    round_id: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(admin_only),
):
    funding_round = await _load_round_for_admin(db, village_id, round_id)
    if _has_received_information(funding_round):
        raise HTTPException(status_code=409, detail="Funding round has received information and cannot be deleted")
    await db.delete(funding_round)
    await db.commit()
    return {"ok": True}


@router.get("/village/funding-rounds", response_model=list[FundingRoundOut])
async def list_village_funding_rounds(db: AsyncSession = Depends(get_db), user=Depends(village_only)):
    result = await db.execute(
        select(FundingRound)
        .where(FundingRound.village_id == user["village_id"])
        .order_by(FundingRound.round_number.asc())
    )
    return [_serialize_round(item) for item in result.scalars().all()]


@router.patch("/village/funding-rounds/{round_id}", response_model=FundingRoundOut)
async def update_village_funding_round(
    round_id: str,
    body: FundingRoundUpdateIn,
    db: AsyncSession = Depends(get_db),
    user=Depends(village_only),
):
    funding_round = await _load_round_for_village(db, user["village_id"], round_id)
    payload = body.model_dump(exclude_unset=True)
    if "funding_received_date" in payload:
        funding_round.funding_received_date = payload["funding_received_date"]
    if "funding_status_note" in payload:
        note = payload["funding_status_note"]
        funding_round.funding_status_note = note.strip() if isinstance(note, str) and note.strip() else None
    if "funding_received_message" in payload:
        message = payload["funding_received_message"]
        funding_round.funding_received_message = message.strip() if isinstance(message, str) and message.strip() else None
    await db.commit()
    await db.refresh(funding_round)
    return _serialize_round(funding_round)
