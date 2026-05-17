from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class SecurityPatrol(Base):
    __tablename__ = "security_patrols"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    society_id: Mapped[int] = mapped_column(ForeignKey("societies.id"), nullable=False, index=True)
    staff_member_id: Mapped[int | None] = mapped_column(ForeignKey("staff_members.id"), nullable=True, index=True)
    patrol_type: Mapped[str] = mapped_column(String(30), default="regular")  # regular, emergency, random
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_time: Mapped[datetime | None] = mapped_column(DateTime)
    route: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(30), default="in_progress")  # scheduled, in_progress, completed, missed
    created_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class PatrolCheckpoint(Base):
    __tablename__ = "patrol_checkpoints"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    patrol_id: Mapped[int] = mapped_column(ForeignKey("security_patrols.id"), nullable=False, index=True)
    checkpoint_name: Mapped[str] = mapped_column(String(120), nullable=False)
    scanned_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    location: Mapped[str | None] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(30), default="ok")  # ok, issue
    notes: Mapped[str | None] = mapped_column(Text)