from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.product import ProductVariantResponse
from app.schemas.experience import ExperienceReportResponse, ExperienceReportCreate

class OwnershipCreate(BaseModel):
    product_id: str
    variant_id: Optional[str] = None
    purchase_date: date
    purchase_price: Optional[Decimal] = Field(None, example=64999.00)
    currency: Optional[str] = "INR"
    purchase_country: Optional[str] = "India"
    ownership_start_date: Optional[date] = None
    ownership_end_date: Optional[date] = None
    status: str = "CURRENTLY_OWNING" # CURRENTLY_OWNING, PREVIOUSLY_OWNED
    previous_phone: Optional[str] = Field(None, example="iPhone 12")
    purchase_source: Optional[str] = Field("Online Retailer", example="Online Retailer")
    
    # Optional initial report to submit at the same time
    initial_report: Optional[ExperienceReportCreate] = None

class OwnershipResponse(BaseModel):
    id: str
    product_id: str
    variant_id: Optional[str]
    purchase_date: date
    purchase_price: Optional[Decimal]
    currency: Optional[str]
    purchase_country: Optional[str]
    ownership_start_date: date
    ownership_end_date: Optional[date]
    status: str
    previous_phone: Optional[str]
    purchase_source: Optional[str]
    created_at: datetime
    variant: Optional[ProductVariantResponse] = None
    reports: List[ExperienceReportResponse] = []
    model_config = ConfigDict(from_attributes=True)
