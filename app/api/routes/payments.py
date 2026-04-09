from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.entities import Invoice, Payment
from app.core.enums import PaymentProvider
from app.schemas.dto import CreatePaymentOrderRequest, PaymentCreate
from app.services.payment_gateways import create_payment_order, verify_webhook

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/orders")
def create_order(payload: CreatePaymentOrderRequest, db: Session = Depends(get_db)):
    invoice = db.get(Invoice, payload.invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    order = create_payment_order(payload.provider, invoice.total_amount)
    return order


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


@router.post("/webhooks/{provider}")
async def webhook_handler(
    provider: str,
    request: Request,
    x_razorpay_signature: str | None = Header(default=None),
    stripe_signature: str | None = Header(default=None, alias="stripe-signature"),
):
    raw_body = await request.body()
    signature = stripe_signature or x_razorpay_signature

    try:
        provider_enum = PaymentProvider(provider)
        result = verify_webhook(provider=provider_enum, raw_payload=raw_body, signature=signature)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {"status": "processed", "result": result}
