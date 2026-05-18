from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.enums import Role, VisitorType, PaymentMethod, PaymentProvider
from app.core.security import hash_password
from app.models.entities import AIAutomationJob, AuditLog, ERPRecord, IntegrationEndpoint, Invoice, Notification, Payment, ResidentProfile, Society, Tenant, Unit, User, VisitorLog, WorkflowDefinition
from app.schemas.dto import (
    AIAutomationJobRead,
    ERPRecordCreate,
    ERPRecordRead,
    ERPRecordUpdate,
    ERPSuiteCapability,
    ERPSuiteOverview,
    IntegrationEndpointRead,
    NotificationRead,
    TenantRead,
    WorkflowDefinitionRead,
)

router = APIRouter(prefix="/erp", tags=["Society ERP"])

CORE_MODULES = [
    {
        "key": "resident-unit-management",
        "name": "Residents, Units & Tenants",
        "description": "Society onboarding, towers/units, owners, tenants, families, move-in/move-out records, emergency contacts, and approval flows.",
        "status": "foundation",
        "features": ["society-onboarding", "unit-master", "owner-tenant-records", "move-in-out", "family-profiles", "resident-approvals"],
    },
    {
        "key": "gate-security",
        "name": "Gate, Visitor & Security",
        "description": "Visitor logs, QR/OTP entry, delivery tracking, gate pass management, guard workflows, and downloadable movement reports.",
        "status": "foundation",
        "features": ["visitor-entry-exit", "qr-otp", "delivery-log", "gate-passes", "guard-dashboard", "movement-reports"],
    },
    {
        "key": "vehicle-parking",
        "name": "Vehicle & Parking",
        "description": "Resident vehicles, sticker numbers, parking slots, movement logs, and unauthorized vehicle tracking.",
        "status": "api-ready",
        "features": ["vehicle-master", "parking-slots", "stickers", "movement-log", "access-control"],
    },
    {
        "key": "staff-daily-help",
        "name": "Staff & Daily Help",
        "description": "Service provider registration, ID proof, passcodes, departments, shifts, attendance, and daily help availability.",
        "status": "api-ready",
        "features": ["staff-master", "daily-help", "id-proof", "passcode", "attendance", "shift-roster"],
    },
    {
        "key": "maintenance-billing-accounting",
        "name": "Maintenance Billing & Accounting",
        "description": "Auto bill generation, invoices, resident statements, dues, payments, ledgers, expenses, vendor bills, and audit reports.",
        "status": "foundation",
        "features": ["auto-billing", "resident-statements", "dues", "online-payments", "general-ledger", "vendor-expenses", "audit-reports"],
    },
    {
        "key": "helpdesk-complaints",
        "name": "Helpdesk & Complaints",
        "description": "Category-wise resident complaints, photo evidence, assignment, status tracking, staff/vendor routing, and closure history.",
        "status": "foundation",
        "features": ["complaints", "categories", "photo-evidence", "assignment", "status-tracking", "resident-updates"],
    },
    {
        "key": "amenities-facility-booking",
        "name": "Amenities & Facility Booking",
        "description": "Clubhouse and amenity bookings, slot availability, resident payments, booking status, and double-booking controls.",
        "status": "api-ready",
        "features": ["facility-booking", "slot-calendar", "resident-payments", "booking-rules", "availability"],
    },
    {
        "key": "assets-inventory-procurement",
        "name": "Assets, Inventory & Procurement",
        "description": "Society assets, AMC reminders, inventory stock, reorder alerts, purchase requests, and approval hierarchy.",
        "status": "api-ready",
        "features": ["asset-master", "amc-reminders", "inventory", "reorder-alerts", "purchase-requests", "committee-approvals"],
    },
    {
        "key": "communication-documents",
        "name": "Communication & Documents",
        "description": "Notices, email/WhatsApp updates, resident directory controls, society documents, agreements, and circulars.",
        "status": "scaffolded",
        "features": ["notices", "email", "whatsapp", "documents", "rental-agreements", "masked-directory"],
    },
    {
        "key": "committee-compliance-reports",
        "name": "Committee, Compliance & Reports",
        "description": "Committee access controls, privacy/data requests, audit logs, CSV/PDF/XLSX reports, and operational dashboards.",
        "status": "demo-ready",
        "features": ["module-access", "privacy-events", "audit-log", "reports", "exports", "operations-dashboard"],
    },
]

AI_AUTOMATIONS = [
    {
        "key": "dues-reminder",
        "name": "Maintenance Dues Reminder",
        "description": "Identifies unpaid invoices and drafts resident email/WhatsApp reminders for committee approval.",
        "confidence_score": 0.94,
    },
    {
        "key": "vendor-invoice-review",
        "name": "Vendor Invoice Review",
        "description": "Flags duplicate vendor invoices, unusual expenses, and missing GST/TDS information before payment.",
        "confidence_score": 0.91,
    },
    {
        "key": "complaint-routing",
        "name": "Complaint Routing",
        "description": "Suggests the right department, staff member, or vendor based on complaint category and workload.",
        "confidence_score": 0.88,
    },
    {
        "key": "inventory-reorder",
        "name": "Society Inventory Reorder",
        "description": "Recommends reorder quantities for security, housekeeping, electrical, plumbing, and maintenance stock.",
        "confidence_score": 0.9,
    },
    {
        "key": "amc-renewal",
        "name": "AMC Renewal Watch",
        "description": "Highlights assets with warranty or AMC expiry approaching in the next 30 days.",
        "confidence_score": 0.87,
    },
]

SAMPLE_WORKFLOWS = [
    {
        "key": "purchase-approval",
        "name": "Committee Purchase Approval",
        "trigger": "purchase_request.created",
        "definition": "Route purchase requests to the society committee, require higher approval above configured amount, then notify vendor/accounts.",
    },
    {
        "key": "invoice-follow-up",
        "name": "Maintenance Dues Follow-up",
        "trigger": "invoice.overdue",
        "definition": "Send resident email/WhatsApp reminder and create a collection task when maintenance invoices are overdue by 7 days.",
    },
    {
        "key": "complaint-auto-assignment",
        "name": "Complaint Auto Assignment",
        "trigger": "ticket.created",
        "definition": "Assign plumbing/electrical/security complaints to the right department and escalate when SLA is breached.",
    },
]


def _tenant_scope(current_user: User) -> str:
    return f"society:{current_user.society_id}" if current_user.society_id else "platform"


@router.get("/capabilities", response_model=ERPSuiteOverview)
def get_capabilities() -> ERPSuiteOverview:
    """Public product blueprint used by the landing page and API documentation."""

    return ERPSuiteOverview(
        platform="SocietyMan Society ERP",
        architecture=[
            "FastAPI REST API for society onboarding, residents, security, billing, helpdesk, amenities, staff, and committee workflows",
            "React/Vite admin dashboard for developer admins, society admins, and module-level access control",
            "PostgreSQL primary database with SQLite local compatibility, Redis-ready background jobs, and report exports",
            "Society-scoped RBAC, approval trails, soft-delete capable records, SMTP/WhatsApp hooks, and Docker deployment",
        ],
        modules=[ERPSuiteCapability(**module) for module in CORE_MODULES],
        ai_automations=[AIAutomationJobRead(**job, status="ready", scheduled_for=datetime.utcnow()) for job in AI_AUTOMATIONS],
        workflows=[WorkflowDefinitionRead(**workflow, id=index + 1, is_active=True) for index, workflow in enumerate(SAMPLE_WORKFLOWS)],
        integrations=[
            IntegrationEndpointRead(id=1, name="Stripe Billing", provider="stripe", status="configured-by-env", webhook_url="/api/v1/payments/webhooks/stripe"),
            IntegrationEndpointRead(id=2, name="Razorpay + UPI", provider="razorpay", status="configured-by-env", webhook_url="/api/v1/payments/webhooks/razorpay"),
            IntegrationEndpointRead(id=3, name="WhatsApp Messaging", provider="meta/twilio/gupshup", status="configured-by-env", webhook_url="/api/v1/communications/whatsapp"),
            IntegrationEndpointRead(id=4, name="SMTP Email", provider="smtp", status="configured-by-env", webhook_url="/api/v1/auth/login"),
            IntegrationEndpointRead(id=5, name="Gate Hardware / QR Scanner", provider="security", status="planned", webhook_url="/api/v1/visitors/entry"),
        ],
        deployment_targets=["Docker Compose", "Vercel", "Render", "Railway", "GitHub Actions CI/CD"],
        security_controls=["OWASP headers", "rate limiting plan", "secure cookies", "RBAC", "CSRF-ready forms", "SQLAlchemy parameterization", "audit logs"],
    )


@router.get("/tenants", response_model=list[TenantRead])
def list_tenants(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="Developer admin access required")
    return db.query(Tenant).order_by(Tenant.created_at.desc()).all()


@router.post("/records", response_model=ERPRecordRead)
def create_record(payload: ERPRecordCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    record = ERPRecord(
        tenant_key=_tenant_scope(current_user),
        module_key=payload.module_key,
        record_type=payload.record_type,
        title=payload.title,
        status=payload.status,
        payload_json=payload.payload_json,
        owner_user_id=current_user.id,
    )
    db.add(record)
    db.add(AuditLog(actor_user_id=current_user.id, tenant_key=record.tenant_key, action="erp.record.created", entity_type="ERPRecord", metadata_json=payload.payload_json))
    db.commit()
    db.refresh(record)
    return record


@router.get("/records", response_model=list[ERPRecordRead])
def list_records(
    module_key: str | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(ERPRecord).filter(ERPRecord.deleted_at.is_(None))
    if current_user.role != Role.ADMIN:
        query = query.filter(ERPRecord.tenant_key == _tenant_scope(current_user))
    if module_key:
        query = query.filter(ERPRecord.module_key == module_key)
    return query.order_by(ERPRecord.updated_at.desc()).limit(200).all()


@router.patch("/records/{record_id}", response_model=ERPRecordRead)
def update_record(record_id: int, payload: ERPRecordUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    record = db.get(ERPRecord, record_id)
    if not record or record.deleted_at:
        raise HTTPException(status_code=404, detail="ERP record not found")
    if current_user.role != Role.ADMIN and record.tenant_key != _tenant_scope(current_user):
        raise HTTPException(status_code=403, detail="Record is outside your tenant scope")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(record, key, value)
    record.updated_at = datetime.utcnow()
    db.add(AuditLog(actor_user_id=current_user.id, tenant_key=record.tenant_key, action="erp.record.updated", entity_type="ERPRecord", entity_id=str(record.id)))
    db.commit()
    db.refresh(record)
    return record


@router.delete("/records/{record_id}", response_model=ERPRecordRead)
def soft_delete_record(record_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    record = db.get(ERPRecord, record_id)
    if not record or record.deleted_at:
        raise HTTPException(status_code=404, detail="ERP record not found")
    if current_user.role != Role.ADMIN and record.tenant_key != _tenant_scope(current_user):
        raise HTTPException(status_code=403, detail="Record is outside your tenant scope")
    record.deleted_at = datetime.utcnow()
    record.updated_at = datetime.utcnow()
    db.add(AuditLog(actor_user_id=current_user.id, tenant_key=record.tenant_key, action="erp.record.deleted", entity_type="ERPRecord", entity_id=str(record.id)))
    db.commit()
    db.refresh(record)
    return record


@router.get("/notifications", response_model=list[NotificationRead])
def notification_center(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Notification).filter(Notification.user_id == current_user.id).order_by(Notification.created_at.desc()).limit(100).all()


@router.post("/demo/seed")
def seed_society_demo(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="Developer admin access required")

    demo_society = db.query(Society).filter(Society.name == "Green Valley Apartments").first()
    if not demo_society:
        demo_society = Society(
            name="Green Valley Apartments",
            address="123 Main Street, Mumbai, Maharashtra 400001",
            city="Mumbai",
            state="Maharashtra",
            pincode="400001",
            admin_contact_name="Green Valley Admin",
            admin_contact_email="admin@society.com",
            admin_contact_phone="9999999999",
            is_approved=True,
            approved_at=datetime.utcnow(),
        )
        db.add(demo_society)
        db.flush()

    sample_users = [
        {
            "full_name": "Society Admin",
            "email": "admin@society.com",
            "phone": "9999999999",
            "password": "admin123",
            "role": Role.SOCIETY_ADMIN,
            "is_active": True,
            "access_erp": True,
            "access_gatekeeper": True,
            "access_billing": True,
            "access_payments": True,
            "access_communications": True,
            "access_reports": True,
            "access_documents": True,
            "access_visitor_management": True,
        },
        {
            "full_name": "Society Gatekeeper",
            "email": "gatekeeper@society.com",
            "phone": "9999990001",
            "password": "gate123",
            "role": Role.GATEKEEPER,
            "is_active": True,
            "access_gatekeeper": True,
            "access_visitor_management": True,
        },
        {
            "full_name": "Priya Sharma",
            "email": "resident1@society.com",
            "phone": "9000000001",
            "password": "resident123",
            "role": Role.RESIDENT,
            "is_active": True,
        },
        {
            "full_name": "Rahul Verma",
            "email": "resident2@society.com",
            "phone": "9000000002",
            "password": "resident123",
            "role": Role.RESIDENT,
            "is_active": True,
        },
        {
            "full_name": "Anjali Patel",
            "email": "resident3@society.com",
            "phone": "9000000003",
            "password": "resident123",
            "role": Role.RESIDENT,
            "is_active": True,
        },
        {
            "full_name": "Vikram Singh",
            "email": "resident4@society.com",
            "phone": "9000000004",
            "password": "resident123",
            "role": Role.RESIDENT,
            "is_active": True,
        },
        {
            "full_name": "Sneha Reddy",
            "email": "resident5@society.com",
            "phone": "9000000005",
            "password": "resident123",
            "role": Role.RESIDENT,
            "is_active": True,
        },
    ]

    for user_data in sample_users:
        existing_user = db.query(User).filter(User.email == user_data["email"]).first()
        if not existing_user:
            db.add(
                User(
                    full_name=user_data["full_name"],
                    email=user_data["email"],
                    phone=user_data["phone"],
                    password_hash=hash_password(user_data["password"]),
                    role=user_data["role"],
                    society_id=demo_society.id,
                    is_active=user_data["is_active"],
                    access_erp=user_data.get("access_erp", False),
                    access_gatekeeper=user_data.get("access_gatekeeper", False),
                    access_billing=user_data.get("access_billing", False),
                    access_payments=user_data.get("access_payments", False),
                    access_communications=user_data.get("access_communications", False),
                    access_reports=user_data.get("access_reports", False),
                    access_documents=user_data.get("access_documents", False),
                    access_visitor_management=user_data.get("access_visitor_management", False),
                )
            )

    tenant = db.query(Tenant).filter(Tenant.slug == "green-heights-rwa").first()
    if not tenant:
        tenant = Tenant(name="Green Heights RWA", slug="green-heights-rwa", region="IN", plan="society-pro")
        db.add(tenant)
        db.flush()

    existing = db.query(ERPRecord).filter(ERPRecord.tenant_key == "platform", ERPRecord.module_key == "helpdesk-complaints", ERPRecord.title == "Water leakage in Tower A").first()
    if not existing:
        demo_records = [
            ERPRecord(tenant_key="platform", module_key="helpdesk-complaints", record_type="ticket", title="Water leakage in Tower A", status="in_progress", payload_json='{"category": "plumbing", "priority": "high"}'),
            ERPRecord(tenant_key="platform", module_key="assets-inventory-procurement", record_type="stock_alert", title="Security register books below reorder threshold", status="needs_action", payload_json='{"sku": "SEC-REG-01", "quantity": 3, "min_quantity": 10}'),
            ERPRecord(tenant_key="platform", module_key="maintenance-billing-accounting", record_type="dues_alert", title="12 flats have overdue maintenance", status="review", payload_json='{"amount": 86000, "currency": "INR"}'),
        ]
        db.add_all(demo_records)

    for job in AI_AUTOMATIONS:
        if not db.query(AIAutomationJob).filter(AIAutomationJob.key == job["key"]).first():
            db.add(AIAutomationJob(**job, status="ready", scheduled_for=datetime.utcnow() + timedelta(minutes=15)))
    for workflow in SAMPLE_WORKFLOWS:
        if not db.query(WorkflowDefinition).filter(WorkflowDefinition.key == workflow["key"]).first():
            db.add(WorkflowDefinition(**workflow, tenant_key="platform"))

    db.add(Notification(user_id=current_user.id, tenant_key="platform", title="Society demo seeded", body="Helpdesk, inventory, billing, AI, and committee workflow demo records are ready.", channel="in-app"))
    db.commit()
    return {"status": "ok", "message": "Society ERP demo data seeded"}


@router.post("/demo/comprehensive-seed")
def seed_comprehensive_data(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create 5+ societies with 50+ members, units, visitor logs, and bills for last 12 months"""
    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="Developer admin access required")

    # Define 5 societies with their details
    societies_data = [
        {
            "name": "Green Valley Apartments",
            "address": "123 Main Street, Bandra",
            "city": "Mumbai",
            "state": "Maharashtra",
            "pincode": "400050",
            "admin_email": "admin@greenvalle.com",
        },
        {
            "name": "Skyline Towers",
            "address": "456 Business Road, Gurgaon",
            "city": "Gurgaon",
            "state": "Haryana",
            "pincode": "122001",
            "admin_email": "admin@skyline.com",
        },
        {
            "name": "Westend Park",
            "address": "789 Park Avenue, Bangalore",
            "city": "Bangalore",
            "state": "Karnataka",
            "pincode": "560001",
            "admin_email": "admin@westend.com",
        },
        {
            "name": "Riverside Heights",
            "address": "321 River Road, Delhi",
            "city": "Delhi",
            "state": "Delhi",
            "pincode": "110001",
            "admin_email": "admin@riverside.com",
        },
        {
            "name": "Pearl Residency",
            "address": "654 Marine Drive, Chennai",
            "city": "Chennai",
            "state": "Tamil Nadu",
            "pincode": "600001",
            "admin_email": "admin@pearl.com",
        },
    ]

    created_societies = []
    total_members = 0
    total_visitors = 0
    total_bills = 0

    for society_data in societies_data:
        # Check if society already exists
        existing_society = db.query(Society).filter(Society.name == society_data["name"]).first()
        if existing_society:
            created_societies.append(existing_society)
            continue

        # Create society
        society = Society(
            name=society_data["name"],
            address=society_data["address"],
            city=society_data["city"],
            state=society_data["state"],
            pincode=society_data["pincode"],
            admin_contact_name=f"{society_data['name']} Admin",
            admin_contact_email=society_data["admin_email"],
            admin_contact_phone="9999999999",
            is_approved=True,
            approved_at=datetime.utcnow(),
        )
        db.add(society)
        db.flush()
        created_societies.append(society)

        # Create units for this society (10 units)
        units_per_society = []
        buildings = ["Tower A", "Tower B"]
        for building in buildings:
            for unit_num in range(1, 6):
                unit = Unit(
                    building=building,
                    unit_number=f"{unit_num}01",
                    unit_type="residential",
                    parking_car_slots=1,
                    parking_bike_slots=1,
                )
                db.add(unit)
                db.flush()
                units_per_society.append(unit)

        # Create residents (10-12 per society) - total 50-60 members
        first_names = ["Rajesh", "Priya", "Arun", "Sneha", "Vikram", "Anjali", "Rahul", "Neha", "Karan", "Pooja", "Deepak", "Zara"]
        last_names = ["Sharma", "Patel", "Verma", "Singh", "Reddy", "Kumar", "Nair", "Iyer", "Gupta", "Desai"]

        for idx, (first_name, last_name) in enumerate([(first_names[i], last_names[i % len(last_names)]) for i in range(10)]):
            email = f"resident{idx+1}@{society_data['name'].lower().replace(' ', '')}.com"
            phone = f"9{9000000000 + idx}"

            # Check if user already exists
            existing_user = db.query(User).filter(User.email == email).first()
            if existing_user:
                continue

            # Create resident user
            user = User(
                full_name=f"{first_name} {last_name}",
                email=email,
                phone=phone,
                password_hash=hash_password("resident123"),
                role=Role.RESIDENT,
                society_id=society.id,
                is_active=True,
            )
            db.add(user)
            db.flush()
            total_members += 1

            # Create resident profile with unit assignment
            resident_profile = ResidentProfile(
                user_id=user.id,
                unit_id=units_per_society[idx % len(units_per_society)].id,
                occupancy_type="owner",
                move_in_date=datetime.utcnow() - timedelta(days=365),
            )
            db.add(resident_profile)

            # Create visitor logs for this resident (2-3 visitors in past 12 months)
            visitor_types = [VisitorType.GUEST, VisitorType.DELIVERY]
            visitor_names = ["Friend", "Delivery Boy", "Family Member", "Service Provider", "Guest"]
            for visitor_idx in range(2):
                entry_date = datetime.utcnow() - timedelta(days=365 - (visitor_idx * 60))
                visitor = VisitorLog(
                    resident_user_id=user.id,
                    visitor_name=visitor_names[visitor_idx % len(visitor_names)],
                    visitor_phone=f"98{7000000 + visitor_idx:07d}",
                    visitor_type=visitor_types[visitor_idx % len(visitor_types)],
                    purpose=f"Visit {visitor_idx + 1}",
                    entry_at=entry_date,
                    exit_at=entry_date + timedelta(hours=2),
                )
                db.add(visitor)
                total_visitors += 1

            # Create invoices for last 12 months (12 bills per resident)
            for month_offset in range(12):
                invoice_date = datetime.utcnow() - timedelta(days=30 * (11 - month_offset))
                billing_month = invoice_date.strftime("%Y-%m")

                # Check if invoice already exists
                existing_invoice = db.query(Invoice).filter(
                    Invoice.unit_id == units_per_society[idx % len(units_per_society)].id,
                    Invoice.billing_month == billing_month
                ).first()
                if existing_invoice:
                    continue

                # Create invoice
                maintenance_charge = 3500
                parking_charge = 500
                special_levy = 1000 if month_offset % 3 == 0 else 0
                late_penalty = 0
                adjustments = -500 if month_offset % 4 == 0 else 0
                total_amount = maintenance_charge + parking_charge + special_levy + late_penalty + adjustments

                invoice = Invoice(
                    unit_id=units_per_society[idx % len(units_per_society)].id,
                    billing_month=billing_month,
                    maintenance_charge=maintenance_charge,
                    parking_charge=parking_charge,
                    special_levy=special_levy,
                    late_penalty=late_penalty,
                    adjustments=adjustments,
                    total_amount=total_amount,
                    status="paid" if month_offset > 3 else ("pending" if month_offset < 2 else "unpaid"),
                )
                db.add(invoice)
                db.flush()
                total_bills += 1

                # Create payment for some invoices (70% paid)
                if month_offset > 3 and (month_offset % 3 != 0):  # Skip some months
                    payment = Payment(
                        invoice_id=invoice.id,
                        amount=total_amount,
                        method=PaymentMethod.UPI if month_offset % 2 == 0 else PaymentMethod.NET_BANKING,
                        provider=PaymentProvider.RAZORPAY,
                        provider_order_id=f"order_{invoice.id}_{month_offset}",
                        provider_payment_id=f"pay_{invoice.id}_{month_offset}",
                        reference_id=f"ref_{invoice.id}_{month_offset}",
                        paid_at=invoice_date + timedelta(days=5),
                    )
                    db.add(payment)

    # Create tenant record
    tenant = db.query(Tenant).filter(Tenant.slug == "societyman-demo").first()
    if not tenant:
        tenant = Tenant(name="SocietyMan Demo", slug="societyman-demo", region="IN", plan="society-pro")
        db.add(tenant)

    db.commit()

    return {
        "status": "ok",
        "message": "Comprehensive demo data seeded successfully",
        "data": {
            "societies_created": len(created_societies),
            "total_members": total_members,
            "total_visitor_logs": total_visitors,
            "total_bills": total_bills,
            "summary": f"Created {len(created_societies)} societies with {total_members} members, {total_visitors} visitor logs, and {total_bills} bills"
        }
    }


@router.websocket("/ws/notifications/{user_id}")
async def notification_socket(websocket: WebSocket, user_id: int):
    await websocket.accept()
    try:
        await websocket.send_json({"type": "connected", "user_id": user_id, "message": "Realtime society notification channel connected"})
        while True:
            await websocket.receive_text()
            await websocket.send_json({"type": "heartbeat", "message": "SocietyMan realtime channel is alive"})
    except WebSocketDisconnect:
        return
