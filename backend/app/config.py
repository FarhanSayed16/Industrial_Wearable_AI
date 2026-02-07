"""
Industrial Wearable AI — Backend Configuration
Loads env from .env and exports settings for DB, auth, CORS.
"""
import os
from typing import List

from dotenv import load_dotenv

load_dotenv()

# Database
DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/wearable_ai",
)

# Auth (JWT)
SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production-use-long-random-string")
ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# CORS — must be a list for FastAPI middleware
_cors_raw: str = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000")
CORS_ORIGINS: List[str] = [origin.strip() for origin in _cors_raw.split(",") if origin.strip()]
