import csv
import io

from fastapi import APIRouter, Depends
from fastapi.responses import Response, StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
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
