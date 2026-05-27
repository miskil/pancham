import uuid
from datetime import datetime
from sqlalchemy import String, ForeignKey, DateTime, Boolean, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..db import Base


class StatusUpdate(Base):
    __tablename__ = "status_updates"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    village_id: Mapped[str] = mapped_column(String, ForeignKey("villages.id"), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)

    village: Mapped["Village"] = relationship("Village", back_populates="status_updates")  # noqa: F821
    media_files: Mapped[list["MediaFile"]] = relationship("MediaFile", back_populates="status_update")  # noqa: F821
    thread_messages: Mapped[list["UpdateThread"]] = relationship("UpdateThread", back_populates="status_update", order_by="UpdateThread.sent_at")  # noqa: F821


class MediaFile(Base):
    __tablename__ = "media_files"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    status_update_id: Mapped[str] = mapped_column(String, ForeignKey("status_updates.id"), nullable=False)
    media_type: Mapped[str] = mapped_column(String, nullable=False)  # PHOTO | VIDEO
    file_url: Mapped[str] = mapped_column(String, nullable=False)
    caption: Mapped[str] = mapped_column(String, nullable=True)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    status_update: Mapped["StatusUpdate"] = relationship("StatusUpdate", back_populates="media_files")  # noqa: F821
