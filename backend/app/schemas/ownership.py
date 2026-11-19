from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.common import UTCDateTime
from app.schemas.product import ProductVariantResponse
from app.schemas.experience import ExperienceReportResponse, ExperienceReportCreate

class OwnershipCreate(BaseModel):
    product_id: str
    variant_id: Optional[str] = None
    purchase_date: date
    purchase_price: Optional[Decimal] = Field(None, example=64999.00)
    currency: Optional[str] = "INR"
    
    # Optional initial report to submit at the same time
    initial_report: Optional[ExperienceReportCreate] = None

class OwnershipResponse(BaseModel):
    id: str
    product_id: str
    variant_id: Optional[str]
    purchase_date: date
    purchase_price: Optional[Decimal]
    currency: Optional[str]
    created_at: UTCDateTime
    variant: Optional[ProductVariantResponse] = None
    reports: List[ExperienceReportResponse] = []
    model_config = ConfigDict(from_attributes=True)
