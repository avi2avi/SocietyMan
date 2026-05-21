from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.enums import Role
from app.models.entities import User
from app.models.photo_gallery import NoticeEnhanced
from app.schemas.dto import NoticeEnhancedCreate, NoticeEnhancedRead

router = APIRouter(prefix="/notices-enhanced", tags=["Enhanced Notices"])


@router.post("", response_model=NoticeEnhancedRead)
def create_notice(
    payload: NoticeEnhancedCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role not in (Role.ADMIN, Role.SOCIETY_ADMIN):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    society_id = current_user.society_id
    if current_user.role == Role.ADMIN:
        society_id = society_id or 1

    notice = NoticeEnhanced(
        society_id=society_id,
        title=payload.title,
        notice_type=payload.notice_type,
        message=payload.message,
        file_url=payload.file_url,
        is_urgent=payload.is_urgent,
        is_published=payload.is_published,
        published_by_user_id=current_user.id,
        published_at=datetime.utcnow(),
        expires_at=payload.expires_at,
    )
    db.add(notice)
    db.commit()
    db.refresh(notice)
    return notice


@router.get("", response_model=list[NoticeEnhancedRead])
def list_notices(
    society_id: int | None = None,
    notice_type: str | None = None,
    include_expired: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    now = datetime.utcnow()
    query = db.query(NoticeEnhanced)

    if society_id:
        query = query.filter(NoticeEnhanced.society_id == society_id)
    elif current_user.society_id:
        query = query.filter(NoticeEnhanced.society_id == current_user.society_id)

    if notice_type:
        query = query.filter(NoticeEnhanced.notice_type == notice_type)

    # Filter out expired notices unless explicitly requested
    if not include_expired:
        query = query.filter(
            (NoticeEnhanced.expires_at >= now) | (NoticeEnhanced.expires_at.is_(None))
        )

    query = query.filter(NoticeEnhanced.is_published == True)
    return query.order_by(NoticeEnhanced.is_urgent.desc(), NoticeEnhanced.published_at.desc()).all()


@router.get("/urgent", response_model=list[NoticeEnhancedRead])
def list_urgent_notices(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    now = datetime.utcnow()
    query = db.query(NoticeEnhanced).filter(NoticeEnhanced.is_urgent == True)

    if current_user.society_id:
        query = query.filter(NoticeEnhanced.society_id == current_user.society_id)

    query = query.filter(
        NoticeEnhanced.is_published == True,
        (NoticeEnhanced.expires_at >= now) | (NoticeEnhanced.expires_at.is_(None)),
    )
    return query.order_by(NoticeEnhanced.published_at.desc()).all()


@router.get("/types", response_model=list[str])
def list_notice_types():
    return ["general", "event", "emergency", "meeting", "holiday"]


@router.get("/{notice_id}", response_model=NoticeEnhancedRead)
def get_notice(notice_id: int, db: Session = Depends(get_db)):
    notice = db.get(NoticeEnhanced, notice_id)
    if not notice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notice not found")
    return notice


@router.put("/{notice_id}", response_model=NoticeEnhancedRead)
def update_notice(
    notice_id: int,
    payload: NoticeEnhancedCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    notice = db.get(NoticeEnhanced, notice_id)
    if not notice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notice not found")

    if current_user.role not in (Role.ADMIN, Role.SOCIETY_ADMIN):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    notice.title = payload.title
    notice.notice_type = payload.notice_type
    notice.message = payload.message
    notice.file_url = payload.file_url
    notice.is_urgent = payload.is_urgent
    notice.is_published = payload.is_published
    notice.expires_at = payload.expires_at
    notice.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(notice)
    return notice


@router.delete("/{notice_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notice(
    notice_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    notice = db.get(NoticeEnhanced, notice_id)
    if not notice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notice not found")

    if current_user.role not in (Role.ADMIN, Role.SOCIETY_ADMIN):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    db.delete(notice)
    db.commit()