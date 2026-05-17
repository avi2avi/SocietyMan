import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.enums import Role
from app.core.security import (
    TokenError,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.entities import RefreshToken, User
from app.schemas.dto import (
    AdminLoginResponse,
    AdminVerificationRequest,
    LoginRequest,
    RefreshTokenRequest,
    TokenPairResponse,
)
from app.services.notifications import send_admin_verification_code

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = None
    if payload.email:
        user = db.query(User).filter(User.email == payload.email).first()
    if not user and payload.phone:
        user = db.query(User).filter(User.phone == payload.phone).first()

    if not user or (payload.phone and user.phone != payload.phone) or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account not activated yet")

    if user.role in (Role.ADMIN, Role.SOCIETY_ADMIN):
        verification_code = "".join(secrets.choice("0123456789") for _ in range(6))
        expiry = datetime.now(timezone.utc) + timedelta(minutes=10)
        user.admin_login_code = verification_code
        user.admin_login_code_expires_at = expiry
        db.add(user)
        db.commit()
        send_admin_verification_code(user.email, user.phone, verification_code)
        return AdminLoginResponse(
            verification_required=True,
            password_change_required=user.password_change_required,
            message="A verification code has been sent to the registered contact details.",
        )

    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))
    db.add(RefreshToken(user_id=user.id, token=refresh_token))
    db.commit()

    return TokenPairResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/verify", response_model=TokenPairResponse)
def verify_admin_login(payload: AdminVerificationRequest, db: Session = Depends(get_db)):
    try:
        user = None
        if payload.email:
            user = db.query(User).filter(User.email == payload.email).first()
        if not user and payload.phone:
            user = db.query(User).filter(User.phone == payload.phone).first()
        if not user or user.role not in (Role.ADMIN, Role.SOCIETY_ADMIN):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid admin login")
        if not user.admin_login_code or not user.admin_login_code_expires_at:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Verification code required")
        if user.admin_login_code != payload.code:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid verification code")
        expires_at = user.admin_login_code_expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) > expires_at:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Verification code expired")
        if user.password_change_required:
            if not payload.new_password:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New password is required for first-time admin login")
            user.password_hash = hash_password(payload.new_password)
            user.password_change_required = False

        user.admin_login_code = None
        user.admin_login_code_expires_at = None
        db.add(user)

        access_token = create_access_token(str(user.id))
        refresh_token = create_refresh_token(str(user.id))
        db.add(RefreshToken(user_id=user.id, token=refresh_token))
        db.commit()

        return TokenPairResponse(access_token=access_token, refresh_token=refresh_token)
    except HTTPException:
        raise
    except Exception as exc:
        print(f"verify_admin_login error: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/refresh", response_model=TokenPairResponse)
def refresh(payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    token_row = db.query(RefreshToken).filter(RefreshToken.token == payload.refresh_token).first()
    if not token_row or token_row.is_revoked:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token revoked")

    try:
        token_payload = decode_token(payload.refresh_token, expected_type="refresh")
    except TokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    user_id = int(token_payload["sub"])
    access_token = create_access_token(str(user_id))
    new_refresh_token = create_refresh_token(str(user_id))

    token_row.is_revoked = True
    db.add(RefreshToken(user_id=user_id, token=new_refresh_token))
    db.commit()

    return TokenPairResponse(access_token=access_token, refresh_token=new_refresh_token)


@router.post("/logout")
def logout(payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    token_row = db.query(RefreshToken).filter(RefreshToken.token == payload.refresh_token).first()
    if token_row:
        token_row.is_revoked = True
        db.commit()
    return {"status": "logged_out"}
