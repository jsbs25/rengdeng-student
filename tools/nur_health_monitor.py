#!/usr/bin/env python3
"""Small dependency-free runtime monitor for Nour's existing VPS service."""
from __future__ import annotations

import argparse
import gc
import json
import os
import shutil
import ssl
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

UA = "Nour-Runtime-Monitor/1.0"
MAX_LOG_BYTES = 10 * 1024 * 1024
KEEP_LOG_BYTES = 4 * 1024 * 1024
SSL_CONTEXT = ssl._create_unverified_context()


def iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def http_probe(base: str, path: str, timeout: float) -> dict:
    url = base.rstrip("/") + path
    started = time.perf_counter()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json,text/plain,*/*", "Connection": "close"})
        with urllib.request.urlopen(req, timeout=timeout, context=SSL_CONTEXT) as res:
            raw = res.read(16384)
            status = int(res.status)
        parsed = None
        try:
            parsed = json.loads(raw.decode("utf-8", errors="replace"))
        except Exception:
            pass
        return {"ok": status == 200, "status": status,
                "ms": round((time.perf_counter() - started) * 1000, 2),
                "bytes": len(raw), "json": parsed}
    except urllib.error.HTTPError as exc:
        return {"ok": False, "status": int(exc.code),
                "ms": round((time.perf_counter() - started) * 1000, 2),
                "bytes": 0, "error": f"HTTP {exc.code}"}
    except Exception as exc:
        return {"ok": False, "status": 0,
                "ms": round((time.perf_counter() - started) * 1000, 2),
                "bytes": 0, "error": f"{type(exc).__name__}: {exc}"}


def service_active(service: str) -> bool:
    try:
        return subprocess.run(["systemctl", "is-active", "--quiet", service], timeout=8).returncode == 0
    except Exception:
        return False


def system_snapshot() -> dict:
    out = {"load": None, "memory": None, "disk": None}
    try:
        out["load"] = os.getloadavg()
    except Exception:
        pass
    try:
        mem = Path("/proc/meminfo").read_text().splitlines()
        vals = {line.split(":", 1)[0]: int(line.split()[1]) for line in mem if ":" in line}
        total = vals.get("MemTotal", 0); available = vals.get("MemAvailable", 0)
        out["memory"] = {"total_mb": round(total / 1024, 1), "available_mb": round(available / 1024, 1),
                         "used_pct": round((total - available) * 100 / total, 1) if total else None}
    except Exception:
        pass
    try:
        du = shutil.disk_usage("/opt/nur")
        out["disk"] = {"total_gb": round(du.total / 1024**3, 2), "free_gb": round(du.free / 1024**3, 2),
                       "used_pct": round((du.total - du.free) * 100 / du.total, 1)}
    except Exception:
        pass
    return out


def one_check(public_url: str, local_url: str, service: str, timeout: float) -> dict:
    paths = [
        "/",
        "/api/catalog/meta",
        "/api/catalog?page=0&size=1",
        # Do not fetch /api/books here: it is a 1MB+ payload and is not needed
        # for liveness. The catalog meta/page probes cover the same service.
        "/api/islamic/search?source=sunnah&q=&page=1&size=6",
        "/api/quran/tafsir?surah=1&ayah=1",
    ]
    public = {path: http_probe(public_url, path, timeout) for path in paths}
    local = {"/api/home_stats": http_probe(local_url, "/api/home_stats", timeout)}
    meta = public.get("/api/catalog/meta", {}).get("json") or {}
    sunnah = public.get("/api/islamic/search?source=sunnah&q=&page=1&size=6", {}).get("json") or {}
    conditions = {
        "service_active": service_active(service),
        "public_http_all_200": all(x.get("status") == 200 for x in public.values()),
        "local_http_200": local["/api/home_stats"].get("status") == 200,
        "catalog_total_8794": int(meta.get("total") or 0) >= 8794,
        "sunnah_total_6": int(sunnah.get("total") or 0) >= 6,
    }
    return {"timestamp": iso(), "ok": all(conditions.values()), "conditions": conditions,
            "public": public, "local": local, "system": system_snapshot()}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--public-url", default="https://xn--dqry4os3s3gb.com")
    ap.add_argument("--local-url", default="http://127.0.0.1:8080")
    ap.add_argument("--service", default="nur.service")
    ap.add_argument("--interval", type=int, default=60)
    ap.add_argument("--timeout", type=float, default=20)
    ap.add_argument("--log-dir", default="/var/log/nur-monitor")
    ap.add_argument("--once", action="store_true")
    args = ap.parse_args()
    log_dir = Path(args.log_dir); log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "health.jsonl"
    latest = log_dir / "latest.json"
    while True:
        started = time.monotonic()
        record = one_check(args.public_url, args.local_url, args.service, args.timeout)
        line = json.dumps(record, ensure_ascii=False)
        with log_file.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
        # Keep the resident log bounded without reading a potentially huge file.
        # The previous splitlines() implementation could load 100MB+ into RAM.
        try:
            if log_file.stat().st_size > MAX_LOG_BYTES:
                with log_file.open("rb") as src:
                    src.seek(0, os.SEEK_END)
                    end = src.tell()
                    start = max(0, end - KEEP_LOG_BYTES)
                    src.seek(start)
                    tail = src.read(KEEP_LOG_BYTES)
                if start:
                    nl = tail.find(b"\n")
                    if nl >= 0:
                        tail = tail[nl + 1:]
                fd2, tmp2 = tempfile.mkstemp(prefix="health-", dir=str(log_dir))
                try:
                    with os.fdopen(fd2, "wb") as out:
                        out.write(tail)
                    os.replace(tmp2, log_file)
                finally:
                    if os.path.exists(tmp2):
                        os.unlink(tmp2)
        except Exception:
            pass
        fd, tmp = tempfile.mkstemp(prefix="latest-", dir=str(log_dir))
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
            os.replace(tmp, latest)
        finally:
            if os.path.exists(tmp): os.unlink(tmp)
        print(f"[{record['timestamp']}] ok={record['ok']} conditions={record['conditions']}", flush=True)
        if args.once: return 0 if record["ok"] else 2
        gc.collect()
        time.sleep(max(1, args.interval - (time.monotonic() - started)))


if __name__ == "__main__":
    raise SystemExit(main())
