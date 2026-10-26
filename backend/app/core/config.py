import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    """
    Application Settings loaded from environment variables and .env file.
    """
    model_config = SettingsConfigDict(
        env_file=(".env", "backend/.env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    APP_NAME: str = "VeritasAI Real-Time Verification Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # Server binding
    BACKEND_HOST: str = "127.0.0.1"
    BACKEND_PORT: int = 8000
    FRONTEND_ORIGIN: str = "http://localhost:5173"
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]

    # Database
    DATABASE_URL: str = "sqlite:///./fake_news.db"

    # External Provider API Keys
    GEMINI_API_KEY: str = Field(default="", description="Google Gemini API key for structured claim extraction & reasoning")
    GOOGLE_FACT_CHECK_API_KEY: str = Field(default="", description="Google Fact Check Tools API Key")

    # Security & Guardrails
    MAX_CONTENT_LENGTH_MB: int = 10
    REQUEST_TIMEOUT_SECONDS: float = 15.0
    ENABLE_SSRF_PROTECTION: bool = True
    MAX_IMAGE_SIZE_BYTES: int = 5 * 1024 * 1024  # 5 MB
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/png", "image/webp"]

    @property
    def has_gemini_key(self) -> bool:
        return bool(self.GEMINI_API_KEY and self.GEMINI_API_KEY.strip())

    @property
    def has_fact_check_key(self) -> bool:
        return bool(self.GOOGLE_FACT_CHECK_API_KEY and self.GOOGLE_FACT_CHECK_API_KEY.strip())

settings = Settings()
