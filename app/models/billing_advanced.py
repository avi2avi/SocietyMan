from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class BillHead(Base):
    """Bill heads/categories as per MCS Act - admin configurable"""
    __tablename__ = "bill_heads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    society_id: Mapped[int] = mapped_column(ForeignKey("societies.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)  # Maintenance, Repair Fund, Education Fund, Sinking Fund, etc.
    short_code: Mapped[str] = mapped_column(String(20), nullable=False)  # MAINT, REPAIR, EDU, SINKING, etc.
    description: Mapped[str | None] = mapped_column(Text)
    is_mandatory: Mapped[bool] = mapped_column(Boolean, default=True)  # Mandatory as per MCS Act
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    display_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class BillTemplate(Base):
    """Bill template with pre-defined head values"""
    __tablename__ = "bill_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    society_id: Mapped[int] = mapped_column(ForeignKey("societies.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class BillTemplateHead(Base):
    """Amount for each head in a template"""
    __tablename__ = "bill_template_heads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    template_id: Mapped[int] = mapped_column(ForeignKey("bill_templates.id"), nullable=False, index=True)
    head_id: Mapped[int] = mapped_column(ForeignKey("bill_heads.id"), nullable=False, index=True)
    amount: Mapped[float] = mapped_column(Float, default=0)
    is_percentage: Mapped[bool] = mapped_column(Boolean, default=False)
    percentage_value: Mapped[float] = mapped_column(Float, default=0)


class AdvancedInvoice(Base):
    """Enhanced invoice with multiple bill heads"""
    __tablename__ = "advanced_invoices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    society_id: Mapped[int] = mapped_column(ForeignKey("societies.id"), nullable=False, index=True)
    unit_id: Mapped[int] = mapped_column(ForeignKey("units.id"), nullable=False, index=True)
    invoice_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    billing_month: Mapped[str] = mapped_column(String(7), nullable=False, index=True)  # YYYY-MM
    template_id: Mapped[int | None] = mapped_column(ForeignKey("bill_templates.id"), nullable=True)
    previous_balance: Mapped[float] = mapped_column(Float, default=0)
    total_amount: Mapped[float] = mapped_column(Float, default=0)
    total_paid: Mapped[float] = mapped_column(Float, default=0)
    discount: Mapped[float] = mapped_column(Float, default=0)
    late_fee: Mapped[float] = mapped_column(Float, default=0)
    net_amount: Mapped[float] = mapped_column(Float, default=0)  # total - discount + late_fee
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, paid, partially_paid, overdue, cancelled
    due_date: Mapped[datetime | None] = mapped_column(DateTime)
    generated_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime)


class InvoiceLineItem(Base):
    """Individual line items for each invoice"""
    __tablename__ = "invoice_line_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    invoice_id: Mapped[int] = mapped_column(ForeignKey("advanced_invoices.id"), nullable=False, index=True)
    head_id: Mapped[int] = mapped_column(ForeignKey("bill_heads.id"), nullable=False, index=True)
    head_name: Mapped[str] = mapped_column(String(120), nullable=False)  # Snapshot of head name at time of billing
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    quantity: Mapped[float] = mapped_column(Float, default=1)
    total: Mapped[float] = mapped_column(Float, nullable=False)  # amount * quantity
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class InvoiceNumberSequence(Base):
    """Auto-incrementing invoice number per society"""
    __tablename__ = "invoice_number_sequences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    society_id: Mapped[int] = mapped_column(ForeignKey("societies.id"), nullable=False, unique=True, index=True)
    prefix: Mapped[str] = mapped_column(String(20), default="INV")
    last_number: Mapped[int] = mapped_column(Integer, default=0)
    financial_year: Mapped[str] = mapped_column(String(9), nullable=False)  # 2025-2026