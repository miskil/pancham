import uuid
from datetime import datetime
from sqlalchemy import String, ForeignKey, DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..db import Base


class SupportEvidence(Base):
    __tablename__ = "support_evidence"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    village_id: Mapped[str] = mapped_column(String, ForeignKey("villages.id"), nullable=False)
    doc_type: Mapped[str] = mapped_column(String, nullable=False)  # GRAMSABHA | PANCHAYAT | OTHER
    filename: Mapped[str] = mapped_column(String, nullable=False)
    file_url: Mapped[str] = mapped_column(String, nullable=False)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    village: Mapped["Village"] = relationship("Village")  # noqa: F821
