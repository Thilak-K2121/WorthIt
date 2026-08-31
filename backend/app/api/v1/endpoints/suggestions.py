from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_client_session_hash
from app.schemas.suggestion import (
    ProductSuggestionCreate,
    ProductSuggestionResponse,
    ProductSuggestionReview
)
from app.services.suggestion_service import SuggestionService

router = APIRouter()

@router.post("", response_model=ProductSuggestionResponse, status_code=201)
def submit_product_suggestion(
    suggestion_in: ProductSuggestionCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    ip_hash = get_client_session_hash(request)
    return SuggestionService.create_suggestion(db, suggestion_in, ip_hash=ip_hash)

@router.get("", response_model=List[ProductSuggestionResponse])
def list_suggestions(
    status: Optional[str] = Query(None, description="Filter by status: PENDING, APPROVED, REJECTED, DUPLICATE"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    skip = (page - 1) * page_size
    return SuggestionService.list_suggestions(db, status=status, skip=skip, limit=page_size)

@router.post("/{suggestion_id}/review", response_model=ProductSuggestionResponse)
def review_suggestion(
    suggestion_id: str,
    review_in: ProductSuggestionReview,
    db: Session = Depends(get_db)
):
    updated = SuggestionService.review_suggestion(db, suggestion_id, review_in)
    if not updated:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    return updated
