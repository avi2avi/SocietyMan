from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text

from app.api.routes import (
    auth,
    billing,
    billing_advanced,
    communications,
    community,
    dashboard,
    erp,
    operations,
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


def _sql_type(sqlite_type: str, postgres_type: str) -> str:
    return postgres_type if engine.dialect.name == "postgresql" else sqlite_type


def _boolean_default(enabled: bool) -> str:
    if engine.dialect.name == "postgresql":
        return "TRUE" if enabled else "FALSE"
    return "1" if enabled else "0"


def ensure_schema():
    with engine.connect() as connection:
        inspector = inspect(connection)
        if "users" in inspector.get_table_names():
            columns = [column["name"] for column in inspector.get_columns("users")]
            if "society_id" not in columns:
                connection.execute(text("ALTER TABLE users ADD COLUMN society_id INTEGER"))
                connection.commit()
            if "password_change_required" not in columns:
                connection.execute(text(f"ALTER TABLE users ADD COLUMN password_change_required BOOLEAN DEFAULT {_boolean_default(False)}"))
                connection.commit()
            if "admin_login_code" not in columns:
                connection.execute(text("ALTER TABLE users ADD COLUMN admin_login_code VARCHAR(20)"))
                connection.commit()
            if "admin_login_code_expires_at" not in columns:
                connection.execute(text(f"ALTER TABLE users ADD COLUMN admin_login_code_expires_at {_sql_type('DATETIME', 'TIMESTAMP')}"))
                connection.commit()
            for column_name in [
                "access_erp",
                "access_gatekeeper",
                "access_billing",
                "access_payments",
                "access_communications",
                "access_reports",
                "access_documents",
                "access_visitor_management",
            ]:
                if column_name not in columns:
                    connection.execute(text(f"ALTER TABLE users ADD COLUMN {column_name} BOOLEAN DEFAULT {_boolean_default(False)}"))
                    connection.commit()
        if "societies" in inspector.get_table_names():
            columns = [column["name"] for column in inspector.get_columns("societies")]
            if "admin_contact_name" not in columns:
                connection.execute(text("ALTER TABLE societies ADD COLUMN admin_contact_name VARCHAR(120)"))
                connection.commit()
            if "admin_contact_email" not in columns:
                connection.execute(text("ALTER TABLE societies ADD COLUMN admin_contact_email VARCHAR(120)"))
                connection.commit()
            if "admin_contact_phone" not in columns:
                connection.execute(text("ALTER TABLE societies ADD COLUMN admin_contact_phone VARCHAR(20)"))
                connection.commit()
            if "is_approved" not in columns:
                connection.execute(text(f"ALTER TABLE societies ADD COLUMN is_approved BOOLEAN DEFAULT {_boolean_default(True)}"))
                connection.commit()
            if "approved_at" not in columns:
                connection.execute(text(f"ALTER TABLE societies ADD COLUMN approved_at {_sql_type('DATETIME', 'TIMESTAMP')}"))
                connection.commit()


def init_default_admin():
    with SessionLocal() as db:
        default_email = settings.default_admin_email.strip()
        default_password = settings.default_admin_password
        if not default_email or not default_password:
            return

        default_admin = db.query(User).filter(User.email == default_email).first()
        if default_admin:
            return

        admin_phone = settings.default_admin_phone.strip() or "0000000000"
        fallback_index = 1
        while db.query(User).filter(User.phone == admin_phone).first():
            admin_phone = f"000000000{fallback_index}"
            fallback_index += 1

        admin = User(
            full_name=settings.default_admin_name,
            phone=admin_phone,
            email=default_email,
            password_hash=hash_password(default_password),
            role=Role.ADMIN,
            society_id=None,
            password_change_required=False,
        )
        db.add(admin)
        db.commit()


ensure_schema()
Base.metadata.create_all(bind=engine)
try:
    init_default_admin()
except Exception as exc:
    print(f"Warning: failed to create default admin on startup: {exc}")

app = FastAPI(title=settings.app_name)

allowed_origins = [o.strip() for o in settings.cors_allow_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins or ["*"],
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
app.include_router(erp.router, prefix=settings.api_prefix)
app.include_router(operations.router, prefix=settings.api_prefix)
app.include_router(reports.router, prefix=settings.api_prefix)
app.include_router(communications.router, prefix=settings.api_prefix)
app.include_router(billing_advanced.router, prefix=settings.api_prefix)
app.include_router(community.router, prefix=settings.api_prefix)


@app.get("/")
def health():
    return {"status": "ok", "app": settings.app_name}
