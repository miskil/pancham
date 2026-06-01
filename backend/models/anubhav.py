import uuid
from datetime import datetime
from sqlalchemy import String, ForeignKey, DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column
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
