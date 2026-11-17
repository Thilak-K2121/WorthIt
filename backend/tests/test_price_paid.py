REPORT = {
    "ownership_duration_months": 6,
    "overall_satisfaction": 4,
    "battery_satisfaction": 4,
    "performance_satisfaction": 4,
    "software_satisfaction": 4,
    "would_buy_again": "YES",
}


def _own(client, product_id, price=None, variant_id=None):
    body = {"product_id": product_id, "purchase_date": "2025-01-01", "initial_report": REPORT}
    if price is not None:
        body["purchase_price"] = price
    if variant_id:
        body["variant_id"] = variant_id
    res = client.post("/api/v1/ownerships", json=body)
    assert res.status_code == 201, res.text


def test_price_paid_stats_compare_against_variant_launch_price(client):
    product = client.post("/api/v1/products", json={
        "brand": "Pricey", "model_name": "One",
        "variants": [
            {"ram": "8GB", "storage": "128GB", "launch_price": 40000},
            {"ram": "12GB", "storage": "256GB", "launch_price": 50000},
        ],
    }).json()
    v = {f"{x['ram']}/{x['storage']}": x["id"] for x in product["variants"]}

    _own(client, product["id"], 36000, v["8GB/128GB"])   # 10% below its launch price
    _own(client, product["id"], 55000, v["12GB/256GB"])  # 10% above its launch price
    _own(client, product["id"], 32000)                    # no variant: counts for paid stats only
    _own(client, product["id"])                           # no price: ignored

    stats = client.get(f"/api/v1/products/{product['id']}/insights").json()["price_paid"]
    assert stats["sample_size"] == 3
    assert stats["average_paid"] == 41000.0
    assert stats["median_paid"] == 36000.0
    assert stats["min_paid"] == 32000.0 and stats["max_paid"] == 55000.0
    assert stats["launch_comparison_sample_size"] == 2
    assert stats["avg_vs_launch_percentage"] == 0.0


def test_price_paid_empty_when_no_prices(client):
    pid = client.post("/api/v1/products", json={"brand": "Pricey", "model_name": "Two"}).json()["id"]
    _own(client, pid)
    stats = client.get(f"/api/v1/products/{pid}/insights").json()["price_paid"]
    assert stats["sample_size"] == 0
    assert stats["average_paid"] is None
    assert stats["avg_vs_launch_percentage"] is None


def test_variant_from_another_product_is_ignored(client):
    a = client.post("/api/v1/products", json={"brand": "Pricey", "model_name": "A",
                                              "variants": [{"storage": "128GB", "launch_price": 10000}]}).json()
    b = client.post("/api/v1/products", json={"brand": "Pricey", "model_name": "B",
                                              "variants": [{"storage": "128GB", "launch_price": 90000}]}).json()
    _own(client, a["id"], 20000, b["variants"][0]["id"])  # wrong product's variant
    stats = client.get(f"/api/v1/products/{a['id']}/insights").json()["price_paid"]
    assert stats["sample_size"] == 1
    assert stats["launch_comparison_sample_size"] == 0
