import hashlib
import hmac
import uuid

import stripe

from app.core.config import settings
from app.core.enums import PaymentProvider

stripe.api_key = settings.stripe_secret_key or None


def create_payment_order(provider: PaymentProvider, amount: float, currency: str = "INR") -> dict:
    if provider == PaymentProvider.RAZORPAY:
        return {
            "provider": provider.value,
            "order_id": f"order_{uuid.uuid4().hex[:16]}",
            "amount": int(amount * 100),
            "currency": currency,
            "key_id": settings.razorpay_key_id,
        }

    intent = stripe.PaymentIntent.create(
        amount=int(amount * 100),
        currency=currency.lower(),
        automatic_payment_methods={"enabled": True},
    )
    return {
        "provider": provider.value,
        "order_id": intent.id,
        "client_secret": intent.client_secret,
        "amount": intent.amount,
        "currency": intent.currency,
    }


def verify_webhook(provider: PaymentProvider, raw_payload: bytes, signature: str | None) -> dict:
    if provider == PaymentProvider.STRIPE:
        if not settings.stripe_webhook_secret:
            raise ValueError("Stripe webhook secret is not configured")
        event = stripe.Webhook.construct_event(raw_payload, signature, settings.stripe_webhook_secret)
        return event

    if not settings.razorpay_webhook_secret:
        raise ValueError("Razorpay webhook secret is not configured")
    digest = hmac.new(
        settings.razorpay_webhook_secret.encode(), raw_payload, hashlib.sha256
    ).hexdigest()
    if not hmac.compare_digest(digest, signature or ""):
        raise ValueError("Invalid Razorpay webhook signature")
    return {"verified": True}
