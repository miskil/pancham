import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, LargeBinary, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base


class Mou(Base):
    __tablename__ = "mous"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    village_id: Mapped[str] = mapped_column(String, ForeignKey("villages.id"), nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="DRAFT")  # DRAFT | SENT | SIGNED | EXPIRED | TERMINATED
    terms: Mapped[str] = mapped_column(Text, nullable=True)
    admin_notes: Mapped[str] = mapped_column(Text, nullable=True)
    village_notes: Mapped[str] = mapped_column(Text, nullable=True)
    sent_date: Mapped[date] = mapped_column(Date, nullable=True)
    signed_date: Mapped[date] = mapped_column(Date, nullable=True)
    expiry_date: Mapped[date] = mapped_column(Date, nullable=True)
    draft_document_filename: Mapped[str] = mapped_column(String, nullable=True)
    draft_document_content: Mapped[bytes] = mapped_column(LargeBinary, nullable=True)
    signed_document_filename: Mapped[str] = mapped_column(String, nullable=True)
    signed_document_content: Mapped[bytes] = mapped_column(LargeBinary, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    village: Mapped["Village"] = relationship("Village", back_populates="mous")  # noqa: F821
