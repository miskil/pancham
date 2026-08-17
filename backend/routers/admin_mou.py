import mimetypes
from datetime import date, datetime

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import require_role
from ..db import get_db
from ..models.mou import Mou
from ..models.village import Village

router = APIRouter(tags=["admin-mou"])
admin_only = require_role("ADMIN")

STATUSES = {"DRAFT", "SENT", "SIGNED", "EXPIRED", "TERMINATED"}


class MouCreateIn(BaseModel):
    terms: str | None = None
    admin_notes: str | None = None
    expiry_date: date | None = None


class MouUpdateIn(BaseModel):
    terms: str | None = None
    admin_notes: str | None = None
    expiry_date: date | None = None
    sent_date: date | None = None
    signed_date: date | None = None
    status: str | None = None


class MouOut(BaseModel):
    id: str
    village_id: str
    status: str
    terms: str | None = None
    admin_notes: str | None = None
    village_notes: str | None = None
    sent_date: date | None = None
    signed_date: date | None = None
    expiry_date: date | None = None
    draft_document_filename: str | None = None
    signed_document_filename: str | None = None
    created_at: str | None = None
    updated_at: str | None = None

    class Config:
        from_attributes = True


def _serialize(mou: Mou) -> MouOut:
    return MouOut(
        id=mou.id,
        village_id=mou.village_id,
        status=mou.status,
        terms=mou.terms,
        admin_notes=mou.admin_notes,
        village_notes=mou.village_notes,
        sent_date=mou.sent_date,
        signed_date=mou.signed_date,
        expiry_date=mou.expiry_date,
        draft_document_filename=mou.draft_document_filename,
        signed_document_filename=mou.signed_document_filename,
        created_at=mou.created_at.isoformat() if mou.created_at else None,
        updated_at=mou.updated_at.isoformat() if mou.updated_at else None,
    )


async def _load_mou(db: AsyncSession, village_id: str, mou_id: str) -> Mou:
    result = await db.execute(select(Mou).where(Mou.id == mou_id, Mou.village_id == village_id))
    mou = result.scalar_one_or_none()
    if not mou:
        raise HTTPException(status_code=404, detail="MoU not found")
    return mou


@router.get("/admin/villages/{village_id}/mou", response_model=list[MouOut])
async def list_admin_mou(village_id: str, db: AsyncSession = Depends(get_db), _=Depends(admin_only)):
    result = await db.execute(select(Mou).where(Mou.village_id == village_id).order_by(Mou.created_at))
    return [_serialize(item) for item in result.scalars().all()]


@router.post("/admin/villages/{village_id}/mou", response_model=MouOut)
async def create_admin_mou(village_id: str, body: MouCreateIn, db: AsyncSession = Depends(get_db), _=Depends(admin_only)):
    village_result = await db.execute(select(Village).where(Village.id == village_id))
    if not village_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Village not found")

    mou = Mou(
        village_id=village_id,
        status="DRAFT",
        terms=(body.terms or "").strip() or None,
        admin_notes=(body.admin_notes or "").strip() or None,
        expiry_date=body.expiry_date,
    )
    db.add(mou)
    await db.commit()
    await db.refresh(mou)
    return _serialize(mou)


@router.patch("/admin/villages/{village_id}/mou/{mou_id}", response_model=MouOut)
async def update_admin_mou(village_id: str, mou_id: str, body: MouUpdateIn, db: AsyncSession = Depends(get_db), _=Depends(admin_only)):
    mou = await _load_mou(db, village_id, mou_id)
    payload = body.model_dump(exclude_unset=True)

    if "terms" in payload:
        terms = payload["terms"]
        mou.terms = terms.strip() if isinstance(terms, str) and terms.strip() else None
    if "admin_notes" in payload:
        notes = payload["admin_notes"]
        mou.admin_notes = notes.strip() if isinstance(notes, str) and notes.strip() else None
    if "expiry_date" in payload:
        mou.expiry_date = payload["expiry_date"]
    if "sent_date" in payload:
        mou.sent_date = payload["sent_date"]
    if "signed_date" in payload:
        mou.signed_date = payload["signed_date"]
    if "status" in payload:
        status_value = (payload["status"] or "").strip().upper()
        if status_value not in STATUSES:
            raise HTTPException(status_code=400, detail=f"status must be one of {sorted(STATUSES)}")
        mou.status = status_value
        if status_value == "SENT" and not mou.sent_date:
            mou.sent_date = datetime.now().date()
        if status_value == "SIGNED" and not mou.signed_date:
            mou.signed_date = datetime.now().date()

    await db.commit()
    await db.refresh(mou)
    return _serialize(mou)


@router.delete("/admin/villages/{village_id}/mou/{mou_id}")
async def delete_admin_mou(village_id: str, mou_id: str, db: AsyncSession = Depends(get_db), _=Depends(admin_only)):
    mou = await _load_mou(db, village_id, mou_id)
    if mou.status != "DRAFT":
        raise HTTPException(status_code=409, detail="Only a draft MoU (not yet sent or signed) can be deleted")
    await db.delete(mou)
    await db.commit()
    return {"ok": True}


@router.post("/admin/villages/{village_id}/mou/{mou_id}/draft-document", response_model=MouOut)
async def upload_admin_draft_document(
    village_id: str,
    mou_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _=Depends(admin_only),
):
    mou = await _load_mou(db, village_id, mou_id)
    content = await file.read()
    mou.draft_document_filename = file.filename
    mou.draft_document_content = content
    await db.commit()
    await db.refresh(mou)
    return _serialize(mou)


def _document_response(filename: str | None, content: bytes | None) -> Response:
    if not content:
        raise HTTPException(status_code=404, detail="No document uploaded")
    name = filename or "document"
    media_type = mimetypes.guess_type(name)[0] or "application/octet-stream"
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{name}"'},
    )


@router.get("/admin/villages/{village_id}/mou/{mou_id}/draft-document")
async def download_admin_draft_document(village_id: str, mou_id: str, db: AsyncSession = Depends(get_db), _=Depends(admin_only)):
    mou = await _load_mou(db, village_id, mou_id)
    return _document_response(mou.draft_document_filename, mou.draft_document_content)


@router.get("/admin/villages/{village_id}/mou/{mou_id}/signed-document")
async def download_admin_signed_document(village_id: str, mou_id: str, db: AsyncSession = Depends(get_db), _=Depends(admin_only)):
    mou = await _load_mou(db, village_id, mou_id)
    return _document_response(mou.signed_document_filename, mou.signed_document_content)
