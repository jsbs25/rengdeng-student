#!/usr/bin/env python3
"""Bounded local lookup benchmark; no network, AI, auth, or writes."""
from __future__ import annotations
import json
import statistics
import sys
import time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import server  # noqa: E402

WORDS = ['كتاب', 'كِتَاب', 'في', 'السلام', 'مكتبة', 'يوميا', 'مدرسة', 'غيرموجودكلمة']

def measure(fn, values):
    rows = []
    for word in values:
        t = time.perf_counter(); result = fn(word); ms = (time.perf_counter() - t) * 1000
        rows.append({'word': word, 'latency_ms': round(ms, 3), 'found': bool(result.get('found') if 'found' in result else result.get('items'))})
    vals = [r['latency_ms'] for r in rows]
    return {'count': len(vals), 'p50_ms': round(statistics.median(vals), 3),
            'p95_ms': round(sorted(vals)[max(0, int(len(vals) * .95) - 1)], 3),
            'max_ms': round(max(vals), 3), 'samples': rows}

print(json.dumps({'lookup': measure(server._local_dict_lookup, WORDS),
                  'suggest': measure(lambda q: server._dict_suggest(q, 8), ['ك', 'كت', 'كتاب', 'سل', 'مد'])}, ensure_ascii=False, indent=2))
