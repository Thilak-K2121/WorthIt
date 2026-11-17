# ==============================================================================
# Admin Catalog Management - Manual Add / Delete & Cache Controls
# ==============================================================================
# Lets the moderator curate the catalog after the AI discovery pipeline runs:
# add a phone by hand, delete a wrong/duplicate entry, and inspect or flush the
# Redis cache. Every route requires the X-Admin-Key header (see require_admin).
# ==============================================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_admin
from app.core.cache import cache, invalidate_catalog_cache
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductDetailResponse
from app.services.deduplication_service import DeduplicationService
from app.services.product_service import ProductService
from app.api.v1.endpoints.products import build_product_detail

router = APIRouter(dependencies=[Depends(require_admin)])


@router.get("/verify")
def verify_admin_key():
    """Lets the admin console check that the entered key is valid."""
    return {"ok": True}


@router.post("/products", response_model=ProductDetailResponse, status_code=201)
def admin_create_product(product_in: ProductCreate, db: Session = Depends(get_db)):
    """Manually adds a smartphone (with optional variants) to the catalog."""
    if not product_in.brand.strip() or not product_in.model_name.strip():
        raise HTTPException(status_code=422, detail="Brand and model name are required.")

    existing, score = DeduplicationService.find_existing_duplicate(db, product_in.brand, product_in.model_name)
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"'{existing.brand} {existing.model_name}' already exists in the catalog (similarity {score:.2f}).",
        )

    try:
        created = ProductService.create_product(db, product_in)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="A product with this brand and model already exists.")

    invalidate_catalog_cache("admin created product")
    return build_product_detail(db, created.id)


@router.delete("/products/{product_id}")
def admin_delete_product(product_id: str, db: Session = Depends(get_db)):
    """
    Permanently deletes a product. Variants, source citations, ownerships and their
    experience reports are removed with it (ORM cascade).
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    name = f"{product.brand} {product.model_name}"
    owners = len(product.ownerships)
    db.delete(product)
    db.commit()

    invalidate_catalog_cache("admin deleted product")
    return {"deleted": product_id, "name": name, "ownerships_removed": owners}


@router.get("/cache/stats")
def cache_stats():
    """Redis connectivity, hit/miss counters (this process) and cached key count."""
    return cache.stats()


@router.post("/cache/flush")
def cache_flush():
    """Clears every cached WorthIt response."""
    return {"keys_removed": cache.invalidate_all()}
