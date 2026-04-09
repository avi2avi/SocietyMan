import csv
import io

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.entities import Invoice, Payment

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
    writer.writerow(["payment_id", "invoice_id", "amount", "method", "paid_at"])
    for payment in payments:
        writer.writerow([payment.id, payment.invoice_id, payment.amount, payment.method.value, payment.paid_at.isoformat()])

    return StreamingResponse(
        iter([out.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=collections.csv"},
    )
