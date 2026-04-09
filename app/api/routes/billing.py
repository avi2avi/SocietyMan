from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.entities import Invoice, Unit
from app.schemas.dto import MonthlyBillingRequest

router = APIRouter(prefix="/billing", tags=["Billing"])


@router.post("/invoices/generate-monthly")
def generate_monthly_invoices(payload: MonthlyBillingRequest, db: Session = Depends(get_db)):
    units = db.query(Unit).all()
    created = []
    for unit in units:
        parking_charge = (
            unit.parking_car_slots * payload.car_slot_rate
            + unit.parking_bike_slots * payload.bike_slot_rate
        )
        total = (
            payload.maintenance_charge
            + parking_charge
            + payload.special_levy
            + payload.late_penalty
        )
        invoice = Invoice(
            unit_id=unit.id,
            billing_month=payload.billing_month,
            maintenance_charge=payload.maintenance_charge,
            parking_charge=parking_charge,
            special_levy=payload.special_levy,
            late_penalty=payload.late_penalty,
            total_amount=total,
        )
        db.add(invoice)
        created.append(invoice)
    db.commit()
    return {"created_count": len(created)}
