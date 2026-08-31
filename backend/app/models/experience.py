import uuid
from datetime import datetime
from sqlalchemy import Column, String, Date, DateTime, ForeignKey, Numeric, Text, Integer
from sqlalchemy.orm import relationship
from app.core.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class ExperienceReport(Base):
    __tablename__ = "experience_reports"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    ownership_id = Column(String(36), ForeignKey("ownerships.id", ondelete="CASCADE"), nullable=False, index=True)
    report_date = Column(Date, default=datetime.utcnow().date, nullable=False)
    ownership_duration_months = Column(Integer, nullable=False, index=True) # 1, 3, 6, 12, 18, 24, etc.
    report_version = Column(Integer, default=1, nullable=False)

    # Core Structured Ratings (1.0 to 5.0 scale)
    overall_satisfaction = Column(Numeric(2, 1), nullable=False)
    battery_satisfaction = Column(Numeric(2, 1), nullable=False)
    performance_satisfaction = Column(Numeric(2, 1), nullable=False)
    software_satisfaction = Column(Numeric(2, 1), nullable=False)
    camera_satisfaction = Column(Numeric(2, 1), nullable=True)
    build_satisfaction = Column(Numeric(2, 1), nullable=True)

    # Longitudinal Experience Nuances
    battery_degradation_perception = Column(String(50), nullable=True) # NONE, MINOR, MODERATE, SEVERE
    heating_experience = Column(String(50), nullable=True) # COOL, NORMAL, NOTICEABLE_WARMTH, FREQUENT_OVERHEATING
    software_update_experience = Column(String(50), nullable=True) # EXCELLENT, GOOD, BUGGY, DEGRADED_DEVICE
    
    # Primary Long-Term Verdict
    would_buy_again = Column(String(20), nullable=False) # YES, NO, UNSURE
    would_buy_again_reason = Column(Text, nullable=True)

    # Qualitative Reflections
    biggest_positive = Column(Text, nullable=True)
    biggest_problem = Column(Text, nullable=True)
    general_notes = Column(Text, nullable=True)

    # Trust & Verification Level
    trust_status = Column(String(50), nullable=False, default="SELF_REPORTED") # SELF_REPORTED, VERIFIED_PURCHASE, MODERATED, SUSPICIOUS
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    ownership = relationship("Ownership", back_populates="reports")
    issues = relationship("ReportedIssue", back_populates="experience_report", cascade="all, delete-orphan")
    repairs = relationship("RepairRecord", back_populates="experience_report", cascade="all, delete-orphan")
