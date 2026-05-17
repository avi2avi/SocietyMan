from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class DomesticHelp(Base):
    __tablename__ = "domestic_help"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    society_id: Mapped[int] = mapped_column(ForeignKey("societies.id"), nullable=False, index=True)
    unit_id: Mapped[int | None] = mapped_column(ForeignKey("units.id"), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20))
    help_type: Mapped[str] = mapped_column(String(30), default="maid")  # maid, cook, driver, gardener, nanny, other
    working_days: Mapped[str | None] = mapped_column(String(200))  # comma-separated: Monday,Tuesday,...
    working_hours: Mapped[str | None] = mapped_column(String(50))  # e.g. 9:00-11:00
    id_proof_type: Mapped[str | None] = mapped_column(String(50))
    id_proof_number: Mapped[str | None] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)