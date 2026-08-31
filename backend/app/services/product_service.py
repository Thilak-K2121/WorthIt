from typing import List, Optional, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, func
from app.models.product import Product, ProductVariant
from app.models.ownership import Ownership
from app.models.experience import ExperienceReport
from app.schemas.product import ProductCreate, ProductUpdate, ProductSummaryResponse
from app.services.deduplication_service import DeduplicationService

class ProductService:
    @staticmethod
    def get_by_id(db: Session, product_id: str) -> Optional[Product]:
        return (
            db.query(Product)
            .options(joinedload(Product.variants), joinedload(Product.sources))
            .filter(Product.id == product_id)
            .first()
        )

    @staticmethod
    def list_products(
        db: Session,
        search: Optional[str] = None,
        brand: Optional[str] = None,
        status: Optional[str] = "ACTIVE",
        skip: int = 0,
        limit: int = 20,
        sort_by: str = "popularity" # popularity, satisfaction, release_date, name
    ) -> Tuple[List[ProductSummaryResponse], int]:
        query = db.query(Product)

        if status:
            query = query.filter(Product.status == status)

        if brand:
            query = query.filter(Product.brand.ilike(brand))

        if search:
            search_clean = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    Product.brand.ilike(search_clean),
                    Product.model_name.ilike(search_clean),
                    Product.normalized_name.ilike(search_clean),
                    Product.official_name.ilike(search_clean)
                )
            )

        total = query.count()
        products = query.offset(skip).limit(limit).all()

        summaries: List[ProductSummaryResponse] = []
        for p in products:
            # Query stats
            owners_count = db.query(Ownership).filter(Ownership.product_id == p.id).count()
            
            # Long-term reports count (>= 12 months)
            long_term_count = (
                db.query(ExperienceReport)
                .join(Ownership)
                .filter(Ownership.product_id == p.id, ExperienceReport.ownership_duration_months >= 12)
                .count()
            )

            # Average satisfaction
            avg_sat = (
                db.query(func.avg(ExperienceReport.overall_satisfaction))
                .join(Ownership)
                .filter(Ownership.product_id == p.id)
                .scalar()
            )

            # Would buy again %
            total_wba = (
                db.query(ExperienceReport)
                .join(Ownership)
                .filter(Ownership.product_id == p.id)
                .count()
            )
            yes_wba = (
                db.query(ExperienceReport)
                .join(Ownership)
                .filter(Ownership.product_id == p.id, ExperienceReport.would_buy_again == "YES")
                .count()
            )
            wba_pct = round((yes_wba / total_wba) * 100, 1) if total_wba > 0 else None

            summary = ProductSummaryResponse(
                id=p.id,
                brand=p.brand,
                model_name=p.model_name,
                normalized_name=p.normalized_name,
                official_name=p.official_name,
                release_date=p.release_date,
                country_market=p.country_market,
                official_url=p.official_url,
                status=p.status,
                discovery_source=p.discovery_source,
                verification_status=p.verification_status,
                description=p.description,
                created_at=p.created_at,
                updated_at=p.updated_at,
                variant_count=len(p.variants),
                total_owners_count=owners_count,
                long_term_owners_count=long_term_count,
                avg_overall_satisfaction=round(float(avg_sat), 2) if avg_sat else None,
                would_buy_again_percentage=wba_pct
            )
            summaries.append(summary)

        # Sorting logic
        if sort_by == "satisfaction":
            summaries.sort(key=lambda s: s.avg_overall_satisfaction or 0, reverse=True)
        elif sort_by == "long_term_owners":
            summaries.sort(key=lambda s: s.long_term_owners_count, reverse=True)
        elif sort_by == "release_date":
            summaries.sort(key=lambda s: s.release_date or s.created_at.date(), reverse=True)
        else: # popularity / owners count
            summaries.sort(key=lambda s: s.total_owners_count, reverse=True)

        return summaries, total

    @staticmethod
    def create_product(db: Session, product_in: ProductCreate) -> Product:
        canonical_brand = DeduplicationService.normalize_brand(product_in.brand)
        normalized_name = DeduplicationService.generate_normalized_key(canonical_brand, product_in.model_name)

        product = Product(
            brand=canonical_brand,
            model_name=product_in.model_name.strip(),
            normalized_name=normalized_name,
            official_name=product_in.official_name or f"{canonical_brand} {product_in.model_name.strip()}",
            release_date=product_in.release_date,
            country_market=product_in.country_market,
            official_url=product_in.official_url,
            status=product_in.status,
            discovery_source=product_in.discovery_source,
            verification_status=product_in.verification_status,
            description=product_in.description
        )
        db.add(product)
        db.flush()

        if product_in.variants:
            for v in product_in.variants:
                variant = ProductVariant(
                    product_id=product.id,
                    ram=v.ram,
                    storage=v.storage,
                    chipset=v.chipset,
                    launch_price=v.launch_price,
                    currency=v.currency or "INR"
                )
                db.add(variant)

        db.commit()
        db.refresh(product)
        return product

    @staticmethod
    def update_product(db: Session, product_id: str, product_in: ProductUpdate) -> Optional[Product]:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return None

        update_data = product_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(product, field, value)

        db.commit()
        db.refresh(product)
        return product
