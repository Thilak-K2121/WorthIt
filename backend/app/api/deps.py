from typing import Generator
from fastapi import Request
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
import hashlib

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_client_session_hash(request: Request) -> str:
    """Generates an anonymized deterministic client hash for rate-limiting / session tagging."""
    client_host = request.client.host if request.client else "127.0.0.1"
    user_agent = request.headers.get("user-agent", "")
    return hashlib.sha256(f"{client_host}-{user_agent}".encode()).hexdigest()
