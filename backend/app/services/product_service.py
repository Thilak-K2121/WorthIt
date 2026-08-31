from typing import List, Optional, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, func, case
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
        products = query.options(joinedload(Product.variants)).offset(skip).limit(limit).all()

        product_ids = [p.id for p in products]

        # 1. Bulk aggregation of ownership count
        ownership_map = {}
        if product_ids:
            for pid, count in (
                db.query(Ownership.product_id, func.count(Ownership.id))
                .filter(Ownership.product_id.in_(product_ids))
                .group_by(Ownership.product_id)
                .all()
            ):
                ownership_map[pid] = count

        # 2. Bulk aggregation of experience reports metrics
        exp_map = {}
        if product_ids:
            for pid, lt_count, avg_sat, total_wba, yes_wba in (
                db.query(
                    Ownership.product_id,
                    func.sum(case((ExperienceReport.ownership_duration_months >= 12, 1), else_=0)),
                    func.avg(ExperienceReport.overall_satisfaction),
                    func.count(ExperienceReport.id),
                    func.sum(case((ExperienceReport.would_buy_again == "YES", 1), else_=0))
                )
                .join(ExperienceReport, ExperienceReport.ownership_id == Ownership.id)
                .filter(Ownership.product_id.in_(product_ids))
                .group_by(Ownership.product_id)
                .all()
            ):
                exp_map[pid] = {
                    "long_term_count": int(lt_count or 0),
                    "avg_sat": float(avg_sat) if avg_sat is not None else None,
                    "total_wba": int(total_wba or 0),
                    "yes_wba": int(yes_wba or 0)
                }

        summaries: List[ProductSummaryResponse] = []
        for p in products:
            owners_count = ownership_map.get(p.id, 0)
            stats = exp_map.get(p.id, {"long_term_count": 0, "avg_sat": None, "total_wba": 0, "yes_wba": 0})
            
            wba_pct = None
            if stats["total_wba"] > 0:
                wba_pct = round((stats["yes_wba"] / stats["total_wba"]) * 100, 1)

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
                long_term_owners_count=stats["long_term_count"],
                avg_overall_satisfaction=round(stats["avg_sat"], 2) if stats["avg_sat"] is not None else None,
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
