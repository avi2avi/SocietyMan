from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.entities import Ticket
from app.schemas.dto import TicketCreate, TicketUpdateStatus
from app.services.notifications import notify_ticket_update

router = APIRouter(prefix="/tickets", tags=["Tickets"])


@router.post("")
def create_ticket(payload: TicketCreate, db: Session = Depends(get_db)):
    ticket = Ticket(**payload.model_dump())
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


@router.patch("/{ticket_id}/status")
def update_ticket_status(ticket_id: int, payload: TicketUpdateStatus, db: Session = Depends(get_db)):
    ticket = db.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    ticket.status = payload.status
    ticket.assigned_vendor_id = payload.assigned_vendor_id
    db.commit()
    db.refresh(ticket)
    notify_ticket_update(ticket.resident_user_id, ticket.id, ticket.status.value)
    return ticket
