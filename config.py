import os
from typing import List, Optional
from pydantic import BaseSettings, validator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    # Telegram Configuration
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_WEBHOOK_URL: Optional[str] = None
    
    # Kiro API Configuration
    KIRO_API_URL: str = "https://api.kiro.ai/v1"
    KIRO_API_KEY: str
    
    # Admin Configuration
    ADMIN_USER_IDS: List[int] = []
    
    # Server Configuration
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    DEBUG_MODE: bool = False
    LOG_LEVEL: str = "INFO"
    
    @validator("ADMIN_USER_IDS", pre=True)
    def parse_admin_ids(cls, v):
        if isinstance(v, str):
            if not v.strip():
                return []
            return [int(user_id.strip()) for user_id in v.split(",")]
        return v
    
    @validator("TELEGRAM_WEBHOOK_URL")
    def validate_webhook_url(cls, v, values):
        if v and not v.startswith("https://"):
            raise ValueError("TELEGRAM_WEBHOOK_URL must start with https://")
        return v
    
    class Config:
        env_file = ".env"

# Create settings instance
settings = Settings()

# Logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "root": {
        "level": settings.LOG_LEVEL,
        "handlers": ["console"],
    },
}