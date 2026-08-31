from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.models.ownership import Ownership
from app.models.experience import ExperienceReport
from app.models.issue import IssueCategory, ReportedIssue, RepairRecord
from app.schemas.ownership import OwnershipCreate
from app.schemas.experience import ExperienceReportCreate

class OwnershipService:
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
    def create_ownership(db: Session, data: OwnershipCreate, session_hash: Optional[str] = None) -> Ownership:
        ownership = Ownership(
            product_id=data.product_id,
            variant_id=data.variant_id,
            purchase_date=data.purchase_date,
            purchase_price=data.purchase_price,
            currency=data.currency or "INR",
            purchase_country=data.purchase_country or "India",
            ownership_start_date=data.ownership_start_date or data.purchase_date,
            ownership_end_date=data.ownership_end_date,
            status=data.status,
            previous_phone=data.previous_phone,
            purchase_source=data.purchase_source,
            owner_session_hash=session_hash
        )
        db.add(ownership)
        db.flush()

        # If user provided an initial experience report simultaneously
        if data.initial_report:
            ExperienceService.add_experience_report(db, ownership.id, data.initial_report)

        db.commit()
        db.refresh(ownership)
        return ownership

class ExperienceService:
    @staticmethod
    def add_experience_report(db: Session, ownership_id: str, report_in: ExperienceReportCreate) -> ExperienceReport:
        # Determine report version count for this ownership
        existing_reports_count = db.query(ExperienceReport).filter(ExperienceReport.ownership_id == ownership_id).count()

        report = ExperienceReport(
            ownership_id=ownership_id,
            report_date=report_in.report_date or report_in.report_date,
            ownership_duration_months=report_in.ownership_duration_months,
            report_version=existing_reports_count + 1,
            overall_satisfaction=report_in.overall_satisfaction,
            battery_satisfaction=report_in.battery_satisfaction,
            performance_satisfaction=report_in.performance_satisfaction,
            software_satisfaction=report_in.software_satisfaction,
            camera_satisfaction=report_in.camera_satisfaction,
            build_satisfaction=report_in.build_satisfaction,
            battery_degradation_perception=report_in.battery_degradation_perception,
            heating_experience=report_in.heating_experience,
            software_update_experience=report_in.software_update_experience,
            would_buy_again=report_in.would_buy_again,
            would_buy_again_reason=report_in.would_buy_again_reason,
            biggest_positive=report_in.biggest_positive,
            biggest_problem=report_in.biggest_problem,
            general_notes=report_in.general_notes,
            trust_status="SELF_REPORTED"
        )
        db.add(report)
        db.flush()

        # Add structured issues if provided
        if report_in.issues:
            for issue_in in report_in.issues:
                # Find or ensure category
                category = db.query(IssueCategory).filter(IssueCategory.slug == issue_in.category_slug).first()
                if not category:
                    category = IssueCategory(
                        slug=issue_in.category_slug,
                        display_name=issue_in.category_slug.replace("_", " ").title()
                    )
                    db.add(category)
                    db.flush()

                issue = ReportedIssue(
                    experience_report_id=report.id,
                    category_id=category.id,
                    issue_title=issue_in.issue_title,
                    severity=issue_in.severity,
                    occurred_at_month=issue_in.occurred_at_month or report_in.ownership_duration_months,
                    resolved=issue_in.resolved,
                    repair_required=issue_in.repair_required,
                    repair_cost=issue_in.repair_cost,
                    notes=issue_in.notes
                )
                db.add(issue)

        # Add repairs if provided
        if report_in.repairs:
            for rep_in in report_in.repairs:
                repair = RepairRecord(
                    experience_report_id=report.id,
                    part_replaced=rep_in.part_replaced,
                    official_service_center=rep_in.official_service_center,
                    covered_under_warranty=rep_in.covered_under_warranty,
                    cost=rep_in.cost,
                    currency=rep_in.currency or "INR",
                    repair_notes=rep_in.repair_notes
                )
                db.add(repair)

        db.commit()
        db.refresh(report)
        return report

    @staticmethod
    def list_reports_for_product(
        db: Session,
        product_id: str,
        min_duration_months: Optional[int] = None,
        max_duration_months: Optional[int] = None,
        skip: int = 0,
        limit: int = 30
    ) -> List[ExperienceReport]:
        query = (
            db.query(ExperienceReport)
            .join(Ownership)
            .options(
                joinedload(ExperienceReport.issues).joinedload(ReportedIssue.category),
                joinedload(ExperienceReport.repairs),
                joinedload(ExperienceReport.ownership).joinedload(Ownership.variant)
            )
            .filter(Ownership.product_id == product_id)
        )

        if min_duration_months is not None:
            query = query.filter(ExperienceReport.ownership_duration_months >= min_duration_months)
        if max_duration_months is not None:
            query = query.filter(ExperienceReport.ownership_duration_months <= max_duration_months)

        return query.order_by(ExperienceReport.ownership_duration_months.desc(), ExperienceReport.created_at.desc()).offset(skip).limit(limit).all()
