# Frontend → Backend File Map

Every page calls the backend through `frontend/src/services/api.js`.
Each API call lands in one **endpoint file** (`backend/app/api/v1/endpoints/`), which delegates to one **service file** (`backend/app/services/`) with the same name.

Rule of thumb: **`X.py` endpoint → `X_service.py` service.**

| Frontend page / component | `api.js` function | HTTP route | Endpoint file | Service file |
|---|---|---|---|---|
| `ProductListPage` | `getProducts` | `GET /products` | `products.py` | `product_service.py` |
| `ProductListPage` | `getBrands` | `GET /products/brands` | `products.py` | *(query in endpoint)* |
| `ProductDetailPage` (header, variants) | `getProduct` | `GET /products/{id}` | `products.py` | `product_service.py` |
| `ProductDetailPage` → `IntelligenceOverview`, `IssueBreakdown`, `LongitudinalTimeline`, price-paid card | `getProductInsights` | `GET /products/{id}/insights` | `insights.py` | `insights_service.py` |
| `ProductDetailPage` → `ExperienceReportCard` list | `getProductExperiences` | `GET /products/{id}/experiences` | `experiences.py` | `experience_service.py` |
| `ComparePage` → `ComparisonMatrix` | `compareProducts` | `GET /products/compare` | `compare.py` | `compare_service.py` |
| `SubmitExperiencePage` → `OwnershipForm` | `registerOwnership` | `POST /ownerships` | `ownerships.py` | `ownership_service.py` (+ `experience_service.py` for the review) |
| *(follow-up review)* | `addExperienceReport` | `POST /ownerships/{id}/reports` | `ownerships.py` | `experience_service.py` |
| `SuggestProductPage` | `submitSuggestion` | `POST /product-suggestions` | `suggestions.py` | `suggestion_service.py` |
| `AdminDiscoveryPage` → Pipeline logs tab | `triggerDiscovery`, `listDiscoveryRuns` | `POST /discovery/run`, `GET /discovery/runs` | `discovery.py` | `discovery_service.py` |
| `AdminDiscoveryPage` → Suggestions tab (`SuggestionReviewCard`) | `listSuggestions`, `reviewSuggestion` | `GET /product-suggestions`, `POST /product-suggestions/{id}/review` | `suggestions.py` | `suggestion_service.py` |
| `AdminDiscoveryPage` → Catalog Manager tab (`CatalogManager`) | `adminCreateProduct`, `adminRenameProduct`, `adminDeleteProduct`, `adminCacheStats`, `adminFlushCache`, `verifyAdminKey` | `/admin/...` | `admin.py` | `product_service.py`, `deduplication_service.py`, `core/cache.py` |

## Shared helpers (used by several services)

| File | What it does |
|---|---|
| `services/deduplication_service.py` | Normalizes brand names and blocks duplicate phones (discovery, suggestions, admin add/rename) |
| `core/cache.py` | Response cache (RAM or Redis) used by all read endpoints |
| `core/schema_cleanup.py` | Drops retired database columns on startup |
| `providers/` | Tavily web search + Gemini extraction used by `discovery_service.py` |

## Vocabulary
The UI and the code use different words for two concepts:
- **"Share Experience" (UI)** = an **ownership** + its first **experience report** (code).
  An *ownership* is one person + one phone (variant, price paid). *Experience reports* are that person's reviews over time (3 months, 12 months, ...).
- **"Insights" / "Intelligence" (UI)** = `insights_service.py` (one phone). **"Compare" (UI)** = `compare_service.py` (two phones).
