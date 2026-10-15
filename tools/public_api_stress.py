#!/usr/bin/env python3
"""Bounded, read-only public API/catalog pressure test for Nour.

This deliberately avoids auth, payment, admin, AI-generation, TTS, image,
ASR upload, realtime, and other side-effectful/expensive endpoints.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import math
import os
import random
import ssl
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

UA = "Nour-ReadOnly-PressureTest/1.0 (bounded; owner-authorized)"
SSL_CONTEXT = ssl._create_unverified_context()


class RateLimiter:
    def __init__(self, rps: float):
        self.interval = 1.0 / max(0.1, rps)
        self.lock = threading.Lock()
        self.next_at = time.monotonic()

    def wait(self) -> None:
        with self.lock:
            now = time.monotonic()
            if now < self.next_at:
                time.sleep(self.next_at - now)
                now = time.monotonic()
            self.next_at = max(self.next_at, now) + self.interval


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def fetch(base: str, path: str, limiter: RateLimiter, timeout: float = 30.0,
          method: str = "GET", payload: object | None = None,
          expected: set[int] | None = None) -> dict:
    limiter.wait()
    url = base.rstrip("/") + path
    body = None
    headers = {"User-Agent": UA, "Accept": "application/json,text/plain,*/*",
               "X-Load-Test": "nour-readonly-bounded-20260928"}
    if payload is not None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    started = time.perf_counter()
    status = 0
    raw = b""
    error = ""
    try:
        req = urllib.request.Request(url, data=body, method=method, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout, context=SSL_CONTEXT) as res:
            status = int(res.status)
            raw = res.read()
    except urllib.error.HTTPError as exc:
        status = int(exc.code)
        try:
            raw = exc.read(2048)
        except Exception:
            raw = b""
        error = f"HTTP {status}"
    except Exception as exc:  # network timeout, DNS, reset, etc.
        error = f"{type(exc).__name__}: {exc}"
    elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
    ok_status = status in (expected if expected is not None else {200})
    parsed = None
    if raw and (b"{" in raw[:20] or b"[" in raw[:20]):
        try:
            parsed = json.loads(raw.decode("utf-8", errors="replace"))
        except Exception:
            pass
    return {"path": path, "method": method, "status": status, "ok": bool(ok_status),
            "ms": elapsed_ms, "bytes": len(raw), "error": error,
            "json": parsed}


def percentile(values: list[float], p: float) -> float | None:
    if not values:
        return None
    vals = sorted(values)
    idx = min(len(vals) - 1, max(0, math.ceil((p / 100) * len(vals)) - 1))
    return round(vals[idx], 2)


def summarize(results: list[dict]) -> dict:
    by_path = defaultdict(list)
    for item in results:
        by_path[item["path"]].append(item)
    status_counts = Counter(str(x["status"]) for x in results)
    all_ms = [x["ms"] for x in results if x["status"]]
    return {
        "requests": len(results),
        "passed": sum(1 for x in results if x["ok"] and not x.get("guarded")),
        "guarded": sum(1 for x in results if x.get("guarded")),
        "failed": sum(1 for x in results if not x["ok"] and not x.get("guarded")),
        "status_counts": dict(status_counts),
        "latency_ms": {"p50": percentile(all_ms, 50), "p95": percentile(all_ms, 95),
                        "p99": percentile(all_ms, 99), "max": max(all_ms) if all_ms else None},
        "by_endpoint": {
            path: {"requests": len(xs), "passed": sum(1 for x in xs if x["ok"]),
                   "failed": sum(1 for x in xs if not x["ok"]),
                   "p50_ms": percentile([x["ms"] for x in xs], 50),
                   "p95_ms": percentile([x["ms"] for x in xs], 95),
                   "status_counts": dict(Counter(str(x["status"]) for x in xs)),
                   "errors": [x["error"] for x in xs if x["error"]][:3]}
            for path, xs in sorted(by_path.items())
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="https://xn--dqry4os3s3gb.com")
    ap.add_argument("--output", default="tools/manus-results/public-api-stress-20260928/report.json")
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--rps", type=float, default=3.0,
                    help="global request rate; intentionally bounded")
    ap.add_argument("--catalog-size", type=int, default=60)
    ap.add_argument("--catalog-read-samples", type=int, default=16)
    ap.add_argument("--rounds", type=int, default=3)
    ap.add_argument("--timeout", type=float, default=30.0)
    ap.add_argument("--skip-external-nodes", action="store_true",
                    help="skip /api/nodes; by default it now reads a fast cache and refreshes in background")
    args = ap.parse_args()
    base = args.base.rstrip("/")
    limiter = RateLimiter(args.rps)
    started = now_iso()
    all_results: list[dict] = []

    def one(path: str, **kwargs) -> dict:
        result = fetch(base, path, limiter, timeout=args.timeout, **kwargs)
        all_results.append(result)
        return result

    print(f"[baseline] {base}", flush=True)
    meta = one("/api/catalog/meta")
    if not meta["ok"]:
        raise SystemExit(f"catalog meta failed: {meta}")
    meta_json = meta.get("json") or {}
    total = int(meta_json.get("total") or 0)
    if total < 8000:
        raise SystemExit(f"catalog total unexpectedly low: {total}")
    page_size = min(60, max(1, args.catalog_size))
    pages = math.ceil(total / page_size)
    print(f"[catalog] total={total} pages={pages} size={page_size}", flush=True)

    # Enumerate every metadata page and validate IDs/titles without downloading every full text.
    page_paths = [f"/api/catalog?page={i}&size={page_size}" for i in range(pages)]
    catalog_items: list[dict] = []
    catalog_failures: list[dict] = []
    page_results: list[dict] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futures = [pool.submit(one, path) for path in page_paths]
        for i, future in enumerate(futures, 1):
            result = future.result()
            page_results.append(result)
            data = result.get("json") or {}
            items = data.get("items") if isinstance(data, dict) else None
            if result["ok"] and isinstance(items, list):
                catalog_items.extend(x for x in items if isinstance(x, dict))
            else:
                catalog_failures.append({"path": result["path"], "status": result["status"],
                                         "error": result["error"]})
            if i % 20 == 0 or i == pages:
                print(f"[catalog] pages={i}/{pages} items_seen={len(catalog_items)}", flush=True)
    ids = [str(x.get("id") or x.get("_id") or "") for x in catalog_items]
    titles = [str(x.get("t") or x.get("title") or "") for x in catalog_items]
    unique_ids = {x for x in ids if x}
    missing_id = sum(1 for x in ids if not x)
    missing_title = sum(1 for x in titles if not x)
    catalog_summary = {
        "meta_total": total, "page_count": pages, "page_size": page_size,
        "items_seen": len(catalog_items), "unique_ids": len(unique_ids),
        "missing_id": missing_id, "missing_title": missing_title,
        "page_failures": catalog_failures,
    }

    # Sample only application-internal full-text pages. Metadata-only books such as
    # fiqh-risala intentionally use their official BookReader URL and must not be sent
    # to the OpenITI-only /api/catalog/read endpoint.
    readable_items = [x for x in catalog_items if str(x.get("id") or x.get("_id") or "").startswith("openiti-")
                      or x.get("text_mode") == "arabic_original_link"]
    metadata_only_items = [x for x in catalog_items if x not in readable_items]
    read_samples = []
    if readable_items:
        step = max(1, len(readable_items) // max(1, args.catalog_read_samples))
        for item in readable_items[::step][:args.catalog_read_samples]:
            bid = item.get("id") or item.get("_id")
            if not bid:
                continue
            path = "/api/catalog/read?" + urllib.parse.urlencode({"id": bid, "page": 0})
            res = one(path)
            guarded = (res.get("status") == 413 and
                       "较大" in str((res.get("json") or {}).get("error") or ""))
            if guarded:
                res["guarded"] = "oversize_source_protection"
                res["ok"] = True
            read_samples.append({"id": bid, "status": res["status"], "ok": res["ok"],
                                 "guarded": res.get("guarded", False),
                                 "ms": res["ms"], "bytes": res["bytes"], "error": res["error"]})
    catalog_summary["readable_items"] = len(readable_items)
    catalog_summary["metadata_only_items"] = len(metadata_only_items)
    catalog_summary["read_samples"] = read_samples

    # Safe GET endpoints. Dynamic samples are added only after their list endpoints succeed.
    device = "pressure-test-" + str(int(time.time()))
    probes = [
        "/", "/api/home_stats", "/api/catalog/meta", f"/api/catalog?page=0&size={page_size}",
        "/api/books", "/api/articles", "/api/sentences/daily", "/api/sentences", "/api/vocab", "/api/plans",
        "/api/videos", "/api/asr/status", "/api/access/status?device_id=" + device,
        "/api/ai/quota?device_id=" + device, "/api/pay/status?device_id=" + device,
        "/api/history?cat=ar&page=0&size=1", "/api/cnbooks?page=0&size=1",
        "/api/islamic/search?source=sunnah&q=", "/api/quran/tafsir?surah=1&ayah=1",
        "/api/audio/library?limit=1",
    ]
    if not args.skip_external_nodes:
        probes.insert(12, "/api/nodes")
    print(f"[probes] endpoints={len(probes)} rounds={args.rounds}", flush=True)
    probe_paths = probes * max(1, args.rounds)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futures = [pool.submit(one, path) for path in probe_paths]
        for i, future in enumerate(futures, 1):
            future.result()
            if i % 10 == 0 or i == len(futures):
                print(f"[probes] {i}/{len(futures)}", flush=True)

    # Contract checks for the two formerly unbounded homepage paths.
    daily_results = [x for x in all_results if x["path"] == "/api/sentences/daily"]
    daily_items = []
    for result in daily_results:
        payload = result.get("json") or {}
        item = payload.get("item") if isinstance(payload, dict) else None
        valid = (result["ok"] and isinstance(item, dict)
                 and all(isinstance(item.get(k), str) for k in ("a", "e", "c", "cat"))
                 and isinstance(payload.get("date"), str)
                 and isinstance(payload.get("index"), int)
                 and isinstance(payload.get("total"), int))
        daily_items.append({"ok": valid, "ms": result["ms"], "bytes": result["bytes"],
                            "date": payload.get("date"), "total": payload.get("total")})
    nodes_results = [x for x in all_results if x["path"] == "/api/nodes"]
    nodes_contract = []
    for result in nodes_results:
        payload = result.get("json") or {}
        valid = (result["ok"] and isinstance(payload, dict)
                 and isinstance(payload.get("nodes"), list)
                 and isinstance(payload.get("refreshing"), bool)
                 and isinstance(payload.get("stale"), bool))
        nodes_contract.append({"ok": valid, "ms": result["ms"], "bytes": result["bytes"],
                               "refreshing": payload.get("refreshing"), "stale": payload.get("stale")})
    contracts = {
        "sentences_daily": {"requests": len(daily_items), "all_valid": bool(daily_items) and all(x["ok"] and x["bytes"] < 10000 for x in daily_items),
                             "max_bytes": max((x["bytes"] for x in daily_items), default=0), "samples": daily_items[:5]},
        "nodes_async": {"requests": len(nodes_contract), "all_valid": bool(nodes_contract) and all(x["ok"] for x in nodes_contract),
                         "max_ms": max((x["ms"] for x in nodes_contract), default=None), "samples": nodes_contract[:5]},
    }

    # One dynamic read-only Chinese book and local audio-file check.
    cn_probe = one("/api/cnbooks?page=0&size=1")
    cn_items = (cn_probe.get("json") or {}).get("items") or []
    if cn_items and cn_items[0].get("id"):
        one("/api/cnbook?" + urllib.parse.urlencode({"id": cn_items[0]["id"]}))
    audio_probe = one("/api/audio/library?limit=1")
    audio_items = (audio_probe.get("json") or {}).get("items") or []
    if audio_items and audio_items[0].get("root") and audio_items[0].get("name"):
        one("/api/audio/file?" + urllib.parse.urlencode({"root": audio_items[0]["root"],
                                                             "name": audio_items[0]["name"]}))

    # Validation-only POST probes: each is rejected before AI/upstream work or data mutation.
    post_probes = [
        ("/api/page/analyze", {}, {400}),
        ("/api/realtime/session", {}, {400}),
        ("/api/chat/stream_voice", {}, {400}),
        ("/api/asr", b"", {400}),
        ("/api/search", {"q": "سلام"}, {200}),
    ]
    for path, payload, expected in post_probes:
        if path == "/api/asr":
            all_results.append(fetch(base, path, limiter, timeout=args.timeout, method="POST",
                                     payload=None, expected=expected))
        else:
            all_results.append(fetch(base, path, limiter, timeout=args.timeout, method="POST",
                                     payload=payload, expected=expected))

    # Explicitly document intentionally excluded routes.
    skipped = {
        "mutating_or_sensitive": ["/api/auth/register", "/api/auth/login", "/api/unlock/use",
                                   "/api/pay/claim", "/api/vip/activate", "/api/access/leave",
                                   "/api/device/login", "/api/entry/use", "/api/admin/*"],
        "expensive_or_upstream": ["/api/chat/stream_voice", "/api/realtime/session", "/api/tts",
                                   "/api/image", "/api/music", "/api/websearch", "/api/asr",
                                   "/api/recite", "/api/quran/proxy", "/api/coverimg"],
        "metadata_only_catalog_items": "不把没有 text_mode=arabic_original_link 的书目送入 OpenITI 阅读接口；这类条目保留官方 BookReader/来源链接，属于预期外部阅读路径。",
        "external_nodes_probe": {
            "route": "/api/nodes",
            "included": not args.skip_external_nodes,
            "note": "该路由只读最近成功缓存，并单飞触发后台刷新；使用 --skip-external-nodes 可排除节点接口。"
        },
        "reason": "本轮只做低速只读压测；POST 验证仅发送空/无效载荷并预期 400，避免扣费、写入、外部模型或媒体转码。",
    }
    ended = now_iso()
    report = {
        "schema_version": 1, "started_at": started, "ended_at": ended,
        "base": base, "limits": {"workers": args.workers, "global_rps": args.rps,
                                    "timeout_s": args.timeout, "rounds": args.rounds,
                                    "skip_external_nodes": args.skip_external_nodes},
        "catalog": catalog_summary, "contracts": contracts, "summary": summarize(all_results),
        "results": all_results, "skipped": skipped,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    summary = report["summary"]
    print(json.dumps({"output": str(output), "catalog": catalog_summary,
                      "requests": summary["requests"], "passed": summary["passed"],
                      "failed": summary["failed"], "latency_ms": summary["latency_ms"]},
                     ensure_ascii=False, indent=2))
    return 0 if (not catalog_failures and summary["failed"] == 0
                 and contracts["sentences_daily"]["all_valid"]
                 and (args.skip_external_nodes or contracts["nodes_async"]["all_valid"])) else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        raise SystemExit(130)
