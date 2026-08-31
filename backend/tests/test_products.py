def test_create_and_list_products(client):
    payload = {
        "brand": "Google",
        "model_name": "Pixel 9 Pro",
        "official_name": "Google Pixel 9 Pro",
        "release_date": "2024-09-04",
        "variants": [
            {"ram": "16GB", "storage": "128GB", "chipset": "Google Tensor G4", "launch_price": 109999.00},
            {"ram": "16GB", "storage": "256GB", "chipset": "Google Tensor G4", "launch_price": 119999.00}
        ]
    }
    res = client.post("/api/v1/products", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["brand"] == "Google"
    assert data["normalized_name"] == "google-pixel-9-pro"
    assert len(data["variants"]) == 2

    # Test list endpoint
    list_res = client.get("/api/v1/products?search=Pixel")
    assert list_res.status_code == 200
    list_data = list_res.json()
    assert list_data["total"] == 1
    assert list_data["items"][0]["model_name"] == "Pixel 9 Pro"

def test_get_product_not_found(client):
    res = client.get("/api/v1/products/non-existent-uuid")
    assert res.status_code == 404
