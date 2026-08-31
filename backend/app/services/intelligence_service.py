from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
from statistics import median
from app.models.product import Product
from app.models.ownership import Ownership
from app.models.experience import ExperienceReport
from app.models.issue import ReportedIssue, IssueCategory, RepairRecord
from app.schemas.insights import (
    ProductInsightsResponse,
    SampleConfidence,
    MetricScore,
    WouldBuyAgainStats,
    IssueCategoryStats,
    RepairIntelligence,
    OwnershipTimelineMilestone,
    ProductComparisonResponse,
    ProductComparisonItem
)

class IntelligenceService:
    @classmethod
    def get_sample_confidence(cls, sample_size: int, long_term_size: int) -> SampleConfidence:
        if sample_size == 0:
            return SampleConfidence(
                sample_size=0,
                confidence_level="NONE",
                badge_label="No Ownership Data Yet",
                is_authoritative=False,
                explanation="Be the first verified owner to share your long-term experience for this device."
            )
        elif sample_size < 5:
            return SampleConfidence(
                sample_size=sample_size,
                confidence_level="VERY_LOW",
                badge_label=f"Early Data — Based on {sample_size} {'owner' if sample_size == 1 else 'owners'}",
                is_authoritative=False,
                explanation="Sample size is extremely small. Ratings may not represent typical long-term reliability."
            )
        elif sample_size < 25:
            return SampleConfidence(
                sample_size=sample_size,
                confidence_level="LOW",
                badge_label=f"Early Trends — Based on {sample_size} owners",
                is_authoritative=False,
                explanation="Preliminary directional trends. More longitudinal data is being gathered."
            )
        elif sample_size < 100 or long_term_size < 20:
            return SampleConfidence(
                sample_size=sample_size,
                confidence_level="MODERATE",
                badge_label=f"Growing Confidence — {sample_size} owners ({long_term_size} at 12m+)",
                is_authoritative=True,
                explanation="Good statistical representation of initial and mid-term ownership."
            )
        else:
            return SampleConfidence(
                sample_size=sample_size,
                confidence_level="HIGH",
                badge_label=f"High Statistical Confidence — {sample_size} owners ({long_term_size} at 12m+)",
                is_authoritative=True,
                explanation="Robust multi-year dataset with statistically significant sample volume."
            )

    @classmethod
    def compute_product_insights(cls, db: Session, product_id: str) -> Optional[ProductInsightsResponse]:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return None

        total_owners = db.query(Ownership).filter(Ownership.product_id == product_id).count()

        reports: List[ExperienceReport] = (
            db.query(ExperienceReport)
            .join(Ownership)
            .filter(Ownership.product_id == product_id)
            .all()
        )
        total_reports = len(reports)
        long_term_reports = [r for r in reports if r.ownership_duration_months >= 12]
        long_term_count = len(long_term_reports)

        confidence = cls.get_sample_confidence(total_owners, long_term_count)

        # Helper to compute metric average
        def make_score(values: List[float]) -> MetricScore:
            if not values:
                return MetricScore(score=None, sample_size=0, formatted="N/A")
            avg = sum(values) / len(values)
            return MetricScore(
                score=round(avg, 2),
                sample_size=len(values),
                formatted=f"{round(avg, 1)} / 5.0"
            )

        overall_scores = [float(r.overall_satisfaction) for r in reports if r.overall_satisfaction is not None]
        battery_scores = [float(r.battery_satisfaction) for r in reports if r.battery_satisfaction is not None]
        perf_scores = [float(r.performance_satisfaction) for r in reports if r.performance_satisfaction is not None]
        soft_scores = [float(r.software_satisfaction) for r in reports if r.software_satisfaction is not None]
        cam_scores = [float(r.camera_satisfaction) for r in reports if r.camera_satisfaction is not None]
        build_scores = [float(r.build_satisfaction) for r in reports if r.build_satisfaction is not None]

        sat_12m_scores = [float(r.overall_satisfaction) for r in long_term_reports if r.overall_satisfaction is not None]

        # Would buy again calculation
        wba_yes = sum(1 for r in reports if r.would_buy_again == "YES")
        wba_no = sum(1 for r in reports if r.would_buy_again == "NO")
        wba_unsure = sum(1 for r in reports if r.would_buy_again == "UNSURFACE" or r.would_buy_again == "UNSURE")
        
        pos_reasons = [r.would_buy_again_reason for r in reports if r.would_buy_again == "YES" and r.would_buy_again_reason]
        neg_reasons = [r.would_buy_again_reason for r in reports if r.would_buy_again == "NO" and r.would_buy_again_reason]

        wba_stats = WouldBuyAgainStats(
            yes_percentage=round((wba_yes / total_reports) * 100, 1) if total_reports > 0 else None,
            no_percentage=round((wba_no / total_reports) * 100, 1) if total_reports > 0 else None,
            unsure_percentage=round((wba_unsure / total_reports) * 100, 1) if total_reports > 0 else None,
            total_responses=total_reports,
            top_reasons_positive=pos_reasons[:4],
            top_reasons_negative=neg_reasons[:4]
        )

        # Issue Category Statistics
        issues_query = (
            db.query(ReportedIssue)
            .join(ExperienceReport)
            .join(Ownership)
            .filter(Ownership.product_id == product_id)
            .all()
        )
        
        issues_by_cat: Dict[str, List[ReportedIssue]] = {}
        for iss in issues_query:
            cat_slug = iss.category.slug if iss.category else "other"
            issues_by_cat.setdefault(cat_slug, []).append(iss)

        issue_breakdown: List[IssueCategoryStats] = []
        for cat_slug, cat_issues in issues_by_cat.items():
            cat_name = cat_issues[0].category.display_name if cat_issues[0].category else cat_slug.title()
            occurred_months = [i.occurred_at_month for i in cat_issues if i.occurred_at_month is not None]
            repairs_needed = sum(1 for i in cat_issues if i.repair_required)
            pct = round((len(cat_issues) / max(total_owners, 1)) * 100, 1)

            issue_breakdown.append(IssueCategoryStats(
                category_slug=cat_slug,
                category_name=cat_name,
                report_count=len(cat_issues),
                percentage_of_owners=min(pct, 100.0),
                most_common_complaint=cat_issues[0].issue_title if cat_issues else None,
                average_occurred_month=round(sum(occurred_months) / len(occurred_months), 1) if occurred_months else None,
                repair_required_count=repairs_needed
            ))
        issue_breakdown.sort(key=lambda x: x.report_count, reverse=True)

        # Repairs calculation
        repairs_query = (
            db.query(RepairRecord)
            .join(ExperienceReport)
            .join(Ownership)
            .filter(Ownership.product_id == product_id)
            .all()
        )
        repair_costs = [float(r.cost) for r in repairs_query if r.cost is not None and float(r.cost) > 0]
        part_counts: Dict[str, int] = {}
        for r in repairs_query:
            part_counts[r.part_replaced] = part_counts.get(r.part_replaced, 0) + 1

        repair_stats = RepairIntelligence(
            total_repairs_reported=len(repairs_query),
            repair_rate_percentage=round((len(repairs_query) / max(total_owners, 1)) * 100, 1) if total_owners > 0 else 0.0,
            median_repair_cost=round(float(median(repair_costs)), 2) if repair_costs else None,
            currency="INR",
            common_parts=[{"part": k, "count": v} for k, v in sorted(part_counts.items(), key=lambda x: x[1], reverse=True)]
        )

        # Tenure Milestones
        tenure_buckets = [
            ("1-3 Months", 1, 3),
            ("4-6 Months", 4, 6),
            ("7-12 Months", 7, 12),
            ("13-18 Months", 13, 18),
            ("19-24+ Months", 19, 120)
        ]

        tenure_milestones: List[OwnershipTimelineMilestone] = []
        for label, min_m, max_m in tenure_buckets:
            bucket_reports = [r for r in reports if min_m <= r.ownership_duration_months <= max_m]
            if not bucket_reports:
                continue

            b_overall = [float(r.overall_satisfaction) for r in bucket_reports if r.overall_satisfaction is not None]
            b_battery = [float(r.battery_satisfaction) for r in bucket_reports if r.battery_satisfaction is not None]
            b_perf = [float(r.performance_satisfaction) for r in bucket_reports if r.performance_satisfaction is not None]
            b_soft = [float(r.software_satisfaction) for r in bucket_reports if r.software_satisfaction is not None]

            # Battery degradation counts
            degrad_counts: Dict[str, int] = {}
            for r in bucket_reports:
                deg = r.battery_degradation_perception or "NONE"
                degrad_counts[deg] = degrad_counts.get(deg, 0) + 1
            
            degrad_pcts = {k: round((v / len(bucket_reports)) * 100, 1) for k, v in degrad_counts.items()}

            tenure_milestones.append(OwnershipTimelineMilestone(
                tenure_bucket=label,
                min_months=min_m,
                max_months=max_m,
                reports_count=len(bucket_reports),
                avg_overall_satisfaction=round(sum(b_overall) / len(b_overall), 2) if b_overall else None,
                avg_battery_satisfaction=round(sum(b_battery) / len(b_battery), 2) if b_battery else None,
                avg_performance_satisfaction=round(sum(b_perf) / len(b_perf), 2) if b_perf else None,
                avg_software_satisfaction=round(sum(b_soft) / len(b_soft), 2) if b_soft else None,
                battery_degradation_breakdown=degrad_pcts,
                common_issues=[r.biggest_problem for r in bucket_reports if r.biggest_problem][:3]
            ))

        return ProductInsightsResponse(
            product_id=product.id,
            product_name=product.model_name,
            brand=product.brand,
            total_registered_owners=total_owners,
            total_experience_reports=total_reports,
            long_term_owners_12m_plus=long_term_count,
            confidence=confidence,
            overall_satisfaction=make_score(overall_scores),
            battery_satisfaction=make_score(battery_scores),
            performance_satisfaction=make_score(perf_scores),
            software_satisfaction=make_score(soft_scores),
            camera_satisfaction=make_score(cam_scores),
            build_satisfaction=make_score(build_scores),
            satisfaction_at_12m=make_score(sat_12m_scores),
            would_buy_again=wba_stats,
            issue_breakdown=issue_breakdown,
            repair_stats=repair_stats,
            tenure_summary=tenure_milestones
        )

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

        insights = cls.compute_product_insights(db, product_id)
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
