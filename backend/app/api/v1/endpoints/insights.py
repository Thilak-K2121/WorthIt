from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.insights import ProductInsightsResponse
from app.services.intelligence_service import IntelligenceService

router = APIRouter()

@router.get("/products/{product_id}/insights", response_model=ProductInsightsResponse)
def get_product_insights(
    product_id: str,
    db: Session = Depends(get_db)
):
    insights = IntelligenceService.compute_product_insights(db, product_id)
    if not insights:
        raise HTTPException(status_code=404, detail="Product not found or has no insights available")
    return insights
