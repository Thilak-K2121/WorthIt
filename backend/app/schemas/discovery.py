from typing import List, Optional, Dict, Any
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field

class ExtractedVariant(BaseModel):
    ram: Optional[str] = None
    storage: Optional[str] = None
    chipset: Optional[str] = None
    launch_price: Optional[Decimal] = None
    currency: Optional[str] = "INR"

class ExtractedPhoneSpec(BaseModel):
    brand: str
    model_name: str
    official_name: Optional[str] = None
    release_date: Optional[date] = None
    official_url: Optional[str] = None
    country_market: Optional[str] = "Global"
    variants: List[ExtractedVariant] = []
    source_url: str
    source_title: Optional[str] = None
    source_snippet: Optional[str] = None
    confidence_score: float = 1.0

class DiscoveryTriggerRequest(BaseModel):
    query_topic: Optional[str] = Field("latest smartphone launch 2026", example="latest smartphone launch 2026")
    max_results: int = Field(5, ge=1, le=20)
    force_mock: bool = False

class ProductSourceSummaryResponse(BaseModel):
    id: str
    product_id: Optional[str] = None
    product_name: Optional[str] = None
    brand: Optional[str] = None
    model_name: Optional[str] = None
    source_url: str
    source_title: Optional[str] = None
    source_snippet: Optional[str] = None
    provider: str = "TAVILY"
    raw_extracted_json: Optional[Dict[str, Any]] = None
    discovered_at: datetime
    model_config = ConfigDict(from_attributes=True)

class DiscoveryRunResponse(BaseModel):
    id: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: str
    sources_searched: int
    candidates_found: int
    extracted_count: int
    duplicates_detected: int
    new_products_created: int
    failed_count: int
    error_log: Optional[str] = None
    sources: List[ProductSourceSummaryResponse] = []
    model_config = ConfigDict(from_attributes=True)

class DiscoveryRunDetailResponse(DiscoveryRunResponse):
    sources_discovered: List[Dict[str, Any]] = []

