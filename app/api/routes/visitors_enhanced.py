"""
Enhanced Visitor Management with pre-approval and vehicle tracking
Society360 Integration
"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.enums import Role, VisitorType
from app.models.entities import VisitorApproval, VisitorLog, User
from app.schemas.dto import (
    VisitorApprovalCreate,
    VisitorApprovalRead,
    VisitorApprovalUpdate,
    VisitorEntryCreate,
)

router = APIRouter(prefix="/visitors/enhanced", tags=["Visitors Enhanced"])


# ============================================================
# VISITOR PRE-REGISTRATION & APPROVAL
# ============================================================


@router.post("/pre-register", response_model=VisitorApprovalRead)
def pre_register_visitor(
    payload: VisitorApprovalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Pre-register a visitor for approval"""
    # Get the visitor log
    visitor_log = db.get(VisitorLog, payload.visitor_log_id)
    if not visitor_log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Visitor log not found")

    # Check if approval already exists
    existing = db.query(VisitorApproval).filter(
        VisitorApproval.visitor_log_id == payload.visitor_log_id
    ).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Approval already exists for this visitor")

    approval = VisitorApproval(
        resident_user_id=visitor_log.resident_user_id,
        **payload.model_dump()
    )
    db.add(approval)
    db.commit()
    db.refresh(approval)
    return approval


@router.get("/pending-approvals", response_model=list[VisitorApprovalRead])
def list_pending_approvals(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List pending visitor approvals for the resident or admin"""
    query = db.query(VisitorApproval).filter(
        VisitorApproval.approval_status == "pending"
    )

    if current_user.role == Role.RESIDENT:
        # Only show resident's pending approvals
        query = query.filter(VisitorApproval.resident_user_id == current_user.id)
    elif current_user.role == Role.SOCIETY_ADMIN:
        # Show all pending approvals in the society
        from app.models.entities import ResidentProfile, Unit
        society_residents = db.query(User.id).filter(
            User.society_id == current_user.society_id
        ).subquery()
        query = query.filter(VisitorApproval.resident_user_id.in_(society_residents))
    elif current_user.role != Role.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    return query.all()


@router.patch("/approvals/{approval_id}", response_model=VisitorApprovalRead)
def approve_visitor(
    approval_id: int,
    payload: VisitorApprovalUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Approve or reject a visitor"""
    approval = db.get(VisitorApproval, approval_id)
    if not approval:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval not found")

    # Authorization: resident, society admin, or platform admin
    if current_user.role == Role.RESIDENT and approval.resident_user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    elif current_user.role == Role.SOCIETY_ADMIN:
        resident = db.get(User, approval.resident_user_id)
        if resident.society_id != current_user.society_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    # Update approval
    approval.approval_status = payload.approval_status
    if payload.vehicle_number:
        approval.vehicle_number = payload.vehicle_number
    if payload.vehicle_type:
        approval.vehicle_type = payload.vehicle_type
    if payload.parking_slot:
        approval.parking_slot = payload.parking_slot
    if payload.rejection_reason:
        approval.rejection_reason = payload.rejection_reason

    if payload.approval_status == "approved":
        approval.approved_by_user_id = current_user.id
        approval.approved_at = datetime.utcnow()
        # Generate pass number
        import uuid
        approval.pass_number = f"PASS-{uuid.uuid4().hex[:8].upper()}"

    db.commit()
    db.refresh(approval)
    return approval


@router.get("/approvals/{approval_id}")
def get_approval(
    approval_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get visitor approval details"""
    approval = db.get(VisitorApproval, approval_id)
    if not approval:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval not found")

    # Authorization check
    if current_user.role == Role.RESIDENT and approval.resident_user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    return VisitorApprovalRead.model_validate(approval)


# ============================================================
# VISITOR HISTORY & ANALYTICS
# ============================================================


@router.get("/history", response_model=list[dict])
def get_visitor_history(
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get visitor history for a resident or society"""
    query = db.query(VisitorLog)

    # Parse dates if provided
    start = None
    end = None
    if start_date:
        try:
            start = datetime.fromisoformat(start_date)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid start_date format")

    if end_date:
        try:
            end = datetime.fromisoformat(end_date)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid end_date format")

    if current_user.role == Role.RESIDENT:
        query = query.filter(VisitorLog.resident_user_id == current_user.id)
    elif current_user.role == Role.SOCIETY_ADMIN:
        # Filter by society residents
        society_residents = db.query(User.id).filter(
            User.society_id == current_user.society_id
        ).subquery()
        query = query.filter(VisitorLog.resident_user_id.in_(society_residents))

    if start:
        query = query.filter(VisitorLog.entry_at >= start)
    if end:
        query = query.filter(VisitorLog.entry_at <= end)

    visitors = query.order_by(VisitorLog.entry_at.desc()).all()

    # Format response with approval details
    result = []
    for visitor in visitors:
        approval = db.query(VisitorApproval).filter(
            VisitorApproval.visitor_log_id == visitor.id
        ).first()

        visitor_data = {
            "id": visitor.id,
            "name": visitor.visitor_name,
            "phone": visitor.visitor_phone,
            "type": visitor.visitor_type,
            "purpose": visitor.purpose,
            "entry_at": visitor.entry_at,
            "exit_at": visitor.exit_at,
            "approval": {
                "status": approval.approval_status if approval else None,
                "vehicle": f"{approval.vehicle_type}: {approval.vehicle_number}" if approval and approval.vehicle_number else None,
                "parking_slot": approval.parking_slot if approval else None,
                "pass_number": approval.pass_number if approval else None,
            } if approval else None,
        }
        result.append(visitor_data)

    return result


@router.get("/analytics")
def get_visitor_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get visitor analytics for society or platform"""
    if current_user.role not in (Role.ADMIN, Role.SOCIETY_ADMIN):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    query = db.query(VisitorLog)

    if current_user.role == Role.SOCIETY_ADMIN:
        # Filter by society residents
        society_residents = db.query(User.id).filter(
            User.society_id == current_user.society_id
        ).subquery()
        query = query.filter(VisitorLog.resident_user_id.in_(society_residents))

    total_visits = query.count()

    # Count by type
    from sqlalchemy import func
    type_counts = db.query(
        VisitorLog.visitor_type,
        func.count(VisitorLog.id).label("count")
    ).group_by(VisitorLog.visitor_type).all()

    # Count approvals
    approval_query = db.query(VisitorApproval)
    if current_user.role == Role.SOCIETY_ADMIN:
        society_residents = db.query(User.id).filter(
            User.society_id == current_user.society_id
        ).subquery()
        approval_query = approval_query.filter(
            VisitorApproval.resident_user_id.in_(society_residents)
        )

    approved = approval_query.filter(
        VisitorApproval.approval_status == "approved"
    ).count()
    rejected = approval_query.filter(
        VisitorApproval.approval_status == "rejected"
    ).count()
    pending = approval_query.filter(
        VisitorApproval.approval_status == "pending"
    ).count()

    return {
        "total_visits": total_visits,
        "visits_by_type": [{"type": t[0], "count": t[1]} for t in type_counts],
        "approvals": {
            "approved": approved,
            "rejected": rejected,
            "pending": pending,
            "approval_rate": (approved / (approved + rejected) * 100) if (approved + rejected) > 0 else 0,
        },
    }


# ============================================================
# VISITOR PASS GENERATION
# ============================================================


@router.get("/passes/{approval_id}")
def get_visitor_pass(
    approval_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get QR pass for an approved visitor"""
    approval = db.get(VisitorApproval, approval_id)
    if not approval:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval not found")

    if approval.approval_status != "approved":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Visitor not approved")

    # Authorization
    if current_user.role == Role.RESIDENT and approval.resident_user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    visitor = db.get(VisitorLog, approval.visitor_log_id)

    return {
        "pass_number": approval.pass_number,
        "visitor_name": visitor.visitor_name,
        "visitor_phone": visitor.visitor_phone,
        "vehicle": f"{approval.vehicle_type}: {approval.vehicle_number}" if approval.vehicle_number else None,
        "parking_slot": approval.parking_slot,
        "valid_from": visitor.entry_at,
        "valid_until": visitor.exit_at or (visitor.entry_at.replace(day=visitor.entry_at.day + 1) if visitor.entry_at else None),
        "qr_data": f"PASS|{approval.pass_number}|{approval.resident_user_id}",
    }
