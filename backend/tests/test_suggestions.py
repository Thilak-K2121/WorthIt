def test_user_suggestion_and_admin_review(client):
    # 1. Submit suggestion
    s_res = client.post("/api/v1/product-suggestions", json={
        "brand": "iQOO",
        "model_name": "Neo 9 Pro",
        "variant_details": "8GB / 256GB",
        "official_url": "https://iqoo.com",
        "notes": "Launched early 2024"
    })
    assert s_res.status_code == 201
    s_data = s_res.json()
    assert s_data["status"] == "PENDING"
    suggestion_id = s_data["id"]

    # 2. List pending suggestions
    list_res = client.get("/api/v1/product-suggestions?status=PENDING")
    assert list_res.status_code == 200
    assert any(s["id"] == suggestion_id for s in list_res.json())

    # 3. Admin approves suggestion
    review_res = client.post(f"/api/v1/product-suggestions/{suggestion_id}/review", json={
        "action": "APPROVE"
    })
    assert review_res.status_code == 200
    assert review_res.json()["status"] == "APPROVED"
    assert review_res.json()["target_product_id"] is not None

    # 4. Verify product now appears in catalog
    cat_res = client.get("/api/v1/products?search=Neo 9 Pro")
    assert cat_res.status_code == 200
    assert cat_res.json()["total"] == 1
    assert cat_res.json()["items"][0]["brand"] == "iQOO"
