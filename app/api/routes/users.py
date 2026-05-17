from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.enums import Role
from app.core.security import hash_password
from app.models.entities import Society, User
from app.schemas.dto import UserCreate, UserRead

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


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)):
    return current_user
