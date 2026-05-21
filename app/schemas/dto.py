from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, root_validator

from app.core.enums import (
    PaymentMethod,
    PaymentProvider,
    Role,
    TicketStatus,
    VisitorType,
    WhatsAppProvider,
)


class UserAccess(BaseModel):
    erp: bool = False
    gatekeeper: bool = False
    billing: bool = False
    payments: bool = False
    communications: bool = False
    reports: bool = False
    documents: bool = False
    visitor_management: bool = False


class UserCreate(BaseModel):
    full_name: str
    phone: str
    email: EmailStr
    password: str = Field(min_length=8)
    role: Role = Role.RESIDENT
    society_id: int | None = None
    emergency_contact_name: str | None = None
    emergency_contact_phone: str | None = None
    access_erp: bool = False
    access_gatekeeper: bool = False
    access_billing: bool = False
    access_payments: bool = False
    access_communications: bool = False
    access_reports: bool = False
    access_documents: bool = False
    access_visitor_management: bool = False


class LoginRequest(BaseModel):
    email: EmailStr | None = None
    phone: str | None = None
    password: str

    @root_validator(pre=True)
    def require_email_or_phone(cls, values):
        if not values.get("email") and not values.get("phone"):
            raise ValueError("Either email or phone must be provided")
        return values


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class TokenPairResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AdminLoginResponse(BaseModel):
    verification_required: bool
    password_change_required: bool = False
    message: str


class AdminVerificationRequest(BaseModel):
    email: EmailStr | None = None
    phone: str | None = None
    code: str
    new_password: str | None = None

    @root_validator(pre=True)
    def require_email_or_phone(cls, values):
        if not values.get("email") and not values.get("phone"):
            raise ValueError("Either email or phone must be provided")
        return values


class SocietyCreate(BaseModel):
    name: str
    address: str
    city: str
    state: str
    pincode: str
    admin_contact_name: str | None = None
    admin_contact_email: EmailStr | None = None
    admin_contact_phone: str | None = None


class SocietyAdminContactUpdate(BaseModel):
    admin_contact_name: str | None = None
    admin_contact_email: EmailStr | None = None
    admin_contact_phone: str | None = None

    @root_validator(pre=True)
    def require_contact_info(cls, values):
        if not values.get("admin_contact_email") and not values.get("admin_contact_phone") and not values.get("admin_contact_name"):
            raise ValueError("At least one admin contact field must be provided")
        return values


class SocietyRead(BaseModel):
    id: int
    name: str
    address: str
    city: str
    state: str
    pincode: str
    admin_contact_name: str | None = None
    admin_contact_email: EmailStr | None = None
    admin_contact_phone: str | None = None
    is_approved: bool = False

    class Config:
        from_attributes = True


class UserRead(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    phone: str
    role: Role
    society_id: int | None = None
    emergency_contact_name: str | None = None
    emergency_contact_phone: str | None = None
    is_active: bool
    access_erp: bool = False
    access_gatekeeper: bool = False
    access_billing: bool = False
    access_payments: bool = False
    access_communications: bool = False
    access_reports: bool = False
    access_documents: bool = False
    access_visitor_management: bool = False

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    full_name: str | None = None
    phone: str | None = None
    email: str | None = None
    role: Role | None = None
    society_id: int | None = None
    emergency_contact_name: str | None = None
    emergency_contact_phone: str | None = None
    password: str | None = Field(None, min_length=8)
    is_active: bool | None = None


class UserAccessUpdate(BaseModel):
    access_erp: bool | None = None
    access_gatekeeper: bool | None = None
    access_billing: bool | None = None
    access_payments: bool | None = None
    access_communications: bool | None = None
    access_reports: bool | None = None
    access_documents: bool | None = None
    access_visitor_management: bool | None = None
    is_active: bool | None = None


class SettingRead(BaseModel):
    key: str
    value: str
    description: str | None = None

    class Config:
        from_attributes = True


class UnitCreate(BaseModel):
    building: str
    unit_number: str
    unit_type: str = "residential"
    parking_car_slots: int = 0
    parking_bike_slots: int = 0


class ResidentCreate(BaseModel):
    user_id: int
    unit_id: int
    occupancy_type: str = "owner"


class VisitorEntryCreate(BaseModel):
    resident_user_id: int
    visitor_name: str
    visitor_phone: str
    visitor_type: VisitorType
    purpose: str | None = None
    qr_token: str | None = None
    otp_code: str | None = None


class MonthlyBillingRequest(BaseModel):
    billing_month: str
    maintenance_charge: float
    car_slot_rate: float = 0
    bike_slot_rate: float = 0
    special_levy: float = 0
    late_penalty: float = 0


class PaymentCreate(BaseModel):
    invoice_id: int
    amount: float
    method: PaymentMethod
    provider: PaymentProvider
    reference_id: str


class CreatePaymentOrderRequest(BaseModel):
    invoice_id: int
    provider: PaymentProvider


class PaymentWebhookPayload(BaseModel):
    provider: PaymentProvider
    payload: dict
    signature: str | None = None


class VendorCreate(BaseModel):
    name: str
    category: str
    contact_name: str
    contact_phone: str


class AssetCreate(BaseModel):
    society_id: int | None = None
    name: str
    category: str
    location: str
    vendor_id: int | None = None
    manufacturer: str | None = None
    model_number: str | None = None
    purchase_value: float = 0
    installed_at: datetime | None = None
    warranty_expires_at: datetime | None = None
    amc_expires_at: datetime | None = None
    maintenance_cycle_days: int = 90
    status: str = "active"


class AssetRead(AssetCreate):
    id: int
    society_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class InventoryItemCreate(BaseModel):
    society_id: int | None = None
    name: str
    sku: str
    category: str
    location: str = "main store"
    quantity: float = 0
    min_quantity: float = 0
    unit_cost: float = 0
    vendor_id: int | None = None


class InventoryItemUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    location: str | None = None
    quantity: float | None = None
    min_quantity: float | None = None
    unit_cost: float | None = None
    vendor_id: int | None = None


class InventoryItemRead(InventoryItemCreate):
    id: int
    society_id: int
    updated_at: datetime
    created_at: datetime
    needs_reorder: bool = False
    stock_value: float = 0

    class Config:
        from_attributes = True


class PurchaseRequestCreate(BaseModel):
    society_id: int | None = None
    vendor_id: int | None = None
    title: str
    description: str | None = None
    amount: float = 0
    approval_level: str = "committee"


class PurchaseRequestDecision(BaseModel):
    status: str = Field(pattern="^(approved|rejected|pending)$")


class PurchaseRequestRead(PurchaseRequestCreate):
    id: int
    society_id: int
    requested_by_user_id: int
    status: str
    approved_by_user_id: int | None = None
    approved_at: datetime | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class StaffMemberCreate(BaseModel):
    society_id: int | None = None
    full_name: str
    phone: str
    role: str
    department: str | None = None
    shift_name: str | None = None
    id_proof_type: str | None = None
    id_proof_number: str | None = None
    passcode: str | None = None
    is_active: bool = True


class StaffMemberRead(StaffMemberCreate):
    id: int
    society_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class StaffAttendanceCreate(BaseModel):
    society_id: int | None = None
    staff_member_id: int
    status: str = "present"


class StaffAttendanceRead(StaffAttendanceCreate):
    id: int
    society_id: int
    check_in_at: datetime
    check_out_at: datetime | None = None

    class Config:
        from_attributes = True


class VehicleCreate(BaseModel):
    society_id: int | None = None
    unit_id: int | None = None
    owner_user_id: int | None = None
    registration_number: str
    vehicle_type: str = "car"
    sticker_number: str | None = None
    parking_slot: str | None = None
    is_active: bool = True


class VehicleRead(VehicleCreate):
    id: int
    society_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class GatePassCreate(BaseModel):
    society_id: int | None = None
    issued_to_name: str
    issued_to_phone: str | None = None
    pass_type: str = "material"
    purpose: str | None = None
    valid_from: datetime | None = None
    valid_until: datetime | None = None


class GatePassRead(GatePassCreate):
    id: int
    society_id: int
    status: str
    valid_from: datetime
    created_by_user_id: int | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class AmenityBookingCreate(BaseModel):
    society_id: int | None = None
    amenity_name: str
    unit_id: int | None = None
    resident_user_id: int | None = None
    starts_at: datetime
    ends_at: datetime
    amount: float = 0
    status: str = "booked"
    payment_status: str = "unpaid"


class AmenityBookingRead(AmenityBookingCreate):
    id: int
    society_id: int
    resident_user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ComplianceEventCreate(BaseModel):
    society_id: int | None = None
    event_type: str
    title: str
    description: str | None = None
    status: str = "open"
    due_at: datetime | None = None


class ComplianceEventRead(ComplianceEventCreate):
    id: int
    society_id: int
    closed_at: datetime | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class OperationsOverview(BaseModel):
    assets_total: int
    assets_with_amc_due: int
    inventory_items: int
    inventory_reorder_alerts: int
    staff_active: int
    staff_checked_in_today: int
    registered_vehicles: int
    active_gate_passes: int
    open_purchase_requests: int
    amenity_bookings_upcoming: int
    open_compliance_events: int
    privacy_events_open: int
    low_stock_items: list[InventoryItemRead]
    upcoming_amc_assets: list[AssetRead]


class TicketCreate(BaseModel):
    resident_user_id: int
    title: str
    description: str
    media_url: str | None = None


class TicketUpdateStatus(BaseModel):
    status: TicketStatus
    assigned_vendor_id: int | None = None


class WhatsAppMessageRequest(BaseModel):
    user_id: int
    provider: WhatsAppProvider | None = None
    message: str


class ERPSuiteCapability(BaseModel):
    key: str
    name: str
    description: str
    status: str
    features: list[str]


class WorkflowDefinitionRead(BaseModel):
    id: int
    key: str
    name: str
    trigger: str
    definition: str
    is_active: bool = True

    class Config:
        from_attributes = True


class AIAutomationJobRead(BaseModel):
    key: str
    name: str
    description: str
    status: str = "ready"
    confidence_score: float
    scheduled_for: datetime | None = None

    class Config:
        from_attributes = True


class IntegrationEndpointRead(BaseModel):
    id: int
    name: str
    provider: str
    status: str
    webhook_url: str | None = None

    class Config:
        from_attributes = True


class ERPSuiteOverview(BaseModel):
    platform: str
    architecture: list[str]
    modules: list[ERPSuiteCapability]
    ai_automations: list[AIAutomationJobRead]
    workflows: list[WorkflowDefinitionRead]
    integrations: list[IntegrationEndpointRead]
    deployment_targets: list[str]
    security_controls: list[str]


class TenantRead(BaseModel):
    id: int
    uuid: str
    name: str
    slug: str
    region: str
    plan: str
    is_active: bool

    class Config:
        from_attributes = True


class ERPRecordCreate(BaseModel):
    module_key: str
    record_type: str
    title: str
    status: str = "draft"
    payload_json: str = "{}"


class ERPRecordUpdate(BaseModel):
    title: str | None = None
    status: str | None = None
    payload_json: str | None = None


class ERPRecordRead(BaseModel):
    id: int
    uuid: str
    tenant_key: str
    module_key: str
    record_type: str
    title: str
    status: str
    payload_json: str
    owner_user_id: int | None = None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    class Config:
        from_attributes = True


class NotificationRead(BaseModel):
    id: int
    uuid: str
    title: str
    body: str
    channel: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================
# SOCIETY360 ENHANCEMENT SCHEMAS - Phase 1 Features
# ============================================================


class VisitorApprovalCreate(BaseModel):
    visitor_log_id: int
    approval_status: str = "pending"  # pending, approved, rejected
    vehicle_number: str | None = None
    vehicle_type: str | None = None
    parking_slot: str | None = None


class VisitorApprovalUpdate(BaseModel):
    approval_status: str
    vehicle_number: str | None = None
    vehicle_type: str | None = None
    parking_slot: str | None = None
    rejection_reason: str | None = None


class VisitorApprovalRead(BaseModel):
    id: int
    visitor_log_id: int
    resident_user_id: int
    approval_status: str
    vehicle_number: str | None = None
    vehicle_type: str | None = None
    parking_slot: str | None = None
    pass_number: str | None = None
    approved_by_user_id: int | None = None
    rejection_reason: str | None = None
    approved_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MaintenanceCategoryCreate(BaseModel):
    name: str
    description: str | None = None
    icon: str | None = None
    color: str | None = None
    sort_order: int = 0


class MaintenanceCategoryRead(MaintenanceCategoryCreate):
    id: int
    society_id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class MaintenanceWorkLogCreate(BaseModel):
    ticket_id: int
    staff_user_id: int
    description: str
    hours_spent: float | None = None


class MaintenanceWorkLogRead(MaintenanceWorkLogCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class MaintenanceRatingCreate(BaseModel):
    ticket_id: int
    rating: float  # 1-5
    feedback: str | None = None


class MaintenanceRatingRead(MaintenanceRatingCreate):
    id: int
    rated_by_user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class AnnouncementEnhancedCreate(BaseModel):
    title: str
    content: str
    announcement_type: str = "notice"  # notice, meeting, event
    priority: str = "medium"  # low, medium, high
    scheduled_for: datetime | None = None
    expires_at: datetime | None = None


class AnnouncementEnhancedRead(BaseModel):
    id: int
    society_id: int
    title: str
    content: str
    announcement_type: str
    priority: str
    published_by_user_id: int
    status: str
    scheduled_for: datetime | None = None
    published_at: datetime | None = None
    expires_at: datetime | None = None
    view_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ForumPostEnhancedCreate(BaseModel):
    title: str
    content: str
    category: str = "general"
    tags: str = ""  # comma-separated


class ForumPostEnhancedRead(BaseModel):
    id: int
    society_id: int
    title: str
    content: str
    category: str
    author_user_id: int
    tags: str
    status: str
    is_moderated: bool
    reply_count: int
    view_count: int
    engagement_score: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BillCycleCreate(BaseModel):
    cycle_month: str  # YYYY-MM


class BillCycleRead(BillCycleCreate):
    id: int
    society_id: int
    is_generated: bool
    generated_at: datetime | None = None
    bill_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class ReceiptCreate(BaseModel):
    payment_id: int
    receipt_number: str


class ReceiptRead(ReceiptCreate):
    id: int
    generated_at: datetime
    generated_by_user_id: int
    pdf_url: str | None = None

    class Config:
        from_attributes = True


class AmenityCreate(BaseModel):
    name: str
    description: str | None = None
    capacity: int
    location: str | None = None
    rules: str | None = None
    booking_price: float = 0


class AmenityRead(AmenityCreate):
    id: int
    society_id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AmenityBookingCreate(BaseModel):
    amenity_id: int
    start_datetime: datetime
    end_datetime: datetime
    purpose: str | None = None
    notes: str | None = None


class AmenityBookingRead(AmenityBookingCreate):
    id: int
    resident_user_id: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================
# PHOTO GALLERY & ENHANCED NOTICES - From external repo integration
# ============================================================


class PhotoGalleryAlbumCreate(BaseModel):
    title: str
    description: str | None = None
    cover_image_url: str | None = None
    is_published: bool = True
    sort_order: int = 0


class PhotoGalleryAlbumRead(BaseModel):
    id: int
    society_id: int
    title: str
    description: str | None = None
    cover_image_url: str | None = None
    is_published: bool
    sort_order: int
    created_by_user_id: int
    image_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PhotoGalleryImageCreate(BaseModel):
    album_id: int
    title: str | None = None
    image_url: str
    thumbnail_url: str | None = None
    description: str | None = None
    sort_order: int = 0


class PhotoGalleryImageRead(BaseModel):
    id: int
    album_id: int
    title: str | None = None
    image_url: str
    thumbnail_url: str | None = None
    description: str | None = None
    sort_order: int
    is_published: bool
    uploaded_by_user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class NoticeEnhancedCreate(BaseModel):
    title: str
    notice_type: str = "general"  # general, event, emergency, meeting, holiday
    message: str
    file_url: str | None = None
    is_urgent: bool = False
    is_published: bool = True
    expires_at: datetime | None = None


class NoticeEnhancedRead(BaseModel):
    id: int
    society_id: int
    title: str
    notice_type: str
    message: str
    file_url: str | None = None
    is_urgent: bool
    is_published: bool
    published_by_user_id: int
    published_at: datetime
    expires_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
