from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.api.deps import get_db, require_admin
from app.core.cache import invalidate_catalog_cache
from app.schemas.discovery import (
    DiscoveryRunResponse,
    DiscoveryTriggerRequest
)
from app.services.discovery_service import DiscoveryService

router = APIRouter()

@router.post("/run", response_model=DiscoveryRunResponse, dependencies=[Depends(require_admin)])
async def trigger_discovery_run(
    request: DiscoveryTriggerRequest,
    db: Session = Depends(get_db)
):
    """Admin-only: runs the Tavily + Gemini pipeline (spends API quota)."""
    run = await DiscoveryService.run_discovery(
        db=db,
        query_topic=request.query_topic or "latest smartphone launch 2026",
        max_results=request.max_results,
        force_mock=request.force_mock
    )
    # New products and source citations change catalog lists and product detail pages
    if run.new_products_created or run.duplicates_detected:
        invalidate_catalog_cache("discovery run")
    return run

@router.get("/runs", response_model=List[DiscoveryRunResponse])
def list_discovery_runs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db)
):
    skip = (page - 1) * page_size
    return DiscoveryService.list_runs(db, skip=skip, limit=page_size)

@router.get("/runs/{run_id}", response_model=DiscoveryRunResponse)
def get_discovery_run(
    run_id: str,
    db: Session = Depends(get_db)
):
    run = DiscoveryService.get_run(db, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Discovery run not found")
    return run
