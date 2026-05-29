import uuid
from datetime import datetime
from sqlalchemy import String, ForeignKey, DateTime, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..db import Base


class Proposal(Base):
    __tablename__ = "proposals"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    village_id: Mapped[str] = mapped_column(String, ForeignKey("villages.id"), nullable=False)
    status: Mapped[str] = mapped_column(String, default="DRAFT")
    focus_area: Mapped[str] = mapped_column(String, nullable=True)
    per_capita_income: Mapped[str] = mapped_column(String, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    community_context: Mapped[str] = mapped_column(Text, nullable=True)
    key_activities: Mapped[str] = mapped_column(Text, nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    reviewed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    reviewer_notes: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    village: Mapped["Village"] = relationship("Village", back_populates="proposal")  # noqa: F821
    amendments: Mapped[list["ProposalAmendment"]] = relationship("ProposalAmendment", back_populates="proposal", order_by="ProposalAmendment.version_number")  # noqa: F821


class ProposalAmendment(Base):
    __tablename__ = "proposal_amendments"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    proposal_id: Mapped[str] = mapped_column(String, ForeignKey("proposals.id"), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    reviewed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    reviewer_notes: Mapped[str] = mapped_column(Text, nullable=True)

    proposal: Mapped["Proposal"] = relationship("Proposal", back_populates="amendments")  # noqa: F821
