import uuid
from datetime import datetime
from sqlalchemy import String, ForeignKey, DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..db import Base


class AnubhavPost(Base):
    __tablename__ = "anubhav_posts"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String, nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author_role: Mapped[str] = mapped_column(String, nullable=False)  # ADMIN | VILLAGE
    author_village_id: Mapped[str | None] = mapped_column(String, ForeignKey("villages.id"), nullable=True)
    author_admin_id: Mapped[str | None] = mapped_column(String, ForeignKey("admin_users.id"), nullable=True)
    author_display_name: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    media_files: Mapped[list["AnubhavMediaFile"]] = relationship(
        "AnubhavMediaFile",
        back_populates="post",
        order_by="AnubhavMediaFile.uploaded_at",
        cascade="all, delete-orphan",
    )


class AnubhavMediaFile(Base):
    __tablename__ = "anubhav_media_files"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    anubhav_post_id: Mapped[str] = mapped_column(String, ForeignKey("anubhav_posts.id", ondelete="CASCADE"), nullable=False)
    media_type: Mapped[str] = mapped_column(String, nullable=False)  # PHOTO
    file_url: Mapped[str] = mapped_column(String, nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    post: Mapped["AnubhavPost"] = relationship("AnubhavPost", back_populates="media_files")
