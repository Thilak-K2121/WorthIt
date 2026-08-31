import datetime
from decimal import Decimal
from typing import List, Optional
from app.providers.base import DiscoveryProvider, ExtractorProvider, DiscoverySearchResult
from app.schemas.discovery import ExtractedPhoneSpec, ExtractedVariant

class MockTavilyProvider(DiscoveryProvider):
    async def search_smartphone_launches(self, query: str, max_results: int = 5) -> List[DiscoverySearchResult]:
        mock_results = [
            DiscoverySearchResult(
                url="https://gsmarena.com/nothing_phone_3_official_specs_2026",
                title="Nothing Phone (3) Launched with Snapdragon 8s Gen 3, Glyph Matrix 2.0",
                snippet="Nothing has officially unveiled the Nothing Phone (3) featuring Qualcomm Snapdragon 8s Gen 3, 12GB RAM, 256GB storage, and a 6.7-inch OLED 120Hz display starting at ₹49,999 in India."
            ),
            DiscoverySearchResult(
                url="https://gadgets360.com/xiaomi-15-ultra-release-date-price",
                title="Xiaomi 15 Ultra Global Launch: 1-inch Sony Sensor, 16GB RAM, 512GB Storage",
                snippet="Xiaomi 15 Ultra made its global debut featuring Leica quad camera system, Snapdragon 8 Gen 4 processor, 5400mAh battery with 90W fast charging."
            ),
            DiscoverySearchResult(
                url="https://theverge.com/google-pixel-9a-official-announcement",
                title="Google Pixel 9a brings Tensor G4 and clean Android experience for $499",
                snippet="Google officially announced the Pixel 9a featuring Tensor G4 chip, 8GB RAM, 128GB and 256GB storage options with 7 years of OS updates."
            ),
            DiscoverySearchResult(
                url="https://samsung.com/news/galaxy-s25-fe-announced",
                title="Samsung Galaxy S25 FE 5G: Flagship Essentials at an Accessible Price",
                snippet="Samsung introduces Galaxy S25 FE 5G equipped with Exynos 2500, 8GB RAM, 128GB/256GB internal storage, dynamic AMOLED 2X screen."
            )
        ]
        return mock_results[:max_results]

class MockGeminiExtractor(ExtractorProvider):
    async def extract_smartphone_specs(self, source_text: str, source_url: str, source_title: str) -> Optional[ExtractedPhoneSpec]:
        text_lower = (source_text + " " + source_title).lower()

        if "nothing" in text_lower and "phone" in text_lower:
            return ExtractedPhoneSpec(
                brand="Nothing",
                model_name="Phone (3)",
                official_name="Nothing Phone (3)",
                release_date=datetime.date.today(),
                official_url="https://nothing.tech",
                country_market="Global",
                source_url=source_url,
                source_title=source_title,
                source_snippet=source_text[:300],
                confidence_score=0.98,
                variants=[
                    ExtractedVariant(ram="12GB", storage="256GB", chipset="Snapdragon 8s Gen 3", launch_price=Decimal("49999.00"), currency="INR"),
                    ExtractedVariant(ram="16GB", storage="512GB", chipset="Snapdragon 8s Gen 3", launch_price=Decimal("57999.00"), currency="INR")
                ]
            )
        elif "xiaomi" in text_lower:
            return ExtractedPhoneSpec(
                brand="Xiaomi",
                model_name="15 Ultra",
                official_name="Xiaomi 15 Ultra",
                release_date=datetime.date.today(),
                official_url="https://mi.com",
                country_market="Global",
                source_url=source_url,
                source_title=source_title,
                source_snippet=source_text[:300],
                confidence_score=0.95,
                variants=[
                    ExtractedVariant(ram="16GB", storage="512GB", chipset="Snapdragon 8 Gen 4", launch_price=Decimal("89999.00"), currency="INR")
                ]
            )
        elif "pixel" in text_lower and "9a" in text_lower:
            return ExtractedPhoneSpec(
                brand="Google",
                model_name="Pixel 9a",
                official_name="Google Pixel 9a",
                release_date=datetime.date.today(),
                official_url="https://store.google.com",
                country_market="Global",
                source_url=source_url,
                source_title=source_title,
                source_snippet=source_text[:300],
                confidence_score=0.96,
                variants=[
                    ExtractedVariant(ram="8GB", storage="128GB", chipset="Google Tensor G4", launch_price=Decimal("43999.00"), currency="INR"),
                    ExtractedVariant(ram="8GB", storage="256GB", chipset="Google Tensor G4", launch_price=Decimal("49999.00"), currency="INR")
                ]
            )
        elif "galaxy" in text_lower and "fe" in text_lower:
            return ExtractedPhoneSpec(
                brand="Samsung",
                model_name="Galaxy S25 FE",
                official_name="Samsung Galaxy S25 FE 5G",
                release_date=datetime.date.today(),
                official_url="https://samsung.com",
                country_market="Global",
                source_url=source_url,
                source_title=source_title,
                source_snippet=source_text[:300],
                confidence_score=0.94,
                variants=[
                    ExtractedVariant(ram="8GB", storage="128GB", chipset="Exynos 2500", launch_price=Decimal("54999.00"), currency="INR"),
                    ExtractedVariant(ram="8GB", storage="256GB", chipset="Exynos 2500", launch_price=Decimal("59999.00"), currency="INR")
                ]
            )
        else:
            return None
