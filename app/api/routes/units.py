from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.entities import Unit
from app.schemas.dto import UnitCreate

router = APIRouter(prefix="/units", tags=["Units"])


@router.post("")
def create_unit(payload: UnitCreate, db: Session = Depends(get_db)):
    unit = Unit(**payload.model_dump())
    db.add(unit)
    db.commit()
    db.refresh(unit)
    return unit
