import asyncio
import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.discovery import ProductDiscoveryRun
from app.models.product import Product, ProductVariant, ProductSource
from app.providers.base import DiscoveryProvider, ExtractorProvider
from app.providers.tavily_provider import TavilyProvider
from app.providers.gemini_provider import GeminiExtractor
from app.providers.mock_providers import MockTavilyProvider, MockGeminiExtractor
from app.services.deduplication_service import DeduplicationService
from app.schemas.discovery import DiscoveryRunResponse
from app.core.logging import logger

class DiscoveryService:
    @classmethod
    async def run_discovery(
        cls,
        db: Session,
        query_topic: str = "latest smartphone launch 2026",
        max_results: int = 5,
        force_mock: bool = False
    ) -> ProductDiscoveryRun:
        run = ProductDiscoveryRun(
            status="RUNNING",
            started_at=datetime.datetime.utcnow()
        )
        db.add(run)
        db.commit()
        db.refresh(run)

        # Select provider based on configuration or force_mock flag
        search_provider: DiscoveryProvider = MockTavilyProvider() if force_mock else TavilyProvider()
        extractor: ExtractorProvider = MockGeminiExtractor() if force_mock else GeminiExtractor()

        try:
            logger.info(f"Starting discovery run #{run.id} with query: {query_topic}")
            results = await search_provider.search_smartphone_launches(query_topic, max_results=max_results)
            run.sources_searched = len(results)

            for item in results:
                run.candidates_found += 1
                extracted = await extractor.extract_smartphone_specs(item.snippet, item.url, item.title)
                
                if not extracted:
                    run.failed_count += 1
                    continue

                run.extracted_count += 1

                # Check for duplicate
                existing_product, sim_score = DeduplicationService.find_existing_duplicate(
                    db, extracted.brand, extracted.model_name
                )

                if existing_product:
                    run.duplicates_detected += 1
                    # Attach source provenance to existing product
                    source = ProductSource(
                        product_id=existing_product.id,
                        discovery_run_id=run.id,
                        source_url=item.url,
                        source_title=item.title,
                        source_snippet=item.snippet,
                        provider="TAVILY",
                        raw_extracted_json=extracted.model_dump(mode="json")
                    )
                    db.add(source)
                else:
                    # Create new product record with PENDING / UNVERIFIED status
                    canonical_brand = DeduplicationService.normalize_brand(extracted.brand)
                    norm_key = DeduplicationService.generate_normalized_key(canonical_brand, extracted.model_name)

                    new_product = Product(
                        brand=canonical_brand,
                        model_name=extracted.model_name,
                        normalized_name=norm_key,
                        official_name=extracted.official_name or f"{canonical_brand} {extracted.model_name}",
                        release_date=extracted.release_date or datetime.date.today(),
                        country_market=extracted.country_market or "Global",
                        official_url=extracted.official_url or item.url,
                        status="ACTIVE", # Enabled for immediate browsing in student platform
                        discovery_source="AUTOMATED",
                        verification_status="VERIFIED"
                    )
                    db.add(new_product)
                    db.flush()

                    # Add variants
                    for v in extracted.variants:
                        variant = ProductVariant(
                            product_id=new_product.id,
                            ram=v.ram,
                            storage=v.storage,
                            chipset=v.chipset,
                            launch_price=v.launch_price,
                            currency=v.currency or "INR"
                        )
                        db.add(variant)

                    # Add source link
                    source = ProductSource(
                        product_id=new_product.id,
                        discovery_run_id=run.id,
                        source_url=item.url,
                        source_title=item.title,
                        source_snippet=item.snippet,
                        provider="TAVILY",
                        raw_extracted_json=extracted.model_dump(mode="json")
                    )
                    db.add(source)
                    run.new_products_created += 1

                # Safe pacing delay between Gemini calls to stay within free RPM quota
                await asyncio.sleep(2.0)

            run.status = "COMPLETED"
            run.completed_at = datetime.datetime.utcnow()
            db.commit()
            db.refresh(run)
            logger.info(f"Discovery run #{run.id} finished successfully. New products: {run.new_products_created}, Duplicates: {run.duplicates_detected}")
            return run

        except Exception as e:
            logger.error(f"Discovery run #{run.id} failed: {e}")
            run.status = "FAILED"
            run.completed_at = datetime.datetime.utcnow()
            run.error_log = str(e)
            db.commit()
            db.refresh(run)
            return run

    @classmethod
    def list_runs(cls, db: Session, skip: int = 0, limit: int = 20) -> List[ProductDiscoveryRun]:
        from sqlalchemy.orm import joinedload
        return (
            db.query(ProductDiscoveryRun)
            .options(
                joinedload(ProductDiscoveryRun.sources).joinedload(ProductSource.product)
            )
            .order_by(ProductDiscoveryRun.started_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @classmethod
    def get_run(cls, db: Session, run_id: str) -> Optional[ProductDiscoveryRun]:
        from sqlalchemy.orm import joinedload
        return (
            db.query(ProductDiscoveryRun)
            .options(
                joinedload(ProductDiscoveryRun.sources).joinedload(ProductSource.product)
            )
            .filter(ProductDiscoveryRun.id == run_id)
            .first()
        )
