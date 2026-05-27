import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, Integer, DateTime, func
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
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    bhau_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    internal_status: Mapped[str] = mapped_column(String, default="CREATED")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    proposal: Mapped["Proposal"] = relationship("Proposal", back_populates="village", uselist=False)  # noqa: F821
    plans: Mapped[list["ProjectPlan"]] = relationship("ProjectPlan", back_populates="village")  # noqa: F821
    status_updates: Mapped[list["StatusUpdate"]] = relationship("StatusUpdate", back_populates="village")  # noqa: F821
    channel_messages: Mapped[list["VillageChannel"]] = relationship("VillageChannel", back_populates="village")  # noqa: F821
