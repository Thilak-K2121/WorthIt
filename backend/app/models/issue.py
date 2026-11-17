import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric, Text, Integer, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class IssueCategory(Base):
    __tablename__ = "issue_categories"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    slug = Column(String(50), nullable=False, unique=True, index=True) # battery, heating, display, camera, charging, software, performance, connectivity, build, speaker_mic, other
    display_name = Column(String(100), nullable=False)

    # Relationships
    issues = relationship("ReportedIssue", back_populates="category")

class ReportedIssue(Base):
    __tablename__ = "reported_issues"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    experience_report_id = Column(String(36), ForeignKey("experience_reports.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = Column(String(36), ForeignKey("issue_categories.id", ondelete="RESTRICT"), nullable=False, index=True)
    issue_title = Column(String(200), nullable=False)
    occurred_at_month = Column(Integer, nullable=True)
    repair_required = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    experience_report = relationship("ExperienceReport", back_populates="issues")
    category = relationship("IssueCategory", back_populates="issues")

class RepairRecord(Base):
    __tablename__ = "repair_records"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    experience_report_id = Column(String(36), ForeignKey("experience_reports.id", ondelete="CASCADE"), nullable=False, index=True)
    part_replaced = Column(String(100), nullable=False) # SCREEN, BATTERY, MOTHERBOARD, CHARGING_PORT, CAMERA, SPEAKER, OTHER
    official_service_center = Column(Boolean, default=True, nullable=False)
    cost = Column(Numeric(10, 2), nullable=False, default=0.0)
    currency = Column(String(10), nullable=False, default="INR")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    experience_report = relationship("ExperienceReport", back_populates="repairs")
