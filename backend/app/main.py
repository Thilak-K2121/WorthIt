# ==============================================================================
# WorthIt Backend - Main Application Entrypoint
# ==============================================================================
# This file initializes the FastAPI application instance, configures CORS
# middleware, manages application startup/shutdown lifecycles (including table
# creation and catalog seeding), and registers API v1 routers.
# ==============================================================================

from contextlib import asynccontextmanager
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.api.v1.api import api_router
from app.models.issue import IssueCategory
from app.core.logging import logger
from app.core.cache import cache

def seed_initial_issue_categories():
    """
    Seeds default structured hardware/software issue taxonomy categories.
    
    Why this function exists:
    Ensures that whenever a user or test reports a hardware fault (e.g. green lines,
    battery swelling, thermal throttling), standardized categories exist in the database.
    """
    db = SessionLocal()
    try:
        # Standardized taxonomy mapping: (slug, display name, descriptive symptoms)
        categories = [
            ("battery", "Battery Degradation & Life", "Fast draining, capacity reduction, unexpected shutdown"),
            ("heating", "Thermal / Heating", "Excessive heat during charging, gaming, or general use"),
            ("display", "Display & Touch", "Green lines, tint, touch latency, burn-in, brightness anomalies"),
            ("camera", "Camera & Optics", "Lens fogging, autofocus hunting, shutter lag, image processing bugs"),
            ("charging", "Charging & Port", "Slow charging, cable disconnects, loose port, wireless charging failure"),
            ("software", "Software & UI Bugs", "App crashes, UI stutter, update bugs, bootloops"),
            ("performance", "Performance Degradation", "Throttling, lag after updates, RAM management issues"),
            ("connectivity", "Connectivity & Network", "5G/Wi-Fi drops, Bluetooth disconnects, GPS accuracy issues"),
            ("build", "Build & Physical Durability", "Frame chipping, back glass cracking without drop, button rattle"),
            ("speaker_mic", "Speaker & Microphone", "Muffled earpiece, crackling audio, call volume issues"),
            ("other", "Other / Miscellaneous", "Other unclassified hardware or software issues")
        ]
        # Insert only if not already present to ensure idempotency
        for slug, name, desc in categories:
            exists = db.query(IssueCategory).filter(IssueCategory.slug == slug).first()
            if not exists:
                cat = IssueCategory(slug=slug, display_name=name)
                db.add(cat)
        db.commit()
    except Exception as e:
        logger.error(f"Error seeding issue categories: {e}")
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI Lifespan Manager: Manages startup and shutdown hooks.
    
    Startup Actions:
    1. Base.metadata.create_all(bind=engine): Auto-creates database schema if missing.
    2. seed_initial_issue_categories(): Populates standardized issue categories.
    3. seed_famous_smartphones(): Ingests 98+ smartphones across 17 brands on boot.
    """
    logger.info("Initializing WorthIt Platform Backend...")
    # Auto-create tables for local/testing environment (Alembic handles prod migrations)
    Base.metadata.create_all(bind=engine)
    # create_all never removes columns; drop the retired unused ones (idempotent)
    try:
        from app.core.schema_cleanup import drop_retired_columns
        drop_retired_columns(engine)
    except Exception as e:
        logger.error(f"Retired-column cleanup failed (inserts may fail until fixed): {e}")
    seed_initial_issue_categories()
    try:
        from app.seed.seed_famous_smartphones import seed_famous_smartphones
        seed_famous_smartphones()
    except Exception as e:
        logger.error(f"Error seeding famous smartphones on startup: {e}")
    # Startup seeding may have changed the catalog; drop any stale cached responses (matters for shared Redis)
    cache.invalidate_all()
    logger.info(f"Response cache backend: {cache.name}")
    yield
    logger.info("Shutting down WorthIt Platform Backend...")

# Initialize FastAPI instance with project metadata and Swagger/OpenAPI documentation URLs
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan
)

# Configure Cross-Origin Resource Sharing (CORS) to allow requests from frontend SPA & cloud CDN
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if "*" not in settings.CORS_ORIGINS else ["*"],
    allow_origin_regex=r"https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # Let the browser read cache/latency diagnostics headers
    expose_headers=["X-Cache", "X-Process-Time-Ms"],
)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Stamps server-side processing time on every response (used for Redis before/after benchmarks)."""
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Process-Time-Ms"] = f"{(time.perf_counter() - start) * 1000:.2f}"
    return response

@app.get("/health", tags=["System"])
def health_check():
    """
    Cloud Health Check Endpoint.
    
    Returns:
        JSON response with 200 OK indicating the service and environment are active.
    """
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "cache": cache.name
    }

# Register all API version 1 route endpoints under prefix (e.g. /api/v1)
app.include_router(api_router, prefix=settings.API_V1_STR)
