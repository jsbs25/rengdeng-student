#!/usr/bin/env python3
"""Offline contract tests for the bounded daily sentence and async node cache paths."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import server  # noqa: E402


def wait_refresh(timeout: float = 1.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if not server._sub_snapshot()["refreshing"]:
            return
        time.sleep(0.01)
    raise AssertionError("background refresh did not finish")


def main() -> int:
    daily = server._sentence_daily_payload()
    item = daily.get("item") or {}
    assert daily.get("ok") is True
    assert daily.get("total", 0) >= 30000
    assert isinstance(daily.get("date"), str) and len(daily["date"]) == 10
    assert isinstance(daily.get("index"), int)
    assert all(isinstance(item.get(k), str) for k in ("a", "e", "c", "cat"))
    assert item["a"] and item["c"]
    assert len(json.dumps(daily, ensure_ascii=False).encode("utf-8")) < 10000

    original_cache = dict(server._SUB_CACHE)
    original_refresh = server._sub_cache_refresh
    original_interval = server._SUB_REFRESH_INTERVAL
    try:
        server._SUB_REFRESH_INTERVAL = 1800
        server._SUB_CACHE.update({"t": time.time(), "data": "proxies: []\n"})
        warm_started = time.perf_counter()
        warm = server._sub_start_refresh()
        assert time.perf_counter() - warm_started < 0.1
        assert warm["data"] == "proxies: []\n"
        assert warm["stale"] is False

        def fail_refresh():
            raise RuntimeError("offline test source timeout")

        server._SUB_CACHE.update({"t": 0, "data": ""})
        server._sub_cache_refresh = fail_refresh
        cold_started = time.perf_counter()
        cold = server._sub_start_refresh()
        assert time.perf_counter() - cold_started < 0.1
        assert cold["data"] == ""
        wait_refresh()
        failed = server._sub_snapshot()
        assert failed["data"] == ""
        assert "offline test source timeout" in failed["last_error"]
    finally:
        server._sub_cache_refresh = original_refresh
        server._SUB_REFRESH_INTERVAL = original_interval
        with server._SUB_CACHE_LOCK:
            server._SUB_CACHE.clear()
            server._SUB_CACHE.update(original_cache)
            server._SUB_LAST_ERROR = ""
            server._SUB_REFRESHING = False

    print(json.dumps({"ok": True, "daily_total": daily["total"], "daily_bytes": len(json.dumps(daily, ensure_ascii=False).encode("utf-8"))}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
