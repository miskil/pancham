from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..db import get_db
from ..models.evidence import SupportEvidence
from ..auth import require_role
import uuid, os, shutil

router = APIRouter(prefix="/village/evidence", tags=["village-evidence"])
village_only = require_role("VILLAGE")

DOC_TYPES = {"GRAMSABHA", "PANCHAYAT", "OTHER"}
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads/evidence")


class EvidenceOut(BaseModel):
    id: str
    doc_type: str
    filename: str
    file_url: str
    notes: str | None
    uploaded_at: str

    class Config:
        from_attributes = True


@router.get("", response_model=list[EvidenceOut])
async def list_evidence(db: AsyncSession = Depends(get_db), user=Depends(village_only)):
    result = await db.execute(
        select(SupportEvidence)
        .where(SupportEvidence.village_id == user["village_id"])
        .order_by(SupportEvidence.uploaded_at.desc())
    )
    return [_out(e) for e in result.scalars().all()]


@router.post("", response_model=EvidenceOut)
async def upload_evidence(
    doc_type: str = Form(...),
    notes: str = Form(""),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user=Depends(village_only),
):
    if doc_type not in DOC_TYPES:
        raise HTTPException(status_code=400, detail=f"doc_type must be one of {DOC_TYPES}")

    storage_url = os.getenv("STORAGE_URL", "")
    safe_name = f"{uuid.uuid4()}_{file.filename}"

    if storage_url:
        file_url = f"{storage_url}/{safe_name}"
    else:
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        dest = os.path.join(UPLOAD_DIR, safe_name)
        with open(dest, "wb") as f:
            shutil.copyfileobj(file.file, f)
        file_url = f"/uploads/evidence/{safe_name}"

    ev = SupportEvidence(
        village_id=user["village_id"],
        doc_type=doc_type,
        filename=file.filename,
        file_url=file_url,
        notes=notes or None,
    )
    db.add(ev)
    await db.commit()
    await db.refresh(ev)
    return _out(ev)


@router.delete("/{evidence_id}", status_code=204)
async def delete_evidence(evidence_id: str, db: AsyncSession = Depends(get_db), user=Depends(village_only)):
    result = await db.execute(select(SupportEvidence).where(SupportEvidence.id == evidence_id))
    ev = result.scalar_one_or_none()
    if not ev or ev.village_id != user["village_id"]:
        raise HTTPException(status_code=404, detail="Not found")
    await db.delete(ev)
    await db.commit()


def _out(e: SupportEvidence) -> EvidenceOut:
    return EvidenceOut(
        id=e.id,
        doc_type=e.doc_type,
        filename=e.filename,
        file_url=e.file_url,
        notes=e.notes,
        uploaded_at=e.uploaded_at.isoformat(),
    )
