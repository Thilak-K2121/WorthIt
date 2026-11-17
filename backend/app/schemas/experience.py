from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field

# Issue Schemas
class IssueCategoryResponse(BaseModel):
    id: str
    slug: str
    display_name: str
    model_config = ConfigDict(from_attributes=True)

class ReportedIssueCreate(BaseModel):
    category_slug: str = Field(..., example="battery")
    issue_title: str = Field(..., example="Noticeable battery capacity drop after 6 months")
    occurred_at_month: Optional[int] = Field(None, example=6)
    repair_required: bool = False

class ReportedIssueResponse(BaseModel):
    id: str
    experience_report_id: str
    category_id: str
    issue_title: str
    occurred_at_month: Optional[int]
    repair_required: bool
    created_at: datetime
    category: Optional[IssueCategoryResponse] = None
    model_config = ConfigDict(from_attributes=True)

# Repair Schemas
class RepairRecordCreate(BaseModel):
    part_replaced: str = Field(..., example="BATTERY") # SCREEN, BATTERY, MOTHERBOARD, etc.
    official_service_center: bool = True
    cost: Decimal = Field(Decimal("0.0"), example=2500.00)
    currency: str = "INR"

class RepairRecordResponse(BaseModel):
    id: str
    experience_report_id: str
    part_replaced: str
    official_service_center: bool
    cost: Decimal
    currency: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# Experience Report Schemas
class ExperienceReportCreate(BaseModel):
    report_date: Optional[date] = None
    ownership_duration_months: int = Field(..., ge=1, le=120, example=12)
    overall_satisfaction: Decimal = Field(..., ge=1.0, le=5.0, example=4.2)
    battery_satisfaction: Decimal = Field(..., ge=1.0, le=5.0, example=4.0)
    performance_satisfaction: Decimal = Field(..., ge=1.0, le=5.0, example=4.5)
    software_satisfaction: Decimal = Field(..., ge=1.0, le=5.0, example=4.1)
    camera_satisfaction: Optional[Decimal] = Field(None, ge=1.0, le=5.0, example=4.7)
    
    battery_degradation_perception: Optional[str] = Field("MINOR", example="MINOR")
    heating_experience: Optional[str] = Field("NORMAL", example="NORMAL")
    software_update_experience: Optional[str] = Field("GOOD", example="GOOD")
    
    would_buy_again: str = Field(..., example="YES") # YES, NO, UNSURE
    would_buy_again_reason: Optional[str] = Field(None, example="Great camera and consistent battery life despite minor heating during long video calls.")
    
    biggest_positive: Optional[str] = Field(None, example="Display sharpness and telephoto lens.")
    biggest_problem: Optional[str] = Field(None, example="Slightly slow charging speed compared to competition.")

    issues: Optional[List[ReportedIssueCreate]] = None
    repairs: Optional[List[RepairRecordCreate]] = None

class ExperienceReportResponse(BaseModel):
    id: str
    ownership_id: str
    report_date: date
    ownership_duration_months: int
    report_version: int
    overall_satisfaction: Decimal
    battery_satisfaction: Decimal
    performance_satisfaction: Decimal
    software_satisfaction: Decimal
    camera_satisfaction: Optional[Decimal]
    battery_degradation_perception: Optional[str]
    heating_experience: Optional[str]
    software_update_experience: Optional[str]
    would_buy_again: str
    would_buy_again_reason: Optional[str]
    biggest_positive: Optional[str]
    biggest_problem: Optional[str]
    trust_status: str
    created_at: datetime
    issues: List[ReportedIssueResponse] = []
    repairs: List[RepairRecordResponse] = []
    model_config = ConfigDict(from_attributes=True)
