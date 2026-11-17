from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

# Normalize any PostgreSQL URL form (postgres://, postgresql://, postgresql+psycopg://, ...)
# to the psycopg2 driver, which is the one installed via requirements.txt.
# Without this, e.g. a "postgresql+psycopg://" URL crashes startup with "No module named 'psycopg'".
db_url = settings.DATABASE_URL.strip()
_scheme, _sep, _rest = db_url.partition("://")
if _sep and _scheme.split("+", 1)[0] in ("postgres", "postgresql"):
    db_url = f"postgresql+psycopg2://{_rest}"

# Configure SQLite vs PostgreSQL parameters
connect_args = {}
if db_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    db_url,
    connect_args=connect_args,
    pool_pre_ping=True,
    echo=settings.DEBUG and not db_url.startswith("sqlite")
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
