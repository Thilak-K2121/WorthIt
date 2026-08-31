# WorthIt — Long-Term Product Experience Platform (Smartphones)

> **Longitudinal ownership intelligence for consumer technology.**
> Discover what actually happens after 3, 6, 12, and 24 months of smartphone ownership: real-world battery degradation, software update stability, repair frequencies, out-of-pocket costs, and true repurchase intent.

---

## 🌟 Core Problem & Differentiator

Most online product reviews focus exclusively on the product when it is brand new or after a few days of unboxing use. Buyers want to know what happens after **6 months, 1 year, or 2 years** of actual daily wear:
- *Does the battery severely degrade after 12 months?*
- *Did recent OS updates cause thermal throttling or UI stutter?*
- *What is the median repair cost for screen or battery replacement?*
- *Would real owners buy the phone again knowing what they know now?*

WorthIt captures **longitudinal ownership data** rather than generic star reviews.

---

## 🛠 Tech Stack

- **Frontend:** React 18, Vite, JavaScript, Tailwind CSS, Lucide Icons, React Router v6.
- **Backend:** Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.0, Alembic.
- **Database:** PostgreSQL (with SQLite zero-config local mode).
- **External Discovery:** Tavily Search API (launch discovery) & Google Gemini API (structured extraction) with high-fidelity offline mock fallbacks.
- **Testing:** Pytest, pytest-asyncio, FastAPI TestClient.
- **Containerization:** Docker & Docker Compose.

---

## 🚀 Quick Start & Local Setup

### 1. Backend Setup (FastAPI)

```bash
cd backend

# Create virtual environment (optional)
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Seed realistic multi-year longitudinal smartphones dataset
python -m app.seed.seed_data

# Start FastAPI dev server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

FastAPI server runs at `http://127.0.0.1:8000`.
- **Interactive Swagger Docs:** `http://127.0.0.1:8000/api/v1/docs`
- **ReDoc:** `http://127.0.0.1:8000/api/v1/redoc`

---

### 2. Frontend Setup (React + Vite)

```bash
cd frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```

Frontend runs at `http://localhost:5173`.

---

### 3. Docker Compose (Full Stack)

To run the complete production stack (PostgreSQL + FastAPI backend):

```bash
docker compose up --build
```

---

## 🧪 Running Automated Tests

The test suite covers deterministic normalization, duplicate prevention, longitudinal intelligence aggregation, sample confidence tiers, discovery idempotency, and REST CRUD flows:

```bash
cd backend
pytest -v
```

---

## 📑 Key Features & Pages

1. **Home (`/`):** Hero, longitudinal value pillars, 12M+ ownership leaders.
2. **Smartphone Catalog (`/products`):** Multi-facet brand filters, search, and sorting by tenure metrics.
3. **Product Deep-Dive (`/products/:id`):**
   - Sample Size Confidence Transparency Banner (`n=...`)
   - Longitudinal Intelligence Metrics (Battery, Software, Performance, Camera)
   - Longitudinal Ownership Curve (Tenure Milestones: 1-3m, 4-6m, 7-12m, 13-18m, 19-24m+)
   - Structured Problem Taxonomy (User-reported failure patterns)
   - Verified Owner Experience Logs with duration filters
4. **Longitudinal Comparison (`/compare`):** Side-by-side longitudinal intelligence matrix and automated data takeaways.
5. **Log Ownership (`/submit`):** Frictionless flow to log device tenure, ratings, battery degradation perception, and repurchase verdict.
6. **Missing Phone? (`/suggest`):** User suggestion system with automatic duplicate detection.
7. **Discovery & Moderation Console (`/admin`):** Trigger Tavily + Gemini discovery runs, view live run audit logs, and moderate suggestion queue.
8. **Trust Model (`/about`):** Detailed explanation of sample sizes, scientific honesty, and anti-fraud methodology.

---

## 📂 Documentation

- 📄 [System Architecture](docs/architecture.md)
- 🗄 [Database Schema & ERD](docs/database.md)
- 🔌 [REST API Specification](docs/api.md)
- 🤖 [Product Discovery Pipeline](docs/product-discovery.md)

---

## 🔒 Security & Data Trust Model

- **Environment Isolation:** Zero hardcoded API keys; managed via `.env` with fallback mock providers for zero-cost testing.
- **Deterministic Deduplication:** Noise stripping (`5G`, `LTE`, `Global Version`), brand aliasing, and token Jaccard similarity.
- **Scientific Honesty:** Clear distinction between *"Reported by owners"* and OEM laboratory failure rates.
