from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.experience import ExperienceReportResponse
from app.services.ownership_service import ExperienceService

router = APIRouter()

@router.get("/products/{product_id}/experiences", response_model=List[ExperienceReportResponse])
def list_product_experiences(
    product_id: str,
    min_months: Optional[int] = Query(None, description="Minimum ownership duration in months (e.g. 12)"),
    max_months: Optional[int] = Query(None, description="Maximum ownership duration in months"),
    page: int = Query(1, ge=1),
    page_size: int = Query(30, ge=1, le=100),
    db: Session = Depends(get_db)
):
    skip = (page - 1) * page_size
    return ExperienceService.list_reports_for_product(
        db=db,
        product_id=product_id,
        min_duration_months=min_months,
        max_duration_months=max_months,
        skip=skip,
        limit=page_size
    )
