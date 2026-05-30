import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from ..db import Base


class VillageUser(Base):
    __tablename__ = "village_users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    village_id: Mapped[str] = mapped_column(String, ForeignKey("villages.id"), nullable=False)
    display_name: Mapped[str] = mapped_column(String, nullable=True)
    user_type: Mapped[str] = mapped_column(String, nullable=False, default="VDC")
    login_username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    login_password_hash: Mapped[str] = mapped_column(String, nullable=False)
    must_change_password: Mapped[bool] = mapped_column(Boolean, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
