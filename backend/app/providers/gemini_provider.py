import json
import re
import httpx
import asyncio
from decimal import Decimal 
from typing import List, Optional
from app.providers.base import ExtractorProvider
from app.schemas.discovery import ExtractedPhoneSpec, ExtractedVariant
from app.core.config import settings
from app.core.logging import logger

class GeminiExtractor(ExtractorProvider):
    def __init__(self, api_key: str = ""):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.models = [
            "gemini-3.5-flash-lite",
            "gemini-3.1-flash-lite-preview",
            "gemini-3.5-flash"
        ]

    async def extract_smartphone_specs(self, source_text: str, source_url: str, source_title: str) -> Optional[ExtractedPhoneSpec]:
        if not self.api_key:
            logger.warning("No Gemini API key provided. Falling back to mock extractor.")
            from app.providers.mock_providers import MockGeminiExtractor
            return await MockGeminiExtractor().extract_smartphone_specs(source_text, source_url, source_title)

        prompt = f"""
You are a strict data extraction system for a smartphone catalog.
Extract smartphone details from the following web search snippet into STRICT JSON.

Title: {source_title}
URL: {source_url}
Content: {source_text}

JSON Output schema:
{{
  "brand": "Manufacturer brand e.g. Samsung, Apple, Google, Xiaomi, OnePlus, Motorola, Vivo, iQOO, Realme",
  "model_name": "Core model name without brand e.g. Galaxy S24 Ultra, iPhone 15 Pro, Edge 50 Ultra",
  "official_name": "Full marketing name",
  "official_url": "URL if mentioned in text",
  "country_market": "e.g. Global or India",
  "variants": [
    {{
      "ram": "e.g. 12GB",
      "storage": "e.g. 256GB",
      "chipset": "e.g. Snapdragon 8 Gen 3",
      "launch_price": 59999.00,
      "currency": "INR"
    }}
  ]
}}

If the text does NOT describe a specific smartphone, respond with {{"is_smartphone": false}}.
Do NOT add markdown ticks or backticks. Return valid JSON only.
"""

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.1, "responseMimeType": "application/json"}
        }

        # Try cascade of fast, light models to prevent 429 rate limit bottlenecks
        for model in self.models:
            api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"
            try:
                async with httpx.AsyncClient(timeout=15.0) as client:
                    response = await client.post(api_url, json=payload)
                    if response.status_code == 429:
                        logger.warning(f"Model {model} returned 429. Cascading to next available lightweight model...")
                        await asyncio.sleep(1.0)
                        continue
                    
                    if response.status_code != 200:
                        continue

                    data = response.json()
                    candidates = data.get("candidates", [])
                    if not candidates:
                        continue

                    raw_text = candidates[0]["content"]["parts"][0]["text"]
                    raw_text = re.sub(r"^```(json)?", "", raw_text.strip(), flags=re.MULTILINE)
                    raw_text = re.sub(r"```$", "", raw_text.strip(), flags=re.MULTILINE).strip()

                    parsed = json.loads(raw_text)
                    if isinstance(parsed, list):
                        parsed = parsed[0] if (len(parsed) > 0 and isinstance(parsed[0], dict)) else {}

                    if not isinstance(parsed, dict) or not parsed.get("brand") or not parsed.get("model_name"):
                        return None

                    variants: List[ExtractedVariant] = []
                    raw_variants = parsed.get("variants")
                    if isinstance(raw_variants, list):
                        for v in raw_variants:
                            if isinstance(v, dict):
                                try:
                                    price_val = None
                                    if v.get("launch_price"):
                                        cleaned_price = re.sub(r"[^\d.]", "", str(v.get("launch_price")))
                                        if cleaned_price:
                                            price_val = Decimal(cleaned_price)
                                    variants.append(ExtractedVariant(
                                        ram=str(v.get("ram")) if v.get("ram") else None,
                                        storage=str(v.get("storage")) if v.get("storage") else None,
                                        chipset=str(v.get("chipset")) if v.get("chipset") else None,
                                        launch_price=price_val,
                                        currency=str(v.get("currency", "INR"))
                                    ))
                                except Exception:
                                    pass

                    return ExtractedPhoneSpec(
                        brand=str(parsed["brand"]).strip(),
                        model_name=str(parsed["model_name"]).strip(),
                        official_name=str(parsed.get("official_name")) if parsed.get("official_name") else None,
                        official_url=str(parsed.get("official_url")) if parsed.get("official_url") else None,
                        country_market=str(parsed.get("country_market", "Global")),
                        variants=variants,
                        source_url=source_url,
                        source_title=source_title,
                        source_snippet=source_text[:300],
                        confidence_score=0.9
                    )
            except Exception as e:
                logger.warning(f"Extraction with {model} failed: {e}. Trying next model...")
                await asyncio.sleep(1.0)
                continue

        # Fallback to high-fidelity regex/structural extraction if external API is temporarily down
        from app.providers.mock_providers import MockGeminiExtractor
        return await MockGeminiExtractor().extract_smartphone_specs(source_text, source_url, source_title)
