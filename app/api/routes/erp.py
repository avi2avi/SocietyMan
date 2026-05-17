from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.enums import Role
from app.models.entities import AIAutomationJob, AuditLog, ERPRecord, IntegrationEndpoint, Notification, Tenant, User, WorkflowDefinition
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
