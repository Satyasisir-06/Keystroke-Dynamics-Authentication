"""
KeyAuth - Configuration module
Loads settings from environment variables
"""
import os
from pydantic_settings import BaseSettings
from typing import List

IS_VERCEL = os.environ.get("VERCEL", "") == "1"


class Settings(BaseSettings):
    APP_NAME: str = "KeyAuth"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = not IS_VERCEL

    # Database — Supabase PostgreSQL (falls back to SQLite for local dev)
    DATABASE_URL: str = "postgresql://postgres:[YOUR-PASSWORD]@db.jmqxshpddchmkaklxzej.supabase.co:5432/postgres"

    # JWT
    SECRET_KEY: str = "keyauth-dev-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # ML Model
    ENROLLMENT_SAMPLES_REQUIRED: int = 5
    AUTH_CONFIDENCE_THRESHOLD: float = 0.85

    # CORS — allow all on Vercel (same domain), restrict locally
    CORS_ORIGINS: str = (
        "*" if IS_VERCEL
        else "http://localhost:5173,http://localhost:3000"
    )

    @property
    def cors_origins_list(self) -> List[str]:
        if self.CORS_ORIGINS.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
