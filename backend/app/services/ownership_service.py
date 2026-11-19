# ==============================================================================
# Ownership Service - Registering that someone owns a phone
# ==============================================================================
# Frontend: SubmitExperiencePage (OwnershipForm, "Share Experience")
# Endpoints: POST /ownerships, GET /ownerships/{id}  ->  api/v1/endpoints/ownerships.py
#
# An ownership is one person + one phone (+ variant, price paid). Their reviews
# over time are experience reports, handled by ExperienceService.
# ==============================================================================

from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.models.ownership import Ownership
from app.models.product import ProductVariant
from app.models.experience import ExperienceReport
from app.models.issue import ReportedIssue
from app.schemas.ownership import OwnershipCreate
from app.services.experience_service import ExperienceService

class OwnershipService:
    #getting the product by ID
    @staticmethod
    def get_by_id(db: Session, ownership_id: str) -> Optional[Ownership]:
        return (
            db.query(Ownership)
            .options(
                joinedload(Ownership.variant),
                joinedload(Ownership.reports).joinedload(ExperienceReport.issues).joinedload(ReportedIssue.category),
                joinedload(Ownership.reports).joinedload(ExperienceReport.repairs)
            )
            .filter(Ownership.id == ownership_id)
            .first()
        )

    @staticmethod
    def list_by_product(db: Session, product_id: str, skip: int = 0, limit: int = 50) -> List[Ownership]:
        return (
            db.query(Ownership)
            .options(
                joinedload(Ownership.variant),
                joinedload(Ownership.reports)
            )
            .filter(Ownership.product_id == product_id)
            .order_by(Ownership.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def create_ownership(db: Session, data: OwnershipCreate) -> Ownership:
        # Only accept a variant that belongs to this product (it drives the launch-price comparison)
        variant_id = data.variant_id
        if variant_id and not db.query(ProductVariant.id).filter(
            ProductVariant.id == variant_id, ProductVariant.product_id == data.product_id
        ).first():
            variant_id = None

        ownership = Ownership(
            product_id=data.product_id,
            variant_id=variant_id,
            purchase_date=data.purchase_date,
            purchase_price=data.purchase_price,
            currency=data.currency or "INR",
        )
        db.add(ownership)
        db.flush()

        # If user provided an initial experience report simultaneously
        if data.initial_report:
            ExperienceService.add_experience_report(db, ownership.id, data.initial_report)

        db.commit()
        db.refresh(ownership)
        return ownership
