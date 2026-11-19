import datetime

from app.models.discovery import ProductDiscoveryRun


def test_api_timestamps_are_explicit_utc(client):
    """Naive timestamps were parsed by browsers as local time (5h30m off in India),
    which broke the discovery page's completion check."""
    run = client.post("/api/v1/discovery/run", json={"force_mock": True, "max_results": 1}).json()
    assert run["started_at"].endswith("Z")
    assert run["completed_at"].endswith("Z")

    product = client.post("/api/v1/products", json={"brand": "Clock", "model_name": "One"}).json()
    detail = client.get(f"/api/v1/products/{product['id']}").json()
    assert detail["created_at"].endswith("Z") and detail["updated_at"].endswith("Z")


def test_interrupted_runs_are_failed_on_startup(test_db, monkeypatch):
    import app.main as main

    session = test_db()
    session.add(ProductDiscoveryRun(status="RUNNING", started_at=datetime.datetime.utcnow()))
    session.add(ProductDiscoveryRun(status="COMPLETED", started_at=datetime.datetime.utcnow()))
    session.commit()
    session.close()

    monkeypatch.setattr(main, "SessionLocal", test_db)
    main.fail_interrupted_discovery_runs()

    session = test_db()
    statuses = sorted(r.status for r in session.query(ProductDiscoveryRun).all())
    failed = session.query(ProductDiscoveryRun).filter_by(status="FAILED").one()
    session.close()
    assert statuses == ["COMPLETED", "FAILED"]
    assert "restarted" in failed.error_log
    assert failed.completed_at is not None


def test_run_discovery_requires_admin_key(client, monkeypatch):
    from app.core.config import settings
    monkeypatch.setattr(settings, "ADMIN_API_KEY", "s3cret")
    body = {"force_mock": True, "max_results": 1}
    assert client.post("/api/v1/discovery/run", json=body).status_code == 401
    assert client.post("/api/v1/discovery/run", json=body, headers={"X-Admin-Key": "wrong"}).status_code == 401
    assert client.post("/api/v1/discovery/run", json=body, headers={"X-Admin-Key": "s3cret"}).status_code == 200
    # viewing the logs stays public
    assert client.get("/api/v1/discovery/runs").status_code == 200
