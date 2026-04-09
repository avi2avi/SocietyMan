from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "SocietyMan API"
    api_prefix: str = "/api/v1"
    database_url: str = "sqlite:///./societyman.db"


settings = Settings()
