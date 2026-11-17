from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.core.cache import invalidate_catalog_cache
from app.schemas.ownership import OwnershipCreate, OwnershipResponse
from app.schemas.experience import ExperienceReportCreate, ExperienceReportResponse
from app.services.ownership_service import OwnershipService, ExperienceService

router = APIRouter()

@router.post("", response_model=OwnershipResponse, status_code=201)
def register_ownership(
    ownership_in: OwnershipCreate,
    db: Session = Depends(get_db)
):
    created = OwnershipService.create_ownership(db, ownership_in)
    invalidate_catalog_cache("ownership registered")
    return OwnershipService.get_by_id(db, created.id)

@router.get("/{ownership_id}", response_model=OwnershipResponse)
def get_ownership(
    ownership_id: str,
    db: Session = Depends(get_db)
):
    ownership = OwnershipService.get_by_id(db, ownership_id)
    if not ownership:
        raise HTTPException(status_code=404, detail="Ownership record not found")
    return ownership

@router.post("/{ownership_id}/reports", response_model=ExperienceReportResponse, status_code=201)
def add_experience_report(
    ownership_id: str,
    report_in: ExperienceReportCreate,
    db: Session = Depends(get_db)
):
    ownership = OwnershipService.get_by_id(db, ownership_id)
    if not ownership:
        raise HTTPException(status_code=404, detail="Ownership record not found")
    
    report = ExperienceService.add_experience_report(db, ownership_id, report_in)
    invalidate_catalog_cache("experience report added")
    return report
