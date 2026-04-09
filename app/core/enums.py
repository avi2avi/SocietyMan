from enum import Enum


class Role(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    RESIDENT = "resident"
    GATEKEEPER = "gatekeeper"
    VENDOR = "vendor"


class TicketStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"


class PaymentMethod(str, Enum):
    UPI = "upi"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    NET_BANKING = "net_banking"


class PaymentProvider(str, Enum):
    RAZORPAY = "razorpay"
    STRIPE = "stripe"


class VisitorType(str, Enum):
    GUEST = "guest"
    DELIVERY = "delivery"


class WhatsAppProvider(str, Enum):
    META = "meta"
    TWILIO = "twilio"
    GUPSHUP = "gupshup"
