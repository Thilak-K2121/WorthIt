import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.core.database import Base
from app.api.deps import get_db
from app.models.issue import IssueCategory
from app.main import app

@pytest.fixture(scope="function")
def test_db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    
    # Pre-seed categories
    session = TestingSessionLocal()
    categories = [
        ("battery", "Battery Degradation & Life", "Fast draining, capacity reduction"),
        ("heating", "Thermal / Heating", "Excessive heat"),
        ("display", "Display & Touch", "Green lines, tint"),
        ("camera", "Camera & Optics", "Lens fogging"),
        ("charging", "Charging & Port", "Slow charging"),
        ("software", "Software & UI Bugs", "App crashes"),
        ("performance", "Performance Degradation", "Throttling"),
        ("connectivity", "Connectivity & Network", "5G/Wi-Fi drops"),
        ("build", "Build & Physical Durability", "Frame chipping"),
        ("speaker_mic", "Speaker & Microphone", "Muffled earpiece"),
        ("other", "Other / Miscellaneous", "Other")
    ]
    for slug, name, desc in categories:
        cat = IssueCategory(slug=slug, display_name=name, description=desc)
        session.add(cat)
    session.commit()
    session.close()

    try:
        yield TestingSessionLocal
    finally:
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(test_db):
    session = test_db()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture(scope="function")
def client(test_db):
    def override_get_db():
        db = test_db()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
