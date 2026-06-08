import io
import logging
import unicodedata
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

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin/export", tags=["admin-export"])


def _ascii_safe_filename(text: str) -> str:
    """Convert text to ASCII-safe filename by removing non-ASCII characters."""
    if not text:
        return "export"
    # Normalize and remove non-ASCII
    nfkd = unicodedata.normalize('NFKD', text)
    ascii_only = nfkd.encode('ascii', 'ignore').decode('ascii')
    # Remove special characters, keep alphanumeric and basic punctuation
    safe = ''.join(c if c.isalnum() or c in '-_' else '_' for c in ascii_only)
    return safe.strip('_') or "export"


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


def _normalize_categories(milestone: dict) -> str:
    categories = milestone.get("categories") or milestone.get("category") or []
    if isinstance(categories, str):
        categories = [categories]
    cleaned = [str(cat).strip() for cat in categories if str(cat).strip()]
    return ", ".join(cleaned) or "—"


def _normalize_activities(milestone: dict) -> list[dict]:
    activities = milestone.get("activities")
    if isinstance(activities, list) and activities:
        return activities
    return [
        {
            "activity": milestone.get("activity") or milestone.get("details") or "",
            "poc": milestone.get("poc") or "",
            "amount": milestone.get("amount"),
            "notes": milestone.get("notes") or milestone.get("comment") or "",
        }
    ]


FOCUS_AREA_LABELS = {
    "HEALTH": "Health",
    "EDUCATION": "Education",
    "ENVIRONMENT": "Environment",
    "INCOME_GENERATION": "Income Generation",
    "WOMENS_EMPOWERMENT": "Women's Empowerment",
}

VILLAGE_PROFILE_SECTIONS = [
    ("Basic Village Information", [
        ("population", "Population"),
        ("total_families", "Total Families"),
        ("area", "Village Area"),
        ("sc_st_obc_ratio", "SC/ST/OBC & Other Population Ratio"),
        ("literacy_rate", "Literacy Rate"),
        ("migration_families", "Migrating Families"),
    ]),
    ("Poverty & Vulnerability", [
        ("bpl_families", "Below Poverty Line (BPL) Families %"),
        ("landless_families", "Landless Families"),
        ("wage_dependent", "Wage-Dependent Families"),
        ("malnourished_children", "Malnourished Children"),
        ("women_headed", "Women-Headed Families"),
        ("disabled", "Persons with Disability"),
        ("elderly_alone", "Elderly Living Alone"),
    ]),
    ("Water & Water Security", [
        ("drinking_sources", "Drinking Water Sources"),
        ("scarcity_months", "Water Scarcity Months/Year"),
        ("groundwater_level", "Groundwater Level"),
        ("irrigated_area", "Irrigated Area"),
        ("tanker_dependency", "Tanker Dependency"),
        ("conservation_status", "Water Conservation Status"),
    ]),
    ("Agriculture & Livelihoods", [
        ("main_crops", "Main Crops"),
        ("irrigated_rainfed", "Irrigated & Rainfed Area"),
        ("crop_productivity", "Crop Productivity"),
        ("livestock", "Livestock Count"),
        ("fpo_exists", "FPO Exists?"),
        ("non_farm_employment", "Non-Farm Employment Opportunities"),
        ("avg_income", "Average Family Income"),
    ]),
    ("Infrastructure", [
        ("roads", "Road Connectivity"),
        ("electricity", "Electricity Availability"),
        ("mobile_network", "Mobile Network"),
        ("internet", "Internet Facility"),
        ("public_transport", "Public Transport"),
        ("housing", "Housing Condition"),
    ]),
    ("Education", [
        ("schools", "Primary & Secondary Schools"),
        ("attendance", "School Attendance"),
        ("out_of_school", "Out-of-School Children"),
        ("girls_education", "Girls' Education Status"),
        ("digital_education", "Digital Education Facilities"),
    ]),
    ("Health & Nutrition", [
        ("phc_distance", "Distance to PHC"),
        ("asha_anganwadi", "ASHA & Anganwadi Workers"),
        ("maternal_child_health", "Maternal & Child Health"),
        ("anemia", "Anemia"),
        ("vaccination", "Vaccination Coverage"),
    ]),
    ("Local Governance", [
        ("gramsabha_count", "Gram Sabha Count & Regularity"),
        ("gramsabha_attendance", "Gram Sabha Attendance"),
        ("women_participation", "Women's Participation"),
        ("gpdp_quality", "GPDP Quality"),
        ("committees", "Committee Functioning"),
        ("financial_transparency", "Financial Transparency"),
        ("scheme_implementation", "Govt Scheme Implementation"),
    ]),
    ("Community Readiness", [
        ("shramdan", "Readiness for Shramdan"),
        ("financial_contribution", "Financial Contribution Readiness"),
        ("shg_active", "Active Self-Help Groups (SHG)"),
        ("youth_groups", "Youth Groups"),
        ("farmer_groups", "Farmer Groups"),
        ("local_leadership", "Local Leadership"),
        ("collective_history", "History of Collective Work"),
    ]),
    ("Ongoing Projects", [
        ("water_conservation", "Water Conservation Projects"),
        ("csr_projects", "CSR Projects"),
        ("ngo_projects", "Other NGO Projects"),
        ("agriculture_programs", "Agriculture Development Programs"),
        ("infrastructure_schemes", "Infrastructure Schemes"),
    ]),
    ("Environment & Climate Risk", [
        ("drought_prone", "Drought Proneness"),
        ("flood_risk", "Flood Risk"),
        ("soil_erosion", "Soil Erosion"),
        ("forest_area", "Forest Area"),
        ("climate_impact", "Climate Change Impact"),
    ]),
    ("Tribal & PESA Status", [
        ("scheduled_area", "Village in Scheduled Area?"),
        ("pesa_applicable", "PESA Applicable?"),
        ("forest_rights", "Forest Rights Claims"),
        ("forest_dependency", "Dependence on Forest Resources"),
    ]),
]


# ── Proposal export ──────────────────────────────────────────────────────────

@router.post("/proposals/{proposal_id}")
async def export_proposal(
    proposal_id: str,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    try:
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

        _heading(doc, "NGO Partner", level=2)
        _row(doc, "NGO Name", village.ngo_name or "—")
        _row(doc, "FCRA Number", village.fcra_number or "—")
        _row(doc, "FCRA Expiry", str(village.fcra_expiry_date) if village.fcra_expiry_date else "—")
        _row(doc, "NGO Lead", village.ngo_contact_name or "—")
        _row(doc, "NGO Lead Phone", village.ngo_contact_phone or "—")
        if village.ngo_whatsapp_phone:
            _row(doc, "WhatsApp", village.ngo_whatsapp_phone)
        _row(doc, "Bank Account Number", village.bank_account_number or "—")
        _row(doc, "IFSC Code", village.ifsc_code or "—")
        doc.add_paragraph()

        _heading(doc, "Village Lead", level=2)
        _row(doc, "Name", village.village_lead_name or "—")
        _row(doc, "Phone", village.village_lead_phone or "—")
        doc.add_paragraph()

        _heading(doc, "Focus Areas", level=2)
        raw_areas = [item.strip() for item in (proposal.focus_area or "").split(",") if item.strip()]
        labeled_areas = ", ".join(FOCUS_AREA_LABELS.get(a, a) for a in raw_areas) or "—"
        doc.add_paragraph(labeled_areas)
        doc.add_paragraph()

        _heading(doc, "Geographic & Social Description", level=2)
        doc.add_paragraph(proposal.description or "—")

        _heading(doc, "Village Needs / Community Context", level=2)
        doc.add_paragraph(proposal.community_context or "—")

        _heading(doc, "Key Activities Planned", level=2)
        doc.add_paragraph(proposal.key_activities or "—")

        JS_KEY_MAP = {
            "basic_village_information": "basic",
            "poverty_and_vulnerability": "poverty",
            "water_and_water_security": "water",
            "agriculture_and_livelihoods": "agriculture",
            "infrastructure": "infrastructure",
            "education": "education",
            "health_and_nutrition": "health",
            "local_governance": "governance",
            "community_readiness": "community",
            "ongoing_projects": "projects",
            "environment_and_climate_risk": "environment",
            "tribal_and_pesa_status": "tribal",
        }
        profile = village.village_profile or {}
        for section_title, fields in VILLAGE_PROFILE_SECTIONS:
            section_key = section_title.lower().replace(" ", "_").replace("&", "and").replace("/", "_")
            js_key = JS_KEY_MAP.get(section_key, section_key)
            section_data = profile.get(js_key, {})
            _heading(doc, section_title, level=2)
            for field_key, field_label in fields:
                val = section_data.get(field_key)
                _row(doc, field_label, str(val) if val else "—")
            doc.add_paragraph()

        if proposal.reviewer_notes:
            _heading(doc, "Reviewer Notes", level=2)
            doc.add_paragraph(proposal.reviewer_notes)

        village_slug = _ascii_safe_filename(village.name if village else proposal.village_id)
        filename = f"{village_slug}-Proposal-{date.today()}.docx"
        content = _docx_bytes(doc)
        headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
        return StreamingResponse(
            io.BytesIO(content),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers=headers,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Export proposal failed for {proposal_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


# ── Plan export ───────────────────────────────────────────────────────────────

@router.post("/plans/{plan_id}")
async def export_plan(
    plan_id: str,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    try:
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

        _heading(doc, "Village Lead", level=2)
        _row(doc, "Name", village.village_lead_name or "—")
        _row(doc, "Phone", village.village_lead_phone or "—")
        doc.add_paragraph()

        _heading(doc, "NGO Partner", level=2)
        _row(doc, "NGO Name", village.ngo_name or "—")
        _row(doc, "Contact Name", village.ngo_contact_name or "—")
        _row(doc, "Phone", village.ngo_contact_phone or "—")
        if village.ngo_whatsapp_phone:
            _row(doc, "WhatsApp", village.ngo_whatsapp_phone)
        doc.add_paragraph()

        plan_data = plan.plan_data or {}
        for year_key in ["1", "2", "3"]:
            milestones = plan_data.get(year_key, [])
            if not milestones:
                continue
            _heading(doc, f"Year {year_key}", level=2)
            for idx, milestone in enumerate(milestones, start=1):
                milestone_title = milestone.get("milestone") or milestone.get("title") or f"Milestone {idx}"
                _heading(doc, milestone_title, level=3)
                _row(doc, "Categories", _normalize_categories(milestone))
                _row(doc, "Impact", milestone.get("impact") or milestone.get("impact_box") or "")

                table = doc.add_table(rows=1, cols=4)
                table.style = "Light List Accent 1"
                hdr = table.rows[0].cells
                hdr[0].text = "Activity"
                hdr[1].text = "POC"
                hdr[2].text = "Notes"
                hdr[3].text = "Amount"

                for activity in _normalize_activities(milestone):
                    cells = table.add_row().cells
                    cells[0].text = activity.get("activity", "") or "—"
                    cells[1].text = activity.get("poc", "") or "—"
                    cells[2].text = activity.get("notes", "") or "—"
                    amount = activity.get("amount")
                    cells[3].text = str(amount) if amount is not None else "—"
                doc.add_paragraph()

        village_slug = _ascii_safe_filename(village.name if village else plan.village_id)
        filename = f"{village_slug}-Plan-{date.today()}.docx"
        content = _docx_bytes(doc)
        headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
        return StreamingResponse(
            io.BytesIO(content),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers=headers,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Export plan failed for {plan_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")
