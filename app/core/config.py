from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "SocietyMan API"
    api_prefix: str = "/api/v1"
    database_url: str = "sqlite:///./societyman.db"
    secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expiry_minutes: int = 30
    refresh_token_expiry_days: int = 30
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    razorpay_key_id: str = ""
    razorpay_key_secret: str = ""
    razorpay_webhook_secret: str = ""
    whatsapp_provider: str = "meta"
    whatsapp_meta_token: str = ""
    whatsapp_meta_phone_id: str = ""
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_whatsapp_from: str = ""
    gupshup_api_key: str = ""
    gupshup_app_name: str = ""
    redis_url: str = "redis://localhost:6379/0"


settings = Settings()
