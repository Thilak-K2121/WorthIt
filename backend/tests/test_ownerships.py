def test_register_ownership_and_add_report(client):
    # 1. Create a product first
    p_res = client.post("/api/v1/products", json={
        "brand": "OnePlus",
        "model_name": "12R",
        "variants": [{"ram": "8GB", "storage": "128GB", "launch_price": 39999.00}]
    })
    product_id = p_res.json()["id"]

    # 2. Register ownership with initial report
    ownership_payload = {
        "product_id": product_id,
        "purchase_date": "2024-02-15",
        "purchase_price": 39999.00,
        "ownership_start_date": "2024-02-15",
        "status": "CURRENTLY_OWNING",
        "initial_report": {
            "ownership_duration_months": 6,
            "overall_satisfaction": 4.5,
            "battery_satisfaction": 4.8,
            "performance_satisfaction": 4.7,
            "software_satisfaction": 4.2,
            "would_buy_again": "YES",
            "would_buy_again_reason": "Battery endurance is fantastic.",
            "issues": [
                {
                    "category_slug": "software",
                    "issue_title": "Occasional notification delay after latest OTA",
                    "severity": "LOW",
                    "resolved": True
                }
            ],
            "repairs": []
        }
    }
    o_res = client.post("/api/v1/ownerships", json=ownership_payload)
    assert o_res.status_code == 201
    o_data = o_res.json()
    assert o_data["product_id"] == product_id
    assert len(o_data["reports"]) == 1
    assert o_data["reports"][0]["ownership_duration_months"] == 6

    # 3. Add a subsequent 12-month report
    ownership_id = o_data["id"]
    report_12m_payload = {
        "ownership_duration_months": 12,
        "overall_satisfaction": 4.3,
        "battery_satisfaction": 4.4,
        "performance_satisfaction": 4.7,
        "software_satisfaction": 4.0,
        "battery_degradation_perception": "MINOR",
        "would_buy_again": "YES",
        "would_buy_again_reason": "Still very fast and charges rapidly.",
        "issues": []
    }
    r_res = client.post(f"/api/v1/ownerships/{ownership_id}/reports", json=report_12m_payload)
    assert r_res.status_code == 201
    assert r_res.json()["report_version"] == 2

    # 4. Verify product experiences endpoint returns reports
    exp_res = client.get(f"/api/v1/products/{product_id}/experiences?min_months=12")
    assert exp_res.status_code == 200
    exp_data = exp_res.json()
    assert len(exp_data) == 1
    assert exp_data[0]["ownership_duration_months"] == 12
