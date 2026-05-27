import uuid
from datetime import datetime, date
from sqlalchemy import String, ForeignKey, DateTime, Date, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..db import Base

PLAN_CATEGORIES = [
    "Education",
    "Environment",
    "Healthcare",
    "Income Generation",
    "Women's Empowerment",
    "Admin Cost",
]


def empty_plan_data() -> dict:
    return {
        str(yr): [
            {"category": cat, "details": "", "poc": "", "amount": None}
            for cat in PLAN_CATEGORIES
        ]
        for yr in [1, 2, 3]
    }


class ProjectPlan(Base):
    __tablename__ = "project_plans"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    village_id: Mapped[str] = mapped_column(String, ForeignKey("villages.id"), nullable=False)
    version_type: Mapped[str] = mapped_column(String, nullable=False)  # BASELINE | WIP
    status: Mapped[str] = mapped_column(String, default="DRAFT")
    start_date: Mapped[date] = mapped_column(Date, nullable=True)
    end_date: Mapped[date] = mapped_column(Date, nullable=True)
    frozen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_from_plan_id: Mapped[str] = mapped_column(String, ForeignKey("project_plans.id"), nullable=True)
    plan_data: Mapped[dict] = mapped_column(JSONB, nullable=False, default=empty_plan_data)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    village: Mapped["Village"] = relationship("Village", back_populates="plans")  # noqa: F821
