from pydantic import BaseModel, EmailStr

from app.core.enums import PaymentMethod, Role, TicketStatus, VisitorType


class UserCreate(BaseModel):
    full_name: str
    phone: str
    email: EmailStr
    role: Role
    emergency_contact_name: str | None = None
    emergency_contact_phone: str | None = None


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
    reference_id: str


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
