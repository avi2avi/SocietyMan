# SocietyMan — Housing Society Management Platform

SocietyMan is a modern, automation-first housing society management platform inspired by ADDA, MyGate, and ApnaComplex.

## Implemented in this revision

### Backend (FastAPI)
- Full authentication flow: register, login, refresh token rotation, logout/revoke.
- JWT access + refresh token support with secure password hashing.
- Payment gateway integration surface for Razorpay and Stripe.
- Webhook verification endpoints for both providers.
- WhatsApp provider integration abstraction for Meta, Twilio, and Gupshup.
- BI-grade reports in CSV, PDF, and XLSX formats.
- Background jobs scaffold using Arq for scheduled monthly billing and payment reminders.

### Frontend clients
- **React web dashboard** scaffold in `web-dashboard/`.
- **React Native (Expo) mobile app** scaffold in `mobile-app/`.

## Quick Start (Backend)
This repository includes:
- **Backend API (FastAPI)** for operations, billing, security, finance, and communication.
- **Modular domain models** covering residents, units, visitors, tickets, vendors, documents, and payments.
- **Automation service stubs** for WhatsApp notifications, AI insights, audit prep, and predictive maintenance.
- **Role-based access control (RBAC)** foundations for Admin, Manager, Resident, Gatekeeper, and Vendor.

## 1) Product Scope Coverage

### Core Modules
1. User & Role Management
2. Gatekeeper & Visitor Management (with QR/OTP hooks)
3. Billing & Maintenance
4. Online Payment Integration (provider-agnostic stubs)
5. Financial Management & Audit
6. Vendor & Bill Management
7. Parking Management
8. Staff & Daily Help Management
9. Communication (notices + messages)
10. Complaint / Ticket Management
11. Amenity & Facility Booking
12. Document Repository
13. Notifications
14. Admin Dashboard Metrics
15. Reports & Download Center (CSV now, PDF/Excel hook-ready)
16. Multi-platform readiness (Web + Mobile APIs)

### Innovation Layer (Included as service interfaces)
- WhatsApp notification integration interface
- AI financial insights engine scaffold
- Smart QR visitor entry workflow scaffold
- Automated audit export prep
- Predictive maintenance alerts

## 2) Tech Stack

- **Backend:** Python 3.11+, FastAPI, SQLAlchemy, Pydantic
- **Database:** PostgreSQL 16 primary database via SQLAlchemy + psycopg; SQLite remains only as a legacy demo override
- **Auth:** JWT-ready placeholder flow with role checks
- **Reports:** CSV export (expandable to PDF/XLSX)

## 3) Quick Start

```bash
docker compose up postgres redis -d
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API docs: `http://127.0.0.1:8000/docs`

> Developer admin account created on startup when missing:
> - Email: `admin@gmail.com`
> - Password: `Admin@123`
> - Verification code is emailed or written to `scripts/last_admin_code.txt` when SMTP is not configured.
>
> Default database:
> - PostgreSQL: `postgresql+psycopg://societyman:societyman@localhost:5432/societyman`
> - Start it with `docker compose up postgres redis -d` or run the full stack with `docker compose up --build`.
> - For legacy SQLite demos only, set `DATABASE_URL=sqlite:///./societyman.db`.

## Key API Endpoints

- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`
- `GET /api/v1/users/me`
- `POST /api/v1/payments/orders`
- `POST /api/v1/payments/webhooks/{provider}`
- `POST /api/v1/communications/whatsapp/send`
- `GET /api/v1/operations/overview`
- `POST /api/v1/operations/assets`
- `POST /api/v1/operations/inventory`
- `POST /api/v1/operations/staff`
- `POST /api/v1/operations/staff/attendance`
- `POST /api/v1/operations/vehicles`
- `POST /api/v1/operations/gate-passes`
- `POST /api/v1/operations/purchase-requests`
- `POST /api/v1/operations/amenity-bookings`
- `POST /api/v1/operations/compliance-events`
- `GET /api/v1/reports/financial-summary.pdf`
- `GET /api/v1/reports/financial-summary.xlsx`


## One-command local run (Docker Compose)

```bash
docker compose up --build
```

Then open:
- Backend API: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- Web dashboard: `http://localhost:5173`

Stop with `Ctrl+C` or:

```bash
docker compose down
```

## Web Dashboard

```bash
cd web-dashboard
npm install
npm run dev
```

## Mobile App (Expo)

```bash
cd mobile-app
npm install
npm run start
```

## Background Jobs (Arq)

```bash
arq app.services.jobs.WorkerSettings
```

> Requires Redis (`settings.redis_url`) and a DB session injection strategy in production worker startup.
Open API docs at: `http://127.0.0.1:8000/docs`

## SMTP Email Setup

Admin and society-admin login codes are sent through SMTP when these `.env` values are configured:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-gmail-address@gmail.com
SMTP_PASSWORD=your-16-character-app-password
SMTP_FROM=your-gmail-address@gmail.com
SMTP_USE_TLS=true
```

For Gmail, create an App Password from Google Account > Security > 2-Step Verification > App passwords. Use that app password in `SMTP_PASSWORD`; do not use your normal Gmail password.

Test delivery:

```bash
python scripts/test_smtp.py recipient@example.com
```

If SMTP is missing or fails during local development, the admin login code is still written to `scripts/last_admin_code.txt`.

## 4) API Highlights

- `POST /api/v1/users`
- `POST /api/v1/units`
- `POST /api/v1/residents`
- `POST /api/v1/visitors/entry`
- `POST /api/v1/visitors/exit/{visitor_id}`
- `POST /api/v1/billing/invoices/generate-monthly`
- `POST /api/v1/payments`
- `POST /api/v1/tickets`
- `GET /api/v1/dashboard/admin`
- `GET /api/v1/reports/outstanding-dues.csv`

## 5) Project Structure

```text
app/
  api/
    deps.py
    routes/
      billing.py
      dashboard.py
      payments.py
      reports.py
      residents.py
      tickets.py
      units.py
      users.py
      vendors.py
      visitors.py
  core/
    config.py
    database.py
    enums.py
    rbac.py
  models/
    entities.py
  schemas/
    dto.py
  services/
    ai_insights.py
    audit.py
    notifications.py
    predictive_maintenance.py
  main.py
```

## 6) New Community & Lifestyle Features (NoBroker/ADDA Inspired)

### Community Module (`/api/v1/community/*`)
The following features have been added, inspired by NoBrokerHood and ADDA:

| Feature | API Endpoints | Description |
|---------|--------------|-------------|
| **Family Members** | POST/GET/PATCH/DELETE `/api/v1/community/families` | Manage family relationships (spouse, children, parents) per unit |
| **Parcel/Delivery** | POST/GET `/api/v1/community/parcels`, POST `/collect`, GET `/stats/summary` | Track deliveries, courier pickup, collection status |
| **Meetings & AGM** | POST/GET/PATCH `/api/v1/community/meetings`, POST `/attendees` | Schedule society meetings, AGM, mark attendance |
| **Polls & Voting** | POST/GET `/api/v1/community/polls`, POST `/vote` | Create polls with multiple options, anonymous/visible voting |
| **Society Events** | POST/GET/PATCH `/api/v1/community/events`, POST `/register` | Cultural/community events with registration and payment |
| **Expense Categories** | POST/GET `/api/v1/community/expense-categories` | Categorize society expenses with budget tracking |
| **Expense Tracking** | POST/GET `/api/v1/community/expenses`, PATCH `/approve`, GET `/summary` | Record, approve, and summarize society expenses |
| **Utility Readings** | POST/GET `/api/v1/community/utilities`, GET `/summary` | Track water, electricity, gas, solar readings and costs |
| **Security Patrols** | POST/GET `/api/v1/community/patrols`, POST `/complete`, POST `/checkpoints` | Guard patrol management with checkpoint scanning |
| **Domestic Help** | POST/GET `/api/v1/community/domestic-help`, PATCH `/toggle` | Register maids, cooks, drivers per unit with ID proof |
| **Society Directory** | GET `/api/v1/community/directory` | View all residents per building/unit with contact info |
| **Community Dashboard** | GET `/api/v1/community/dashboard` | Aggregate metrics for all community features |

### New Backend Tables
- `family_members` - Family relationships
- `parcels` - Delivery/parcel tracking
- `meetings`, `meeting_attendees`, `meeting_attachments` - Meeting management
- `polls`, `poll_options`, `poll_votes` - Voting system
- `society_events`, `event_registrations` - Event management
- `expense_categories`, `expenses` - Expense tracking
- `utility_readings` - Utility usage tracking
- `security_patrols`, `patrol_checkpoints` - Security management
- `domestic_help` - Domestic help registration

### Frontend Menu Additions (Society Admin Panel)
- Community & Lifestyle: Community Dashboard, Events, Poll & Voting, Meetings & AGM, Expense Tracking, Expense Categories, Utility Readings
- Gate & Security: Parcel/Delivery, Security Patrols, Domestic Help
- Members Management: Family Members, Society Directory

## 7) Next Implementation Steps

- Add full authentication and refresh token flow.
- Integrate payment gateways (Razorpay/Stripe) + webhooks.
- Add WhatsApp provider integration (Meta/Twilio/Gupshup).
- Add React web dashboard + React Native/Flutter mobile apps.
- Add BI-grade reporting (PDF/XLSX templates).
- Add background jobs (Celery/RQ/Arq) for reminders & scheduled billing.
- Add complaint SLA tracking with escalation matrix.
- Add real-time notifications via WebSocket for community features.

## Society ERP upgrade

SocietyMan is scoped as a housing society ERP, not a generic business ERP. The module map is inspired by society-management products such as NoBrokerHood and ADDA: security, residents, tenants, staff, vehicles, maintenance billing, accounting, helpdesk, amenities, vendors, assets, documents, and committee controls.

- **Society capability API:** `GET /api/v1/erp/capabilities` returns only society ERP modules: residents/units, gate security, vehicles/parking, staff/daily help, maintenance billing/accounting, helpdesk, amenities, assets/inventory/procurement, documents/communication, and committee reports.
- **Society-scoped ERP records:** `POST/GET/PATCH/DELETE /api/v1/erp/records` remains as a flexible extension backbone for society-specific records such as committee approvals, resident requests, and audit trails.
- **Society operations APIs:** `/api/v1/operations/*` adds product-ready resources for asset/AMC tracking, inventory reorder alerts, staff and attendance, vehicles, gate passes, purchase approval requests, amenity bookings, compliance events, and privacy/data-request monitoring.
- **Automation scaffolding:** demo data covers maintenance dues reminders, vendor invoice review, complaint routing, inventory reorder alerts, AMC renewal tracking, approval chains, and scheduled follow-ups.
- **Notification center and realtime channel:** `/api/v1/erp/notifications` and `/api/v1/erp/ws/notifications/{user_id}` provide in-app and WebSocket notification foundations.
- **Production deployment assets:** Docker Compose includes PostgreSQL and Redis, while Vercel, Render, Railway, and GitHub Actions configuration files are included for free-tier deployments.
- **Database blueprints:** SQLAlchemy models are used by the current FastAPI app; a Prisma schema is provided as the TypeScript/Next.js migration contract with UUIDs, soft delete, audit trails, timestamps, indexing, and tenant relationships.

### Society ERP quick start

```bash
cp .env.example .env
docker compose up postgres redis -d
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

In a second terminal:

```bash
cd web-dashboard
npm install
VITE_API_BASE_URL=http://localhost:8000/api/v1 npm run dev
```

Or run the production-like local stack:

```bash
docker compose up --build
```

### Key files

- Backend ERP routes: `app/api/routes/erp.py`
- SQLAlchemy ERP entities: `app/models/entities.py`
- API DTOs and society operations contracts: `app/schemas/dto.py`
- React society dashboard experience: `web-dashboard/src/App.jsx` and `web-dashboard/src/styles.css`
- Prisma database blueprint: `prisma/schema.prisma`
- Deployment guide: `docs/DEPLOYMENT.md`
- API guide: `docs/API.md`
