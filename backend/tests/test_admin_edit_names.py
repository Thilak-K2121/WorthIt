from app.core.config import settings


def _product(client, brand, model):
    res = client.post("/api/v1/admin/products", json={"brand": brand, "model_name": model})
    assert res.status_code == 201, res.text
    return res.json()["id"]


def _suggest(client, brand, model, variant=None):
    res = client.post("/api/v1/product-suggestions", json={"brand": brand, "model_name": model, "variant_details": variant})
    assert res.status_code == 201, res.text
    return res.json()["id"]


# ------------------------------------------------------------------ rename existing phones
def test_rename_product_updates_name_search_and_cache(client):
    pid = _product(client, "Samsng", "Galaxy S25 Ultr")
    client.get(f"/api/v1/products/{pid}")  # warm the cache

    res = client.patch(f"/api/v1/admin/products/{pid}", json={"brand": "samsung", "model_name": "Galaxy S25 Ultra"})
    assert res.status_code == 200, res.text
    assert res.json()["brand"] == "Samsung"
    assert res.json()["model_name"] == "Galaxy S25 Ultra"

    assert client.get(f"/api/v1/products/{pid}").json()["model_name"] == "Galaxy S25 Ultra"
    found = client.get("/api/v1/products", params={"search": "S25 Ultra"}).json()
    assert [p["id"] for p in found["items"]] == [pid]


def test_rename_only_model_keeps_brand(client):
    pid = _product(client, "Google", "Pixel 9 Pr")
    res = client.patch(f"/api/v1/admin/products/{pid}", json={"model_name": "Pixel 9 Pro"})
    assert res.status_code == 200
    assert res.json()["brand"] == "Google"


def test_rename_to_own_name_is_allowed(client):
    pid = _product(client, "Nothing", "Phone (3)")
    res = client.patch(f"/api/v1/admin/products/{pid}", json={"brand": "Nothing", "model_name": "Phone (3)"})
    assert res.status_code == 200


def test_rename_into_existing_phone_is_rejected(client):
    _product(client, "Apple", "iPhone 16 Pro")
    pid = _product(client, "Apple", "iPhone 16")
    res = client.patch(f"/api/v1/admin/products/{pid}", json={"model_name": "iPhone 16 Pro"})
    assert res.status_code == 409
    assert client.get(f"/api/v1/products/{pid}").json()["model_name"] == "iPhone 16"


def test_rename_missing_product_404(client):
    assert client.patch("/api/v1/admin/products/nope", json={"model_name": "X"}).status_code == 404


# ------------------------------------------------------------------ edit suggestions before approving
def test_approve_suggestion_with_edited_name(client):
    sid = _suggest(client, "oneplus", "13 R typo", "8GB / 128GB")
    res = client.post(f"/api/v1/product-suggestions/{sid}/review", json={
        "action": "APPROVE", "brand": "OnePlus", "model_name": "13R", "variant_details": "12GB / 256GB",
    })
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["status"] == "APPROVED"
    assert (body["brand"], body["model_name"], body["variant_details"]) == ("OnePlus", "13R", "12GB / 256GB")

    product = client.get(f"/api/v1/products/{body['target_product_id']}").json()
    assert (product["brand"], product["model_name"]) == ("OnePlus", "13R")
    assert (product["variants"][0]["ram"], product["variants"][0]["storage"]) == ("12GB", "256GB")

    # ...and it stays editable after approval
    renamed = client.patch(f"/api/v1/admin/products/{product['id']}", json={"model_name": "13R 5G"})
    assert renamed.status_code == 200
    assert renamed.json()["model_name"] == "13R 5G"


def test_approving_into_duplicate_is_409_not_500(client):
    _product(client, "Vivo", "X200 Pro")
    sid = _suggest(client, "Vivo", "X200")
    res = client.post(f"/api/v1/product-suggestions/{sid}/review", json={"action": "APPROVE", "model_name": "X200 Pro"})
    assert res.status_code == 409
    # suggestion untouched, still pending and editable
    pending = client.get("/api/v1/product-suggestions", params={"status": "PENDING"}).json()
    assert any(s["id"] == sid and s["model_name"] == "X200" for s in pending)


def test_review_and_rename_require_admin_key(client, monkeypatch):
    sid = _suggest(client, "Realme", "GT 7")
    pid = _product(client, "Realme", "GT 6")
    monkeypatch.setattr(settings, "ADMIN_API_KEY", "s3cret")

    assert client.post(f"/api/v1/product-suggestions/{sid}/review", json={"action": "APPROVE"}).status_code == 401
    assert client.patch(f"/api/v1/admin/products/{pid}", json={"model_name": "GT 6T"}).status_code == 401

    ok = {"X-Admin-Key": "s3cret"}
    assert client.post(f"/api/v1/product-suggestions/{sid}/review", json={"action": "APPROVE"}, headers=ok).status_code == 200
    assert client.patch(f"/api/v1/admin/products/{pid}", json={"model_name": "GT 6T"}, headers=ok).status_code == 200
