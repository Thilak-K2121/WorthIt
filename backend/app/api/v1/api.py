from fastapi import APIRouter
from app.api.v1.endpoints import (
    compare,
    products,
    ownerships,
    experiences,
    insights,
    suggestions,
    discovery
)

api_router = APIRouter()

# Mount specific product routes before parameterised /{product_id}
api_router.include_router(compare.router, prefix="/products/compare", tags=["Product Comparison"])
api_router.include_router(products.router, prefix="/products", tags=["Products"])
api_router.include_router(ownerships.router, prefix="/ownerships", tags=["Ownerships"])
api_router.include_router(experiences.router, tags=["Experience Reports"])
api_router.include_router(insights.router, tags=["Product Intelligence"])
api_router.include_router(suggestions.router, prefix="/product-suggestions", tags=["Product Suggestions"])
api_router.include_router(discovery.router, prefix="/discovery", tags=["Automated Discovery"])
