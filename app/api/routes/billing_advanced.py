from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status, Response
from fastapi import UploadFile, File, Form
from fastapi.responses import StreamingResponse
import csv
from io import TextIOWrapper
import io
import json
from openpyxl import Workbook
from sqlalchemy import func, extract, desc
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.enums import Role
from app.models.entities import Unit, User, ResidentProfile, Invoice as OldInvoice
from app.models.billing_advanced import (
    BillHead,
    BillTemplate,
    BillTemplateHead,
    AdvancedInvoice,
    InvoiceLineItem,
    InvoiceNumberSequence,
)
from app.schemas.billing_advanced import (
    BillHeadCreate,
    BillHeadRead,
    BillTemplateCreate,
    BillTemplateRead,
    BillTemplateHeadCreate,
    AdvancedInvoiceCreate,
    AdvancedInvoiceRead,
    AdvancedInvoiceGenerateRequest,
    BillHeadsBulkSetup,
)

router = APIRouter(prefix="/billing-advanced", tags=["Advanced Billing"])


def _is_admin(user: User) -> bool:
    return user.role == Role.ADMIN


def _society_scope(user: User, requested_society_id: int | None = None) -> int | None:
    if _is_admin(user):
        return requested_society_id
    if not user.society_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Society-scoped account required")
    if requested_society_id and requested_society_id != user.society_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Requested society is outside your scope")
    return user.society_id


def _required_society(user: User, requested_society_id: int | None = None) -> int:
    society_id = _society_scope(user, requested_society_id)
    if society_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="society_id is required")
    return society_id


def _get_or_create_sequence(society_id: int, db: Session) -> str:
    """Auto-generate invoice number like INV-2025-0001"""
    now = datetime.utcnow()
    fy = f"{now.year}-{now.year + 1}" if now.month >= 4 else f"{now.year - 1}-{now.year}"
    seq = db.query(InvoiceNumberSequence).filter(
        InvoiceNumberSequence.society_id == society_id,
        InvoiceNumberSequence.financial_year == fy,
    ).first()
    if not seq:
        seq = InvoiceNumberSequence(
            society_id=society_id,
            prefix="INV",
            last_number=0,
            financial_year=fy,
        )
        db.add(seq)
        db.flush()
    seq.last_number += 1
    inv_no = f"{seq.prefix}-{fy[:4]}-{seq.last_number:04d}"
    return inv_no


# ===== BILL HEADS (MCS Act compliant) =====

DEFAULT_BILL_HEADS = [
    {"name": "Maintenance Charges", "short_code": "MAINT", "description": "Regular maintenance charges for common area upkeep", "is_mandatory": True, "display_order": 1},
    {"name": "Sinking Fund", "short_code": "SINK", "description": "Reserve fund for major repairs as per MCS Act", "is_mandatory": True, "display_order": 2},
    {"name": "Repair & Maintenance Fund", "short_code": "REPAIR", "description": "Fund for building repairs and maintenance", "is_mandatory": True, "display_order": 3},
    {"name": "Non-Agricultural Tax (N.A. Tax)", "short_code": "NATAX", "description": "Property tax payable to municipal corporation", "is_mandatory": True, "display_order": 4},
    {"name": "Water Charges", "short_code": "WATER", "description": "Water supply and maintenance charges", "is_mandatory": False, "display_order": 5},
    {"name": "Electricity Charges (Common)", "short_code": "ELEC", "description": "Common area electricity charges", "is_mandatory": True, "display_order": 6},
    {"name": "Parking Charges", "short_code": "PARK", "description": "Vehicle parking fees", "is_mandatory": False, "display_order": 7},
    {"name": "Insurance Premium", "short_code": "INSUR", "description": "Building and property insurance", "is_mandatory": True, "display_order": 8},
    {"name": "Education Fund", "short_code": "EDU", "description": "Fund for educational activities and awareness", "is_mandatory": False, "display_order": 9},
    {"name": "Inlet/Outlet Charges", "short_code": "INLET", "description": "Charges for inlet/outlet maintenance", "is_mandatory": False, "display_order": 10},
    {"name": "Corpus Fund", "short_code": "CORPUS", "description": "One-time corpus contribution", "is_mandatory": False, "display_order": 11},
    {"name": "Late Payment Penalty", "short_code": "LATE", "description": "Penalty for delayed payment", "is_mandatory": True, "display_order": 12},
    {"name": "Miscellaneous", "short_code": "MISC", "description": "Other charges not covered above", "is_mandatory": False, "display_order": 13},
]


@router.post("/bill-heads/setup-defaults")
def setup_default_bill_heads(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Initialize default MCS Act compliant bill heads for a society"""
    society_id = _required_society(current_user)
    existing = db.query(BillHead).filter(BillHead.society_id == society_id).count()
    if existing > 0:
        return {"message": f"Bill heads already exist ({existing} found)", "count": existing}
    created = []
    for head_data in DEFAULT_BILL_HEADS:
        head = BillHead(society_id=society_id, **head_data)
        db.add(head)
        created.append(head)
    db.commit()
    return {"message": f"Created {len(created)} default bill heads", "count": len(created)}


@router.post("/bill-heads", response_model=BillHeadRead)
def create_bill_head(payload: BillHeadCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    society_id = _required_society(current_user, payload.society_id)
    head = BillHead(**payload.model_dump(exclude={"society_id"}), society_id=society_id)
    db.add(head)
    db.commit()
    db.refresh(head)
    return head


@router.get("/bill-heads", response_model=list[BillHeadRead])
def list_bill_heads(
    society_id: int | None = Query(default=None),
    active_only: bool = Query(default=True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    scoped_society_id = _society_scope(current_user, society_id)
    query = db.query(BillHead)
    if scoped_society_id is not None:
        query = query.filter(BillHead.society_id == scoped_society_id)
    if active_only:
        query = query.filter(BillHead.is_active.is_(True))
    return query.order_by(BillHead.display_order, BillHead.name).all()


@router.patch("/bill-heads/{head_id}", response_model=BillHeadRead)
def update_bill_head(head_id: int, payload: BillHeadCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    head = db.get(BillHead, head_id)
    if not head:
        raise HTTPException(status_code=404, detail="Bill head not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        if key != "society_id":
            setattr(head, key, value)
    db.commit()
    db.refresh(head)
    return head


@router.delete("/bill-heads/{head_id}")
def delete_bill_head(head_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    head = db.get(BillHead, head_id)
    if not head:
        raise HTTPException(status_code=404, detail="Bill head not found")
    head.is_active = False
    db.commit()
    return {"detail": "Bill head deactivated"}


# ===== BILL TEMPLATES =====

@router.post("/templates", response_model=BillTemplateRead)
def create_template(payload: BillTemplateCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    society_id = _required_society(current_user, payload.society_id)
    template = BillTemplate(
        society_id=society_id,
        name=payload.name,
        created_by_user_id=current_user.id,
    )
    db.add(template)
    db.flush()
    for head_item in payload.heads:
        head = db.get(BillHead, head_item.head_id)
        if not head or head.society_id != society_id:
            raise HTTPException(status_code=400, detail=f"Bill head {head_item.head_id} not found")
        tpl_head = BillTemplateHead(
            template_id=template.id,
            head_id=head_item.head_id,
            amount=head_item.amount,
            is_percentage=head_item.is_percentage,
            percentage_value=head_item.percentage_value,
        )
        db.add(tpl_head)
    db.commit()
    db.refresh(template)
    return _get_template_with_heads(template, db)


def _get_template_with_heads(template: BillTemplate, db: Session) -> dict:
    heads = db.query(BillTemplateHead, BillHead).join(
        BillHead, BillTemplateHead.head_id == BillHead.id
    ).filter(BillTemplateHead.template_id == template.id).all()
    data = {
        "id": template.id,
        "society_id": template.society_id,
        "name": template.name,
        "is_active": template.is_active,
        "created_by_user_id": template.created_by_user_id,
        "created_at": template.created_at,
        "heads": [
            {
                "id": tpl_head.id,
                "head_id": tpl_head.head_id,
                "head_name": bh.name,
                "short_code": bh.short_code,
                "amount": tpl_head.amount,
                "is_percentage": tpl_head.is_percentage,
                "percentage_value": tpl_head.percentage_value,
            }
            for tpl_head, bh in heads
        ],
    }
    return data


@router.get("/templates", response_model=list[dict])
def list_templates(
    society_id: int | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    scoped_society_id = _society_scope(current_user, society_id)
    query = db.query(BillTemplate)
    if scoped_society_id is not None:
        query = query.filter(BillTemplate.society_id == scoped_society_id)
    templates = query.order_by(BillTemplate.name).all()
    return [_get_template_with_heads(t, db) for t in templates]


@router.delete("/templates/{template_id}")
def delete_template(template_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    template = db.get(BillTemplate, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    db.query(BillTemplateHead).filter(BillTemplateHead.template_id == template_id).delete()
    db.delete(template)
    db.commit()
    return {"detail": "Template deleted"}


# ===== ADVANCED INVOICES =====

@router.post("/invoices/generate", response_model=list[dict])
def generate_invoices(
    payload: AdvancedInvoiceGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate invoices for all units using a template"""
    society_id = _required_society(current_user, payload.society_id)
    template = db.get(BillTemplate, payload.template_id)
    if not template or template.society_id != society_id:
        raise HTTPException(status_code=404, detail="Template not found")

    template_heads = db.query(BillTemplateHead).filter(
        BillTemplateHead.template_id == template.id
    ).all()
    if not template_heads:
        raise HTTPException(status_code=400, detail="Template has no heads configured")

    units = db.query(Unit).all()
    if not units:
        raise HTTPException(status_code=400, detail="No units found")

    created = []
    for unit in units:
        inv_no = _get_or_create_sequence(society_id, db)
        line_items = []
        total_amount = 0

        for th in template_heads:
            head = db.get(BillHead, th.head_id)
            if not head:
                continue
            amount = th.amount
            line_total = amount
            line_items.append({
                "head_id": th.head_id,
                "head_name": head.name,
                "amount": amount,
                "quantity": 1,
                "total": line_total,
            })
            total_amount += line_total

        previous_due = db.query(func.coalesce(func.sum(AdvancedInvoice.net_amount - AdvancedInvoice.total_paid), 0)).filter(
            AdvancedInvoice.unit_id == unit.id,
            AdvancedInvoice.status.in_(["pending", "overdue", "partially_paid"]),
        ).scalar() or 0

        net_amount = total_amount + previous_due
        due_date = datetime.utcnow() + timedelta(days=15)

        invoice = AdvancedInvoice(
            society_id=society_id,
            unit_id=unit.id,
            invoice_number=inv_no,
            billing_month=payload.billing_month,
            template_id=template.id,
            previous_balance=float(previous_due),
            total_amount=total_amount,
            net_amount=net_amount,
            status="pending",
            due_date=due_date,
            generated_by_user_id=current_user.id,
            notes=payload.notes,
        )
        db.add(invoice)
        db.flush()

        for li in line_items:
            item = InvoiceLineItem(
                invoice_id=invoice.id,
                head_id=li["head_id"],
                head_name=li["head_name"],
                amount=li["amount"],
                quantity=li["quantity"],
                total=li["total"],
            )
            db.add(item)

        created.append({
            "invoice_id": invoice.id,
            "invoice_number": inv_no,
            "unit_id": unit.id,
            "total_amount": total_amount,
            "previous_balance": float(previous_due),
            "net_amount": net_amount,
            "status": "pending",
        })

    db.commit()
    return created


@router.post("/invoices/manual", response_model=dict)
def create_manual_invoice(
    payload: AdvancedInvoiceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a manual invoice for a specific unit with custom line items"""
    society_id = _required_society(current_user, payload.society_id)
    unit = db.get(Unit, payload.unit_id)
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")

    inv_no = _get_or_create_sequence(society_id, db)

    # Validate heads
    total_amount = 0
    for li in payload.line_items:
        head = db.get(BillHead, li.head_id)
        if not head or head.society_id != society_id:
            raise HTTPException(status_code=400, detail=f"Bill head {li.head_id} not found in this society")

    previous_due = db.query(func.coalesce(func.sum(AdvancedInvoice.net_amount - AdvancedInvoice.total_paid), 0)).filter(
        AdvancedInvoice.unit_id == unit.id,
        AdvancedInvoice.status.in_(["pending", "overdue", "partially_paid"]),
    ).scalar() or 0

    line_total = sum(li.amount * (li.quantity or 1) for li in payload.line_items)
    net_amount = line_total + float(previous_due) + payload.late_fee - payload.discount
    due_date = payload.due_date or (datetime.utcnow() + timedelta(days=15))

    invoice = AdvancedInvoice(
        society_id=society_id,
        unit_id=unit.id,
        invoice_number=inv_no,
        billing_month=payload.billing_month,
        previous_balance=float(previous_due),
        total_amount=line_total,
        discount=payload.discount,
        late_fee=payload.late_fee,
        net_amount=net_amount,
        status="pending",
        due_date=due_date,
        generated_by_user_id=current_user.id,
        notes=payload.notes,
    )
    db.add(invoice)
    db.flush()

    for li in payload.line_items:
        head = db.get(BillHead, li.head_id)
        item = InvoiceLineItem(
            invoice_id=invoice.id,
            head_id=li.head_id,
            head_name=head.name,
            amount=li.amount,
            quantity=li.quantity or 1,
            total=li.amount * (li.quantity or 1),
        )
        db.add(item)

    db.commit()
    db.refresh(invoice)
    return _get_invoice_with_items(invoice, db)


def _get_invoice_with_items(invoice: AdvancedInvoice, db: Session) -> dict:
    items = db.query(InvoiceLineItem).filter(InvoiceLineItem.invoice_id == invoice.id).all()
    unit = db.get(Unit, invoice.unit_id)
    profile = db.query(ResidentProfile).filter(ResidentProfile.unit_id == invoice.unit_id).first()
    resident_name = None
    if profile:
        user = db.get(User, profile.user_id)
        resident_name = user.full_name if user else None

    return {
        "id": invoice.id,
        "invoice_number": invoice.invoice_number,
        "society_id": invoice.society_id,
        "unit_id": invoice.unit_id,
        "building": unit.building if unit else None,
        "unit_number": unit.unit_number if unit else None,
        "resident_name": resident_name,
        "billing_month": invoice.billing_month,
        "previous_balance": invoice.previous_balance,
        "total_amount": invoice.total_amount,
        "discount": invoice.discount,
        "late_fee": invoice.late_fee,
        "net_amount": invoice.net_amount,
        "total_paid": invoice.total_paid,
        "status": invoice.status,
        "due_date": invoice.due_date.isoformat() if invoice.due_date else None,
        "notes": invoice.notes,
        "created_at": invoice.created_at.isoformat(),
        "line_items": [
            {
                "id": item.id,
                "head_name": item.head_name,
                "amount": item.amount,
                "quantity": item.quantity,
                "total": item.total,
            }
            for item in items
        ],
    }


@router.get("/invoices", response_model=list[dict])
def list_invoices(
    society_id: int | None = Query(default=None),
    unit_id: int | None = Query(default=None),
    status: str | None = Query(default=None),
    billing_month: str | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    scoped_society_id = _society_scope(current_user, society_id)
    query = db.query(AdvancedInvoice)
    if scoped_society_id is not None:
        query = query.filter(AdvancedInvoice.society_id == scoped_society_id)
    if unit_id:
        query = query.filter(AdvancedInvoice.unit_id == unit_id)
    if status:
        query = query.filter(AdvancedInvoice.status == status)
    if billing_month:
        query = query.filter(AdvancedInvoice.billing_month == billing_month)
    invoices = query.order_by(AdvancedInvoice.created_at.desc()).limit(200).all()
    return [_get_invoice_with_items(inv, db) for inv in invoices]


@router.get("/invoices/{invoice_id}", response_model=dict)
def get_invoice(invoice_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    invoice = db.get(AdvancedInvoice, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return _get_invoice_with_items(invoice, db)


@router.get("/invoices/stats/summary")
def invoice_summary(
    society_id: int | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    scoped_society_id = _society_scope(current_user, society_id)
    query = db.query(AdvancedInvoice)
    if scoped_society_id is not None:
        query = query.filter(AdvancedInvoice.society_id == scoped_society_id)
    
    total = query.count()
    pending = query.filter(AdvancedInvoice.status == "pending").count()
    paid = query.filter(AdvancedInvoice.status == "paid").count()
    overdue = query.filter(AdvancedInvoice.status == "overdue").count()
    total_amount = query.with_entities(func.coalesce(func.sum(AdvancedInvoice.net_amount), 0)).scalar() or 0
    total_collected = query.with_entities(func.coalesce(func.sum(AdvancedInvoice.total_paid), 0)).scalar() or 0
    
    return {
        "total_invoices": total,
        "pending": pending,
        "paid": paid,
        "overdue": overdue,
        "total_amount": float(total_amount),
        "total_collected": float(total_collected),
        "outstanding": float(total_amount - total_collected),
    }



@router.get("/invoices/stats/dashboard")
def invoice_dashboard(
    society_id: int | None = Query(default=None),
    status: str | None = Query(default=None),
    billing_month: str | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    scoped_society_id = _society_scope(current_user, society_id)
    query = db.query(AdvancedInvoice)
    if scoped_society_id is not None:
        query = query.filter(AdvancedInvoice.society_id == scoped_society_id)
    if status:
        query = query.filter(AdvancedInvoice.status == status)
    if billing_month:
        query = query.filter(AdvancedInvoice.billing_month == billing_month)

    invoices = query.order_by(AdvancedInvoice.due_date.asc()).all()
    monthly = defaultdict(lambda: {"billing_month": None, "count": 0, "total_billed": 0.0, "total_collected": 0.0, "outstanding": 0.0, "pending": 0, "paid": 0, "overdue": 0, "partially_paid": 0})
    summary = {
        "total_invoices": 0,
        "pending": 0,
        "paid": 0,
        "overdue": 0,
        "partially_paid": 0,
        "total_billed": 0.0,
        "total_collected": 0.0,
        "outstanding": 0.0,
    }
    overdue_items = []

    for inv in invoices:
        summary["total_invoices"] += 1
        summary["total_billed"] += inv.net_amount
        summary["total_collected"] += inv.total_paid
        summary["outstanding"] += max(0.0, inv.net_amount - inv.total_paid)
        if inv.status in summary:
            summary[inv.status] += 1

        month_data = monthly[inv.billing_month]
        month_data["billing_month"] = inv.billing_month
        month_data["count"] += 1
        month_data["total_billed"] += inv.net_amount
        month_data["total_collected"] += inv.total_paid
        month_data["outstanding"] += max(0.0, inv.net_amount - inv.total_paid)
        if inv.status in month_data:
            month_data[inv.status] += 1
        monthly[inv.billing_month] = month_data

        if inv.status == "overdue":
            overdue_items.append({
                "invoice_id": inv.id,
                "invoice_number": inv.invoice_number,
                "unit_id": inv.unit_id,
                "billing_month": inv.billing_month,
                "net_amount": inv.net_amount,
                "total_paid": inv.total_paid,
                "outstanding": float(max(0.0, inv.net_amount - inv.total_paid)),
                "due_date": inv.due_date.isoformat() if inv.due_date else None,
            })

    overdue_items.sort(key=lambda item: item["outstanding"], reverse=True)

    return {
        "summary": {k: float(v) if isinstance(v, float) else v for k, v in summary.items()},
        "monthly_breakdown": list(monthly.values()),
        "overdue_alerts": overdue_items[:5],
    }


@router.post("/invoices/import")
def import_invoices(file: UploadFile = File(...), society_id: int = Form(...), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    society_id = _required_society(current_user, society_id)
    # Accept CSV with headers: unit_id,billing_month,net_amount
    # Each row may include a "line_items" column containing JSON list of {"head_id":int,"amount":float,"quantity":int}
    # Or an "items" column with semicolon-separated entries like "head_id:amount:quantity;head_id:amount"
    try:
        stream = TextIOWrapper(file.file, encoding="utf-8")
        reader = csv.DictReader(stream)
        created = 0
        for row in reader:
            unit_id = int(row.get("unit_id") or 0)
            billing_month = row.get("billing_month")
            raw_net = row.get("net_amount") or row.get("amount")
            net_amount = float(raw_net) if raw_net else None
            # parse line items
            line_items = []
            if row.get("line_items"):
                import json
                try:
                    parsed = json.loads(row.get("line_items"))
                    for li in parsed:
                        head_id = int(li.get("head_id"))
                        amount = float(li.get("amount") or 0)
                        quantity = int(li.get("quantity") or 1)
                        line_items.append({"head_id": head_id, "amount": amount, "quantity": quantity})
                except Exception:
                    pass
            elif row.get("items"):
                # items format: head:amount:qty;head:amount
                parts = row.get("items").split(";")
                for p in parts:
                    if not p.strip():
                        continue
                    pieces = p.split(":")
                    try:
                        h = int(pieces[0])
                        a = float(pieces[1]) if len(pieces) > 1 and pieces[1] else 0
                        q = int(pieces[2]) if len(pieces) > 2 and pieces[2] else 1
                        line_items.append({"head_id": h, "amount": a, "quantity": q})
                    except Exception:
                        continue

            if not unit_id or not billing_month:
                continue

            # If no line items provided, fall back to net_amount
            if not line_items and (net_amount is None or net_amount <= 0):
                continue

            inv_no = _get_or_create_sequence(society_id, db)
            total_amount = sum(li["amount"] * (li.get("quantity", 1) or 1) for li in line_items) if line_items else (net_amount or 0)

            invoice = AdvancedInvoice(
                society_id=society_id,
                unit_id=unit_id,
                invoice_number=inv_no,
                billing_month=billing_month,
                total_amount=total_amount,
                net_amount=total_amount,
                status="pending",
                generated_by_user_id=current_user.id,
            )
            db.add(invoice)
            db.flush()

            # create line item records
            for li in line_items:
                head = db.get(BillHead, li["head_id"])
                head_name = head.name if head else f"Head {li['head_id']}"
                item = InvoiceLineItem(
                    invoice_id=invoice.id,
                    head_id=li["head_id"],
                    head_name=head_name,
                    amount=li["amount"],
                    quantity=li.get("quantity", 1) or 1,
                    total=li["amount"] * (li.get("quantity", 1) or 1),
                )
                db.add(item)
            created += 1
        db.commit()
        return {"imported": created}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to import CSV: {exc}") from exc


@router.post("/header-footer")
def save_header_footer(society_id: int, header_html: str | None = None, footer_html: str | None = None, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    society_id = _required_society(current_user, society_id)
    # Store in settings table
    from app.models.entities import Setting

    if header_html is not None:
        key = f"billing_header_{society_id}"
        s = db.query(Setting).filter(Setting.key == key).first()
        if not s:
            s = Setting(key=key, value=header_html)
            db.add(s)
        else:
            s.value = header_html

    if footer_html is not None:
        keyf = f"billing_footer_{society_id}"
        sf = db.query(Setting).filter(Setting.key == keyf).first()
        if not sf:
            sf = Setting(key=keyf, value=footer_html)
            db.add(sf)
        else:
            sf.value = footer_html

    db.commit()
    return {"status": "saved"}


@router.get("/header-footer")
def get_header_footer(society_id: int | None = Query(default=None), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    society_id = _required_society(current_user, society_id)
    from app.models.entities import Setting
    header = db.query(Setting).filter(Setting.key == f"billing_header_{society_id}").first()
    footer = db.query(Setting).filter(Setting.key == f"billing_footer_{society_id}").first()
    return {"header_html": header.value if header else None, "footer_html": footer.value if footer else None}


@router.get("/invoices/{invoice_id}/export")
def export_invoice_html(invoice_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        invoice = db.get(AdvancedInvoice, invoice_id)
        if not invoice:
                raise HTTPException(status_code=404, detail="Invoice not found")

        # Authorization: admin or society admin for same society
        if current_user.role != Role.ADMIN and not (current_user.role == Role.SOCIETY_ADMIN and current_user.society_id == invoice.society_id):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to export this invoice")

        inv_data = _get_invoice_with_items(invoice, db)

        # load header/footer
        from app.models.entities import Setting
        header = db.query(Setting).filter(Setting.key == f"billing_header_{invoice.society_id}").first()
        footer = db.query(Setting).filter(Setting.key == f"billing_footer_{invoice.society_id}").first()
        header_html = header.value if header else ""
        footer_html = footer.value if footer else ""

        # build simple invoice HTML
        items_html = ""
        for it in inv_data.get("line_items", []):
                items_html += f"<tr><td>{it['head_name']}</td><td>{it['quantity']}</td><td>{it['amount']:.2f}</td><td>{it['total']:.2f}</td></tr>"

        body = f"""
        <!doctype html>
        <html>
            <head>
                <meta charset='utf-8'/>
                <title>Invoice {inv_data.get('invoice_number')}</title>
                <style>body{{font-family: Arial, Helvetica, sans-serif; padding:20px}} table{{width:100%;border-collapse:collapse}} td,th{{border:1px solid #ddd;padding:8px}}</style>
            </head>
            <body>
                <div class='header'>{header_html}</div>
                <h2>Invoice {inv_data.get('invoice_number')}</h2>
                <div><strong>Unit:</strong> {inv_data.get('building')} {inv_data.get('unit_number')} — <strong>Resident:</strong> {inv_data.get('resident_name') or ''}</div>
                <div><strong>Billing month:</strong> {inv_data.get('billing_month')}</div>
                <table>
                    <thead><tr><th>Head</th><th>Qty</th><th>Rate</th><th>Total</th></tr></thead>
                    <tbody>
                        {items_html}
                    </tbody>
                </table>
                <div style='margin-top:12px'><strong>Net amount:</strong> {inv_data.get('net_amount')}</div>
                <div class='footer' style='margin-top:30px'>{footer_html}</div>
            </body>
        </html>
        """
        return Response(content=body, media_type="text/html")


@router.get("/invoices/export")
def export_invoices_csv(
    society_id: int | None = Query(default=None),
    status: str | None = Query(default=None),
    billing_month: str | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Export invoices as CSV for selected filters (admin/society scope enforced)"""
    scoped_society_id = _society_scope(current_user, society_id)
    query = db.query(AdvancedInvoice)
    if scoped_society_id is not None:
        query = query.filter(AdvancedInvoice.society_id == scoped_society_id)
    if status:
        query = query.filter(AdvancedInvoice.status == status)
    if billing_month:
        query = query.filter(AdvancedInvoice.billing_month == billing_month)

    invoices = query.order_by(AdvancedInvoice.created_at.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    # header
    writer.writerow([
        "id",
        "invoice_number",
        "society_id",
        "unit_id",
        "building",
        "unit_number",
        "resident_name",
        "billing_month",
        "previous_balance",
        "total_amount",
        "discount",
        "late_fee",
        "net_amount",
        "total_paid",
        "status",
        "due_date",
        "notes",
        "created_at",
        "line_items",
    ])

    for inv in invoices:
        inv_data = _get_invoice_with_items(inv, db)
        line_items_json = json.dumps(inv_data.get("line_items", []), ensure_ascii=False)
        writer.writerow([
            inv_data.get("id"),
            inv_data.get("invoice_number"),
            inv_data.get("society_id"),
            inv_data.get("unit_id"),
            inv_data.get("building"),
            inv_data.get("unit_number"),
            inv_data.get("resident_name"),
            inv_data.get("billing_month"),
            inv_data.get("previous_balance"),
            inv_data.get("total_amount"),
            inv_data.get("discount"),
            inv_data.get("late_fee"),
            inv_data.get("net_amount"),
            inv_data.get("total_paid"),
            inv_data.get("status"),
            inv_data.get("due_date"),
            (inv_data.get("notes") or ""),
            inv_data.get("created_at"),
            line_items_json,
        ])

    content = output.getvalue()
    output.close()
    headers = {"Content-Disposition": "attachment; filename=invoices.csv"}
    return Response(content=content, media_type="text/csv", headers=headers)


@router.get("/invoices/export.xlsx")
def export_invoices_xlsx(
    society_id: int | None = Query(default=None),
    status: str | None = Query(default=None),
    billing_month: str | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Export invoices as XLSX workbook with optional status and billing month filters."""
    scoped_society_id = _society_scope(current_user, society_id)
    query = db.query(AdvancedInvoice)
    if scoped_society_id is not None:
        query = query.filter(AdvancedInvoice.society_id == scoped_society_id)
    if status:
        query = query.filter(AdvancedInvoice.status == status)
    if billing_month:
        query = query.filter(AdvancedInvoice.billing_month == billing_month)

    invoices = query.order_by(AdvancedInvoice.created_at.desc()).all()

    workbook = Workbook(write_only=True)
    sheet = workbook.create_sheet(title="Invoices")
    headers = [
        "id",
        "invoice_number",
        "society_id",
        "unit_id",
        "building",
        "unit_number",
        "resident_name",
        "billing_month",
        "previous_balance",
        "total_amount",
        "discount",
        "late_fee",
        "net_amount",
        "total_paid",
        "status",
        "due_date",
        "notes",
        "created_at",
        "line_items",
    ]
    sheet.append(headers)

    for inv in invoices:
        inv_data = _get_invoice_with_items(inv, db)
        line_items_json = json.dumps(inv_data.get("line_items", []), ensure_ascii=False)
        sheet.append([
            inv_data.get("id"),
            inv_data.get("invoice_number"),
            inv_data.get("society_id"),
            inv_data.get("unit_id"),
            inv_data.get("building"),
            inv_data.get("unit_number"),
            inv_data.get("resident_name"),
            inv_data.get("billing_month"),
            inv_data.get("previous_balance"),
            inv_data.get("total_amount"),
            inv_data.get("discount"),
            inv_data.get("late_fee"),
            inv_data.get("net_amount"),
            inv_data.get("total_paid"),
            inv_data.get("status"),
            inv_data.get("due_date"),
            inv_data.get("notes"),
            inv_data.get("created_at"),
            line_items_json,
        ])

    stream = io.BytesIO()
    workbook.save(stream)
    stream.seek(0)

    def iter_xlsx():
        while True:
            chunk = stream.read(8192)
            if not chunk:
                break
            yield chunk

    headers = {"Content-Disposition": "attachment; filename=invoices.xlsx"}
    return StreamingResponse(
        iter_xlsx(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )