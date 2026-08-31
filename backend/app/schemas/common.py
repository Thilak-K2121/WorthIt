from typing import TypeVar, Generic, List, Optional
from pydantic import BaseModel

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
