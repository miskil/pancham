import io
from datetime import date

from docx import Document
from docx.shared import Pt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import get_current_user
from ..db import get_db
from ..models.plan import ProjectPlan
from ..models.proposal import Proposal
from ..models.village import Village

router = APIRouter(prefix="/admin/export", tags=["admin-export"])


def _docx_bytes(doc: Document) -> bytes:
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def _heading(doc: Document, text: str, level: int = 1):
    p = doc.add_heading(text, level=level)
    p.runs[0].font.size = Pt(14 if level == 1 else 12)


def _row(doc: Document, label: str, value: str):
    p = doc.add_paragraph()
    run = p.add_run(f"{label}: ")
    run.bold = True
    p.add_run(value or "—")


# ── Proposal export ──────────────────────────────────────────────────────────

@router.post("/proposals/{proposal_id}")
async def export_proposal(
    proposal_id: str,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    result = await db.execute(
        select(Proposal).where(Proposal.id == proposal_id)
    )
    proposal = result.scalar_one_or_none()
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")

    if user["role"] not in ["ADMIN", "VILLAGE"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    if user["role"] == "VILLAGE" and user.get("village_id") != proposal.village_id:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    village = await db.get(Village, proposal.village_id)

    doc = Document()
    doc.core_properties.author = "Pancham"

    _heading(doc, f"Proposal — {village.name if village else proposal.village_id}")
    _row(doc, "Village", village.name if village else "")
    _row(doc, "District", village.district if village else "")
    _row(doc, "Taluka", village.taluka if village else "")
    _row(doc, "Status", proposal.status)
    _row(doc, "Submitted", str(proposal.submitted_at.date()) if proposal.submitted_at else "Not submitted")
    doc.add_paragraph()

    _heading(doc, "Proposal Details", level=2)
    _row(doc, "Focus Area", proposal.focus_area or "")
    doc.add_paragraph()

    _heading(doc, "Description", level=2)
    doc.add_paragraph(proposal.description or "—")

    _heading(doc, "Community Context", level=2)
    doc.add_paragraph(proposal.community_context or "—")

    _heading(doc, "Key Activities", level=2)
    doc.add_paragraph(proposal.key_activities or "—")

    if proposal.reviewer_notes:
        _heading(doc, "Reviewer Notes", level=2)
        doc.add_paragraph(proposal.reviewer_notes)

    filename = f"Proposal_{village.name if village else proposal.village_id}_{date.today()}.docx"
    content = _docx_bytes(doc)
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(
        io.BytesIO(content),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers=headers,
    )


# ── Plan export ───────────────────────────────────────────────────────────────

@router.post("/plans/{plan_id}")
async def export_plan(
    plan_id: str,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    result = await db.execute(
        select(ProjectPlan).where(ProjectPlan.id == plan_id)
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    if user["role"] not in ["ADMIN", "VILLAGE"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    if user["role"] == "VILLAGE" and user.get("village_id") != plan.village_id:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    village = await db.get(Village, plan.village_id)

    doc = Document()
    doc.core_properties.author = "Pancham"

    _heading(doc, f"Project Plan — {village.name if village else plan.village_id}")
    _row(doc, "Village", village.name if village else "")
    _row(doc, "District", village.district if village else "")
    _row(doc, "Version", plan.version_type)
    _row(doc, "Status", plan.status)
    _row(doc, "Start Date", str(plan.start_date) if plan.start_date else "—")
    _row(doc, "End Date", str(plan.end_date) if plan.end_date else "—")
    if plan.frozen_at:
        _row(doc, "Frozen At", str(plan.frozen_at.date()))
    doc.add_paragraph()

    plan_data = plan.plan_data or {}
    for year_key in ["1", "2", "3"]:
        rows = plan_data.get(year_key, [])
        if not rows:
            continue
        _heading(doc, f"Year {year_key}", level=2)
        table = doc.add_table(rows=1, cols=4)
        table.style = "Light List Accent 1"
        hdr = table.rows[0].cells
        hdr[0].text = "Category"
        hdr[1].text = "Details"
        hdr[2].text = "POC"
        hdr[3].text = "Amount"
        for item in rows:
            cells = table.add_row().cells
            cells[0].text = item.get("category", "")
            cells[1].text = item.get("details", "") or "—"
            cells[2].text = item.get("poc", "") or "—"
            amount = item.get("amount")
            cells[3].text = str(amount) if amount is not None else "—"
        doc.add_paragraph()

    filename = f"Plan_{plan.version_type}_{village.name if village else plan.village_id}_{date.today()}.docx"
    content = _docx_bytes(doc)
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(
        io.BytesIO(content),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers=headers,
    )
