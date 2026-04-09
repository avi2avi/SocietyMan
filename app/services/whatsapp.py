from app.core.config import settings
from app.core.enums import WhatsAppProvider


def send_whatsapp_message(provider: WhatsAppProvider, to_phone: str, message: str) -> dict:
    if provider == WhatsAppProvider.META:
        return {
            "provider": provider.value,
            "status": "queued",
            "channel_id": settings.whatsapp_meta_phone_id,
            "to": to_phone,
            "preview": message[:80],
        }

    if provider == WhatsAppProvider.TWILIO:
        return {
            "provider": provider.value,
            "status": "queued",
            "sid_hint": settings.twilio_account_sid[:6],
            "to": to_phone,
            "preview": message[:80],
        }

    return {
        "provider": provider.value,
        "status": "queued",
        "app": settings.gupshup_app_name,
        "to": to_phone,
        "preview": message[:80],
    }
