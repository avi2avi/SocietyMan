from fastapi import APIRouter, Depends, Query
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


@router.get("")
def list_units(unit_type: str | None = Query(default=None), db: Session = Depends(get_db)):
    query = db.query(Unit)
    if unit_type:
        query = query.filter(Unit.unit_type == unit_type)
    return query.order_by(Unit.building, Unit.unit_number).all()
