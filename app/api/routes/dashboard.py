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
    Unit,
    ResidentProfile,
    VendorInvoice,
    VisitorLog,
    GatePass,
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


@router.get("/admin/units")
def admin_units(
    current_role: Role = Depends(get_current_role),
    db: Session = Depends(get_db),
):
    if current_role != Role.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    total_units = db.query(func.count(Unit.id)).scalar()
    total_resident_profiles = db.query(func.count(ResidentProfile.id)).scalar()
    total_residents = db.query(func.count(User.id)).filter(User.role == Role.RESIDENT).scalar()
    occupied_units = total_resident_profiles
    unoccupied_units = max(total_units - occupied_units, 0)

    return {
        "total_units": total_units,
        "occupied_units": occupied_units,
        "unoccupied_units": unoccupied_units,
        "total_residents": total_residents,
    }


@router.get("/admin/ledger")
def admin_ledger(
    current_role: Role = Depends(get_current_role),
    db: Session = Depends(get_db),
):
    if current_role != Role.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    total_income = db.query(func.coalesce(func.sum(Payment.amount), 0.0)).scalar()
    pending_dues = db.query(func.coalesce(func.sum(Invoice.total_amount), 0.0)).filter(Invoice.status == "unpaid").scalar()
    vendor_payables = db.query(func.coalesce(func.sum(VendorInvoice.amount), 0.0)).filter(VendorInvoice.status != "paid").scalar()
    vendor_expenses = db.query(func.coalesce(func.sum(VendorInvoice.amount), 0.0)).scalar()
    bank_cash = total_income - vendor_payables
    ledger_balance = total_income - vendor_expenses
    utility_spend = db.query(func.coalesce(func.sum(VendorInvoice.amount), 0.0)).filter(VendorInvoice.description.ilike("%utility%",)).scalar()
    vendor_invoices = db.query(func.count(VendorInvoice.id)).scalar()

    return {
        "total_income": total_income,
        "pending_dues": pending_dues,
        "vendor_payables": vendor_payables,
        "vendor_expenses": vendor_expenses,
        "bank_cash": bank_cash,
        "ledger_balance": ledger_balance,
        "utility_spend": utility_spend,
        "vendor_invoices": vendor_invoices,
    }


@router.get("/admin/tickets")
def admin_tickets(
    current_role: Role = Depends(get_current_role),
    db: Session = Depends(get_db),
):
    if current_role != Role.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    tickets = db.query(Ticket).order_by(Ticket.created_at.desc()).limit(200).all()
    results = []
    for ticket in tickets:
        resident = db.get(User, ticket.resident_user_id)
        vendor = db.get(Vendor, ticket.assigned_vendor_id) if ticket.assigned_vendor_id else None
        results.append(
            {
                "id": ticket.id,
                "title": ticket.title,
                "description": ticket.description,
                "status": ticket.status.value if hasattr(ticket.status, "value") else str(ticket.status),
                "assigned_vendor": vendor.name if vendor else None,
                "resident_name": resident.full_name if resident else None,
                "created_at": ticket.created_at.isoformat(),
            }
        )

    return results


@router.get("/admin/gatekeeper")
def admin_gatekeeper(
    current_role: Role = Depends(get_current_role),
    db: Session = Depends(get_db),
):
    if current_role != Role.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    visitors_today = db.query(func.count(VisitorLog.id)).scalar()
    active_gate_passes = db.query(func.count(GatePass.id)).filter(GatePass.status == "issued").scalar()
    return {
        "visitors_today": visitors_today,
        "active_gate_passes": active_gate_passes,
        "open_tickets": db.query(func.count(Ticket.id)).filter(Ticket.status != "resolved").scalar(),
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
    if db_url.startswith("sqlite"):
        database_type = "sqlite"
    elif db_url.startswith("postgresql"):
        database_type = "postgresql"
    else:
        database_type = "database"
    info = {"database_type": database_type}
    if db_url.startswith("sqlite"):
        info["database_file"] = db_url.replace("sqlite:///", "")
    else:
        info["database_url"] = _mask_db_url(db_url)
    return info
