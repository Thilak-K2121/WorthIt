def test_intelligence_empty_data(client):
    p_res = client.post("/api/v1/products", json={"brand": "Sony", "model_name": "Xperia 1 VI"})
    pid = p_res.json()["id"]

    res = client.get(f"/api/v1/products/{pid}/insights")
    assert res.status_code == 200
    data = res.json()
    assert data["total_registered_owners"] == 0
    assert data["confidence"]["confidence_level"] == "NONE"
    assert data["confidence"]["is_authoritative"] is False
    assert data["overall_satisfaction"]["score"] is None

def test_intelligence_sample_confidence_and_aggregation(client):
    p_res = client.post("/api/v1/products", json={"brand": "Nothing", "model_name": "Phone (2a)"})
    pid = p_res.json()["id"]

    # Register 6 owners with varying durations
    for dur, sat in [(3, 4.0), (6, 4.2), (12, 4.6), (12, 4.4), (18, 4.8), (24, 4.2)]:
        client.post("/api/v1/ownerships", json={
            "product_id": pid,
            "purchase_date": "2024-03-10",
            "ownership_start_date": "2024-03-10",
            "initial_report": {
                "ownership_duration_months": dur,
                "overall_satisfaction": sat,
                "battery_satisfaction": 4.5,
                "performance_satisfaction": 4.2,
                "software_satisfaction": 4.4,
                "would_buy_again": "YES" if sat >= 4.2 else "NO"
            }
        })

    res = client.get(f"/api/v1/products/{pid}/insights")
    assert res.status_code == 200
    data = res.json()
    assert data["total_registered_owners"] == 6
    assert data["long_term_owners_12m_plus"] == 4
    assert data["confidence"]["confidence_level"] == "LOW"
    assert data["overall_satisfaction"]["score"] > 4.0
    assert data["would_buy_again"]["yes_percentage"] is not None

def test_product_comparison(client):
    p1 = client.post("/api/v1/products", json={"brand": "BrandA", "model_name": "Phone A"}).json()["id"]
    p2 = client.post("/api/v1/products", json={"brand": "BrandB", "model_name": "Phone B"}).json()["id"]

    res = client.get(f"/api/v1/products/compare?product_a={p1}&product_b={p2}")
    assert res.status_code == 200
    data = res.json()
    assert data["product_a"]["model_name"] == "Phone A"
    assert data["product_b"]["model_name"] == "Phone B"
    assert len(data["key_takeaways"]) > 0
