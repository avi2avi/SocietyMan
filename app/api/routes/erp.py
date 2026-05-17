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

router = APIRouter(prefix="/erp", tags=["Enterprise ERP"])

CORE_MODULES = [
    {
        "key": "auth-security",
        "name": "Authentication & Security",
        "description": "JWT sessions, Google OAuth-ready identity, RBAC, 2FA, audit logs, device history, and IP monitoring.",
        "status": "foundation",
        "features": ["login", "register", "2fa", "email-verification", "password-reset", "audit-logs", "ip-monitoring"],
    },
    {
        "key": "dashboard-ai",
        "name": "Executive Dashboard",
        "description": "Real-time KPIs, revenue charts, department overviews, custom widgets, and AI insights.",
        "status": "demo-ready",
        "features": ["realtime-analytics", "kpi-widgets", "ai-insights", "drag-drop-widgets", "dark-light-mode"],
    },
    {
        "key": "hrm",
        "name": "Human Resource Management",
        "description": "Employee records, attendance, leave, payroll, recruitment, shifts, reviews, and self-service.",
        "status": "scaffolded",
        "features": ["employees", "attendance", "leave", "payroll", "recruitment", "performance", "shift-scheduling"],
    },
    {
        "key": "crm",
        "name": "Customer Relationship Management",
        "description": "Lead pipeline, customer interactions, automated follow-ups, WhatsApp/email integration, and sales forecasts.",
        "status": "scaffolded",
        "features": ["leads", "pipeline", "contacts", "whatsapp", "email", "forecasting", "follow-ups"],
    },
    {
        "key": "inventory",
        "name": "Inventory & Warehouse",
        "description": "Products, barcodes, stock transfers, purchase orders, suppliers, batches, expiry, and AI stock prediction.",
        "status": "scaffolded",
        "features": ["catalog", "barcode", "warehouses", "transfers", "alerts", "purchase-orders", "batch-expiry"],
    },
    {
        "key": "finance",
        "name": "Accounting & Finance",
        "description": "Ledger, AP/AR, GST India support, invoices, expenses, reconciliation, tax reports, P&L, and balance sheet.",
        "status": "foundation",
        "features": ["general-ledger", "ap-ar", "gst", "invoicing", "expenses", "reconciliation", "financial-statements"],
    },
    {
        "key": "projects-manufacturing",
        "name": "Projects & Manufacturing",
        "description": "Kanban/Gantt, time tracking, collaboration, BOM, work orders, maintenance, quality checks, and production analytics.",
        "status": "scaffolded",
        "features": ["kanban", "gantt", "time-tracking", "bom", "work-orders", "maintenance", "quality"],
    },
    {
        "key": "procurement-pos-commerce",
        "name": "Procurement, POS & Commerce",
        "description": "Vendors, RFQs, approval chains, offline POS, UPI/QR payments, receipts, and Shopify/Woo/Amazon sync.",
        "status": "scaffolded",
        "features": ["vendors", "rfq", "approvals", "offline-pos", "thermal-print", "upi", "commerce-sync"],
    },
    {
        "key": "documents-communications",
        "name": "Documents & Communications",
        "description": "Cloud uploads, OCR, e-signatures, version history, internal chat, meetings, SMS/email/push notifications.",
        "status": "scaffolded",
        "features": ["uploads", "ocr", "digital-signatures", "versions", "chat", "video", "notifications"],
    },
    {
        "key": "automation-reporting",
        "name": "Automation & Reporting",
        "description": "Workflow builder, approval chains, scheduled jobs, custom reports, PDF/Excel/CSV exports, and AI summaries.",
        "status": "demo-ready",
        "features": ["workflow-builder", "approval-chains", "scheduled-jobs", "report-builder", "exports", "ai-summaries"],
    },
]

AI_AUTOMATIONS = [
    {
        "key": "chatbot",
        "name": "ERP AI Assistant",
        "description": "Conversational assistant that can answer operational questions and draft actions for human approval.",
        "confidence_score": 0.94,
    },
    {
        "key": "invoice-ocr",
        "name": "Invoice OCR Scanner",
        "description": "Extracts supplier, GSTIN, invoice lines, taxes, and due dates from uploaded invoices.",
        "confidence_score": 0.91,
    },
    {
        "key": "sales-forecasting",
        "name": "Sales Forecasting",
        "description": "Predicts revenue and pipeline risk from CRM activity, seasonality, and historical conversion.",
        "confidence_score": 0.88,
    },
    {
        "key": "inventory-prediction",
        "name": "Smart Inventory Prediction",
        "description": "Recommends reorder points and identifies likely stock-outs before they affect fulfillment.",
        "confidence_score": 0.9,
    },
    {
        "key": "finance-anomaly",
        "name": "Finance Anomaly Detection",
        "description": "Flags duplicate payments, unusual ledger entries, margin drops, and reconciliation anomalies.",
        "confidence_score": 0.87,
    },
]

SAMPLE_WORKFLOWS = [
    {
        "key": "purchase-approval",
        "name": "Purchase Approval Chain",
        "trigger": "purchase_order.created",
        "definition": "Request manager approval above ₹25,000, finance approval above ₹100,000, then notify procurement.",
    },
    {
        "key": "invoice-follow-up",
        "name": "Automated Invoice Follow-up",
        "trigger": "invoice.overdue",
        "definition": "Send email, WhatsApp reminder, and create a finance task when invoices are overdue by 7 days.",
    },
    {
        "key": "inventory-reorder",
        "name": "AI Inventory Reorder",
        "trigger": "inventory.forecast_below_threshold",
        "definition": "Generate supplier RFQ and route to warehouse manager for approval when forecasted stock is low.",
    },
]


def _tenant_scope(current_user: User) -> str:
    return f"society:{current_user.society_id}" if current_user.society_id else "platform"


@router.get("/capabilities", response_model=ERPSuiteOverview)
def get_capabilities() -> ERPSuiteOverview:
    """Public product blueprint used by the landing page and API documentation."""

    return ERPSuiteOverview(
        platform="SocietyMan Enterprise ERP",
        architecture=[
            "FastAPI REST API with OpenAPI/Swagger docs and WebSocket notification channel",
            "React/Vite dashboard ready to migrate module-by-module to Next.js + TypeScript",
            "PostgreSQL primary database with SQLite demo mode and Redis-ready caching hooks",
            "RBAC, tenant scoping, audit trails, soft-delete fields, environment-based config, and Docker deployment",
        ],
        modules=[ERPSuiteCapability(**module) for module in CORE_MODULES],
        ai_automations=[AIAutomationJobRead(**job, status="ready", scheduled_for=datetime.utcnow()) for job in AI_AUTOMATIONS],
        workflows=[WorkflowDefinitionRead(**workflow, id=index + 1, is_active=True) for index, workflow in enumerate(SAMPLE_WORKFLOWS)],
        integrations=[
            IntegrationEndpointRead(id=1, name="Stripe Billing", provider="stripe", status="configured-by-env", webhook_url="/api/v1/payments/webhooks/stripe"),
            IntegrationEndpointRead(id=2, name="Razorpay + UPI", provider="razorpay", status="configured-by-env", webhook_url="/api/v1/payments/webhooks/razorpay"),
            IntegrationEndpointRead(id=3, name="WhatsApp Messaging", provider="meta/twilio/gupshup", status="configured-by-env", webhook_url="/api/v1/communications/whatsapp"),
            IntegrationEndpointRead(id=4, name="Shopify/WooCommerce/Amazon", provider="commerce", status="planned", webhook_url="/api/v1/erp/integrations/commerce"),
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
def seed_enterprise_demo(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="Developer admin access required")

    tenant = db.query(Tenant).filter(Tenant.slug == "acme-global").first()
    if not tenant:
        tenant = Tenant(name="Acme Global Operations", slug="acme-global", region="IN", plan="enterprise")
        db.add(tenant)
        db.flush()

    existing = db.query(ERPRecord).filter(ERPRecord.tenant_key == "platform", ERPRecord.module_key == "crm", ERPRecord.title == "Enterprise expansion opportunity").first()
    if not existing:
        demo_records = [
            ERPRecord(tenant_key="platform", module_key="crm", record_type="lead", title="Enterprise expansion opportunity", status="qualified", payload_json='{"value": 1250000, "currency": "INR", "probability": 0.72}'),
            ERPRecord(tenant_key="platform", module_key="inventory", record_type="stock_alert", title="Barcode scanners below reorder threshold", status="needs_action", payload_json='{"sku": "SCAN-900", "forecast_days_left": 11}'),
            ERPRecord(tenant_key="platform", module_key="finance", record_type="anomaly", title="Duplicate supplier invoice detected", status="review", payload_json='{"supplier": "Northwind Traders", "risk": "high"}'),
        ]
        db.add_all(demo_records)

    for job in AI_AUTOMATIONS:
        if not db.query(AIAutomationJob).filter(AIAutomationJob.key == job["key"]).first():
            db.add(AIAutomationJob(**job, status="ready", scheduled_for=datetime.utcnow() + timedelta(minutes=15)))
    for workflow in SAMPLE_WORKFLOWS:
        if not db.query(WorkflowDefinition).filter(WorkflowDefinition.key == workflow["key"]).first():
            db.add(WorkflowDefinition(**workflow, tenant_key="platform"))

    db.add(Notification(user_id=current_user.id, tenant_key="platform", title="Enterprise demo seeded", body="CRM, inventory, finance, AI, and workflow demo records are ready.", channel="in-app"))
    db.commit()
    return {"status": "ok", "message": "Enterprise ERP demo data seeded"}


@router.websocket("/ws/notifications/{user_id}")
async def notification_socket(websocket: WebSocket, user_id: int):
    await websocket.accept()
    try:
        await websocket.send_json({"type": "connected", "user_id": user_id, "message": "Realtime ERP notification channel connected"})
        while True:
            await websocket.receive_text()
            await websocket.send_json({"type": "heartbeat", "message": "SocietyMan ERP realtime channel is alive"})
    except WebSocketDisconnect:
        return
