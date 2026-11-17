# ==============================================================================
# Response Cache Layer - Read-Through JSON Cache (in-process RAM or Redis)
# ==============================================================================
# Caches fully-serialized JSON API responses (catalog list, brands, product
# detail, longitudinal insights, comparisons, experience reports).
#
# Backends (CACHE_BACKEND env var):
#   "auto"   (default) Redis when REDIS_URL is set, otherwise in-process memory
#   "memory" in-process LRU + TTL cache held in the server's RAM
#   "redis"  Redis / Render Key Value at REDIS_URL
#   "off"    no caching
#
# Design goals:
# 1. Raw JSON storage: hits return the stored bytes directly, skipping SQL,
#    ORM hydration AND Pydantic re-validation/serialization.
# 2. Write invalidation: any catalog/ownership write wipes the namespace, so
#    readers never see stale aggregates. TTL is a second safety net.
# 3. Bounded memory: the RAM backend evicts least-recently-used entries once
#    CACHE_MAX_MB is reached, so it can never exhaust the instance's memory.
# 4. Fail-open (Redis): if Redis is unreachable the API serves from PostgreSQL,
#    and a circuit breaker skips Redis for a cooldown window.
#
# Note: the memory backend is per-process. The Dockerfile runs a single uvicorn
# worker, so invalidation is global. With multiple workers/instances, use Redis.
# ==============================================================================

import hashlib
import json
import threading
import time
from collections import OrderedDict
from typing import Any, Callable, Optional

from fastapi import Request
from fastapi.responses import Response
from pydantic import TypeAdapter

from app.core.config import settings
from app.core.logging import logger

try:  # redis is optional; only needed for the redis backend
    import redis
except ImportError:  # pragma: no cover
    redis = None


BYPASS_HEADER = "x-cache-bypass"
PREFIX = "worthit:v1:"


class _BaseCache:
    name = "off"

    def __init__(self, default_ttl: int = 600):
        self.default_ttl = default_ttl
        self.hits = 0
        self.misses = 0
        self.errors = 0

    @property
    def configured(self) -> bool:
        return False

    @property
    def available(self) -> bool:
        return self.configured

    def get_raw(self, key: str) -> Optional[bytes]:
        return None

    def set_raw(self, key: str, value: bytes, ttl: Optional[int] = None) -> None:
        return None

    def invalidate_all(self) -> int:
        return 0

    def _count(self, value) -> None:
        if value is None:
            self.misses += 1
        else:
            self.hits += 1

    def stats(self) -> dict:
        total = self.hits + self.misses
        return {
            "backend": self.name,
            "configured": self.configured,
            "connected": self.available,
            "hits": self.hits,
            "misses": self.misses,
            "errors": self.errors,
            "hit_ratio": round(self.hits / total, 3) if total else None,
            "default_ttl_seconds": self.default_ttl,
            "cached_keys": None,
        }


class NullCache(_BaseCache):
    """Caching disabled."""


class MemoryCache(_BaseCache):
    """Thread-safe in-process LRU cache with per-entry TTL and a total byte budget."""

    name = "memory"

    def __init__(self, default_ttl: int = 600, max_bytes: int = 64 * 1024 * 1024):
        super().__init__(default_ttl)
        self.max_bytes = max_bytes
        self._data: "OrderedDict[str, tuple[float, bytes]]" = OrderedDict()
        self._bytes = 0
        self._lock = threading.Lock()  # sync endpoints run in a thread pool

    @property
    def configured(self) -> bool:
        return True

    def get_raw(self, key: str) -> Optional[bytes]:
        now = time.monotonic()
        with self._lock:
            entry = self._data.get(key)
            if entry is not None and entry[0] <= now:  # expired
                self._remove(key)
                entry = None
            if entry is not None:
                self._data.move_to_end(key)  # mark as recently used
            value = entry[1] if entry else None
            self._count(value)
            return value

    def set_raw(self, key: str, value: bytes, ttl: Optional[int] = None) -> None:
        size = len(value)
        if size > self.max_bytes:
            return  # never cache a single value larger than the whole budget
        expires = time.monotonic() + (ttl or self.default_ttl)
        with self._lock:
            if key in self._data:
                self._remove(key)
            self._data[key] = (expires, value)
            self._bytes += size
            while self._bytes > self.max_bytes and self._data:
                oldest = next(iter(self._data))
                self._remove(oldest)

    def _remove(self, key: str) -> None:
        _, value = self._data.pop(key)
        self._bytes -= len(value)

    def invalidate_all(self) -> int:
        with self._lock:
            n = len(self._data)
            self._data.clear()
            self._bytes = 0
            return n

    def stats(self) -> dict:
        info = super().stats()
        with self._lock:
            info["cached_keys"] = len(self._data)
            info["memory_used_mb"] = round(self._bytes / (1024 * 1024), 2)
        info["memory_limit_mb"] = round(self.max_bytes / (1024 * 1024), 2)
        return info


class RedisCache(_BaseCache):
    """Redis-backed cache with fail-open semantics and a circuit breaker."""

    name = "redis"

    def __init__(self, url: str, default_ttl: int = 600, cooldown_seconds: float = 30.0, client=None):
        super().__init__(default_ttl)
        self.url = (url or "").strip()
        self.cooldown_seconds = cooldown_seconds
        self._client = client
        self._disabled_until = 0.0

    @property
    def configured(self) -> bool:
        return self._client is not None or (bool(self.url) and redis is not None)

    @property
    def available(self) -> bool:
        return self.configured and time.monotonic() >= self._disabled_until

    def _get_client(self):
        if not self.available:
            return None  # not configured, or circuit open
        if self._client is None:
            self._client = redis.Redis.from_url(
                self.url,
                socket_connect_timeout=2,
                socket_timeout=1,
                health_check_interval=30,
                retry_on_timeout=False,
            )
        return self._client

    def _trip(self, op: str, exc: Exception) -> None:
        self.errors += 1
        self._disabled_until = time.monotonic() + self.cooldown_seconds
        logger.warning(f"Redis {op} failed ({exc.__class__.__name__}: {exc}); bypassing cache for {self.cooldown_seconds:.0f}s")

    def get_raw(self, key: str) -> Optional[bytes]:
        client = self._get_client()
        if client is None:
            return None
        try:
            value = client.get(key)
        except Exception as exc:
            self._trip("GET", exc)
            return None
        self._count(value)
        return value

    def set_raw(self, key: str, value: bytes, ttl: Optional[int] = None) -> None:
        client = self._get_client()
        if client is None:
            return
        try:
            client.set(key, value, ex=ttl or self.default_ttl)
        except Exception as exc:
            self._trip("SET", exc)

    def invalidate_all(self) -> int:
        """SCAN + UNLINK (non-blocking) every key in this app's namespace."""
        client = self._get_client()
        if client is None:
            return 0
        removed = 0
        try:
            batch = []
            for k in client.scan_iter(match=PREFIX + "*", count=500):
                batch.append(k)
                if len(batch) >= 500:
                    removed += client.unlink(*batch)
                    batch = []
            if batch:
                removed += client.unlink(*batch)
        except Exception as exc:
            self._trip("INVALIDATE", exc)
        return removed

    def stats(self) -> dict:
        info = super().stats()
        client = self._get_client()
        info["connected"] = False
        if client is not None:
            try:
                client.ping()
                info["connected"] = True
                info["cached_keys"] = sum(1 for _ in client.scan_iter(match=PREFIX + "*", count=500))
            except Exception as exc:
                self._trip("PING", exc)
        return info


def build_cache_backend() -> _BaseCache:
    choice = (settings.CACHE_BACKEND or "auto").strip().lower()
    ttl = settings.CACHE_TTL_SECONDS
    if choice == "auto":
        choice = "redis" if settings.REDIS_URL.strip() else "memory"
    if choice == "redis":
        if redis is None or not settings.REDIS_URL.strip():
            logger.warning("CACHE_BACKEND=redis but REDIS_URL/redis package missing; falling back to memory")
            return MemoryCache(ttl, settings.CACHE_MAX_MB * 1024 * 1024)
        return RedisCache(settings.REDIS_URL, ttl)
    if choice == "memory":
        return MemoryCache(ttl, settings.CACHE_MAX_MB * 1024 * 1024)
    return NullCache(ttl)


class CacheProxy:
    """
    Stable handle imported by endpoints. The active backend can be swapped at
    runtime (tests use this) without re-importing modules.
    """

    def __init__(self, backend: _BaseCache):
        self.backend = backend

    def __getattr__(self, name):
        return getattr(self.backend, name)

    @staticmethod
    def key(*parts: Any) -> str:
        return PREFIX + ":".join(str(p) for p in parts)


cache = CacheProxy(build_cache_backend())


# ------------------------------------------------------------------- helpers
_adapters: dict = {}


def _adapter(response_type: Any) -> TypeAdapter:
    adapter = _adapters.get(response_type)
    if adapter is None:
        adapter = _adapters[response_type] = TypeAdapter(response_type)
    return adapter


def params_hash(**params: Any) -> str:
    """Stable short hash of query params for cache keys."""
    raw = json.dumps(params, sort_keys=True, default=str)
    return hashlib.sha1(raw.encode()).hexdigest()[:16]


def cached_json_response(
    request: Request,
    key: str,
    response_type: Any,
    compute: Callable[[], Any],
    ttl: Optional[int] = None,
) -> Response:
    """
    Read-through cache for a JSON endpoint.

    - HIT: returns stored JSON bytes as-is (no DB, no Pydantic work).
    - MISS: runs `compute()`, validates/serializes via `response_type`, stores, returns.
    - BYPASS: with the `X-Cache-Bypass: 1` header the cache is neither read nor
      written (used for before/after latency benchmarks).

    `compute` should raise HTTPException for 4xx cases so errors are never cached.
    Sets an `X-Cache` response header (HIT / MISS / BYPASS / OFF).
    """
    bypass = request.headers.get(BYPASS_HEADER, "").lower() in ("1", "true", "yes")

    if not bypass:
        hit = cache.get_raw(key)
        if hit is not None:
            return Response(content=hit, media_type="application/json", headers={"X-Cache": "HIT"})

    adapter = _adapter(response_type)
    result = compute()
    body = adapter.dump_json(adapter.validate_python(result, from_attributes=True))

    if bypass:
        status = "BYPASS"
    elif cache.available:
        status = "MISS"
        cache.set_raw(key, body, ttl)
    else:
        status = "OFF"
    return Response(content=body, media_type="application/json", headers={"X-Cache": status})


def invalidate_catalog_cache(reason: str = "") -> None:
    """Called after any write that can change catalog/aggregate data."""
    removed = cache.invalidate_all()
    if removed:
        logger.info(f"Cache invalidated ({reason or 'write'}): {removed} entries removed")
