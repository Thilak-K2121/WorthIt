from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.api.v1.api import api_router
from app.models.issue import IssueCategory
from app.core.logging import logger

def seed_initial_issue_categories():
    """Seed initial structured issue taxonomy categories if not present."""
    db = SessionLocal()
    try:
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
        for slug, name, desc in categories:
            exists = db.query(IssueCategory).filter(IssueCategory.slug == slug).first()
            if not exists:
                cat = IssueCategory(slug=slug, display_name=name, description=desc)
                db.add(cat)
        db.commit()
    except Exception as e:
        logger.error(f"Error seeding issue categories: {e}")
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing WorthIt Platform Backend...")
    # Auto-create tables for local/testing environment (Alembic handles prod migrations)
    Base.metadata.create_all(bind=engine)
    seed_initial_issue_categories()
    yield
    logger.info("Shutting down WorthIt Platform Backend...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if "*" not in settings.CORS_ORIGINS else ["*"],
    allow_origin_regex=r"https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT
    }

app.include_router(api_router, prefix=settings.API_V1_STR)
