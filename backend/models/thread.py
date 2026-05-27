import uuid
from datetime import datetime
from sqlalchemy import String, ForeignKey, DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..db import Base


class UpdateThread(Base):
    __tablename__ = "update_threads"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    status_update_id: Mapped[str] = mapped_column(String, ForeignKey("status_updates.id"), nullable=False)
    author_role: Mapped[str] = mapped_column(String, nullable=False)  # ADMIN | VILLAGE
    message: Mapped[str] = mapped_column(Text, nullable=False)
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    status_update: Mapped["StatusUpdate"] = relationship("StatusUpdate", back_populates="thread_messages")  # noqa: F821


class VillageChannel(Base):
    __tablename__ = "village_channels"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    village_id: Mapped[str] = mapped_column(String, ForeignKey("villages.id"), nullable=False)
    author_role: Mapped[str] = mapped_column(String, nullable=False)  # ADMIN | VILLAGE
    message: Mapped[str] = mapped_column(Text, nullable=False)
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    read_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    village: Mapped["Village"] = relationship("Village", back_populates="channel_messages")  # noqa: F821
