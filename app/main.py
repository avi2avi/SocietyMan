from fastapi import FastAPI

from app.api.routes import (
    billing,
    dashboard,
    payments,
    reports,
    residents,
    tickets,
    units,
    users,
    vendors,
    visitors,
)
from app.core.config import settings
from app.core.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name)

app.include_router(users.router, prefix=settings.api_prefix)
app.include_router(units.router, prefix=settings.api_prefix)
app.include_router(residents.router, prefix=settings.api_prefix)
app.include_router(visitors.router, prefix=settings.api_prefix)
app.include_router(billing.router, prefix=settings.api_prefix)
app.include_router(payments.router, prefix=settings.api_prefix)
app.include_router(vendors.router, prefix=settings.api_prefix)
app.include_router(tickets.router, prefix=settings.api_prefix)
app.include_router(dashboard.router, prefix=settings.api_prefix)
app.include_router(reports.router, prefix=settings.api_prefix)


@app.get("/")
def health():
    return {"status": "ok", "app": settings.app_name}
