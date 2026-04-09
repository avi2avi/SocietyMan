from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.enums import PaymentMethod, PaymentProvider, Role, TicketStatus, VisitorType, WhatsAppProvider


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[Role] = mapped_column(Enum(Role), nullable=False)
    emergency_contact_name: Mapped[str | None] = mapped_column(String(120))
    emergency_contact_phone: Mapped[str | None] = mapped_column(String(20))
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    token: Mapped[str] = mapped_column(String(600), nullable=False, unique=True)
    is_revoked: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Unit(Base):
    __tablename__ = "units"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    building: Mapped[str] = mapped_column(String(50), nullable=False)
    unit_number: Mapped[str] = mapped_column(String(20), nullable=False)
    unit_type: Mapped[str] = mapped_column(String(30), default="residential")
    parking_car_slots: Mapped[int] = mapped_column(Integer, default=0)
    parking_bike_slots: Mapped[int] = mapped_column(Integer, default=0)


class ResidentProfile(Base):
    __tablename__ = "resident_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    unit_id: Mapped[int] = mapped_column(ForeignKey("units.id"), nullable=False)
    occupancy_type: Mapped[str] = mapped_column(String(20), default="owner")
    move_in_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class VisitorLog(Base):
    __tablename__ = "visitor_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    resident_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    visitor_name: Mapped[str] = mapped_column(String(120), nullable=False)
    visitor_phone: Mapped[str] = mapped_column(String(20), nullable=False)
    visitor_type: Mapped[VisitorType] = mapped_column(Enum(VisitorType), nullable=False)
    purpose: Mapped[str | None] = mapped_column(String(200))
    entry_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    exit_at: Mapped[datetime | None] = mapped_column(DateTime)
    qr_token: Mapped[str | None] = mapped_column(String(100))
    otp_code: Mapped[str | None] = mapped_column(String(10))


class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    unit_id: Mapped[int] = mapped_column(ForeignKey("units.id"), nullable=False)
    billing_month: Mapped[str] = mapped_column(String(7), nullable=False)
    maintenance_charge: Mapped[float] = mapped_column(Float, default=0)
    parking_charge: Mapped[float] = mapped_column(Float, default=0)
    special_levy: Mapped[float] = mapped_column(Float, default=0)
    late_penalty: Mapped[float] = mapped_column(Float, default=0)
    adjustments: Mapped[float] = mapped_column(Float, default=0)
    total_amount: Mapped[float] = mapped_column(Float, default=0)
    status: Mapped[str] = mapped_column(String(20), default="unpaid")


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    invoice_id: Mapped[int] = mapped_column(ForeignKey("invoices.id"), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    method: Mapped[PaymentMethod] = mapped_column(Enum(PaymentMethod), nullable=False)
    provider: Mapped[PaymentProvider] = mapped_column(Enum(PaymentProvider), nullable=False)
    provider_order_id: Mapped[str | None] = mapped_column(String(100))
    provider_payment_id: Mapped[str | None] = mapped_column(String(100))
    reference_id: Mapped[str] = mapped_column(String(100), nullable=False)
    paid_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Vendor(Base):
    __tablename__ = "vendors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    contact_name: Mapped[str] = mapped_column(String(120), nullable=False)
    contact_phone: Mapped[str] = mapped_column(String(20), nullable=False)


class VendorInvoice(Base):
    __tablename__ = "vendor_invoices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vendor_id: Mapped[int] = mapped_column(ForeignKey("vendors.id"), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    invoice_month: Mapped[str] = mapped_column(String(7), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    description: Mapped[str | None] = mapped_column(Text)


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    resident_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    media_url: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[TicketStatus] = mapped_column(Enum(TicketStatus), default=TicketStatus.OPEN)
    assigned_vendor_id: Mapped[int | None] = mapped_column(ForeignKey("vendors.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Notice(Base):
    __tablename__ = "notices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    created_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    file_url: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[str] = mapped_column(String(20), default="1.0")
    uploaded_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class WhatsAppMessageLog(Base):
    __tablename__ = "whatsapp_message_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    provider: Mapped[WhatsAppProvider] = mapped_column(Enum(WhatsAppProvider), nullable=False)
    message_body: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="queued")
    external_message_id: Mapped[str | None] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
