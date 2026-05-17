from datetime import datetime
import secrets

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.enums import Role
from app.core.security import hash_password
from app.models.entities import Society, User
from app.schemas.dto import SocietyCreate, SocietyRead, SocietyAdminContactUpdate
from app.services.notifications import send_society_admin_credentials

router = APIRouter(prefix="/societies", tags=["Societies"])


def _build_or_update_society_admin(society: Society, db: Session, contact_name: str | None, contact_email: str | None, contact_phone: str | None, password: str) -> User:
    admin_user = None
    if contact_email:
        admin_user = db.query(User).filter(User.email == contact_email).first()
    if not admin_user and contact_phone:
        admin_user = db.query(User).filter(User.phone == contact_phone).first()

    if admin_user and admin_user.society_id and admin_user.society_id != society.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contact belongs to a user attached to a different society",
        )

    if admin_user:
        admin_user.full_name = contact_name or admin_user.full_name
        if contact_email:
            admin_user.email = contact_email
        if contact_phone:
            admin_user.phone = contact_phone
    else:
        admin_user = User(
            full_name=contact_name or society.name,
            email=contact_email or f"admin+{society.id}@societyman.local",
            phone=contact_phone or f"000000{society.id}",
            role=Role.SOCIETY_ADMIN,
            society_id=society.id,
        )

    admin_user.role = Role.SOCIETY_ADMIN
    admin_user.society_id = society.id
    admin_user.password_hash = hash_password(password)
    admin_user.is_active = True
    admin_user.password_change_required = True
    admin_user.access_erp = True
    admin_user.access_gatekeeper = True
    admin_user.access_billing = True
    admin_user.access_payments = True
    admin_user.access_communications = True
    admin_user.access_reports = True
    admin_user.access_documents = True
    admin_user.access_visitor_management = True
    admin_user.full_name = contact_name or admin_user.full_name
    admin_user.email = contact_email or admin_user.email
    admin_user.phone = contact_phone or admin_user.phone

    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    send_society_admin_credentials(contact_email, contact_phone, contact_email or contact_phone or f"society_admin_{society.id}", password)
    return admin_user


@router.post("", response_model=SocietyRead)
def create_society(payload: SocietyCreate, db: Session = Depends(get_db)):
    if db.query(Society).filter(Society.name == payload.name).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Society already registered")

    society = Society(**payload.model_dump(), is_approved=False)
    db.add(society)
    db.commit()
    db.refresh(society)
    return society


@router.get("", response_model=list[SocietyRead])
def list_societies(db: Session = Depends(get_db)):
    return db.query(Society).filter(Society.is_approved.is_(True)).all()


@router.get("/pending", response_model=list[SocietyRead])
def list_pending_societies(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Developer admin access required")
    return db.query(Society).filter(Society.is_approved.is_(False)).all()


@router.post("/{society_id}/approve", response_model=SocietyRead)
def approve_society(society_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Developer admin access required")

    society = db.get(Society, society_id)
    if not society:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Society not found")

    if society.is_approved:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Society is already approved")

    if not society.admin_contact_email and not society.admin_contact_phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Society admin contact email or phone is required to create admin credentials",
        )

    society.is_approved = True
    society.approved_at = datetime.utcnow()
    db.add(society)

    admin_password = "Admin@123" if not society.admin_contact_email else secrets.token_urlsafe(10)[:12]
    _build_or_update_society_admin(
        society,
        db,
        society.admin_contact_name,
        society.admin_contact_email,
        society.admin_contact_phone,
        admin_password,
    )

    db.commit()
    db.refresh(society)
    return society


@router.patch("/{society_id}/admin-contact", response_model=SocietyRead)
def update_society_admin_contact(
    society_id: int,
    payload: SocietyAdminContactUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Developer admin access required")

    society = db.get(Society, society_id)
    if not society:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Society not found")

    update_data = {
        key: value
        for key, value in payload.model_dump(exclude_none=True).items()
        if value not in ("", None)
    }
    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No admin contact data provided")

    if "admin_contact_name" in update_data:
        society.admin_contact_name = update_data["admin_contact_name"]
    if "admin_contact_email" in update_data:
        society.admin_contact_email = update_data["admin_contact_email"]
    if "admin_contact_phone" in update_data:
        society.admin_contact_phone = update_data["admin_contact_phone"]

    if not society.admin_contact_email and not society.admin_contact_phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one admin contact value is required to update society admin details",
        )

    db.add(society)
    db.commit()
    db.refresh(society)

    _build_or_update_society_admin(
        society,
        db,
        society.admin_contact_name,
        society.admin_contact_email,
        society.admin_contact_phone,
        "Admin@123",
    )

    db.refresh(society)
    return society
