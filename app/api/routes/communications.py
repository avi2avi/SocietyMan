from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.enums import WhatsAppProvider
from app.models.entities import User, WhatsAppMessageLog
from app.schemas.dto import WhatsAppMessageRequest
from app.services.whatsapp import send_whatsapp_message

router = APIRouter(prefix="/communications", tags=["Communications"])


@router.post("/whatsapp/send")
def send_whatsapp(payload: WhatsAppMessageRequest, db: Session = Depends(get_db)):
    user = db.get(User, payload.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    provider = payload.provider or WhatsAppProvider(settings.whatsapp_provider)
    response = send_whatsapp_message(provider=provider, to_phone=user.phone, message=payload.message)

    log = WhatsAppMessageLog(
        user_id=user.id,
        provider=provider,
        message_body=payload.message,
        status=response.get("status", "queued"),
        external_message_id=response.get("message_id"),
    )
    db.add(log)
    db.commit()
    return {"message": response, "log_id": log.id}
