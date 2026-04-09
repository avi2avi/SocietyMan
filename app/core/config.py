import os

from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = os.getenv("APP_NAME", "SocietyMan API")
    api_prefix: str = os.getenv("API_PREFIX", "/api/v1")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./societyman.db")
    secret_key: str = os.getenv("SECRET_KEY", "change-me-in-production")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expiry_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRY_MINUTES", "30"))
    refresh_token_expiry_days: int = int(os.getenv("REFRESH_TOKEN_EXPIRY_DAYS", "30"))
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


settings = Settings()
