from datetime import datetime
from pydantic import BaseModel, Field


# === Family Members ===
class FamilyMemberCreate(BaseModel):
    unit_id: int
    name: str
    relationship: str = "family"
    phone: str | None = None
    email: str | None = None
    age: int | None = None
    occupation: str | None = None


class FamilyMemberRead(FamilyMemberCreate):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class FamilyMemberUpdate(BaseModel):
    name: str | None = None
    relationship: str | None = None
    phone: str | None = None
    email: str | None = None
    age: int | None = None
    occupation: str | None = None
    is_active: bool | None = None


# === Parcels ===
class ParcelCreate(BaseModel):
    society_id: int | None = None
    unit_id: int | None = None
    resident_user_id: int | None = None
    courier_name: str
    courier_phone: str | None = None
    delivery_person_name: str | None = None
    tracking_number: str | None = None
    description: str | None = None
    notes: str | None = None


class ParcelRead(ParcelCreate):
    id: int
    society_id: int
    status: str
    received_at: datetime
    collected_at: datetime | None = None
    collected_by_user_id: int | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class ParcelCollect(BaseModel):
    collected_by_user_id: int | None = None


# === Meetings ===
class MeetingCreate(BaseModel):
    society_id: int | None = None
    title: str
    description: str | None = None
    meeting_type: str = "general"
    meeting_date: datetime
    location: str | None = None
    agenda: str | None = None


class MeetingRead(MeetingCreate):
    id: int
    society_id: int
    minutes: str | None = None
    status: str
    created_by_user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class MeetingUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    meeting_date: datetime | None = None
    location: str | None = None
    agenda: str | None = None
    minutes: str | None = None
    status: str | None = None


class MeetingAttendeeCreate(BaseModel):
    meeting_id: int
    user_id: int
    unit_id: int | None = None


# === Polls ===
class PollCreate(BaseModel):
    society_id: int | None = None
    title: str
    description: str | None = None
    poll_type: str = "general"
    starts_at: datetime
    ends_at: datetime
    is_anonymous: bool = False
    is_multiple_choice: bool = False
    options: list[str]


class PollRead(BaseModel):
    id: int
    society_id: int
    title: str
    description: str | None = None
    poll_type: str
    starts_at: datetime
    ends_at: datetime
    is_anonymous: bool
    is_multiple_choice: bool
    status: str
    created_by_user_id: int
    created_at: datetime
    options: list = []

    class Config:
        from_attributes = True


class PollVoteCreate(BaseModel):
    option_id: int


# === Events ===
class SocietyEventCreate(BaseModel):
    society_id: int | None = None
    title: str
    description: str | None = None
    event_type: str = "cultural"
    starts_at: datetime
    ends_at: datetime
    location: str | None = None
    registration_required: bool = False
    registration_fee: float = 0
    max_participants: int | None = None
    organizer_name: str | None = None
    organizer_phone: str | None = None
    banner_url: str | None = None


class SocietyEventRead(SocietyEventCreate):
    id: int
    society_id: int
    status: str
    created_by_user_id: int
    created_at: datetime
    registrations_count: int = 0

    class Config:
        from_attributes = True


class SocietyEventUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    event_type: str | None = None
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    location: str | None = None
    registration_required: bool | None = None
    registration_fee: float | None = None
    max_participants: int | None = None
    status: str | None = None


class EventRegistrationCreate(BaseModel):
    event_id: int
    guest_count: int = 0


# === Expenses ===
class ExpenseCategoryCreate(BaseModel):
    society_id: int | None = None
    name: str
    description: str | None = None
    budget_amount: float = 0


class ExpenseCategoryRead(ExpenseCategoryCreate):
    id: int
    society_id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ExpenseCreate(BaseModel):
    society_id: int | None = None
    category_id: int | None = None
    vendor_id: int | None = None
    title: str
    description: str | None = None
    amount: float
    expense_date: datetime | None = None
    payment_method: str = "cash"
    receipt_url: str | None = None


class ExpenseRead(ExpenseCreate):
    id: int
    society_id: int
    status: str
    approved_by_user_id: int | None = None
    approved_at: datetime | None = None
    created_by_user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class UtilityReadingCreate(BaseModel):
    society_id: int | None = None
    utility_type: str
    reading_date: datetime
    reading_value: float
    unit_of_measure: str = "units"
    cost_per_unit: float = 0
    total_cost: float = 0
    bill_url: str | None = None
    notes: str | None = None


class UtilityReadingRead(UtilityReadingCreate):
    id: int
    society_id: int
    created_by_user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# === Patrols ===
class SecurityPatrolCreate(BaseModel):
    society_id: int | None = None
    staff_member_id: int | None = None
    patrol_type: str = "regular"
    start_time: datetime
    route: str | None = None
    notes: str | None = None


class SecurityPatrolRead(SecurityPatrolCreate):
    id: int
    society_id: int
    end_time: datetime | None = None
    status: str
    created_by_user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class PatrolCheckpointCreate(BaseModel):
    patrol_id: int
    checkpoint_name: str
    location: str | None = None
    status: str = "ok"
    notes: str | None = None


# === Domestic Help ===
class DomesticHelpCreate(BaseModel):
    society_id: int | None = None
    unit_id: int | None = None
    name: str
    phone: str | None = None
    help_type: str = "maid"  # maid, cook, driver, gardener, nanny, other
    working_days: str | None = None  # Monday,Tuesday,Wednesday
    working_hours: str | None = None  # 9:00-11:00
    id_proof_type: str | None = None
    id_proof_number: str | None = None
    is_active: bool = True


class DomesticHelpRead(DomesticHelpCreate):
    id: int
    society_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# === Directory ===
class SocietyDirectoryEntry(BaseModel):
    unit_id: int
    building: str
    unit_number: str
    residents: list = []

    class Config:
        from_attributes = True


# === Community Posts ===
class CommunityPostCreate(BaseModel):
    society_id: int | None = None
    content: str
    post_type: str = "conversation"
    is_announcement: bool = False


class CommunityPostRead(BaseModel):
    id: int
    society_id: int
    user_id: int
    content: str
    post_type: str
    is_announcement: bool
    is_removed: bool
    removed_reason: str | None = None
    author_name: str | None = None
    author_role: str | None = None
    like_count: int = 0
    comment_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


class PostCommentCreate(BaseModel):
    post_id: int
    content: str


class PostCommentRead(BaseModel):
    id: int
    post_id: int
    user_id: int
    content: str
    author_name: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True


# === Emergency Contacts ===
class EmergencyContactCreate(BaseModel):
    society_id: int | None = None
    contact_type: str
    name: str
    phone: str
    address: str | None = None


class EmergencyContactRead(EmergencyContactCreate):
    id: int
    society_id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# === Notice Board ===
class NoticeBoardCreate(BaseModel):
    society_id: int | None = None
    title: str
    content: str
    category: str = "general"
    priority: str = "normal"
    expires_at: datetime | None = None


class NoticeBoardRead(NoticeBoardCreate):
    id: int
    society_id: int
    created_by_user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# === Vehicle Entry Log ===
class VehicleEntryLogCreate(BaseModel):
    society_id: int | None = None
    vehicle_id: int | None = None
    registration_number: str
    driver_name: str | None = None
    driver_phone: str | None = None
    purpose: str | None = None


class VehicleEntryLogRead(VehicleEntryLogCreate):
    id: int
    society_id: int
    entry_at: datetime
    exit_at: datetime | None = None
    status: str
    created_by_user_id: int | None = None

    class Config:
        from_attributes = True


# === Complaints ===
class ComplaintCategoryCreate(BaseModel):
    society_id: int | None = None
    name: str
    sla_hours: int = 48
    description: str | None = None


class ComplaintCategoryRead(ComplaintCategoryCreate):
    id: int
    society_id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ComplaintCreate(BaseModel):
    society_id: int | None = None
    category_id: int | None = None
    title: str
    description: str
    media_url: str | None = None
    priority: str = "medium"


class ComplaintRead(ComplaintCreate):
    id: int
    society_id: int
    user_id: int
    unit_id: int | None = None
    status: str
    assigned_to_user_id: int | None = None
    resolution_notes: str | None = None
    resolved_at: datetime | None = None
    category_name: str | None = None
    user_name: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class ComplaintUpdate(BaseModel):
    status: str | None = None
    assigned_to_user_id: int | None = None
    resolution_notes: str | None = None
    priority: str | None = None
