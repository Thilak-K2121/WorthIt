from typing import Generator, Optional
from fastapi import Header, HTTPException
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import SessionLocal
import hmac

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def require_admin(x_admin_key: Optional[str] = Header(None, alias="X-Admin-Key")) -> None:
    """
    Guards admin-only catalog management routes with a shared secret.

    - ADMIN_API_KEY set: the X-Admin-Key header must match (constant-time compare).
    - ADMIN_API_KEY unset in production: admin routes are refused (fail closed).
    - ADMIN_API_KEY unset in development/tests: routes are open for convenience.
    """
    expected = (settings.ADMIN_API_KEY or "").strip()
    if not expected:
        if settings.ENVIRONMENT.lower() == "production":
            raise HTTPException(status_code=503, detail="Admin access is not configured on the server (set ADMIN_API_KEY).")
        return
    if not x_admin_key or not hmac.compare_digest(x_admin_key.strip(), expected):
        raise HTTPException(status_code=401, detail="Invalid or missing admin key.")
