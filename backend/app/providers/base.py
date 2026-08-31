from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from app.schemas.discovery import ExtractedPhoneSpec

class DiscoverySearchResult:
    def __init__(self, url: str, title: str, snippet: str, raw_data: Optional[Dict[str, Any]] = None):
        self.url = url
        self.title = title
        self.snippet = snippet
        self.raw_data = raw_data or {}

class DiscoveryProvider(ABC):
    @abstractmethod
    async def search_smartphone_launches(self, query: str, max_results: int = 5) -> List[DiscoverySearchResult]:
        """Search the web for smartphone launch announcements and spec pages."""
        pass

class ExtractorProvider(ABC):
    @abstractmethod
    async def extract_smartphone_specs(self, source_text: str, source_url: str, source_title: str) -> Optional[ExtractedPhoneSpec]:
        """Extract strict, structured smartphone specs and variants from raw text."""
        pass
