from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.entities import Invoice, ResidentProfile, Unit, User


def schedule_monthly_billing(ctx: dict) -> dict:
    db: Session = ctx["db"]
    billing_month = datetime.utcnow().strftime("%Y-%m")
    units = db.query(Unit).all()
    created = 0
    for unit in units:
        existing = (
            db.query(Invoice)
            .filter(Invoice.unit_id == unit.id, Invoice.billing_month == billing_month)
            .first()
        )
        if existing:
            continue
        total = 3000 + unit.parking_car_slots * 500 + unit.parking_bike_slots * 150
        db.add(
            Invoice(
                unit_id=unit.id,
                billing_month=billing_month,
                maintenance_charge=3000,
                parking_charge=unit.parking_car_slots * 500 + unit.parking_bike_slots * 150,
                total_amount=total,
            )
        )
        created += 1
    db.commit()
    return {"created": created, "billing_month": billing_month}


def send_payment_reminders(ctx: dict) -> dict:
    db: Session = ctx["db"]
    due_users = (
        db.query(func.count(User.id))
        .join(ResidentProfile, ResidentProfile.user_id == User.id)
        .join(Invoice, Invoice.unit_id == ResidentProfile.unit_id)
        .filter(Invoice.status == "unpaid")
        .scalar()
    )
    return {"reminders_enqueued": due_users or 0}


class WorkerSettings:
    functions = [schedule_monthly_billing, send_payment_reminders]
