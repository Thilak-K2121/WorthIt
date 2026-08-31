from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field

class ProductSuggestionCreate(BaseModel):
    brand: str = Field(..., example="Nothing")
    model_name: str = Field(..., example="Phone (3)")
    variant_details: Optional[str] = Field(None, example="12GB / 256GB")
    official_url: Optional[str] = Field(None, example="https://nothing.tech")
    approximate_release_date: Optional[date] = None
    notes: Optional[str] = Field(None, example="Launched in India in July 2026")

class ProductSuggestionReview(BaseModel):
    action: str = Field(..., example="APPROVE") # APPROVE, REJECT, MARK_DUPLICATE
    target_product_id: Optional[str] = None
    rejection_reason: Optional[str] = None

class ProductSuggestionResponse(BaseModel):
    id: str
    brand: str
    model_name: str
    variant_details: Optional[str]
    official_url: Optional[str]
    approximate_release_date: Optional[date]
    notes: Optional[str]
    status: str
    target_product_id: Optional[str]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
