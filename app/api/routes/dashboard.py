from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.entities import Invoice, Payment, Ticket, VendorInvoice, VisitorLog

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/admin")
def admin_metrics(db: Session = Depends(get_db)):
    total_collected = db.query(func.coalesce(func.sum(Payment.amount), 0.0)).scalar()
    pending_dues = db.query(func.coalesce(func.sum(Invoice.total_amount), 0.0)).filter(Invoice.status == "unpaid").scalar()
    vendor_payables = db.query(func.coalesce(func.sum(VendorInvoice.amount), 0.0)).filter(VendorInvoice.status == "pending").scalar()
    open_tickets = db.query(func.count(Ticket.id)).filter(Ticket.status != "resolved").scalar()
    todays_visitors = db.query(func.count(VisitorLog.id)).scalar()

    return {
        "maintenance_collected": total_collected,
        "pending_dues": pending_dues,
        "vendor_payables": vendor_payables,
        "open_tickets": open_tickets,
        "visitor_activity": todays_visitors,
    }
