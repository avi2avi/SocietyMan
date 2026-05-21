import secrets
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.enums import Role
from app.core.security import hash_password
from app.models.entities import Society, User
from app.schemas.dto import UserCreate, UserRead, UserAccessUpdate, UserUpdate
from app.services.notifications import send_society_admin_credentials

router = APIRouter(prefix="/users", tags=["Users"])


def _create_user(payload: UserCreate, db: Session) -> User:
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")

    if payload.role in (Role.RESIDENT, Role.SOCIETY_ADMIN):
        society = db.get(Society, payload.society_id)
        if not society or not society.is_approved:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Society must be registered and approved before user signup")

    data = payload.model_dump(exclude={"password"})
    is_active = True if payload.role != Role.RESIDENT else False
    user = User(**data, password_hash=hash_password(payload.password), is_active=is_active)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("")
def create_user(payload: UserCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Developer admin access required")
    if payload.role == Role.RESIDENT:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Use /users/register to create resident users")
    if payload.role in (Role.ADMIN, Role.SOCIETY_ADMIN):
        if payload.role == Role.SOCIETY_ADMIN:
            society = db.get(Society, payload.society_id)
            if not society or not society.is_approved:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Society must be registered and approved to create a society admin")

        payload_dict = payload.model_dump(exclude={"password"})
        payload_dict["password_change_required"] = True
        user = User(**payload_dict, password_hash=hash_password(payload.password), is_active=True)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    return _create_user(payload, db)


@router.post("/register", response_model=UserRead)
def register_user(payload: UserCreate, db: Session = Depends(get_db)):
    if payload.role != Role.RESIDENT:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Public registration supports resident role only")
    return _create_user(payload, db)


@router.get("/pending", response_model=list[UserRead])
def list_pending_users(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role == Role.ADMIN:
        return db.query(User).filter(User.role == Role.RESIDENT, User.is_active.is_(False)).all()
    if current_user.role == Role.SOCIETY_ADMIN:
        return db.query(User).filter(
            User.role == Role.RESIDENT,
            User.society_id == current_user.society_id,
            User.is_active.is_(False),
        ).all()
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Society or developer admin access required")


@router.post("/{user_id}/approve", response_model=UserRead)
def approve_user(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    pending_user = db.get(User, user_id)
    if not pending_user or pending_user.role != Role.RESIDENT or pending_user.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pending resident not found")

    if current_user.role == Role.ADMIN:
        pending_user.is_active = True
    elif current_user.role == Role.SOCIETY_ADMIN and pending_user.society_id == current_user.society_id:
        pending_user.is_active = True
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to approve this resident")

    db.add(pending_user)
    db.commit()
    db.refresh(pending_user)
    return pending_user


@router.get("/society/{society_id}/users", response_model=list[UserRead])
def list_society_users(society_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    society = db.get(Society, society_id)
    if not society:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Society not found")

    if current_user.role != Role.ADMIN and not (
        current_user.role == Role.SOCIETY_ADMIN and current_user.society_id == society_id
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Developer or society admin access required")

    return db.query(User).filter(User.society_id == society_id).all()


@router.patch("/{user_id}/access", response_model=UserRead)
def update_user_access(user_id: int, payload: UserAccessUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if current_user.role != Role.ADMIN and not (
        current_user.role == Role.SOCIETY_ADMIN and current_user.society_id == user.society_id
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this user")

    updates = payload.model_dump(exclude_none=True)
    for field, value in updates.items():
        setattr(user, field, value)

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/{user_id}/promote", response_model=UserRead)
def promote_to_society_admin(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user or not user.society_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Society user not found")

    if current_user.role != Role.ADMIN and not (
        current_user.role == Role.SOCIETY_ADMIN and current_user.society_id == user.society_id
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to promote this user")

    if user.role == Role.SOCIETY_ADMIN:
        return user

    new_password = secrets.token_urlsafe(10)[:12]
    user.role = Role.SOCIETY_ADMIN
    user.password_hash = hash_password(new_password)
    user.password_change_required = True
    user.is_active = True
    user.access_erp = True
    user.access_gatekeeper = True
    user.access_billing = True
    user.access_payments = True
    user.access_communications = True
    user.access_reports = True
    user.access_documents = True
    user.access_visitor_management = True

    db.add(user)
    db.commit()
    db.refresh(user)

    send_society_admin_credentials(user.email, user.phone, user.email or user.phone, new_password)
    return user


@router.patch("/{user_id}", response_model=UserRead)
def update_user(user_id: int, payload: UserUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update user profile details. Admin can update any user; society_admin can update users in their own society."""
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if current_user.role != Role.ADMIN and not (
        current_user.role == Role.SOCIETY_ADMIN and current_user.society_id == user.society_id
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this user")

    updates = payload.model_dump(exclude_none=True)
    password = updates.pop("password", None)
    if password:
        updates["password_hash"] = hash_password(password)

    for field, value in updates.items():
        setattr(user, field, value)

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)):
    return current_user
