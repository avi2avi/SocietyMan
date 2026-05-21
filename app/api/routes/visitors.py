from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.enums import Role
from app.models.entities import VisitorLog, User
from app.schemas.dto import VisitorEntryCreate
from app.services.notifications import notify_visitor_arrival

router = APIRouter(prefix="/visitors", tags=["Visitors"])


def _authorize_for_resident_action(current_user: User, resident_user_id: int, db: Session) -> None:
    resident = db.get(User, resident_user_id)
    if not resident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resident not found")

    # Admins can act across societies
    if current_user.role == Role.ADMIN:
        return

    # Society admins can act for residents in their society
    if current_user.role == Role.SOCIETY_ADMIN and current_user.society_id == resident.society_id:
        return

    # Gatekeepers can act for residents in their society
    if current_user.role == Role.GATEKEEPER and current_user.society_id == resident.society_id:
        return

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized for this resident")


@router.post("/entry")
def log_visitor_entry(payload: VisitorEntryCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Only admin, society_admin, and gatekeeper can create visitor entries
    if current_user.role not in (Role.ADMIN, Role.SOCIETY_ADMIN, Role.GATEKEEPER):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to log visitor entries")

    _authorize_for_resident_action(current_user, payload.resident_user_id, db)

    visitor = VisitorLog(**payload.model_dump())
    db.add(visitor)
    db.commit()
    db.refresh(visitor)
    try:
        notify_visitor_arrival(visitor.resident_user_id, visitor.visitor_name)
    except Exception:
        pass
    return visitor


@router.post("/exit/{visitor_id}")
def log_visitor_exit(visitor_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    visitor = db.get(VisitorLog, visitor_id)
    if not visitor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Visitor log not found")

    _authorize_for_resident_action(current_user, visitor.resident_user_id, db)

    visitor.exit_at = datetime.utcnow()
    db.commit()
    db.refresh(visitor)
    return visitor


@router.patch("/{visitor_id}")
def update_visitor(visitor_id: int, payload: VisitorEntryCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    visitor = db.get(VisitorLog, visitor_id)
    if not visitor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Visitor log not found")

    # Authorization based on resident linked to the visitor
    _authorize_for_resident_action(current_user, visitor.resident_user_id, db)

    updates = payload.model_dump(exclude_none=True)
    for field, value in updates.items():
        setattr(visitor, field, value)

    db.add(visitor)
    db.commit()
    db.refresh(visitor)
    return visitor
