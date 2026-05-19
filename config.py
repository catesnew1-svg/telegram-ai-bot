import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import validator
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_WEBHOOK_URL: Optional[str] = None
    KIRO_API_URL: str = "https://api.groq.com/openai/v1"
    KIRO_API_KEY: str
    ADMIN_USER_IDS: List[int] = []
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    DEBUG_MODE: bool = False
    LOG_LEVEL: str = "INFO"
    ACCESS_CODE: str = ""

    @validator("ADMIN_USER_IDS", pre=True)
    def parse_admin_ids(cls, v):
        if isinstance(v, str):
            if not v.strip():
                return []
            return [int(uid.strip()) for uid in v.split(",") if uid.strip()]
        return v

    class Config:
        env_file = ".env"

settings = Settings()

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"default": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"}},
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "default"}},
    "root": {"level": settings.LOG_LEVEL, "handlers": ["console"]},
}
