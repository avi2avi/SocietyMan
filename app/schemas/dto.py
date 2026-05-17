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
        orm_mode = True


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
        orm_mode = True


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
        orm_mode = True


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
