#!/usr/bin/env python3
"""NOUR read-only performance baseline; never calls AI, auth, payment or write APIs."""
from __future__ import annotations
import argparse, json, re, subprocess, sys, time, urllib.request, urllib.parse
from pathlib import Path
from statistics import median

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ASSETS = [
    'data/builtin_sentences.js', 'data/builtin_books.js',
    'data/builtin_quran.js', 'data/builtin_hadith.js',
    'data/builtin_vocab.js', 'data/builtin_history.js',
    'data/course.js', 'data/views2.js',
]
LAZY_ASSETS = {
    'data/builtin_sentences.js', 'data/builtin_books.js', 'data/builtin_quran.js',
    'data/builtin_hadith.js', 'data/builtin_vocab.js', 'data/builtin_history.js',
}

def fetch(url: str, timeout: float = 30.0, accept_encoding: str = 'gzip') -> dict:
    req = urllib.request.Request(url, headers={
        'User-Agent': 'NOUR-performance-baseline/1.0',
        'Accept-Encoding': accept_encoding,
    })
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read()
            elapsed = (time.perf_counter() - started) * 1000
            return {
                'url': url, 'status': getattr(r, 'status', 200),
                'latency_ms': round(elapsed, 2),
                'wire_bytes': len(body),
                'content_encoding': r.headers.get('Content-Encoding', ''),
                'cache_control': r.headers.get('Cache-Control', ''),
                'etag': bool(r.headers.get('ETag')),
                'last_modified': bool(r.headers.get('Last-Modified')),
                'content_type': r.headers.get('Content-Type', ''),
            }
    except Exception as e:
        return {'url': url, 'status': 0, 'latency_ms': round((time.perf_counter()-started)*1000, 2), 'error': type(e).__name__ + ': ' + str(e)[:180]}

def api_samples(base: str) -> list[dict]:
    paths = [
        '/', '/api/home_stats', '/api/catalog/meta',
        '/api/catalog?page=1&size=60', '/api/library/classics?size=5',
        '/api/library/fiqh-schools?size=5', '/api/dict/lookup?w=%D9%83%D8%AA%D8%A7%D8%A8',
    ]
    return [fetch(base.rstrip('/') + p) for p in paths]

def asset_samples(base: str, html_result: dict) -> tuple[list[dict], list[dict]]:
    """Return (initial_assets, deferred_assets) from the current build.

    Data modules referenced only by NOUR_DATA_ASSETS are intentionally measured
    separately: they are real public resources, but are not downloaded on the
    initial page.
    """
    html_path = ROOT / 'arabic_learning.html'
    found = []
    deferred_paths = []
    version = ''
    if html_path.exists():
        text = html_path.read_text(encoding='utf-8', errors='ignore')
        found = [item for item in re.findall(r"(?:src|href)=[\"']([^\"']+)[\"']", text)
                 if item.startswith('data/')]
        m = re.search(r"NOUR_ASSET_VERSION\s*=\s*[\"']([^\"']+)", text)
        version = m.group(1) if m else ''
        mapped = set(re.findall(r"data/builtin_(?:sentences|books|quran|hadith|vocab|history)\.js", text))
        deferred_paths = sorted(mapped)
    assets = list(found)
    represented = {item.split('?', 1)[0] for item in found}
    for fallback in DEFAULT_ASSETS:
        if fallback not in represented and fallback not in LAZY_ASSETS:
            assets.append(fallback)
    assets = list(dict.fromkeys(assets))
    initial = [fetch(base.rstrip('/') + '/' + a.lstrip('/')) for a in assets]
    deferred = []
    for path in deferred_paths:
        url = path
        if version:
            url += '?v=' + urllib.parse.quote(version, safe='')
        item = fetch(base.rstrip('/') + '/' + url.lstrip('/'))
        item['load_mode'] = 'deferred'
        deferred.append(item)
    return initial, deferred

def local_dict_benchmark() -> dict:
    # Import only the existing local lookup function; no network and no AI call.
    sys.path.insert(0, str(ROOT))
    import server  # noqa: E402
    raw = json.loads((ROOT / 'data' / 'vocab_meanings.json').read_text(encoding='utf-8'))
    words = list(raw.keys())[:20] + ['كتاب', 'كِتَاب', 'سلام', 'مدرسة', 'غيرموجودكلمة']
    warm = []
    for word in words:
        started = time.perf_counter()
        result = server._local_dict_lookup(word)
        warm.append({'word': word, 'latency_ms': round((time.perf_counter()-started)*1000, 3), 'found': bool(result.get('found'))})
    cold_code = (
        'import sys,json,time; sys.path.insert(0,' + repr(str(ROOT)) + '); '
        'import server; t=time.perf_counter(); r=server._local_dict_lookup(sys.argv[1]); '
        'print(json.dumps({"latency_ms":round((time.perf_counter()-t)*1000,3),"found":bool(r.get("found"))}))'
    )
    cold = []
    for word in words[:8]:
        try:
            p = subprocess.run([sys.executable, '-c', cold_code, word], cwd=str(ROOT), capture_output=True, text=True, timeout=20)
            line = p.stdout.strip().splitlines()[-1] if p.stdout.strip() else '{}'
            cold.append({'word': word, **json.loads(line)})
        except Exception as e:
            cold.append({'word': word, 'error': type(e).__name__ + ': ' + str(e)[:160]})
    def summary(rows):
        vals = [float(x['latency_ms']) for x in rows if 'latency_ms' in x]
        return {'count': len(vals), 'p50_ms': round(median(vals), 3) if vals else None, 'max_ms': round(max(vals), 3) if vals else None}
    return {'warm': {'summary': summary(warm), 'samples': warm}, 'cold': {'summary': summary(cold), 'samples': cold}}

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--public-base', default='https://xn--dqry4os3s3gb.com')
    ap.add_argument('--local-base', default='')
    ap.add_argument('--output', default='docs/20261006-phase7-performance-baseline.json')
    args = ap.parse_args()
    initial_assets, deferred_assets = asset_samples(args.public_base, {})
    result = {
        'generated_at_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'scope': 'read-only; no AI, auth, payment, TTS, ASR or write endpoints',
        'public_base': args.public_base,
        'public_api': api_samples(args.public_base),
        'public_assets': initial_assets,
        'public_deferred_assets': deferred_assets,
        'local_dictionary': local_dict_benchmark(),
    }
    if args.local_base:
        result['local_base'] = args.local_base
        result['local_api'] = api_samples(args.local_base)
    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({
        'output': str(out),
        'public_api_ok': sum(1 for x in result['public_api'] if x.get('status') == 200),
        'public_asset_count': len(result['public_assets']),
        'public_deferred_asset_count': len(result['public_deferred_assets']),
        'dict_warm': result['local_dictionary']['warm']['summary'],
        'dict_cold': result['local_dictionary']['cold']['summary'],
    }, ensure_ascii=False))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
