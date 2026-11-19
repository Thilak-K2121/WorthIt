# ==============================================================================
# Compare Service - Side-by-Side Comparison of TWO phones
# ==============================================================================
# Frontend: ComparePage (ComparisonMatrix)
# Endpoint: GET /products/compare?product_a=..&product_b=..  ->  api/v1/endpoints/compare.py
#
# Builds a comparison row for each phone from its insights (InsightsService)
# and generates plain-language key takeaways.
# ==============================================================================

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.product import Product
from app.schemas.insights import ProductComparisonResponse, ProductComparisonItem
from app.services.insights_service import InsightsService


class CompareService:
    @classmethod
    def compare_products(cls, db: Session, product_a_id: str, product_b_id: str) -> Optional[ProductComparisonResponse]:
        item_a = cls._build_comparison_item(db, product_a_id)
        item_b = cls._build_comparison_item(db, product_b_id)

        if not item_a or not item_b:
            return None

        # Generate automated key takeaways based on data
        takeaways: List[str] = []
        
        if item_a.overall_satisfaction.score and item_b.overall_satisfaction.score:
            diff = round(item_a.overall_satisfaction.score - item_b.overall_satisfaction.score, 2)
            if abs(diff) >= 0.2:
                higher = item_a.model_name if diff > 0 else item_b.model_name
                lower = item_b.model_name if diff > 0 else item_a.model_name
                takeaways.append(f"{higher} leads in overall owner satisfaction ({max(item_a.overall_satisfaction.score, item_b.overall_satisfaction.score):.1f}/5.0 vs {min(item_a.overall_satisfaction.score, item_b.overall_satisfaction.score):.1f}/5.0).")

        if item_a.battery_satisfaction.score and item_b.battery_satisfaction.score:
            diff_bat = round(item_a.battery_satisfaction.score - item_b.battery_satisfaction.score, 2)
            if abs(diff_bat) >= 0.3:
                higher = item_a.model_name if diff_bat > 0 else item_b.model_name
                takeaways.append(f"Long-term battery satisfaction is markedly higher on {higher}.")

        if item_a.would_buy_again_percentage and item_b.would_buy_again_percentage:
            takeaways.append(f"Owner repurchase intent: {item_a.model_name} ({item_a.would_buy_again_percentage:.0f}%) vs {item_b.model_name} ({item_b.would_buy_again_percentage:.0f}%).")

        if not takeaways:
            takeaways.append("Both smartphones exhibit comparable owner satisfaction across tracked ownership intervals.")

        return ProductComparisonResponse(
            product_a=item_a,
            product_b=item_b,
            key_takeaways=takeaways
        )

    @classmethod
    def _build_comparison_item(cls, db: Session, product_id: str) -> Optional[ProductComparisonItem]:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return None

        insights = InsightsService.compute_product_insights(db, product_id)
        if not insights:
            return None

        top_issues = [i.category_name for i in insights.issue_breakdown[:3]]
        variants_summary = [f"{v.ram or ''} / {v.storage or ''} ({v.chipset or ''})".strip(" /") for v in product.variants if v.ram or v.storage]

        return ProductComparisonItem(
            product_id=product.id,
            brand=product.brand,
            model_name=product.model_name,
            release_date=str(product.release_date) if product.release_date else None,
            official_url=product.official_url,
            total_owners=insights.total_registered_owners,
            long_term_owners=insights.long_term_owners_12m_plus,
            confidence=insights.confidence,
            overall_satisfaction=insights.overall_satisfaction,
            battery_satisfaction=insights.battery_satisfaction,
            performance_satisfaction=insights.performance_satisfaction,
            software_satisfaction=insights.software_satisfaction,
            would_buy_again_percentage=insights.would_buy_again.yes_percentage,
            repair_rate_percentage=insights.repair_stats.repair_rate_percentage,
            median_repair_cost=insights.repair_stats.median_repair_cost,
            top_issues=top_issues,
            variants_summary=variants_summary
        )
