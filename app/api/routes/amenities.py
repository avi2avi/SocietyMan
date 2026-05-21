"""
Amenities Management and Booking System
"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_, desc, func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.enums import Role
from app.models.entities import Amenity, AmenityBooking, User
from app.schemas.dto import (
    AmenityBookingCreate,
    AmenityBookingRead,
    AmenityCreate,
    AmenityRead,
)

router = APIRouter(prefix="/amenities", tags=["Amenities"])


# ============================================================
# AMENITIES MANAGEMENT
# ============================================================


@router.post("", response_model=AmenityRead)
def create_amenity(
    payload: AmenityCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new amenity (Admin/Society Admin only)"""
    if current_user.role not in (Role.ADMIN, Role.SOCIETY_ADMIN):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    society_id = current_user.society_id if current_user.role == Role.SOCIETY_ADMIN else None

    amenity = Amenity(
        society_id=society_id,
        **payload.model_dump()
    )
    db.add(amenity)
    db.commit()
    db.refresh(amenity)
    return amenity


@router.get("", response_model=list[AmenityRead])
def list_amenities(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all active amenities"""
    query = db.query(Amenity).filter(Amenity.is_active == True)

    if current_user.role == Role.SOCIETY_ADMIN:
        query = query.filter(Amenity.society_id == current_user.society_id)
    elif current_user.role == Role.RESIDENT:
        from app.models.entities import ResidentProfile, Unit
        profile = db.query(ResidentProfile).filter(ResidentProfile.user_id == current_user.id).first()
        if profile:
            unit = db.get(Unit, profile.unit_id)
            if unit and unit.society_id:
                query = query.filter(Amenity.society_id == unit.society_id)

    return query.all()


@router.get("/{amenity_id}", response_model=AmenityRead)
def get_amenity(
    amenity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get amenity details"""
    amenity = db.get(Amenity, amenity_id)
    if not amenity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Amenity not found")

    return amenity


# ============================================================
# AMENITY BOOKINGS
# ============================================================


@router.post("/{amenity_id}/bookings", response_model=AmenityBookingRead)
def create_booking(
    amenity_id: int,
    payload: AmenityBookingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new amenity booking"""
    amenity = db.get(Amenity, amenity_id)
    if not amenity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Amenity not found")

    # Only residents can book
    if current_user.role != Role.RESIDENT:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only residents can book amenities")

    # Check for conflicting bookings
    conflicting = db.query(AmenityBooking).filter(
        AmenityBooking.amenity_id == amenity_id,
        AmenityBooking.status.in_(["pending", "confirmed"]),
        and_(
            AmenityBooking.start_datetime < payload.end_datetime,
            AmenityBooking.end_datetime > payload.start_datetime,
        )
    ).first()

    if conflicting:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Amenity is already booked for this time period"
        )

    booking = AmenityBooking(
        amenity_id=amenity_id,
        resident_user_id=current_user.id,
        **payload.model_dump()
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


@router.get("/{amenity_id}/bookings", response_model=list[AmenityBookingRead])
def list_bookings(
    amenity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List bookings for an amenity"""
    amenity = db.get(Amenity, amenity_id)
    if not amenity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Amenity not found")

    # Authorization: only admins or booking residents can view
    if current_user.role not in (Role.ADMIN, Role.SOCIETY_ADMIN):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    bookings = db.query(AmenityBooking).filter(
        AmenityBooking.amenity_id == amenity_id
    ).order_by(desc(AmenityBooking.start_datetime)).all()

    return bookings


@router.get("/{amenity_id}/availability")
def check_availability(
    amenity_id: int,
    start_datetime: str,
    end_datetime: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Check availability of amenity for a time range"""
    amenity = db.get(Amenity, amenity_id)
    if not amenity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Amenity not found")

    # Parse datetime strings
    try:
        start = datetime.fromisoformat(start_datetime)
        end = datetime.fromisoformat(end_datetime)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid datetime format")

    # Check for conflicts
    conflicts = db.query(AmenityBooking).filter(
        AmenityBooking.amenity_id == amenity_id,
        AmenityBooking.status.in_(["pending", "confirmed"]),
        and_(
            AmenityBooking.start_datetime < end,
            AmenityBooking.end_datetime > start,
        )
    ).count()

    return {
        "amenity_id": amenity_id,
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
        "is_available": conflicts == 0,
        "conflicts": conflicts,
    }


@router.patch("/{amenity_id}/bookings/{booking_id}/confirm")
def confirm_booking(
    amenity_id: int,
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Confirm a booking (Admin/Society Admin only)"""
    if current_user.role not in (Role.ADMIN, Role.SOCIETY_ADMIN):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    booking = db.get(AmenityBooking, booking_id)
    if not booking or booking.amenity_id != amenity_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    booking.status = "confirmed"
    db.commit()
    db.refresh(booking)
    return booking


@router.delete("/{amenity_id}/bookings/{booking_id}")
def cancel_booking(
    amenity_id: int,
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Cancel a booking"""
    booking = db.get(AmenityBooking, booking_id)
    if not booking or booking.amenity_id != amenity_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    # Authorization: resident who booked it or admin
    if current_user.role == Role.RESIDENT and booking.resident_user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    elif current_user.role not in (Role.ADMIN, Role.SOCIETY_ADMIN, Role.RESIDENT):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    booking.status = "cancelled"
    db.commit()

    return {"status": "cancelled", "booking_id": booking_id}


@router.get("/{amenity_id}/usage-stats")
def get_usage_stats(
    amenity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get usage statistics for an amenity"""
    if current_user.role not in (Role.ADMIN, Role.SOCIETY_ADMIN):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    amenity = db.get(Amenity, amenity_id)
    if not amenity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Amenity not found")

    total_bookings = db.query(AmenityBooking).filter(
        AmenityBooking.amenity_id == amenity_id
    ).count()

    completed = db.query(AmenityBooking).filter(
        AmenityBooking.amenity_id == amenity_id,
        AmenityBooking.status == "completed"
    ).count()

    cancelled = db.query(AmenityBooking).filter(
        AmenityBooking.amenity_id == amenity_id,
        AmenityBooking.status == "cancelled"
    ).count()

    confirmed = db.query(AmenityBooking).filter(
        AmenityBooking.amenity_id == amenity_id,
        AmenityBooking.status == "confirmed"
    ).count()

    return {
        "amenity_id": amenity_id,
        "amenity_name": amenity.name,
        "total_bookings": total_bookings,
        "completed": completed,
        "confirmed": confirmed,
        "cancelled": cancelled,
        "pending": total_bookings - completed - cancelled - confirmed,
        "utilization_rate": (completed / total_bookings * 100) if total_bookings > 0 else 0,
    }
