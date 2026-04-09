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

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API docs: `http://127.0.0.1:8000/docs`

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
