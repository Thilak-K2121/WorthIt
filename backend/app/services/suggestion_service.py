from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from app.models.suggestion import ProductSuggestion
from app.models.product import Product, ProductVariant
from app.schemas.suggestion import ProductSuggestionCreate, ProductSuggestionReview
from app.services.deduplication_service import DeduplicationService

class DuplicateProductError(ValueError):
    """Raised when an approved/renamed name collides with an existing catalog entry."""


class SuggestionService:
    @staticmethod
    def create_suggestion(db: Session, suggestion_in: ProductSuggestionCreate) -> ProductSuggestion:
        # Check if already in catalog
        existing, _ = DeduplicationService.find_existing_duplicate(db, suggestion_in.brand, suggestion_in.model_name)
        status = "DUPLICATE" if existing else "PENDING"
        target_id = existing.id if existing else None

        suggestion = ProductSuggestion(
            brand=DeduplicationService.normalize_brand(suggestion_in.brand),
            model_name=suggestion_in.model_name.strip(),
            variant_details=suggestion_in.variant_details,
            official_url=suggestion_in.official_url,
            notes=suggestion_in.notes,
            status=status,
            target_product_id=target_id,
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
            # Apply the admin's corrections first, so the suggestion record matches what was published
            if review.brand is not None and review.brand.strip():
                suggestion.brand = DeduplicationService.normalize_brand(review.brand)
            if review.model_name is not None and review.model_name.strip():
                suggestion.model_name = review.model_name.strip()
            if review.variant_details is not None:
                suggestion.variant_details = review.variant_details.strip() or None

            existing, _ = DeduplicationService.find_existing_duplicate(db, suggestion.brand, suggestion.model_name)
            if existing:
                db.rollback()
                raise DuplicateProductError(
                    f"'{existing.brand} {existing.model_name}' is already in the catalog. "
                    "Edit the name, or mark this suggestion as a duplicate."
                )

            # Promote to full product catalog
            canonical_brand = DeduplicationService.normalize_brand(suggestion.brand)
            norm_key = DeduplicationService.generate_normalized_key(canonical_brand, suggestion.model_name)

            new_product = Product(
                brand=canonical_brand,
                model_name=suggestion.model_name,
                normalized_name=norm_key,
                official_name=f"{canonical_brand} {suggestion.model_name}",
                official_url=suggestion.official_url,
                status="ACTIVE",
                discovery_source="USER_SUGGESTED",
            )
            db.add(new_product)
            db.flush()

            # Create default hardware variant from user details if provided
            ram_val = "8GB"
            storage_val = "128GB"
            if suggestion.variant_details:
                parts = [p.strip() for p in suggestion.variant_details.split("/") if p.strip()]
                if len(parts) >= 1:
                    ram_val = parts[0]
                if len(parts) >= 2:
                    storage_val = parts[1]

            variant = ProductVariant(
                product_id=new_product.id,
                ram=ram_val,
                storage=storage_val,
                chipset="Standard Processor",
                launch_price=0,
                currency="INR"
            )
            db.add(variant)

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
