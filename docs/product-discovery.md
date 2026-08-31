# Product Discovery & Structured Extraction Pipeline

The automated discovery pipeline ensures that newly released smartphones appear in the catalog without requiring manual input for every phone, while preserving strict source evidence and deduplication integrity.

---

## 1. Pipeline Architecture

```
Scheduled Job / Manual Trigger
       ↓
Tavily Search Provider
  (Queries recent smartphone announcements & specs)
       ↓
Search Results (URLs, Titles, Snippets)
       ↓
Google Gemini Extractor
  (Strict JSON Schema specification enforcement)
       ↓
Pydantic v2 Validation
  (Type checking, variant parsing, price decimal validation)
       ↓
Deterministic Deduplication Engine
  - Brand alias normalization ("Mi" → "Xiaomi", "One Plus" → "OnePlus")
  - Noise stripping ("5G", "4G LTE", "Global Edition")
  - Token-set Jaccard similarity comparison
       ↓
[Duplicate Found] ───→ Link Product Source provenance to existing device
       ↓
[New Device]      ───→ Ingest Product + Variants + Source Evidence
       ↓
Finalize Product Discovery Run Audit Record
```

---

## 2. Deterministic Deduplication Engine

The backend relies on deterministic normalization rather than non-deterministic AI for catalog identity:

1. **Brand Normalization:**
   - Canonical map for known aliases: `galaxy` $\rightarrow$ `Samsung`, `apple inc` $\rightarrow$ `Apple`, `1+` / `one plus` $\rightarrow$ `OnePlus`, `mi` / `redmi` $\rightarrow$ `Xiaomi`, `nothing tech` $\rightarrow$ `Nothing`.
2. **Normalized Key Generation:**
   - Strips marketing noise (`5G`, `LTE`, `Global Version`, `Dual SIM`).
   - Generates lowercase hyphenated slug (e.g. `Samsung Galaxy S24 Ultra 5G` $\rightarrow$ `samsung-galaxy-s24-ultra`).
3. **Fuzzy Token Matching:**
   - Evaluates token set Jaccard similarity ($\ge 0.8$) against devices of the same canonical brand to handle out-of-order words (e.g. `Galaxy S24 Ultra Samsung`).

---

## 3. Observability & Provenance

Every discovery execution creates a `ProductDiscoveryRun` containing:
- `started_at` & `completed_at`
- `sources_searched`
- `candidates_found`
- `extracted_count`
- `duplicates_detected`
- `new_products_created`
- `failed_count`
- `error_log`

Every discovered product retains linked `product_sources` records storing the source URL, title, snippet, and raw extraction payload.
