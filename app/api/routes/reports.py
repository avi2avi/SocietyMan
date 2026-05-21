import csv
import io

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response, StreamingResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.enums import Role
from app.models.expense import Expense
from app.models.billing_advanced import AdvancedInvoice
from app.models.entities import Invoice, Payment
from app.services.reporting import build_bi_pdf_report, build_bi_xlsx_report

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/outstanding-dues.csv")
def outstanding_dues_report(db: Session = Depends(get_db)):
    invoices = db.query(Invoice).filter(Invoice.status == "unpaid").all()
    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(["invoice_id", "unit_id", "billing_month", "total_amount", "status"])
    for inv in invoices:
        writer.writerow([inv.id, inv.unit_id, inv.billing_month, inv.total_amount, inv.status])

    return StreamingResponse(
        iter([out.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=outstanding_dues.csv"},
    )


@router.get("/collections.csv")
def collection_report(db: Session = Depends(get_db)):
    payments = db.query(Payment).all()
    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(["payment_id", "invoice_id", "amount", "provider", "method", "paid_at"])
    for payment in payments:
        writer.writerow(
            [
                payment.id,
                payment.invoice_id,
                payment.amount,
                payment.provider.value,
                payment.method.value,
                payment.paid_at.isoformat(),
            ]
        )

    return StreamingResponse(
        iter([out.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=collections.csv"},
    )


@router.get("/financial-summary.pdf")
def financial_summary_pdf(db: Session = Depends(get_db)):
    invoices = db.query(Invoice).all()
    rows = [(i.id, i.unit_id, i.billing_month, i.total_amount, i.status) for i in invoices]
    report = build_bi_pdf_report("Financial Summary", rows)
    return Response(
        content=report,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=financial_summary.pdf"},
    )


def _society_scope(user, requested_society_id: int | None = None) -> int | None:
    if user.role == Role.ADMIN:
        return requested_society_id
    if not user.society_id:
        raise HTTPException(status_code=403, detail="Society-scoped account required")
    if requested_society_id and requested_society_id != user.society_id:
        raise HTTPException(status_code=403, detail="Requested society is outside your scope")
    return user.society_id


@router.get("/committee-account-summary")
def committee_account_summary(
    society_id: int | None = Query(default=None),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    scoped_society_id = _society_scope(current_user, society_id)
    invoice_query = db.query(AdvancedInvoice)
    if scoped_society_id is not None:
        invoice_query = invoice_query.filter(AdvancedInvoice.society_id == scoped_society_id)

    total_billed = invoice_query.with_entities(func.coalesce(func.sum(AdvancedInvoice.net_amount), 0.0)).scalar() or 0.0
    total_collected = invoice_query.with_entities(func.coalesce(func.sum(AdvancedInvoice.total_paid), 0.0)).scalar() or 0.0
    outstanding = total_billed - total_collected
    counts = {
        "pending": invoice_query.filter(AdvancedInvoice.status == "pending").count(),
        "paid": invoice_query.filter(AdvancedInvoice.status == "paid").count(),
        "overdue": invoice_query.filter(AdvancedInvoice.status == "overdue").count(),
        "partially_paid": invoice_query.filter(AdvancedInvoice.status == "partially_paid").count(),
    }

    top_overdue = (
        invoice_query
        .filter(AdvancedInvoice.status == "overdue")
        .order_by((AdvancedInvoice.net_amount - AdvancedInvoice.total_paid).desc())
        .limit(5)
        .all()
    )

    expense_query = db.query(Expense)
    if scoped_society_id is not None:
        expense_query = expense_query.filter(Expense.society_id == scoped_society_id)

    total_expenses = expense_query.with_entities(func.coalesce(func.sum(Expense.amount), 0.0)).scalar() or 0.0
    approved_expenses = expense_query.filter(Expense.status == "approved").with_entities(func.coalesce(func.sum(Expense.amount), 0.0)).scalar() or 0.0
    pending_expenses = expense_query.filter(Expense.status == "pending").with_entities(func.coalesce(func.sum(Expense.amount), 0.0)).scalar() or 0.0

    return {
        "total_billed": float(total_billed),
        "total_collected": float(total_collected),
        "outstanding_dues": float(outstanding),
        "invoice_counts": counts,
        "total_expenses": float(total_expenses),
        "approved_expenses": float(approved_expenses),
        "pending_expenses": float(pending_expenses),
        "net_balance": float(total_collected - approved_expenses),
        "top_overdue_invoices": [
            {
                "invoice_id": inv.id,
                "invoice_number": inv.invoice_number,
                "unit_id": inv.unit_id,
                "billing_month": inv.billing_month,
                "net_amount": inv.net_amount,
                "total_paid": inv.total_paid,
                "outstanding": float(inv.net_amount - inv.total_paid),
            }
            for inv in top_overdue
        ],
    }


@router.get("/financial-summary.xlsx")
def financial_summary_xlsx(db: Session = Depends(get_db)):
    invoices = db.query(Invoice).all()
    rows = [(i.id, i.unit_id, i.billing_month, i.total_amount, i.status) for i in invoices]
    report = build_bi_xlsx_report(
        "Financial Summary",
        headers=["Invoice ID", "Unit ID", "Month", "Amount", "Status"],
        rows=rows,
    )
    return Response(
        content=report,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=financial_summary.xlsx"},
    )
