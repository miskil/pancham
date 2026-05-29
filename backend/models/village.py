import uuid
from datetime import datetime, date
from sqlalchemy import String, Boolean, Integer, DateTime, Date, Text, Float, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..db import Base


class Village(Base):
    __tablename__ = "villages"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String, nullable=False)
    district: Mapped[str] = mapped_column(String, nullable=False)
    taluka: Mapped[str] = mapped_column(String, nullable=False)
    population: Mapped[int] = mapped_column(Integer, nullable=True)
    login_username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    login_password_hash: Mapped[str] = mapped_column(String, nullable=False)
    must_change_password: Mapped[bool] = mapped_column(Boolean, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    bhau_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    internal_status: Mapped[str] = mapped_column(String, default="CREATED")
    ngo_name: Mapped[str] = mapped_column(String, nullable=True)
    ngo_contact_name: Mapped[str] = mapped_column(String, nullable=True)
    ngo_contact_phone: Mapped[str] = mapped_column(String, nullable=True)
    village_lead_name: Mapped[str] = mapped_column(String, nullable=True)
    village_lead_phone: Mapped[str] = mapped_column(String, nullable=True)
    ngo_whatsapp_phone: Mapped[str] = mapped_column(String, nullable=True)
    funding_sent_date: Mapped[date] = mapped_column(Date, nullable=True)
    funding_received_date: Mapped[date] = mapped_column(Date, nullable=True)
    funding_amount: Mapped[float] = mapped_column(Float, nullable=True)
    funding_status_note: Mapped[str] = mapped_column(Text, nullable=True)
    vdc_members: Mapped[list[dict]] = mapped_column(JSONB, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    proposal: Mapped["Proposal"] = relationship("Proposal", back_populates="village", uselist=False)  # noqa: F821
    plans: Mapped[list["ProjectPlan"]] = relationship("ProjectPlan", back_populates="village")  # noqa: F821
    funding_rounds: Mapped[list["FundingRound"]] = relationship("FundingRound", back_populates="village", order_by="FundingRound.round_number")  # noqa: F821
    status_updates: Mapped[list["StatusUpdate"]] = relationship("StatusUpdate", back_populates="village")  # noqa: F821
    channel_messages: Mapped[list["VillageChannel"]] = relationship("VillageChannel", back_populates="village")  # noqa: F821
