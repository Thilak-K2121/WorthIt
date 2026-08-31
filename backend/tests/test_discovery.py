def test_automated_discovery_run_and_idempotency(client):
    # Trigger discovery run with force_mock=True
    res = client.post("/api/v1/discovery/run", json={"force_mock": True, "max_results": 2})
    assert res.status_code == 200
    run1 = res.json()
    assert run1["status"] == "COMPLETED"
    assert run1["new_products_created"] >= 1
    initial_created = run1["new_products_created"]

    # Trigger second run with identical mock data to test idempotency and duplicate detection
    res2 = client.post("/api/v1/discovery/run", json={"force_mock": True, "max_results": 2})
    assert res2.status_code == 200
    run2 = res2.json()
    assert run2["status"] == "COMPLETED"
    # Products discovered in run 1 must now be detected as duplicates
    assert run2["duplicates_detected"] >= initial_created
    assert run2["new_products_created"] == 0

    # Verify run list endpoint
    runs_res = client.get("/api/v1/discovery/runs")
    assert runs_res.status_code == 200
    assert len(runs_res.json()) >= 2
