from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.enums import Role
from app.models.entities import Society, User
from app.schemas.dto import SocietyCreate, SocietyRead

router = APIRouter(prefix="/societies", tags=["Societies"])


@router.post("", response_model=SocietyRead)
def create_society(payload: SocietyCreate, db: Session = Depends(get_db)):
    if db.query(Society).filter(Society.name == payload.name).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Society already registered")

    society = Society(**payload.model_dump(), is_approved=False)
    db.add(society)
    db.commit()
    db.refresh(society)
    return society


@router.get("", response_model=list[SocietyRead])
def list_societies(db: Session = Depends(get_db)):
    return db.query(Society).filter(Society.is_approved.is_(True)).all()


@router.get("/pending", response_model=list[SocietyRead])
def list_pending_societies(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Developer admin access required")
    return db.query(Society).filter(Society.is_approved.is_(False)).all()


@router.post("/{society_id}/approve", response_model=SocietyRead)
def approve_society(society_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Developer admin access required")

    society = db.get(Society, society_id)
    if not society:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Society not found")
    society.is_approved = True
    society.approved_at = datetime.utcnow()
    db.add(society)
    db.commit()
    db.refresh(society)
    return society
