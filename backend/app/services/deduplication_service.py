import re
from typing import Tuple, Optional
from sqlalchemy.orm import Session
from app.models.product import Product

class DeduplicationService:
    # Common Brand Normalization Map
    BRAND_ALIASES = {
        "samsung electronics": "Samsung",
        "galaxy": "Samsung",
        "samsung": "Samsung",
        "apple inc": "Apple",
        "apple": "Apple",
        "iphone": "Apple",
        "google": "Google",
        "pixel": "Google",
        "oneplus": "OnePlus",
        "one plus": "OnePlus",
        "1+": "OnePlus",
        "xiaomi": "Xiaomi",
        "mi": "Xiaomi",
        "redmi": "Xiaomi",
        "poco": "POCO",
        "motorola": "Motorola",
        "moto": "Motorola",
        "realme": "Realme",
        "oppo": "OPPO",
        "vivo": "Vivo",
        "iqoo": "iQOO",
        "nothing": "Nothing",
        "nothing tech": "Nothing",
        "asus": "ASUS",
        "rog": "ASUS",
        "sony": "Sony",
        "xperia": "Sony",
        "honor": "Honor",
        "huawei": "Huawei"
    }

    # Noise tokens to strip from normalized key
    NOISE_PATTERNS = [
        r"\b5g\b",
        r"\b4g\b",
        r"\blte\b",
        r"\bglobal\s*edition\b",
        r"\bglobal\s*version\b",
        r"\bindian\s*edition\b",
        r"\bsmartphone\b",
        r"\bmobile\b",
        r"\bphone\b",
        r"\bseries\b",
        r"\bdual\s*sim\b"
    ]

    @classmethod
    def normalize_brand(cls, brand_raw: str) -> str:
        if not brand_raw:
            return "Generic"
        cleaned = brand_raw.strip().lower()
        return cls.BRAND_ALIASES.get(cleaned, brand_raw.strip().title())

    @classmethod
    def generate_normalized_key(cls, brand: str, model_name: str) -> str:
        """
        Creates a deterministic normalized key, e.g.
        'Samsung', 'Galaxy S26 Ultra 5G' -> 'samsung-galaxy-s26-ultra'
        'Apple Inc', 'iPhone 15 Pro Max (Global)' -> 'apple-iphone-15-pro-max'
        """
        norm_brand = cls.normalize_brand(brand).lower()
        model_clean = model_name.lower().strip()

        # If model already starts with brand name (e.g. 'Samsung Galaxy S24'), don't repeat brand
        if model_clean.startswith(norm_brand):
            combined = model_clean
        else:
            combined = f"{norm_brand} {model_clean}"

        # Strip noise patterns
        for pattern in cls.NOISE_PATTERNS:
            combined = re.sub(pattern, "", combined, flags=re.IGNORECASE)

        # Remove special characters except hyphens and spaces
        combined = re.sub(r"[^\w\s-]", "", combined)
        # Collapse multiple spaces and hyphens
        combined = re.sub(r"[\s_]+", "-", combined.strip())
        combined = re.sub(r"-+", "-", combined).strip("-")

        return combined

    @classmethod
    def find_existing_duplicate(cls, db: Session, brand: str, model_name: str) -> Tuple[Optional[Product], float]:
        """
        Check if product already exists via:
        1. Exact normalized_name match (1.0 confidence)
        2. Token-set match (0.95 confidence)
        """
        norm_key = cls.generate_normalized_key(brand, model_name)

        # 1. Exact normalized key match
        exact_match = db.query(Product).filter(Product.normalized_name == norm_key).first()
        if exact_match:
            return exact_match, 1.0

        # 2. Token-set comparison across the same brand
        canonical_brand = cls.normalize_brand(brand)
        candidates = db.query(Product).filter(Product.brand.ilike(canonical_brand)).all()
        
        target_tokens = set(norm_key.split("-"))
        # Remove brand token from comparison if present
        target_tokens.discard(canonical_brand.lower())

        for candidate in candidates:
            cand_tokens = set(candidate.normalized_name.split("-"))
            cand_tokens.discard(candidate.brand.lower())
            
            if target_tokens and cand_tokens:
                intersection = target_tokens.intersection(cand_tokens)
                union = target_tokens.union(cand_tokens)
                jaccard = len(intersection) / len(union) if union else 0.0

                # High token similarity threshold
                if jaccard >= 0.8:
                    return candidate, jaccard

        return None, 0.0
