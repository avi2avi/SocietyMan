from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text

from app.api.routes import (
    auth,
    billing,
    communications,
    dashboard,
    payments,
    reports,
    residents,
    societies,
    tickets,
    units,
    users,
    vendors,
    visitors,
)
from app.core.config import settings
from app.core.database import Base, engine, SessionLocal
from app.core.enums import Role
from app.core.security import hash_password
from app.models.entities import User


def ensure_schema():
    with engine.connect() as connection:
        inspector = inspect(connection)
        if "users" in inspector.get_table_names():
            columns = [column["name"] for column in inspector.get_columns("users")]
            if "society_id" not in columns:
                connection.execute(text("ALTER TABLE users ADD COLUMN society_id INTEGER"))
                connection.commit()
            if "password_change_required" not in columns:
                connection.execute(text("ALTER TABLE users ADD COLUMN password_change_required BOOLEAN DEFAULT 0"))
                connection.commit()
            if "admin_login_code" not in columns:
                connection.execute(text("ALTER TABLE users ADD COLUMN admin_login_code VARCHAR(20)"))
                connection.commit()
            if "admin_login_code_expires_at" not in columns:
                connection.execute(text("ALTER TABLE users ADD COLUMN admin_login_code_expires_at DATETIME"))
                connection.commit()
        if "societies" in inspector.get_table_names():
            columns = [column["name"] for column in inspector.get_columns("societies")]
            if "is_approved" not in columns:
                connection.execute(text("ALTER TABLE societies ADD COLUMN is_approved BOOLEAN DEFAULT 1"))
                connection.commit()
            if "approved_at" not in columns:
                connection.execute(text("ALTER TABLE societies ADD COLUMN approved_at DATETIME"))
                connection.commit()


def init_default_admin():
    with SessionLocal() as db:
        existing_admin = db.query(User).filter(User.role == Role.ADMIN).first()
        if existing_admin:
            return

        if not settings.default_admin_email or not settings.default_admin_password:
            return

        if db.query(User).filter(User.email == settings.default_admin_email).first():
            return

        admin = User(
            full_name=settings.default_admin_name,
            phone=settings.default_admin_phone,
            email=settings.default_admin_email,
            password_hash=hash_password(settings.default_admin_password),
            role=Role.ADMIN,
            society_id=None,
            password_change_required=True,
        )
        db.add(admin)
        db.commit()


ensure_schema()
Base.metadata.create_all(bind=engine)
init_default_admin()

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(users.router, prefix=settings.api_prefix)
app.include_router(societies.router, prefix=settings.api_prefix)
app.include_router(units.router, prefix=settings.api_prefix)
app.include_router(residents.router, prefix=settings.api_prefix)
app.include_router(visitors.router, prefix=settings.api_prefix)
app.include_router(billing.router, prefix=settings.api_prefix)
app.include_router(payments.router, prefix=settings.api_prefix)
app.include_router(vendors.router, prefix=settings.api_prefix)
app.include_router(tickets.router, prefix=settings.api_prefix)
app.include_router(dashboard.router, prefix=settings.api_prefix)
app.include_router(reports.router, prefix=settings.api_prefix)
app.include_router(communications.router, prefix=settings.api_prefix)


@app.get("/")
def health():
    return {"status": "ok", "app": settings.app_name}
