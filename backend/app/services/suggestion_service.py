from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from app.models.suggestion import ProductSuggestion
from app.models.product import Product, ProductVariant
from app.schemas.suggestion import ProductSuggestionCreate, ProductSuggestionReview
from app.services.deduplication_service import DeduplicationService

class SuggestionService:
    @staticmethod
    def create_suggestion(db: Session, suggestion_in: ProductSuggestionCreate, ip_hash: Optional[str] = None) -> ProductSuggestion:
        # Check if already in catalog
        existing, _ = DeduplicationService.find_existing_duplicate(db, suggestion_in.brand, suggestion_in.model_name)
        status = "DUPLICATE" if existing else "PENDING"
        target_id = existing.id if existing else None

        suggestion = ProductSuggestion(
            brand=DeduplicationService.normalize_brand(suggestion_in.brand),
            model_name=suggestion_in.model_name.strip(),
            variant_details=suggestion_in.variant_details,
            official_url=suggestion_in.official_url,
            approximate_release_date=suggestion_in.approximate_release_date,
            notes=suggestion_in.notes,
            status=status,
            target_product_id=target_id,
            submitter_ip_hash=ip_hash
        )
        db.add(suggestion)
        db.commit()
        db.refresh(suggestion)
        return suggestion

    @staticmethod
    def list_suggestions(db: Session, status: Optional[str] = None, skip: int = 0, limit: int = 50) -> List[ProductSuggestion]:
        query = db.query(ProductSuggestion)
        if status:
            query = query.filter(ProductSuggestion.status == status)
        return query.order_by(ProductSuggestion.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def review_suggestion(db: Session, suggestion_id: str, review: ProductSuggestionReview) -> Optional[ProductSuggestion]:
        suggestion = db.query(ProductSuggestion).filter(ProductSuggestion.id == suggestion_id).first()
        if not suggestion:
            return None

        if review.action == "APPROVE":
            # Promote to full product catalog
            canonical_brand = DeduplicationService.normalize_brand(suggestion.brand)
            norm_key = DeduplicationService.generate_normalized_key(canonical_brand, suggestion.model_name)

            new_product = Product(
                brand=canonical_brand,
                model_name=suggestion.model_name,
                normalized_name=norm_key,
                official_name=f"{canonical_brand} {suggestion.model_name}",
                release_date=suggestion.approximate_release_date,
                official_url=suggestion.official_url,
                status="ACTIVE",
                discovery_source="USER_SUGGESTED",
                verification_status="VERIFIED"
            )
            db.add(new_product)
            db.flush()

            suggestion.status = "APPROVED"
            suggestion.target_product_id = new_product.id
        elif review.action == "MARK_DUPLICATE":
            suggestion.status = "DUPLICATE"
            suggestion.target_product_id = review.target_product_id
        else: # REJECT
            suggestion.status = "REJECTED"

        db.commit()
        db.refresh(suggestion)
        return suggestion
