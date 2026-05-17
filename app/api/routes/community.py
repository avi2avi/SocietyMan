from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.enums import Role
from app.models.entities import (
    Unit,
    User,
    ResidentProfile,
    AmenityBooking,
    Asset,
    InventoryItem,
    StaffMember,
    StaffAttendance,
    Vehicle,
    GatePass,
    PurchaseRequest,
    ComplianceEvent,
    Ticket,
    Notice,
    Document,
    VendorInvoice,
    Payment,
    Invoice,
    VisitorLog,
)
from app.models.family import FamilyMember
from app.models.parcel import Parcel
from app.models.meeting import Meeting, MeetingAttachment, MeetingAttendee
from app.models.poll import Poll, PollOption, PollVote
from app.models.event import SocietyEvent, EventRegistration
from app.models.expense import ExpenseCategory, Expense, UtilityReading
from app.models.patrol import SecurityPatrol, PatrolCheckpoint
from app.models.domestic_help import DomesticHelp
from app.schemas.community import (
    FamilyMemberCreate,
    FamilyMemberRead,
    FamilyMemberUpdate,
    ParcelCreate,
    ParcelRead,
    ParcelCollect,
    MeetingCreate,
    MeetingRead,
    MeetingUpdate,
    MeetingAttendeeCreate,
    PollCreate,
    PollRead,
    PollVoteCreate,
    SocietyEventCreate,
    SocietyEventRead,
    SocietyEventUpdate,
    EventRegistrationCreate,
    ExpenseCategoryCreate,
    ExpenseCategoryRead,
    ExpenseCreate,
    ExpenseRead,
    UtilityReadingCreate,
    UtilityReadingRead,
    SecurityPatrolCreate,
    SecurityPatrolRead,
    PatrolCheckpointCreate,
    DomesticHelpCreate,
    DomesticHelpRead,
    SocietyDirectoryEntry,
    CommunityPostCreate,
    CommunityPostRead,
    PostCommentCreate,
    PostCommentRead,
    EmergencyContactCreate,
    EmergencyContactRead,
    NoticeBoardCreate,
    NoticeBoardRead,
    VehicleEntryLogCreate,
    VehicleEntryLogRead,
    ComplaintCategoryCreate,
    ComplaintCategoryRead,
    ComplaintCreate,
    ComplaintRead,
    ComplaintUpdate,
)
from app.models.community_interactions import (
    CommunityPost,
    PostComment,
    PostLike,
    EmergencyContact,
    NoticeBoard,
    VehicleEntryLog,
    ComplaintCategory,
    Complaint,
)

router = APIRouter(prefix="/community", tags=["Community & Lifestyle"])


def _is_admin(user: User) -> bool:
    return user.role == Role.ADMIN


def _society_scope(user: User, requested_society_id: int | None = None) -> int | None:
    if _is_admin(user):
        return requested_society_id
    if not user.society_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Society-scoped account required")
    if requested_society_id and requested_society_id != user.society_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Requested society is outside your scope")
    return user.society_id


def _required_society(user: User, requested_society_id: int | None = None) -> int:
    society_id = _society_scope(user, requested_society_id)
    if society_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="society_id is required for platform admin actions")
    return society_id


# ===== FAMILY MEMBERS =====

@router.post("/families", response_model=FamilyMemberRead)
def create_family_member(payload: FamilyMemberCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    member = FamilyMember(**payload.model_dump())
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


@router.get("/families", response_model=list[FamilyMemberRead])
def list_family_members(unit_id: int | None = Query(default=None), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(FamilyMember).filter(FamilyMember.is_active.is_(True))
    if unit_id:
        query = query.filter(FamilyMember.unit_id == unit_id)
    return query.order_by(FamilyMember.created_at.desc()).limit(200).all()


@router.get("/families/{member_id}", response_model=FamilyMemberRead)
def get_family_member(member_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    member = db.get(FamilyMember, member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Family member not found")
    return member


@router.patch("/families/{member_id}", response_model=FamilyMemberRead)
def update_family_member(member_id: int, payload: FamilyMemberUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    member = db.get(FamilyMember, member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Family member not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(member, key, value)
    db.commit()
    db.refresh(member)
    return member


@router.delete("/families/{member_id}")
def delete_family_member(member_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    member = db.get(FamilyMember, member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Family member not found")
    member.is_active = False
    db.commit()
    return {"detail": "Family member removed"}


# ===== PARCELS / DELIVERY MANAGEMENT =====

@router.post("/parcels", response_model=ParcelRead)
def create_parcel(payload: ParcelCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    society_id = _required_society(current_user, payload.society_id)
    parcel = Parcel(**payload.model_dump(exclude={"society_id"}), society_id=society_id)
    db.add(parcel)
    db.commit()
    db.refresh(parcel)
    return parcel


@router.get("/parcels", response_model=list[ParcelRead])
def list_parcels(
    society_id: int | None = Query(default=None),
    status: str | None = Query(default=None),
    unit_id: int | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    scoped_society_id = _society_scope(current_user, society_id)
    query = db.query(Parcel)
    if scoped_society_id is not None:
        query = query.filter(Parcel.society_id == scoped_society_id)
    if status:
        query = query.filter(Parcel.status == status)
    if unit_id:
        query = query.filter(Parcel.unit_id == unit_id)
    if current_user.role == Role.RESIDENT:
        query = query.filter(Parcel.resident_user_id == current_user.id)
    return query.order_by(Parcel.received_at.desc()).limit(200).all()


@router.get("/parcels/{parcel_id}", response_model=ParcelRead)
def get_parcel(parcel_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    parcel = db.get(Parcel, parcel_id)
    if not parcel:
        raise HTTPException(status_code=404, detail="Parcel not found")
    return parcel


@router.post("/parcels/{parcel_id}/collect", response_model=ParcelRead)
def collect_parcel(parcel_id: int, payload: ParcelCollect = ParcelCollect(), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    parcel = db.get(Parcel, parcel_id)
    if not parcel:
        raise HTTPException(status_code=404, detail="Parcel not found")
    if parcel.status == "collected":
        raise HTTPException(status_code=400, detail="Parcel already collected")
    parcel.status = "collected"
    parcel.collected_at = datetime.utcnow()
    parcel.collected_by_user_id = payload.collected_by_user_id or current_user.id
    db.commit()
    db.refresh(parcel)
    return parcel


@router.get("/parcels/stats/summary")
def parcel_summary(
    society_id: int | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    scoped_society_id = _society_scope(current_user, society_id)
    query = db.query(Parcel)
    if scoped_society_id is not None:
        query = query.filter(Parcel.society_id == scoped_society_id)
    total = query.count()
    pending = query.filter(Parcel.status == "pending").count()
    collected_today = query.filter(
        Parcel.status == "collected",
        func.date(Parcel.collected_at) == func.current_date(),
    ).count()
    return {"total_parcels": total, "pending_collection": pending, "collected_today": collected_today}


# ===== MEETINGS & AGM =====

@router.post("/meetings", response_model=MeetingRead)
def create_meeting(payload: MeetingCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    society_id = _required_society(current_user, payload.society_id)
    meeting = Meeting(**payload.model_dump(exclude={"society_id"}), society_id=society_id, created_by_user_id=current_user.id)
    db.add(meeting)
    db.commit()
    db.refresh(meeting)
    return meeting


@router.get("/meetings", response_model=list[MeetingRead])
def list_meetings(
    society_id: int | None = Query(default=None),
    status: str | None = Query(default=None),
    meeting_type: str | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    scoped_society_id = _society_scope(current_user, society_id)
    query = db.query(Meeting)
    if scoped_society_id is not None:
        query = query.filter(Meeting.society_id == scoped_society_id)
    if status:
        query = query.filter(Meeting.status == status)
    if meeting_type:
        query = query.filter(Meeting.meeting_type == meeting_type)
    return query.order_by(Meeting.meeting_date.desc()).limit(200).all()


@router.get("/meetings/{meeting_id}", response_model=MeetingRead)
def get_meeting(meeting_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    meeting = db.get(Meeting, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting


@router.patch("/meetings/{meeting_id}", response_model=MeetingRead)
def update_meeting(meeting_id: int, payload: MeetingUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    meeting = db.get(Meeting, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(meeting, key, value)
    db.commit()
    db.refresh(meeting)
    return meeting


@router.post("/meetings/{meeting_id}/attendees")
def mark_attendance(meeting_id: int, payload: MeetingAttendeeCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    meeting = db.get(Meeting, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    existing = db.query(MeetingAttendee).filter(
        MeetingAttendee.meeting_id == meeting_id,
        MeetingAttendee.user_id == payload.user_id,
    ).first()
    if existing:
        existing.attended = True
    else:
        attendee = MeetingAttendee(**payload.model_dump(), attended=True)
        db.add(attendee)
    db.commit()
    return {"detail": "Attendance marked"}


# ===== POLLS & VOTING =====

@router.post("/polls", response_model=PollRead)
def create_poll(payload: PollCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    society_id = _required_society(current_user, payload.society_id)
    if not payload.options:
        raise HTTPException(status_code=400, detail="At least one option is required")
    if payload.ends_at <= payload.starts_at:
        raise HTTPException(status_code=400, detail="End time must be after start time")

    poll = Poll(
        society_id=society_id,
        title=payload.title,
        description=payload.description,
        poll_type=payload.poll_type,
        starts_at=payload.starts_at,
        ends_at=payload.ends_at,
        is_anonymous=payload.is_anonymous,
        is_multiple_choice=payload.is_multiple_choice,
        created_by_user_id=current_user.id,
    )
    db.add(poll)
    db.flush()

    for option_text in payload.options:
        db.add(PollOption(poll_id=poll.id, option_text=option_text))
    db.commit()
    db.refresh(poll)
    return _poll_with_options(poll, db)


def _poll_with_options(poll: Poll, db: Session) -> dict:
    options = db.query(PollOption).filter(PollOption.poll_id == poll.id).all()
    data = {
        "id": poll.id,
        "society_id": poll.society_id,
        "title": poll.title,
        "description": poll.description,
        "poll_type": poll.poll_type,
        "starts_at": poll.starts_at,
        "ends_at": poll.ends_at,
        "is_anonymous": poll.is_anonymous,
        "is_multiple_choice": poll.is_multiple_choice,
        "status": poll.status,
        "created_by_user_id": poll.created_by_user_id,
        "created_at": poll.created_at,
        "options": [{"id": o.id, "option_text": o.option_text, "vote_count": o.vote_count} for o in options],
    }
    return data


@router.get("/polls", response_model=list[dict])
def list_polls(
    society_id: int | None = Query(default=None),
    status: str | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    scoped_society_id = _society_scope(current_user, society_id)
    query = db.query(Poll)
    if scoped_society_id is not None:
        query = query.filter(Poll.society_id == scoped_society_id)
    if status:
        query = query.filter(Poll.status == status)
    polls = query.order_by(Poll.created_at.desc()).limit(50).all()
    return [_poll_with_options(p, db) for p in polls]


@router.get("/polls/{poll_id}", response_model=dict)
def get_poll(poll_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    poll = db.get(Poll, poll_id)
    if not poll:
        raise HTTPException(status_code=404, detail="Poll not found")
    return _poll_with_options(poll, db)


@router.post("/polls/{poll_id}/vote")
def vote_poll(poll_id: int, payload: PollVoteCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    poll = db.get(Poll, poll_id)
    if not poll:
        raise HTTPException(status_code=404, detail="Poll not found")
    if poll.status != "active":
        raise HTTPException(status_code=400, detail="Poll is not active")
    if datetime.utcnow() > poll.ends_at:
        poll.status = "closed"
        db.commit()
        raise HTTPException(status_code=400, detail="Poll has ended")

    option = db.get(PollOption, payload.option_id)
    if not option or option.poll_id != poll_id:
        raise HTTPException(status_code=404, detail="Option not found")

    existing = db.query(PollVote).filter(
        PollVote.poll_id == poll_id,
        PollVote.user_id == current_user.id,
    ).first()
    if existing and not poll.is_multiple_choice:
        raise HTTPException(status_code=400, detail="You have already voted on this poll")

    vote = PollVote(
        poll_id=poll_id,
        option_id=payload.option_id,
        user_id=current_user.id,
    )
    option.vote_count += 1
    db.add(vote)
    db.commit()
    return {"detail": "Vote recorded"}


# ===== EVENTS =====

@router.post("/events", response_model=SocietyEventRead)
def create_event(payload: SocietyEventCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    society_id = _required_society(current_user, payload.society_id)
    if payload.ends_at <= payload.starts_at:
        raise HTTPException(status_code=400, detail="End time must be after start time")
    event = SocietyEvent(**payload.model_dump(exclude={"society_id"}), society_id=society_id, created_by_user_id=current_user.id)
    db.add(event)
    db.commit()
    db.refresh(event)
    return {**event.__dict__, "registrations_count": 0}


@router.get("/events", response_model=list[dict])
def list_events(
    society_id: int | None = Query(default=None),
    status: str | None = Query(default=None),
    event_type: str | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    scoped_society_id = _society_scope(current_user, society_id)
    query = db.query(SocietyEvent)
    if scoped_society_id is not None:
        query = query.filter(SocietyEvent.society_id == scoped_society_id)
    if status:
        query = query.filter(SocietyEvent.status == status)
    if event_type:
        query = query.filter(SocietyEvent.event_type == event_type)
    events = query.order_by(SocietyEvent.starts_at.desc()).limit(100).all()
    result = []
    for event in events:
        count = db.query(func.count(EventRegistration.id)).filter(EventRegistration.event_id == event.id).scalar() or 0
        data = {**event.__dict__, "registrations_count": count}
        result.append(data)
    return result


@router.get("/events/{event_id}", response_model=dict)
def get_event(event_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    event = db.get(SocietyEvent, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    count = db.query(func.count(EventRegistration.id)).filter(EventRegistration.event_id == event.id).scalar() or 0
    return {**event.__dict__, "registrations_count": count}


@router.patch("/events/{event_id}", response_model=SocietyEventRead)
def update_event(event_id: int, payload: SocietyEventUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    event = db.get(SocietyEvent, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(event, key, value)
    db.commit()
    db.refresh(event)
    return event


@router.post("/events/{event_id}/register")
def register_for_event(event_id: int, payload: EventRegistrationCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    event = db.get(SocietyEvent, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if event.status == "cancelled":
        raise HTTPException(status_code=400, detail="Event is cancelled")
    if event.max_participants:
        current_count = db.query(func.count(EventRegistration.id)).filter(EventRegistration.event_id == event_id).scalar() or 0
        if current_count + payload.guest_count + 1 > event.max_participants:
            raise HTTPException(status_code=400, detail="Event is full")

    existing = db.query(EventRegistration).filter(
        EventRegistration.event_id == event_id,
        EventRegistration.user_id == current_user.id,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already registered")

    registration = EventRegistration(
        event_id=event_id,
        user_id=current_user.id,
        guest_count=payload.guest_count,
    )
    db.add(registration)
    db.commit()
    return {"detail": "Registered successfully"}


# ===== EXPENSE CATEGORIES =====

@router.post("/expense-categories", response_model=ExpenseCategoryRead)
def create_expense_category(payload: ExpenseCategoryCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    society_id = _required_society(current_user, payload.society_id)
    category = ExpenseCategory(**payload.model_dump(exclude={"society_id"}), society_id=society_id)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.get("/expense-categories", response_model=list[ExpenseCategoryRead])
def list_expense_categories(
    society_id: int | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    scoped_society_id = _society_scope(current_user, society_id)
    query = db.query(ExpenseCategory)
    if scoped_society_id is not None:
        query = query.filter(ExpenseCategory.society_id == scoped_society_id)
    return query.order_by(ExpenseCategory.name).all()


# ===== EXPENSES =====

@router.post("/expenses", response_model=ExpenseRead)
def create_expense(payload: ExpenseCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    society_id = _required_society(current_user, payload.society_id)
    expense = Expense(
        **payload.model_dump(exclude={"society_id", "expense_date"}),
        society_id=society_id,
        expense_date=payload.expense_date or datetime.utcnow(),
        created_by_user_id=current_user.id,
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


@router.get("/expenses", response_model=list[ExpenseRead])
def list_expenses(
    society_id: int | None = Query(default=None),
    category_id: int | None = Query(default=None),
    status: str | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    scoped_society_id = _society_scope(current_user, society_id)
    query = db.query(Expense)
    if scoped_society_id is not None:
        query = query.filter(Expense.society_id == scoped_society_id)
    if category_id:
        query = query.filter(Expense.category_id == category_id)
    if status:
        query = query.filter(Expense.status == status)
    return query.order_by(Expense.expense_date.desc()).limit(200).all()


@router.patch("/expenses/{expense_id}/approve", response_model=ExpenseRead)
def approve_expense(expense_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    expense = db.get(Expense, expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    expense.status = "approved"
    expense.approved_by_user_id = current_user.id
    expense.approved_at = datetime.utcnow()
    db.commit()
    db.refresh(expense)
    return expense


@router.get("/expenses/summary")
def expense_summary(
    society_id: int | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    scoped_society_id = _society_scope(current_user, society_id)
    query = db.query(Expense)
    if scoped_society_id is not None:
        query = query.filter(Expense.society_id == scoped_society_id)
    total = db.query(func.sum(Expense.amount)).filter(Expense.society_id == scoped_society_id).scalar() or 0
    pending = query.filter(Expense.status == "pending").count()
    approved = query.filter(Expense.status == "approved").count()
    return {"total_expenses": float(total), "pending": pending, "approved": approved}


# ===== UTILITY READINGS =====

@router.post("/utilities", response_model=UtilityReadingRead)
def create_utility_reading(payload: UtilityReadingCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    society_id = _required_society(current_user, payload.society_id)
    reading = UtilityReading(**payload.model_dump(exclude={"society_id"}), society_id=society_id, created_by_user_id=current_user.id)
    db.add(reading)
    db.commit()
    db.refresh(reading)
    return reading


@router.get("/utilities", response_model=list[UtilityReadingRead])
def list_utility_readings(
    society_id: int | None = Query(default=None),
    utility_type: str | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    scoped_society_id = _society_scope(current_user, society_id)
    query = db.query(UtilityReading)
    if scoped_society_id is not None:
        query = query.filter(UtilityReading.society_id == scoped_society_id)
    if utility_type:
        query = query.filter(UtilityReading.utility_type == utility_type)
    return query.order_by(UtilityReading.reading_date.desc()).limit(200).all()


@router.get("/utilities/summary")
def utility_summary(
    society_id: int | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    scoped_society_id = _society_scope(current_user, society_id)
    from sqlalchemy import func as sa_func
    query = db.query(UtilityReading.utility_type, sa_func.sum(UtilityReading.total_cost), sa_func.count(UtilityReading.id))
    if scoped_society_id is not None:
        query = query.filter(UtilityReading.society_id == scoped_society_id)
    results = query.group_by(UtilityReading.utility_type).all()
    return [{"utility_type": r[0], "total_cost": float(r[1] or 0), "readings_count": r[2]} for r in results]


# ===== SECURITY PATROLS =====

@router.post("/patrols", response_model=SecurityPatrolRead)
def create_patrol(payload: SecurityPatrolCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    society_id = _required_society(current_user, payload.society_id)
    patrol = SecurityPatrol(**payload.model_dump(exclude={"society_id"}), society_id=society_id, created_by_user_id=current_user.id)
    db.add(patrol)
    db.commit()
    db.refresh(patrol)
    return patrol


@router.get("/patrols", response_model=list[SecurityPatrolRead])
def list_patrols(
    society_id: int | None = Query(default=None),
    status: str | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    scoped_society_id = _society_scope(current_user, society_id)
    query = db.query(SecurityPatrol)
    if scoped_society_id is not None:
        query = query.filter(SecurityPatrol.society_id == scoped_society_id)
    if status:
        query = query.filter(SecurityPatrol.status == status)
    return query.order_by(SecurityPatrol.start_time.desc()).limit(100).all()


@router.post("/patrols/{patrol_id}/complete", response_model=SecurityPatrolRead)
def complete_patrol(patrol_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    patrol = db.get(SecurityPatrol, patrol_id)
    if not patrol:
        raise HTTPException(status_code=404, detail="Patrol not found")
    patrol.status = "completed"
    patrol.end_time = datetime.utcnow()
    db.commit()
    db.refresh(patrol)
    return patrol


@router.post("/patrols/{patrol_id}/checkpoints", response_model=dict)
def add_checkpoint(patrol_id: int, payload: PatrolCheckpointCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    patrol = db.get(SecurityPatrol, patrol_id)
    if not patrol:
        raise HTTPException(status_code=404, detail="Patrol not found")
    checkpoint = PatrolCheckpoint(**payload.model_dump())
    db.add(checkpoint)
    db.commit()
    return {"detail": "Checkpoint recorded", "checkpoint_id": checkpoint.id}


# ===== DOMESTIC HELP =====

@router.post("/domestic-help", response_model=DomesticHelpRead)
def create_domestic_help(payload: DomesticHelpCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    society_id = _required_society(current_user, payload.society_id)
    help_entry = DomesticHelp(**payload.model_dump(exclude={"society_id"}), society_id=society_id)
    db.add(help_entry)
    db.commit()
    db.refresh(help_entry)
    return help_entry


@router.get("/domestic-help", response_model=list[DomesticHelpRead])
def list_domestic_help(
    society_id: int | None = Query(default=None),
    help_type: str | None = Query(default=None),
    unit_id: int | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    scoped_society_id = _society_scope(current_user, society_id)
    query = db.query(DomesticHelp)
    if scoped_society_id is not None:
        query = query.filter(DomesticHelp.society_id == scoped_society_id)
    if help_type:
        query = query.filter(DomesticHelp.help_type == help_type)
    if unit_id:
        query = query.filter(DomesticHelp.unit_id == unit_id)
    return query.order_by(DomesticHelp.created_at.desc()).limit(200).all()


@router.patch("/domestic-help/{help_id}/toggle")
def toggle_domestic_help(help_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    help_entry = db.get(DomesticHelp, help_id)
    if not help_entry:
        raise HTTPException(status_code=404, detail="Domestic help not found")
    help_entry.is_active = not help_entry.is_active
    db.commit()
    return {"detail": f"Domestic help {'activated' if help_entry.is_active else 'deactivated'}"}


# ===== COMMUNITY POSTS (Conversations Feed like Adda/NoBroker) =====

@router.post("/posts", response_model=CommunityPostRead)
def create_post(payload: CommunityPostCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    society_id = _required_society(current_user, payload.society_id)
    post = CommunityPost(**payload.model_dump(exclude={"society_id"}), society_id=society_id, user_id=current_user.id)
    db.add(post)
    db.commit()
    db.refresh(post)
    return _enrich_post(post, db)


def _enrich_post(post: CommunityPost, db: Session) -> dict:
    user = db.get(User, post.user_id)
    like_count = db.query(func.count(PostLike.id)).filter(PostLike.post_id == post.id).scalar() or 0
    comment_count = db.query(func.count(PostComment.id)).filter(PostComment.post_id == post.id).scalar() or 0
    data = {**post.__dict__}
    data["author_name"] = user.full_name if user else "Unknown"
    data["author_role"] = user.role.value if user else "resident"
    data["like_count"] = like_count
    data["comment_count"] = comment_count
    return data


@router.get("/posts", response_model=list[dict])
def list_posts(
    society_id: int | None = Query(default=None),
    post_type: str | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    scoped_society_id = _society_scope(current_user, society_id)
    query = db.query(CommunityPost)
    if scoped_society_id is not None:
        query = query.filter(CommunityPost.society_id == scoped_society_id)
    if post_type:
        query = query.filter(CommunityPost.post_type == post_type)
    query = query.filter(CommunityPost.is_removed.is_(False))
    posts = query.order_by(CommunityPost.created_at.desc()).limit(100).all()
    return [_enrich_post(p, db) for p in posts]


@router.get("/posts/{post_id}", response_model=dict)
def get_post(post_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    post = db.get(CommunityPost, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return _enrich_post(post, db)


@router.delete("/posts/{post_id}")
def remove_post(post_id: int, reason: str | None = Query(default=None), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    post = db.get(CommunityPost, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    post.is_removed = True
    post.removed_reason = reason or "Moderator action"
    db.commit()
    return {"detail": "Post removed"}


@router.post("/posts/{post_id}/like")
def like_post(post_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    post = db.get(CommunityPost, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    existing = db.query(PostLike).filter(PostLike.post_id == post_id, PostLike.user_id == current_user.id).first()
    if existing:
        db.delete(existing)
        db.commit()
        return {"detail": "Like removed"}
    like = PostLike(post_id=post_id, user_id=current_user.id)
    db.add(like)
    db.commit()
    return {"detail": "Post liked"}


@router.post("/posts/{post_id}/comments", response_model=PostCommentRead)
def add_comment(post_id: int, payload: PostCommentCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    post = db.get(CommunityPost, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    comment = PostComment(**payload.model_dump(), user_id=current_user.id)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    user = db.get(User, comment.user_id)
    data = {**comment.__dict__, "author_name": user.full_name if user else "Unknown"}
    return data


@router.get("/posts/{post_id}/comments", response_model=list[dict])
def list_comments(post_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    post = db.get(CommunityPost, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    comments = db.query(PostComment).filter(PostComment.post_id == post_id).order_by(PostComment.created_at.asc()).all()
    result = []
    for c in comments:
        user = db.get(User, c.user_id)
        result.append({**c.__dict__, "author_name": user.full_name if user else "Unknown"})
    return result


# ===== EMERGENCY CONTACTS =====

@router.post("/emergency-contacts", response_model=EmergencyContactRead)
def create_emergency_contact(payload: EmergencyContactCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    society_id = _required_society(current_user, payload.society_id)
    contact = EmergencyContact(**payload.model_dump(exclude={"society_id"}), society_id=society_id)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


@router.get("/emergency-contacts", response_model=list[EmergencyContactRead])
def list_emergency_contacts(
    society_id: int | None = Query(default=None),
    contact_type: str | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    scoped_society_id = _society_scope(current_user, society_id)
    query = db.query(EmergencyContact).filter(EmergencyContact.is_active.is_(True))
    if scoped_society_id is not None:
        query = query.filter(EmergencyContact.society_id == scoped_society_id)
    if contact_type:
        query = query.filter(EmergencyContact.contact_type == contact_type)
    return query.order_by(EmergencyContact.contact_type, EmergencyContact.name).all()


# ===== NOTICE BOARD =====

@router.post("/notices", response_model=NoticeBoardRead)
def create_notice(payload: NoticeBoardCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    society_id = _required_society(current_user, payload.society_id)
    notice = NoticeBoard(**payload.model_dump(exclude={"society_id"}), society_id=society_id, created_by_user_id=current_user.id)
    db.add(notice)
    db.commit()
    db.refresh(notice)
    return notice


@router.get("/notices", response_model=list[NoticeBoardRead])
def list_notices(
    society_id: int | None = Query(default=None),
    category: str | None = Query(default=None),
    priority: str | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    scoped_society_id = _society_scope(current_user, society_id)
    now = datetime.utcnow()
    query = db.query(NoticeBoard).filter(
        (NoticeBoard.expires_at.is_(None)) | (NoticeBoard.expires_at >= now)
    )
    if scoped_society_id is not None:
        query = query.filter(NoticeBoard.society_id == scoped_society_id)
    if category:
        query = query.filter(NoticeBoard.category == category)
    if priority:
        query = query.filter(NoticeBoard.priority == priority)
    return query.order_by(NoticeBoard.created_at.desc()).limit(100).all()


# ===== VEHICLE ENTRY LOGS =====

@router.post("/vehicle-logs", response_model=VehicleEntryLogRead)
def create_vehicle_log(payload: VehicleEntryLogCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    society_id = _required_society(current_user, payload.society_id)
    log = VehicleEntryLog(**payload.model_dump(exclude={"society_id"}), society_id=society_id, created_by_user_id=current_user.id)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@router.get("/vehicle-logs", response_model=list[VehicleEntryLogRead])
def list_vehicle_logs(
    society_id: int | None = Query(default=None),
    status: str | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    scoped_society_id = _society_scope(current_user, society_id)
    query = db.query(VehicleEntryLog)
    if scoped_society_id is not None:
        query = query.filter(VehicleEntryLog.society_id == scoped_society_id)
    if status:
        query = query.filter(VehicleEntryLog.status == status)
    return query.order_by(VehicleEntryLog.entry_at.desc()).limit(200).all()


@router.post("/vehicle-logs/{log_id}/exit")
def vehicle_exit(log_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    log = db.get(VehicleEntryLog, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Vehicle log not found")
    if log.status == "exited":
        raise HTTPException(status_code=400, detail="Vehicle already marked as exited")
    log.status = "exited"
    log.exit_at = datetime.utcnow()
    db.commit()
    return {"detail": "Vehicle exit recorded"}


# ===== COMPLAINTS (Enhanced Helpdesk with Categories) =====

@router.post("/complaint-categories", response_model=ComplaintCategoryRead)
def create_complaint_category(payload: ComplaintCategoryCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    society_id = _required_society(current_user, payload.society_id)
    category = ComplaintCategory(**payload.model_dump(exclude={"society_id"}), society_id=society_id)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.get("/complaint-categories", response_model=list[ComplaintCategoryRead])
def list_complaint_categories(
    society_id: int | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    scoped_society_id = _society_scope(current_user, society_id)
    query = db.query(ComplaintCategory).filter(ComplaintCategory.is_active.is_(True))
    if scoped_society_id is not None:
        query = query.filter(ComplaintCategory.society_id == scoped_society_id)
    return query.order_by(ComplaintCategory.name).all()


@router.post("/complaints", response_model=ComplaintRead)
def create_complaint(payload: ComplaintCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    society_id = _required_society(current_user, payload.society_id)
    complaint = Complaint(
        **payload.model_dump(exclude={"society_id"}),
        society_id=society_id,
        user_id=current_user.id,
    )
    # Get the user's unit
    profile = db.query(ResidentProfile).filter(ResidentProfile.user_id == current_user.id).first()
    if profile:
        complaint.unit_id = profile.unit_id
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    return _enrich_complaint(complaint, db)


def _enrich_complaint(complaint: Complaint, db: Session) -> dict:
    data = {**complaint.__dict__}
    user = db.get(User, complaint.user_id)
    data["user_name"] = user.full_name if user else "Unknown"
    if complaint.category_id:
        cat = db.get(ComplaintCategory, complaint.category_id)
        data["category_name"] = cat.name if cat else None
    else:
        data["category_name"] = None
    return data


@router.get("/complaints", response_model=list[dict])
def list_complaints(
    society_id: int | None = Query(default=None),
    status: str | None = Query(default=None),
    category_id: int | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    scoped_society_id = _society_scope(current_user, society_id)
    query = db.query(Complaint)
    if scoped_society_id is not None:
        query = query.filter(Complaint.society_id == scoped_society_id)
    if status:
        query = query.filter(Complaint.status == status)
    if category_id:
        query = query.filter(Complaint.category_id == category_id)
    if current_user.role == Role.RESIDENT:
        query = query.filter(Complaint.user_id == current_user.id)
    complaints = query.order_by(Complaint.created_at.desc()).limit(200).all()
    return [_enrich_complaint(c, db) for c in complaints]


@router.get("/complaints/{complaint_id}", response_model=dict)
def get_complaint(complaint_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    complaint = db.get(Complaint, complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return _enrich_complaint(complaint, db)


@router.patch("/complaints/{complaint_id}", response_model=dict)
def update_complaint(complaint_id: int, payload: ComplaintUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    complaint = db.get(Complaint, complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(complaint, key, value)
    if payload.status == "resolved":
        complaint.resolved_at = datetime.utcnow()
    db.commit()
    db.refresh(complaint)
    return _enrich_complaint(complaint, db)


@router.get("/complaints/stats/summary")
def complaint_stats(
    society_id: int | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    scoped_society_id = _society_scope(current_user, society_id)
    query = db.query(Complaint)
    if scoped_society_id is not None:
        query = query.filter(Complaint.society_id == scoped_society_id)
    total = query.count()
    open_count = query.filter(Complaint.status == "open").count()
    in_progress = query.filter(Complaint.status == "in_progress").count()
    resolved = query.filter(Complaint.status == "resolved").count()
    return {"total": total, "open": open_count, "in_progress": in_progress, "resolved": resolved}


# ===== SOCIETY DIRECTORY =====

@router.get("/directory", response_model=list[SocietyDirectoryEntry])
def society_directory(
    society_id: int | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    scoped_society_id = _society_scope(current_user, society_id)
    query = db.query(Unit)
    if scoped_society_id is not None:
        # Filter units by society through resident_profiles
        query = query.filter(
            Unit.id.in_(
                db.query(ResidentProfile.unit_id).filter(
                    ResidentProfile.unit_id == Unit.id,
                    ResidentProfile.id.isnot(None),
                )
            )
        )
    units = query.order_by(Unit.building, Unit.unit_number).limit(500).all()

    directory = []
    for unit in units:
        profiles = db.query(ResidentProfile).filter(ResidentProfile.unit_id == unit.id).all()
        residents = []
        for profile in profiles:
            user = db.get(User, profile.user_id)
            if user and user.is_active:
                residents.append({
                    "name": user.full_name,
                    "phone": user.phone,
                    "email": user.email,
                    "occupancy_type": profile.occupancy_type,
                })
        directory.append(SocietyDirectoryEntry(
            unit_id=unit.id,
            building=unit.building,
            unit_number=unit.unit_number,
            residents=residents,
        ))
    return directory


# ===== COMMUNITY DASHBOARD =====

@router.get("/dashboard")
def community_dashboard(
    society_id: int | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    scoped_society_id = _society_scope(current_user, society_id)

    def count_active(model, extra_filters=None):
        q = db.query(func.count(model.id))
        if scoped_society_id is not None and hasattr(model, "society_id"):
            q = q.filter(model.society_id == scoped_society_id)
        if extra_filters:
            q = q.filter(*extra_filters)
        return q.scalar() or 0

    now = datetime.utcnow()

    return {
        "upcoming_events": count_active(SocietyEvent, [SocietyEvent.starts_at >= now, SocietyEvent.status == "upcoming"]),
        "active_polls": count_active(Poll, [Poll.ends_at >= now, Poll.status == "active"]),
        "pending_parcels": count_active(Parcel, [Parcel.status == "pending"]),
        "upcoming_meetings": count_active(Meeting, [Meeting.meeting_date >= now, Meeting.status == "scheduled"]),
        "active_family_members": count_active(FamilyMember, [FamilyMember.is_active.is_(True)]),
        "active_domestic_help": count_active(DomesticHelp, [DomesticHelp.is_active.is_(True)]),
        "active_patrols": count_active(SecurityPatrol, [SecurityPatrol.status == "in_progress"]),
        "pending_expenses": count_active(Expense, [Expense.status == "pending"]),
        "utility_types": len(db.query(UtilityReading.utility_type).distinct().all()),
    }