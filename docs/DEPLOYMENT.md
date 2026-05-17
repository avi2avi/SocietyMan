# Deployment Guide

## Local Docker

```bash
cp .env.example .env
docker compose up --build
```

## Vercel + Render/Railway

- Deploy `web-dashboard` to Vercel with `VITE_API_BASE_URL` pointing to the API.
- Deploy the FastAPI service to Render or Railway using `Dockerfile.backend`.
- Attach PostgreSQL and Redis add-ons, then set `DATABASE_URL`, `REDIS_URL`, `SECRET_KEY`, and gateway credentials.
- Configure scheduled database backups in the host dashboard and export snapshots to object storage.

## API docs

Swagger/OpenAPI is available at `/docs` for every FastAPI environment.
