# API Overview

- `GET /api/v1/erp/capabilities` exposes the enterprise ERP module, AI, workflow, integration, deployment, and security blueprint.
- `POST /api/v1/erp/demo/seed` seeds enterprise demo data for a developer admin.
- `GET|POST|PATCH|DELETE /api/v1/erp/records` provides a tenant-scoped generic record API for HRM, CRM, inventory, finance, manufacturing, procurement, POS, commerce, and document modules.
- `GET /api/v1/erp/notifications` powers the notification center.
- `WS /api/v1/erp/ws/notifications/{user_id}` provides the real-time notification channel.
