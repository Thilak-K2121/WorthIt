"""
Response-cache before/after latency benchmark for the WorthIt API.

For each hot read endpoint it sends interleaved request pairs:
  * "before"  -> header X-Cache-Bypass: 1  (cache skipped, full PostgreSQL + Python path)
  * "after"   -> normal request            (served from the cache once warm)

It records both the server-side processing time (X-Process-Time-Ms header, excludes
network) and the end-to-end client latency, then prints a markdown table and writes
the raw numbers to JSON.

Usage:
  python scripts/benchmark_cache.py --base-url https://<your-backend>.onrender.com/api/v1 -n 30
  python scripts/benchmark_cache.py --base-url http://127.0.0.1:8000/api/v1
"""

import argparse
import json
import statistics
import sys
import time
from datetime import datetime, timezone

import httpx

BYPASS = {"X-Cache-Bypass": "1"}


def pct(values, p):
    s = sorted(values)
    k = max(0, min(len(s) - 1, round(p / 100 * (len(s) - 1))))
    return s[k]


def summarize(values):
    return {
        "median": round(statistics.median(values), 2),
        "p95": round(pct(values, 95), 2),
        "mean": round(statistics.fmean(values), 2),
        "min": round(min(values), 2),
    }


def timed_get(client, path, headers=None):
    t0 = time.perf_counter()
    r = client.get(path, headers=headers or {})
    client_ms = (time.perf_counter() - t0) * 1000
    r.raise_for_status()
    server_ms = float(r.headers.get("X-Process-Time-Ms", "nan"))
    return server_ms, client_ms, r.headers.get("X-Cache", "?")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", required=True, help="API base, e.g. http://127.0.0.1:8000/api/v1")
    ap.add_argument("-n", "--iterations", type=int, default=30)
    ap.add_argument("--out", default="benchmark_results.json")
    args = ap.parse_args()

    base = args.base_url.rstrip("/")
    with httpx.Client(base_url=base, timeout=60) as client:
        # Wake the service (Render free tier cold start) and discover real product ids
        listing = client.get("/products", params={"page_size": 50, "sort_by": "popularity"}, headers=BYPASS).json()
        items = listing.get("items", [])
        if len(items) < 2:
            sys.exit("Need at least 2 products in the catalog to benchmark.")
        a, b = items[0]["id"], items[1]["id"]

        endpoints = [
            ("Catalog list (500 phones)", "/products?page_size=500"),
            ("Brand list", "/products/brands"),
            ("Product detail", f"/products/{a}"),
            ("Longitudinal insights", f"/products/{a}/insights"),
            ("Experience reports", f"/products/{a}/experiences"),
            ("Side-by-side compare", f"/products/compare?product_a={a}&product_b={b}"),
        ]

        results = []
        for label, path in endpoints:
            # warm-up: one bypass (DB connection pool / plans) and one MISS to populate the cache
            timed_get(client, path, BYPASS)
            _, _, first_status = timed_get(client, path)

            before_s, before_c, after_s, after_c, statuses = [], [], [], [], []
            for _ in range(args.iterations):
                s, c, _ = timed_get(client, path, BYPASS)
                before_s.append(s); before_c.append(c)
                s, c, st = timed_get(client, path)
                after_s.append(s); after_c.append(c); statuses.append(st)

            hit_ratio = statuses.count("HIT") / len(statuses)
            row = {
                "endpoint": label,
                "path": path,
                "server_before": summarize(before_s),
                "server_after": summarize(after_s),
                "client_before": summarize(before_c),
                "client_after": summarize(after_c),
                "hit_ratio": hit_ratio,
            }
            row["server_speedup"] = round(row["server_before"]["median"] / max(row["server_after"]["median"], 0.01), 1)
            row["client_reduction_pct"] = round(
                (1 - row["client_after"]["median"] / row["client_before"]["median"]) * 100, 1
            )
            results.append(row)
            print(f"  done: {label} (hit ratio {hit_ratio:.0%})", file=sys.stderr)

    if all(r["hit_ratio"] == 0 for r in results):
        print("\nWARNING: no cache HITs observed - is CACHE_BACKEND set to 'off' on the server?\n", file=sys.stderr)

    print(f"\n### Response cache benchmark - {base} - n={args.iterations} per mode\n")
    print("| Endpoint | Server median before | Server median after | Server speedup | E2E median before | E2E median after | E2E reduction |")
    print("|---|---:|---:|---:|---:|---:|---:|")
    for r in results:
        print(
            f"| {r['endpoint']} | {r['server_before']['median']} ms | {r['server_after']['median']} ms | "
            f"{r['server_speedup']}x | {r['client_before']['median']} ms | {r['client_after']['median']} ms | "
            f"{r['client_reduction_pct']}% |"
        )

    with open(args.out, "w") as f:
        json.dump({
            "base_url": base,
            "iterations": args.iterations,
            "run_at": datetime.now(timezone.utc).isoformat(),
            "results": results,
        }, f, indent=2)
    print(f"\nRaw numbers written to {args.out}")


if __name__ == "__main__":
    main()
