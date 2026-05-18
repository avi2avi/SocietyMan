import os
from pathlib import Path

from pydantic import BaseModel

DEFAULT_POSTGRES_URL = "postgresql+psycopg://societyman:societyman@localhost:5432/societyman"


def _load_local_env() -> None:
    env_path = Path(".env")
    if not env_path.exists():
        return

    for raw_line in env_path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


_load_local_env()


class Settings(BaseModel):
    app_name: str = os.getenv("APP_NAME", "SocietyMan API")
    api_prefix: str = os.getenv("API_PREFIX", "/api/v1")
    cors_allow_origins: str = os.getenv("CORS_ALLOW_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000")
    database_url: str = os.getenv("DATABASE_URL", os.getenv("POSTGRES_DATABASE_URL", DEFAULT_POSTGRES_URL))
    secret_key: str = os.getenv("SECRET_KEY", "change-me-in-production")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")    
    access_token_expiry_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRY_MINUTES", "30"))
    refresh_token_expiry_days: int = int(os.getenv("REFRESH_TOKEN_EXPIRY_DAYS", "30"))
    default_admin_email: str = os.getenv("DEFAULT_ADMIN_EMAIL", "admin@gmail.com")
    default_admin_password: str = os.getenv("DEFAULT_ADMIN_PASSWORD", "Admin@123")
    default_admin_name: str = os.getenv("DEFAULT_ADMIN_NAME", "Developer Admin")
    default_admin_phone: str = os.getenv("DEFAULT_ADMIN_PHONE", "0000000000")
    stripe_secret_key: str = os.getenv("STRIPE_SECRET_KEY", "")
    stripe_webhook_secret: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    razorpay_key_id: str = os.getenv("RAZORPAY_KEY_ID", "")
    razorpay_key_secret: str = os.getenv("RAZORPAY_KEY_SECRET", "")
    razorpay_webhook_secret: str = os.getenv("RAZORPAY_WEBHOOK_SECRET", "")
    whatsapp_provider: str = os.getenv("WHATSAPP_PROVIDER", "meta")
    whatsapp_meta_token: str = os.getenv("WHATSAPP_META_TOKEN", "")
    whatsapp_meta_phone_id: str = os.getenv("WHATSAPP_META_PHONE_ID", "")
    twilio_account_sid: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    twilio_auth_token: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    twilio_whatsapp_from: str = os.getenv("TWILIO_WHATSAPP_FROM", "")
    gupshup_api_key: str = os.getenv("GUPSHUP_API_KEY", "")
    gupshup_app_name: str = os.getenv("GUPSHUP_APP_NAME", "")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    # SMTP settings for sending emails
    smtp_host: str = os.getenv("SMTP_HOST", "")
    smtp_port: int = int(os.getenv("SMTP_PORT", "0"))
    smtp_username: str = os.getenv("SMTP_USERNAME", "")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")
    smtp_from: str = os.getenv("SMTP_FROM", "")
    smtp_use_tls: bool = os.getenv("SMTP_USE_TLS", "true").lower() in ("1", "true", "yes")


settings = Settings()
