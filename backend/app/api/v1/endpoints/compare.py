from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.insights import ProductComparisonResponse
from app.services.intelligence_service import IntelligenceService

router = APIRouter()

@router.get("", response_model=ProductComparisonResponse)
def compare_products(
    product_a: str = Query(..., description="ID of first product"),
    product_b: str = Query(..., description="ID of second product"),
    db: Session = Depends(get_db)
):
    if product_a == product_b:
        raise HTTPException(status_code=400, detail="Cannot compare a product with itself")
        
    result = IntelligenceService.compare_products(db, product_a, product_b)
    if not result:
        raise HTTPException(status_code=404, detail="One or both products could not be found")
    return result
