from datetime import datetime
from pydantic import BaseModel, Field


# === Bill Heads ===
class BillHeadCreate(BaseModel):
    society_id: int | None = None
    name: str
    short_code: str
    description: str | None = None
    is_mandatory: bool = True
    is_active: bool = True
    display_order: int = 0


class BillHeadRead(BillHeadCreate):
    id: int
    society_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class BillHeadsBulkSetup(BaseModel):
    society_id: int | None = None


# === Bill Template Heads ===
class BillTemplateHeadCreate(BaseModel):
    head_id: int
    amount: float = 0
    is_percentage: bool = False
    percentage_value: float = 0


# === Bill Templates ===
class BillTemplateCreate(BaseModel):
    society_id: int | None = None
    name: str
    heads: list[BillTemplateHeadCreate]


class BillTemplateRead(BaseModel):
    id: int
    society_id: int
    name: str
    is_active: bool
    created_by_user_id: int
    created_at: datetime
    heads: list = []

    class Config:
        from_attributes = True


# === Invoice Line Items ===
class InvoiceLineItemCreate(BaseModel):
    head_id: int
    amount: float = Field(gt=0)
    quantity: float = 1


# === Advanced Invoice ===
class AdvancedInvoiceCreate(BaseModel):
    society_id: int | None = None
    unit_id: int
    billing_month: str  # YYYY-MM
    line_items: list[InvoiceLineItemCreate]
    discount: float = 0
    late_fee: float = 0
    due_date: datetime | None = None
    notes: str | None = None


class AdvancedInvoiceRead(BaseModel):
    id: int
    society_id: int
    unit_id: int
    invoice_number: str
    billing_month: str
    template_id: int | None = None
    previous_balance: float = 0
    total_amount: float = 0
    total_paid: float = 0
    discount: float = 0
    late_fee: float = 0
    net_amount: float = 0
    status: str
    due_date: datetime | None = None
    notes: str | None = None
    created_at: datetime
    line_items: list = []

    class Config:
        from_attributes = True


class AdvancedInvoiceGenerateRequest(BaseModel):
    society_id: int | None = None
    template_id: int
    billing_month: str
    notes: str | None = None