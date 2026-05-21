"""
Enhanced Maintenance & Complaint Management with Society360 features
Includes: Categories, Work logs, Ratings, Priority-based workflows
"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.enums import Role, TicketStatus
from app.models.entities import (
    MaintenanceCategory,
    MaintenanceWorkLog,
    MaintenanceRating,
    Ticket,
    User,
)
from app.schemas.dto import (
    MaintenanceCategoryCreate,
    MaintenanceCategoryRead,
    MaintenanceWorkLogCreate,
    MaintenanceWorkLogRead,
    MaintenanceRatingCreate,
    MaintenanceRatingRead,
    TicketCreate,
)

router = APIRouter(prefix="/maintenance", tags=["Maintenance Enhanced"])


# ============================================================
# MAINTENANCE CATEGORIES
# ============================================================


@router.post("/categories", response_model=MaintenanceCategoryRead)
def create_category(
    payload: MaintenanceCategoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new maintenance category (Admin/Society Admin only)"""
    if current_user.role not in (Role.ADMIN, Role.SOCIETY_ADMIN):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    society_id = current_user.society_id if current_user.role == Role.SOCIETY_ADMIN else None
    if not society_id and current_user.role == Role.SOCIETY_ADMIN:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Society ID required")

    category = MaintenanceCategory(
        society_id=society_id,
        **payload.model_dump()
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.get("/categories", response_model=list[MaintenanceCategoryRead])
def list_categories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all maintenance categories for user's society"""
    if current_user.role not in (Role.ADMIN, Role.SOCIETY_ADMIN, Role.RESIDENT, Role.GATEKEEPER):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    query = db.query(MaintenanceCategory).filter(MaintenanceCategory.is_active == True)

    if current_user.role == Role.SOCIETY_ADMIN:
        query = query.filter(MaintenanceCategory.society_id == current_user.society_id)
    elif current_user.role == Role.RESIDENT:
        # Get resident's society through their unit/profile
        from app.models.entities import ResidentProfile
        profile = db.query(ResidentProfile).filter(ResidentProfile.user_id == current_user.id).first()
        if profile:
            from app.models.entities import Unit
            unit = db.get(Unit, profile.unit_id)
            if unit and unit.society_id:
                query = query.filter(MaintenanceCategory.society_id == unit.society_id)

    return query.order_by(MaintenanceCategory.sort_order).all()


# ============================================================
# WORK LOGS
# ============================================================


@router.post("/{ticket_id}/work-logs", response_model=MaintenanceWorkLogRead)
def add_work_log(
    ticket_id: int,
    payload: MaintenanceWorkLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add a work log entry to a maintenance ticket"""
    ticket = db.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    # Authorization: staff/vendor or admin can add work logs
    if current_user.role not in (Role.ADMIN, Role.SOCIETY_ADMIN):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    work_log = MaintenanceWorkLog(**payload.model_dump())
    db.add(work_log)
    db.commit()
    db.refresh(work_log)
    return work_log


@router.get("/{ticket_id}/work-logs", response_model=list[MaintenanceWorkLogRead])
def get_work_logs(
    ticket_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all work logs for a maintenance ticket"""
    ticket = db.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    # Authorization check
    if current_user.role == Role.RESIDENT and ticket.resident_user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    logs = db.query(MaintenanceWorkLog).filter(
        MaintenanceWorkLog.ticket_id == ticket_id
    ).order_by(desc(MaintenanceWorkLog.created_at)).all()

    return logs


# ============================================================
# RATINGS & FEEDBACK
# ============================================================


@router.post("/{ticket_id}/rate", response_model=MaintenanceRatingRead)
def rate_ticket(
    ticket_id: int,
    payload: MaintenanceRatingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Rate and provide feedback on a completed maintenance ticket"""
    ticket = db.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    # Only resident who created the ticket can rate it
    if ticket.resident_user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    # Check if already rated
    existing_rating = db.query(MaintenanceRating).filter(
        MaintenanceRating.ticket_id == ticket_id
    ).first()
    if existing_rating:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ticket already rated")

    # Validate rating
    if not 1 <= payload.rating <= 5:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Rating must be between 1 and 5")

    rating = MaintenanceRating(
        ticket_id=ticket_id,
        rating=payload.rating,
        feedback=payload.feedback,
        rated_by_user_id=current_user.id,
    )
    db.add(rating)
    db.commit()
    db.refresh(rating)
    return rating


@router.get("/{ticket_id}/rating", response_model=MaintenanceRatingRead | None)
def get_ticket_rating(
    ticket_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get rating and feedback for a maintenance ticket"""
    ticket = db.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    rating = db.query(MaintenanceRating).filter(
        MaintenanceRating.ticket_id == ticket_id
    ).first()

    return rating


# ============================================================
# ANALYTICS & REPORTING
# ============================================================


@router.get("/analytics/summary")
def get_maintenance_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get maintenance analytics for the society/platform"""
    if current_user.role not in (Role.ADMIN, Role.SOCIETY_ADMIN):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    # Build query based on role
    query = db.query(Ticket)

    if current_user.role == Role.SOCIETY_ADMIN:
        from app.models.entities import ResidentProfile, Unit, User as UserModel
        # Filter by society residents
        society_residents = db.query(UserModel.id).filter(
            UserModel.society_id == current_user.society_id
        ).subquery()
        query = query.filter(Ticket.resident_user_id.in_(society_residents))

    # Calculate stats
    total_tickets = query.count()
    open_tickets = query.filter(Ticket.status == TicketStatus.OPEN).count()
    in_progress = query.filter(Ticket.status == TicketStatus.IN_PROGRESS).count()
    resolved = query.filter(Ticket.status == TicketStatus.RESOLVED).count()

    # Get average rating
    avg_rating = db.query(func.avg(MaintenanceRating.rating)).first()[0]

    # Get most common categories
    from sqlalchemy import func
    top_categories = db.query(
        MaintenanceCategory.name,
        func.count(Ticket.id).label("count")
    ).join(
        Ticket, Ticket.id == MaintenanceWorkLog.ticket_id
    ).group_by(
        MaintenanceCategory.name
    ).order_by(desc("count")).limit(5).all()

    return {
        "total_tickets": total_tickets,
        "open": open_tickets,
        "in_progress": in_progress,
        "resolved": resolved,
        "resolution_rate": (resolved / total_tickets * 100) if total_tickets > 0 else 0,
        "average_rating": float(avg_rating) if avg_rating else 0,
        "top_categories": [{"name": cat[0], "count": cat[1]} for cat in top_categories],
    }
