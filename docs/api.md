# REST API Specification: WorthIt Platform

All API endpoints are prefixed with `/api/v1` and return structured JSON responses.

Interactive OpenAPI documentation is hosted at:
- **Swagger UI:** `http://127.0.0.1:8000/api/v1/docs`
- **ReDoc:** `http://127.0.0.1:8000/api/v1/redoc`

---

## 1. Endpoints Summary

### Products & Catalog
- `GET /api/v1/products`: Query and search products with pagination, brand filtering, and sorting (`popularity`, `satisfaction`, `long_term_owners`, `release_date`).
- `GET /api/v1/products/{id}`: Detailed product info, official variants, discovery sources, and owner counts.
- `POST /api/v1/products`: Create a new smartphone record.

### Longitudinal Product Intelligence & Insights
- `GET /api/v1/products/{id}/insights`: Compute sample-size-aware intelligence:
  - `confidence`: Sample tier (`VERY_LOW`, `LOW`, `MODERATE`, `HIGH`), badge label, authoritativeness.
  - `overall_satisfaction`, `battery_satisfaction`, `performance_satisfaction`, `software_satisfaction`.
  - `satisfaction_at_12m`: Long-term satisfaction isolated to 12+ month owners.
  - `would_buy_again`: Yes / Unsure / No percentages and top verified reasons.
  - `issue_breakdown`: Structured problem frequency distribution across owner base.
  - `repair_stats`: Repair rate percentage, median repair cost, and most frequently replaced components.
  - `tenure_summary`: Milestone progression curve across 1-3m, 4-6m, 7-12m, 13-18m, 19-24m+.
- `GET /api/v1/products/{id}/experiences`: Paginated list of raw owner experience reports with optional tenure filter (`min_months`, `max_months`).

### Longitudinal Product Comparison
- `GET /api/v1/products/compare?product_a={id}&product_b={id}`: Side-by-side longitudinal intelligence comparison with automatically computed key takeaways.

### Ownership & Experience Logging
- `POST /api/v1/ownerships`: Register device ownership with optional initial experience report.
- `GET /api/v1/ownerships/{id}`: Get ownership details and chronological reports.
- `POST /api/v1/ownerships/{id}/reports`: Add a subsequent longitudinal experience report (e.g. at 6 months or 12 months).

### Product Suggestions & Moderation
- `POST /api/v1/product-suggestions`: Submit a missing smartphone suggestion (runs deduplication check).
- `GET /api/v1/product-suggestions`: List submitted suggestions (filter by `status`).
- `POST /api/v1/product-suggestions/{id}/review`: Approve/reject or link duplicate suggestion.

### Automated Product Discovery
- `POST /api/v1/discovery/run`: Trigger a scheduled discovery run with search query topic and optional `force_mock` flag.
- `GET /api/v1/discovery/runs`: List historical discovery runs with audit statistics.
- `GET /api/v1/discovery/runs/{id}`: Inspect run logs and discovered sources.
