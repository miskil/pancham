import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base


class FundingRound(Base):
    __tablename__ = "funding_rounds"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    village_id: Mapped[str] = mapped_column(String, ForeignKey("villages.id"), nullable=False)
    round_number: Mapped[int] = mapped_column(Integer, nullable=False)
    funding_amount: Mapped[float] = mapped_column(Float, nullable=True)
    funding_sent_date: Mapped[date] = mapped_column(Date, nullable=True)
    funding_received_date: Mapped[date] = mapped_column(Date, nullable=True)
    funding_status_note: Mapped[str] = mapped_column(Text, nullable=True)
    admin_funding_note: Mapped[str] = mapped_column(Text, nullable=True)
    village_funding_note: Mapped[str] = mapped_column(Text, nullable=True)
    funding_received_message: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    village: Mapped["Village"] = relationship("Village", back_populates="funding_rounds")  # noqa: F821
