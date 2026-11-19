from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.core.cache import cache, cached_json_response
from app.schemas.insights import ProductComparisonResponse
from app.services.compare_service import CompareService

router = APIRouter()

@router.get("", response_model=ProductComparisonResponse)
def compare_products(
    request: Request,
    product_a: str = Query(..., description="ID of first product"),
    product_b: str = Query(..., description="ID of second product"),
    db: Session = Depends(get_db)
):
    if product_a == product_b:
        raise HTTPException(status_code=400, detail="Cannot compare a product with itself")

    def compute():
        result = CompareService.compare_products(db, product_a, product_b)
        if not result:
            raise HTTPException(status_code=404, detail="One or both products could not be found")
        return result

    # Order matters (A vs B takeaways), so the key is not sorted
    return cached_json_response(request, cache.key("compare", product_a, product_b), ProductComparisonResponse, compute)
