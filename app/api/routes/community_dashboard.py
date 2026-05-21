from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.enums import Role
from app.models.entities import (
    Notice,
    Ticket,
    User,
    Unit,
    ResidentProfile,
    VisitorLog,
    Invoice,
    Payment,
    AmenityBooking,
)
from app.models.photo_gallery import PhotoGalleryAlbum, PhotoGalleryImage, NoticeEnhanced
from app.schemas.dto import (
    AssetRead,
    InventoryItemRead,
    PhotoGalleryAlbumRead,
    NoticeEnhancedRead,
)
from pydantic import BaseModel
from pydantic import Field


class SocietyCommunityStats(BaseModel):
    """Community dashboard stats - inspired by external repo's member/notice/complaint counts"""
    total_members: int = 0
    active_members: int = 0
    total_units: int = 0
    occupied_units: int = 0
    total_notices: int = 0
    active_notices: int = 0
    total_complaints: int = 0
    open_complaints: int = 0
    resolved_complaints: int = 0
    total_invoices: int = 0
    paid_invoices: int = 0
    unpaid_invoices: int = 0
    total_payments: float = 0
    pending_payments: float = 0
    upcoming_events: int = 0
    photo_albums: int = 0
    total_photos: int = 0
    visitor_count_today: int = 0
    amenity_bookings_today: int = 0


router = APIRouter(prefix="/community", tags=["Community Dashboard"])


@router.get("/stats", response_model=SocietyCommunityStats)
def get_community_stats(
    society_id: int | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get comprehensive society community dashboard statistics"""
    sid = society_id or current_user.society_id

    if not sid:
        # If no society context, return zero stats
        return SocietyCommunityStats()

    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # Member stats
    total_members = db.query(func.count(User.id)).filter(
        User.society_id == sid, User.role != Role.ADMIN
    ).scalar() or 0

    active_members = db.query(func.count(User.id)).filter(
        User.society_id == sid, User.is_active == True, User.role != Role.ADMIN
    ).scalar() or 0

    # Unit stats
    total_units = db.query(func.count(Unit.id)).scalar() or 0
    occupied_units = db.query(func.count(ResidentProfile.id)).scalar() or 0

    # Notice stats
    total_notices = db.query(func.count(NoticeEnhanced.id)).filter(
        NoticeEnhanced.society_id == sid
    ).scalar() or 0

    active_notices = db.query(func.count(NoticeEnhanced.id)).filter(
        NoticeEnhanced.society_id == sid,
        NoticeEnhanced.is_published == True,
        (NoticeEnhanced.expires_at >= now) | (NoticeEnhanced.expires_at.is_(None)),
    ).scalar() or 0

    # Ticket/complaint stats
    total_complaints = db.query(func.count(Ticket.id)).filter(
        Ticket.id > 0  # All tickets - join via resident's society
    ).scalar() or 0

    open_complaints = db.query(func.count(Ticket.id)).filter(
        Ticket.status.in_(["OPEN", "IN_PROGRESS"])
    ).scalar() or 0

    resolved_complaints = db.query(func.count(Ticket.id)).filter(
        Ticket.status == "RESOLVED"
    ).scalar() or 0

    # Invoice stats
    total_invoices = db.query(func.count(Invoice.id)).scalar() or 0
    paid_invoices = db.query(func.count(Invoice.id)).filter(
        Invoice.status == "paid"
    ).scalar() or 0
    unpaid_invoices = db.query(func.count(Invoice.id)).filter(
        Invoice.status == "unpaid"
    ).scalar() or 0

    # Payment stats
    total_payments = db.query(func.coalesce(func.sum(Payment.amount), 0)).scalar() or 0
    pending_payments = db.query(func.coalesce(func.sum(Invoice.total_amount), 0)).filter(
        Invoice.status == "unpaid"
    ).scalar() or 0

    # Photo gallery stats
    photo_albums = db.query(func.count(PhotoGalleryAlbum.id)).filter(
        PhotoGalleryAlbum.society_id == sid
    ).scalar() or 0

    total_photos = db.query(func.count(PhotoGalleryImage.id)).filter(
        PhotoGalleryImage.id > 0
    ).scalar() or 0

    # Visitor stats (today)
    visitor_count_today = db.query(func.count(VisitorLog.id)).filter(
        VisitorLog.entry_at >= today_start
    ).scalar() or 0

    # Amenity bookings (today)
    amenity_bookings_today = db.query(func.count(AmenityBooking.id)).filter(
        AmenityBooking.created_at >= today_start
    ).scalar() or 0

    return SocietyCommunityStats(
        total_members=total_members,
        active_members=active_members,
        total_units=total_units,
        occupied_units=occupied_units,
        total_notices=total_notices,
        active_notices=active_notices,
        total_complaints=total_complaints,
        open_complaints=open_complaints,
        resolved_complaints=resolved_complaints,
        total_invoices=total_invoices,
        paid_invoices=paid_invoices,
        unpaid_invoices=unpaid_invoices,
        total_payments=total_payments,
        pending_payments=pending_payments,
        upcoming_events=0,
        photo_albums=photo_albums,
        total_photos=total_photos,
        visitor_count_today=visitor_count_today,
        amenity_bookings_today=amenity_bookings_today,
    )