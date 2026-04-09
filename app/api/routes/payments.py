from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.entities import Invoice, Payment
from app.schemas.dto import PaymentCreate

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("")
def add_payment(payload: PaymentCreate, db: Session = Depends(get_db)):
    invoice = db.get(Invoice, payload.invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    payment = Payment(**payload.model_dump())
    db.add(payment)

    if payload.amount >= invoice.total_amount:
        invoice.status = "paid"

    db.commit()
    db.refresh(payment)
    return payment
