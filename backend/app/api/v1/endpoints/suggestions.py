from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.core.cache import invalidate_catalog_cache
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
    db: Session = Depends(get_db)
):
    return SuggestionService.create_suggestion(db, suggestion_in)

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
    invalidate_catalog_cache("suggestion reviewed")
    return updated
