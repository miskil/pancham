from datetime import datetime

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import require_role
from ..db import get_db
from ..models.mou import Mou
from ..models.village_user import VillageUser
from .admin_mou import MouOut, _document_response, _serialize

router = APIRouter(tags=["village-mou"])
village_only = require_role("VILLAGE")


class MouVillageNotesIn(BaseModel):
    village_notes: str | None = None


async def _ensure_ngo_lead_user(db: AsyncSession, village_id: str, username: str | None) -> None:
    if not username:
        raise HTTPException(status_code=403, detail="Only NGO lead can sign an MoU")
    result = await db.execute(
        select(VillageUser).where(
            VillageUser.village_id == village_id,
            VillageUser.login_username == username,
            VillageUser.is_active == True,  # noqa: E712
        )
    )
    village_user = result.scalar_one_or_none()
    if not village_user or (village_user.user_type or "").upper() != "NGO":
        raise HTTPException(status_code=403, detail="Only NGO lead can sign an MoU")


async def _load_village_mou(db: AsyncSession, village_id: str, mou_id: str) -> Mou:
    result = await db.execute(select(Mou).where(Mou.id == mou_id, Mou.village_id == village_id))
    mou = result.scalar_one_or_none()
    if not mou:
        raise HTTPException(status_code=404, detail="MoU not found")
    return mou


@router.get("/village/mou", response_model=list[MouOut])
async def list_village_mou(db: AsyncSession = Depends(get_db), user=Depends(village_only)):
    result = await db.execute(select(Mou).where(Mou.village_id == user["village_id"]).order_by(Mou.created_at))
    return [_serialize(item) for item in result.scalars().all()]


@router.patch("/village/mou/{mou_id}", response_model=MouOut)
async def update_village_mou_notes(mou_id: str, body: MouVillageNotesIn, db: AsyncSession = Depends(get_db), user=Depends(village_only)):
    mou = await _load_village_mou(db, user["village_id"], mou_id)
    notes = body.village_notes
    mou.village_notes = notes.strip() if isinstance(notes, str) and notes.strip() else None
    await db.commit()
    await db.refresh(mou)
    return _serialize(mou)


@router.post("/village/mou/{mou_id}/signed-document", response_model=MouOut)
async def upload_village_signed_document(
    mou_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user=Depends(village_only),
):
    await _ensure_ngo_lead_user(db, user["village_id"], user.get("sub"))
    mou = await _load_village_mou(db, user["village_id"], mou_id)
    if mou.status in {"EXPIRED", "TERMINATED"}:
        raise HTTPException(status_code=409, detail="This MoU is no longer active")

    content = await file.read()
    mou.signed_document_filename = file.filename
    mou.signed_document_content = content
    if not mou.signed_date:
        mou.signed_date = datetime.now().date()
    mou.status = "SIGNED"
    await db.commit()
    await db.refresh(mou)
    return _serialize(mou)


@router.get("/village/mou/{mou_id}/draft-document")
async def download_village_draft_document(mou_id: str, db: AsyncSession = Depends(get_db), user=Depends(village_only)):
    mou = await _load_village_mou(db, user["village_id"], mou_id)
    return _document_response(mou.draft_document_filename, mou.draft_document_content)


@router.get("/village/mou/{mou_id}/signed-document")
async def download_village_signed_document(mou_id: str, db: AsyncSession = Depends(get_db), user=Depends(village_only)):
    mou = await _load_village_mou(db, user["village_id"], mou_id)
    return _document_response(mou.signed_document_filename, mou.signed_document_content)
