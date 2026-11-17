import time

import fakeredis
import pytest

from app.core.cache import cache, MemoryCache, NullCache, RedisCache
from app.core.config import settings


@pytest.fixture(params=["memory", "redis"])
def any_cache(request):
    """Runs the test against the RAM backend and against Redis (in-memory fake)."""
    original = cache.backend
    if request.param == "memory":
        cache.backend = MemoryCache(default_ttl=600)
    else:
        cache.backend = RedisCache("", client=fakeredis.FakeRedis())
    yield cache.backend
    cache.backend = original


@pytest.fixture
def redis_cache():
    original = cache.backend
    cache.backend = RedisCache("", client=fakeredis.FakeRedis())
    yield cache.backend
    cache.backend = original


def _create(client, brand="Sony", model="Xperia 10 VI"):
    res = client.post("/api/v1/admin/products", json={"brand": brand, "model_name": model})
    assert res.status_code == 201, res.text
    return res.json()["id"]


def test_product_list_miss_then_hit(client, any_cache):
    _create(client)
    first = client.get("/api/v1/products")
    second = client.get("/api/v1/products")
    assert first.headers["X-Cache"] == "MISS"
    assert second.headers["X-Cache"] == "HIT"
    assert first.json() == second.json()
    assert "X-Process-Time-Ms" in second.headers


def test_bypass_header_skips_cache(client, any_cache):
    _create(client)
    client.get("/api/v1/products/brands")
    res = client.get("/api/v1/products/brands", headers={"X-Cache-Bypass": "1"})
    assert res.headers["X-Cache"] == "BYPASS"


def test_write_invalidates_cached_list(client, any_cache):
    _create(client, "Sony", "Xperia 10 VI")
    assert client.get("/api/v1/products").json()["total"] == 1
    assert client.get("/api/v1/products").headers["X-Cache"] == "HIT"

    _create(client, "Nothing", "Phone (3)")
    res = client.get("/api/v1/products")
    assert res.headers["X-Cache"] == "MISS"
    assert res.json()["total"] == 2


def test_errors_are_not_cached(client, any_cache):
    assert client.get("/api/v1/products/does-not-exist").status_code == 404
    assert client.get("/api/v1/products/does-not-exist").status_code == 404
    assert any_cache.hits == 0


def test_cache_off(client):
    original = cache.backend
    cache.backend = NullCache()
    try:
        res = client.get("/api/v1/products")
        assert res.status_code == 200
        assert res.headers["X-Cache"] == "OFF"
    finally:
        cache.backend = original


def test_redis_failure_fails_open(client, redis_cache):
    class BrokenRedis:
        def __getattr__(self, name):
            def boom(*a, **k):
                raise ConnectionError("redis down")
            return boom

    redis_cache._client = BrokenRedis()
    res = client.get("/api/v1/products")
    assert res.status_code == 200
    assert redis_cache.errors >= 1


def test_admin_delete_removes_product_and_invalidates(client, any_cache):
    pid = _create(client)
    assert client.get(f"/api/v1/products/{pid}").status_code == 200  # cached
    res = client.delete(f"/api/v1/admin/products/{pid}")
    assert res.status_code == 200
    assert res.json()["deleted"] == pid
    assert client.get(f"/api/v1/products/{pid}").status_code == 404
    assert client.delete(f"/api/v1/admin/products/{pid}").status_code == 404


def test_admin_delete_cascades_ownerships(client):
    pid = _create(client)
    own = client.post("/api/v1/ownerships", json={
        "product_id": pid,
        "purchase_date": "2025-01-10",
        "initial_report": {
            "ownership_duration_months": 3,
            "overall_satisfaction": 4,
            "battery_satisfaction": 4,
            "performance_satisfaction": 4,
            "software_satisfaction": 4,
            "would_buy_again": "YES",
        },
    })
    assert own.status_code == 201, own.text
    res = client.delete(f"/api/v1/admin/products/{pid}")
    assert res.status_code == 200
    assert res.json()["ownerships_removed"] == 1


def test_admin_create_rejects_duplicate(client):
    _create(client, "Samsung", "Galaxy S25")
    res = client.post("/api/v1/admin/products", json={"brand": "samsung", "model_name": "Galaxy S25"})
    assert res.status_code == 409


def test_admin_key_enforced(client, monkeypatch):
    monkeypatch.setattr(settings, "ADMIN_API_KEY", "s3cret")
    assert client.get("/api/v1/admin/verify").status_code == 401
    assert client.get("/api/v1/admin/verify", headers={"X-Admin-Key": "wrong"}).status_code == 401
    assert client.get("/api/v1/admin/verify", headers={"X-Admin-Key": "s3cret"}).status_code == 200


def test_admin_fails_closed_in_production_without_key(client, monkeypatch):
    monkeypatch.setattr(settings, "ADMIN_API_KEY", "")
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    assert client.get("/api/v1/admin/verify").status_code == 503


# ----------------------------------------------------------------- RAM backend unit tests
def test_memory_cache_ttl_expiry():
    c = MemoryCache(default_ttl=600)
    c.set_raw("k", b"v", ttl=0.05)
    assert c.get_raw("k") == b"v"
    time.sleep(0.08)
    assert c.get_raw("k") is None


def test_memory_cache_lru_eviction_respects_byte_budget():
    c = MemoryCache(max_bytes=10)
    c.set_raw("a", b"12345")
    c.set_raw("b", b"12345")
    c.get_raw("a")             # "a" is now most recently used
    c.set_raw("c", b"12345")   # over budget -> evicts least recently used ("b")
    assert c.get_raw("b") is None
    assert c.get_raw("a") == b"12345"
    assert c.get_raw("c") == b"12345"
    assert c.stats()["memory_used_mb"] <= 10 / (1024 * 1024) + 0.01


def test_memory_cache_skips_oversized_values_and_invalidates():
    c = MemoryCache(max_bytes=4)
    c.set_raw("big", b"123456")
    assert c.get_raw("big") is None
    c.set_raw("x", b"1")
    assert c.invalidate_all() == 1
    assert c.get_raw("x") is None
