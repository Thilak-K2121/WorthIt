from datetime import datetime, timezone
from typing import Annotated, TypeVar, Generic, List, Optional
from pydantic import BaseModel, PlainSerializer


def _to_utc_iso(value: datetime) -> str:
    """Timestamps are stored as naive UTC; emit them with an explicit 'Z' so browsers
    don't misread them as local time (which shifted times by the viewer's UTC offset)."""
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


# Use for every datetime field in API responses.
UTCDateTime = Annotated[datetime, PlainSerializer(_to_utc_iso, return_type=str, when_used="json")]

T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int

class APIResponse(BaseModel, Generic[T]):
    success: bool = True
    message: Optional[str] = None
    data: Optional[T] = None
