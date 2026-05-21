from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.entities import Invoice, Payment
from app.core.enums import PaymentProvider
from app.schemas.dto import CreatePaymentOrderRequest, PaymentCreate
from app.services.payment_gateways import create_payment_order, verify_webhook
from app.api.deps import get_current_user
from app.models.billing_advanced import AdvancedInvoice
from app.core.enums import Role

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


@router.get("", response_model=list[dict])
def list_payments(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    # Admin: return all payments. Society admins: payments for invoices in their society.
    if current_user.role == Role.ADMIN:
        payments = db.query(Payment).order_by(Payment.id.desc()).limit(500).all()
        return [p.__dict__ for p in payments]

    if current_user.role == Role.SOCIETY_ADMIN and current_user.society_id:
        payments = (
            db.query(Payment)
            .join(AdvancedInvoice, Payment.invoice_id == AdvancedInvoice.id)
            .filter(AdvancedInvoice.society_id == current_user.society_id)
            .order_by(Payment.id.desc())
            .limit(500)
            .all()
        )
        return [p.__dict__ for p in payments]

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view payments")


@router.get("/{payment_id}")
def get_payment(payment_id: int, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    payment = db.get(Payment, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    if current_user.role == Role.ADMIN:
        return payment

    # If society admin, ensure the payment belongs to an advanced invoice in their society
    if current_user.role == Role.SOCIETY_ADMIN and current_user.society_id:
        adv = db.get(AdvancedInvoice, payment.invoice_id)
        if adv and adv.society_id == current_user.society_id:
            return payment

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this payment")
