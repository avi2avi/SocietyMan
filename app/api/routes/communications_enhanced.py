"""
Enhanced Communication Module with Society360 features
Includes: Announcement types, scheduling, engagement tracking
"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.enums import Role
from app.models.entities import (
    AnnouncementEnhanced,
    ForumPostEnhanced,
    User,
)
from app.schemas.dto import (
    AnnouncementEnhancedCreate,
    AnnouncementEnhancedRead,
    ForumPostEnhancedCreate,
    ForumPostEnhancedRead,
)

router = APIRouter(prefix="/communications", tags=["Communications Enhanced"])


# ============================================================
# ANNOUNCEMENTS ENHANCED
# ============================================================


@router.post("/announcements", response_model=AnnouncementEnhancedRead)
def create_announcement(
    payload: AnnouncementEnhancedCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new announcement (Admin/Society Admin only)"""
    if current_user.role not in (Role.ADMIN, Role.SOCIETY_ADMIN):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    society_id = current_user.society_id if current_user.role == Role.SOCIETY_ADMIN else None

    # Determine initial status based on scheduled_for
    initial_status = "scheduled" if payload.scheduled_for else "draft"

    announcement = AnnouncementEnhanced(
        society_id=society_id,
        published_by_user_id=current_user.id,
        status=initial_status,
        **payload.model_dump()
    )
    db.add(announcement)
    db.commit()
    db.refresh(announcement)
    return announcement


@router.get("/announcements", response_model=list[AnnouncementEnhancedRead])
def list_announcements(
    announcement_type: str | None = Query(None),
    priority: str | None = Query(None),
    status: str | None = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List announcements with filtering"""
    query = db.query(AnnouncementEnhanced)

    # Filter by society
    if current_user.role == Role.SOCIETY_ADMIN:
        query = query.filter(AnnouncementEnhanced.society_id == current_user.society_id)
    elif current_user.role == Role.RESIDENT:
        from app.models.entities import ResidentProfile, Unit
        profile = db.query(ResidentProfile).filter(ResidentProfile.user_id == current_user.id).first()
        if profile:
            unit = db.get(Unit, profile.unit_id)
            if unit and unit.society_id:
                query = query.filter(AnnouncementEnhanced.society_id == unit.society_id)

    # Filter by type, priority, status
    if announcement_type:
        query = query.filter(AnnouncementEnhanced.announcement_type == announcement_type)
    if priority:
        query = query.filter(AnnouncementEnhanced.priority == priority)
    if status:
        query = query.filter(AnnouncementEnhanced.status == status)

    # Filter to show only published or scheduled announcements for residents
    if current_user.role == Role.RESIDENT:
        query = query.filter(
            (AnnouncementEnhanced.status.in_(["published", "scheduled"])) |
            (AnnouncementEnhanced.published_at.isnot(None))
        )

    return query.order_by(desc(AnnouncementEnhanced.created_at)).all()


@router.patch("/announcements/{announcement_id}/publish")
def publish_announcement(
    announcement_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Publish or schedule an announcement"""
    announcement = db.get(AnnouncementEnhanced, announcement_id)
    if not announcement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Announcement not found")

    # Authorization: only creator or admin
    if current_user.role == Role.SOCIETY_ADMIN and announcement.society_id != current_user.society_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    elif current_user.role not in (Role.ADMIN, Role.SOCIETY_ADMIN):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    announcement.status = "published"
    announcement.published_at = datetime.utcnow()
    db.commit()
    db.refresh(announcement)
    return announcement


@router.get("/announcements/{announcement_id}")
def get_announcement(
    announcement_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a single announcement and increment view count"""
    announcement = db.get(AnnouncementEnhanced, announcement_id)
    if not announcement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Announcement not found")

    # Check authorization
    if announcement.status not in ("published", "scheduled"):
        if current_user.role not in (Role.ADMIN, Role.SOCIETY_ADMIN):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Announcement not available")

    # Increment view count
    announcement.view_count += 1
    db.commit()
    db.refresh(announcement)

    return AnnouncementEnhancedRead.model_validate(announcement)


# ============================================================
# FORUM POSTS ENHANCED
# ============================================================


@router.post("/forum", response_model=ForumPostEnhancedRead)
def create_forum_post(
    payload: ForumPostEnhancedCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new forum post"""
    if current_user.role not in (Role.RESIDENT, Role.SOCIETY_ADMIN, Role.ADMIN):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    # Get society ID
    society_id = current_user.society_id
    if current_user.role == Role.RESIDENT:
        from app.models.entities import ResidentProfile, Unit
        profile = db.query(ResidentProfile).filter(ResidentProfile.user_id == current_user.id).first()
        if profile:
            unit = db.get(Unit, profile.unit_id)
            if unit:
                society_id = unit.society_id

    post = ForumPostEnhanced(
        society_id=society_id,
        author_user_id=current_user.id,
        **payload.model_dump()
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


@router.get("/forum", response_model=list[ForumPostEnhancedRead])
def list_forum_posts(
    category: str | None = Query(None),
    tag: str | None = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List forum posts with filtering"""
    query = db.query(ForumPostEnhanced).filter(ForumPostEnhanced.status == "active")

    # Filter by society
    if current_user.role == Role.SOCIETY_ADMIN:
        query = query.filter(ForumPostEnhanced.society_id == current_user.society_id)
    elif current_user.role == Role.RESIDENT:
        from app.models.entities import ResidentProfile, Unit
        profile = db.query(ResidentProfile).filter(ResidentProfile.user_id == current_user.id).first()
        if profile:
            unit = db.get(Unit, profile.unit_id)
            if unit and unit.society_id:
                query = query.filter(ForumPostEnhanced.society_id == unit.society_id)

    # Filter by category and tags
    if category:
        query = query.filter(ForumPostEnhanced.category == category)
    if tag:
        query = query.filter(ForumPostEnhanced.tags.like(f"%{tag}%"))

    return query.order_by(desc(ForumPostEnhanced.created_at)).all()


@router.get("/forum/{post_id}")
def get_forum_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a forum post and increment view count"""
    post = db.get(ForumPostEnhanced, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Forum post not found")

    # Increment view count
    post.view_count += 1
    db.commit()
    db.refresh(post)

    return ForumPostEnhancedRead.model_validate(post)


@router.patch("/forum/{post_id}/moderate")
def moderate_forum_post(
    post_id: int,
    moderate: bool,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Moderate a forum post (hide if needed)"""
    if current_user.role not in (Role.ADMIN, Role.SOCIETY_ADMIN):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    post = db.get(ForumPostEnhanced, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Forum post not found")

    if moderate:
        post.status = "hidden"
        post.moderated_by_user_id = current_user.id
        post.is_moderated = True
    else:
        post.status = "active"
        post.is_moderated = False

    db.commit()
    db.refresh(post)
    return post
