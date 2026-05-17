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
8. Communication (notices + messages)
9. Complaint / Ticket Management
10. Document Repository
11. Notifications
12. Admin Dashboard Metrics
13. Reports & Download Center (CSV now, PDF/Excel hook-ready)
14. Multi-platform readiness (Web + Mobile APIs)

### Innovation Layer (Included as service interfaces)
- WhatsApp notification integration interface
- AI financial insights engine scaffold
- Smart QR visitor entry workflow scaffold
- Automated audit export prep
- Predictive maintenance alerts

## 2) Tech Stack

- **Backend:** Python 3.11+, FastAPI, SQLAlchemy, Pydantic
- **Database:** SQLite (development), Postgres-ready via SQLAlchemy URL
- **Auth:** JWT-ready placeholder flow with role checks
- **Reports:** CSV export (expandable to PDF/XLSX)

## 3) Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API docs: `http://127.0.0.1:8000/docs`

> Developer admin account created on startup when missing:
> - Email: `avinash210790@gmail.com`
> - Password: `Admin@123`
> - Verification code is emailed or written to `scripts/last_admin_code.txt` when SMTP is not configured.
>
> Default database:
> - `sqlite:///./societyman.db`
> - Local DB file: `societyman.db`
> - Use a SQLite browser extension or tool to inspect the database file.

## Key API Endpoints

- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`
- `GET /api/v1/users/me`
- `POST /api/v1/payments/orders`
- `POST /api/v1/payments/webhooks/{provider}`
- `POST /api/v1/communications/whatsapp/send`
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

## 6) Next Implementation Steps

- Add full authentication and refresh token flow.
- Integrate payment gateways (Razorpay/Stripe) + webhooks.
- Add WhatsApp provider integration (Meta/Twilio/Gupshup).
- Add React web dashboard + React Native/Flutter mobile apps.
- Add BI-grade reporting (PDF/XLSX templates).
- Add background jobs (Celery/RQ/Arq) for reminders & scheduled billing.

## Enterprise ERP upgrade

SocietyMan now includes an enterprise ERP foundation that keeps the existing society-management flows while adding a scalable ERP product layer:

- **Enterprise capability API:** `GET /api/v1/erp/capabilities` returns the module catalog, AI automation roadmap, workflow samples, integration targets, deployment targets, and security controls used by the landing page.
- **Tenant-scoped generic ERP records:** `POST/GET/PATCH/DELETE /api/v1/erp/records` provides a reusable record backbone for HRM, CRM, inventory, finance, projects, manufacturing, procurement, POS, e-commerce, documents, and reporting modules.
- **AI and automation scaffolding:** demo data covers chatbot assistance, invoice OCR, sales forecasting, inventory prediction, finance anomaly detection, approval chains, scheduled follow-ups, and reorder workflows.
- **Notification center and realtime channel:** `/api/v1/erp/notifications` and `/api/v1/erp/ws/notifications/{user_id}` provide in-app and WebSocket notification foundations.
- **Production deployment assets:** Docker Compose includes PostgreSQL and Redis, while Vercel, Render, Railway, and GitHub Actions configuration files are included for free-tier deployments.
- **Database blueprints:** SQLAlchemy models are used by the current FastAPI app; a Prisma schema is provided as the TypeScript/Next.js migration contract with UUIDs, soft delete, audit trails, timestamps, indexing, and tenant relationships.

### Enterprise quick start

```bash
cp .env.example .env
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
- API DTOs: `app/schemas/dto.py`
- React SaaS landing experience: `web-dashboard/src/App.jsx` and `web-dashboard/src/styles.css`
- Prisma database blueprint: `prisma/schema.prisma`
- Deployment guide: `docs/DEPLOYMENT.md`
- API guide: `docs/API.md`
