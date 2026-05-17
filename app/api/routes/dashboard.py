from urllib.parse import urlparse

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_role
from app.core.config import settings
from app.core.database import get_db
from app.core.enums import Role
from app.models.entities import (
    Invoice,
    Payment,
    Ticket,
    VendorInvoice,
    VisitorLog,
    User,
    Society,
    Vendor,
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def _mask_db_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.password:
        return url.replace(parsed.password, "***")
    return url


@router.get("/admin")
def admin_metrics(
    current_role: Role = Depends(get_current_role),
    db: Session = Depends(get_db),
):
    if current_role != Role.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
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


@router.get("/admin/summary")
def admin_summary(
    current_role: Role = Depends(get_current_role),
    db: Session = Depends(get_db),
):
    if current_role != Role.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    total_societies = db.query(func.count(Society.id)).scalar()
    approved_societies = db.query(func.count(Society.id)).filter(Society.is_approved.is_(True)).scalar()
    pending_societies = db.query(func.count(Society.id)).filter(Society.is_approved.is_(False)).scalar()
    total_users = db.query(func.count(User.id)).scalar()
    active_users = db.query(func.count(User.id)).filter(User.is_active.is_(True)).scalar()
    inactive_users = db.query(func.count(User.id)).filter(User.is_active.is_(False)).scalar()
    total_vendors = db.query(func.count(Vendor.id)).scalar()
    open_tickets = db.query(func.count(Ticket.id)).filter(Ticket.status != "resolved").scalar()
    total_visitors = db.query(func.count(VisitorLog.id)).scalar()

    return {
        "total_societies": total_societies,
        "approved_societies": approved_societies,
        "pending_societies": pending_societies,
        "total_users": total_users,
        "active_users": active_users,
        "inactive_users": inactive_users,
        "total_vendors": total_vendors,
        "open_tickets": open_tickets,
        "total_visitors": total_visitors,
    }


@router.get("/admin/users")
def admin_users(
    current_role: Role = Depends(get_current_role),
    db: Session = Depends(get_db),
):
    if current_role != Role.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    users = db.query(User).all()
    return [
        {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role.value,
            "society_id": user.society_id,
            "is_active": user.is_active,
            "access_erp": user.access_erp,
            "access_gatekeeper": user.access_gatekeeper,
            "access_billing": user.access_billing,
            "access_payments": user.access_payments,
            "access_communications": user.access_communications,
            "access_reports": user.access_reports,
            "access_documents": user.access_documents,
            "access_visitor_management": user.access_visitor_management,
            "created_at": user.created_at.isoformat(),
        }
        for user in users
    ]


@router.get("/admin/societies")
def admin_societies(
    current_role: Role = Depends(get_current_role),
    db: Session = Depends(get_db),
):
    if current_role != Role.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    societies = db.query(Society).all()
    return [
        {
            "id": society.id,
            "name": society.name,
            "city": society.city,
            "state": society.state,
            "is_approved": society.is_approved,
            "created_at": society.created_at.isoformat(),
            "approved_at": society.approved_at.isoformat() if society.approved_at else None,
        }
        for society in societies
    ]


@router.get("/admin/db-info")
def admin_db_info(
    current_role: Role = Depends(get_current_role),
):
    if current_role != Role.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    db_url = settings.database_url
    info = {"database_type": "sqlite" if db_url.startswith("sqlite") else "database"}
    if db_url.startswith("sqlite"):
        info["database_file"] = db_url.replace("sqlite:///", "")
    else:
        info["database_url"] = _mask_db_url(db_url)
    return info
