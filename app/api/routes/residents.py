from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.entities import ResidentProfile
from app.schemas.dto import ResidentCreate

router = APIRouter(prefix="/residents", tags=["Residents"])


@router.post("")
def assign_resident(payload: ResidentCreate, db: Session = Depends(get_db)):
    profile = ResidentProfile(**payload.model_dump())
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile
