from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.entities import VisitorLog
from app.schemas.dto import VisitorEntryCreate
from app.services.notifications import notify_visitor_arrival

router = APIRouter(prefix="/visitors", tags=["Visitors"])


@router.post("/entry")
def log_visitor_entry(payload: VisitorEntryCreate, db: Session = Depends(get_db)):
    visitor = VisitorLog(**payload.model_dump())
    db.add(visitor)
    db.commit()
    db.refresh(visitor)
    notify_visitor_arrival(visitor.resident_user_id, visitor.visitor_name)
    return visitor


@router.post("/exit/{visitor_id}")
def log_visitor_exit(visitor_id: int, db: Session = Depends(get_db)):
    visitor = db.get(VisitorLog, visitor_id)
    if not visitor:
        raise HTTPException(status_code=404, detail="Visitor log not found")
    visitor.exit_at = datetime.utcnow()
    db.commit()
    db.refresh(visitor)
    return visitor
