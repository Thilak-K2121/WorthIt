import os
from pathlib import Path
from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
import json

# Explicitly load .env from backend folder or workspace root
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

class Settings(BaseSettings):
    PROJECT_NAME: str = "WorthIt - Longitudinal Smartphone Experience Platform"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"

    DATABASE_URL: str = "sqlite:///./worthit.db"

    # External APIs
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    DISCOVERY_CRON_SCHEDULE: str = "0 2 * * *"
    DISCOVERY_ENABLED: bool = True
    MAX_CANDIDATES_PER_RUN: int = 10

    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://localhost:8000"
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, str) and v.startswith("["):
            try:
                return json.loads(v)
            except Exception:
                return [v]
        return v

    model_config = SettingsConfigDict(
        extra="ignore"
    )

settings = Settings()

