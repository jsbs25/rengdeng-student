#!/usr/bin/env python3
"""Bounded public-source refresh for the Arabic learning site.

This job only reads official allow-listed endpoints and atomically updates a
small, reviewable cache. It never crawls a site tree, downloads bulk archives,
or overwrites user/member/AI data.
"""
from __future__ import annotations
import json, os, re, sys, time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / 'data' / 'public_source_cache'
CACHE.mkdir(parents=True, exist_ok=True)
UA = 'NourArabicLearning/1.0 (+https://xn--dqry4os3s3gb.com/; public-source-sync)'
MAX_BYTES = 2 * 1024 * 1024
TIMEOUT = 18

SOURCES = [
    {'id': 'ar-wiktionary', 'url': 'https://ar.wiktionary.org/w/api.php',
     'license': 'CC BY-SA 4.0 / GFDL per entry; verify entry and media terms',
     'kind': 'dictionary'},
    {'id': 'tatoeba', 'url': 'https://api.tatoeba.org/',
     'license': 'Per-sentence CC BY 2.0 FR or CC0; audio is separately licensed',
     'kind': 'sentences'},
    {'id': 'openiti-release', 'url': 'https://github.com/OpenITI/RELEASE',
     'license': 'CC BY-NC-SA 4.0; non-commercial and attribution/share-alike',
     'kind': 'texts'},
    {'id': 'arabic-wikipedia', 'url': 'https://ar.wikipedia.org/w/api.php',
     'license': 'Usually CC BY-SA 4.0; verify page and media provenance',
     'kind': 'reading'},
    {'id': 'common-voice-mdc',
     'url': 'https://mozilladatacollective.com/datasets/cmu5wom3z00ceo107guxtg4xa',
     'license': 'CC0 dataset label with MDC/Mozilla distribution terms',
     'kind': 'audio-metadata'},
]


def now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def fetch(url: str, params: dict | None = None):
    if params:
        url += ('&' if '?' in url else '?') + urlencode(params)
    req = Request(url, headers={'User-Agent': UA, 'Accept': 'application/json,text/plain;q=0.9'})
    with urlopen(req, timeout=TIMEOUT) as r:
        status = getattr(r, 'status', 200)
        data = r.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES:
            raise ValueError('response exceeds bounded 2 MiB limit')
        return status, dict(r.headers), data


def atomic_json(path: Path, obj):
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    os.replace(tmp, path)


def wiktionary_sample():
    status, headers, body = fetch('https://ar.wiktionary.org/w/api.php', {
        'action': 'query', 'prop': 'extracts|info', 'explaintext': '1',
        'inprop': 'url', 'format': 'json', 'redirects': '1', 'maxlag': '5',
        'titles': 'سلام'
    })
    data = json.loads(body.decode('utf-8'))
    pages = (data.get('query') or {}).get('pages') or {}
    page = next(iter(pages.values()), {})
    return {'source_id': 'ar-wiktionary', 'title': page.get('title', 'سلام'),
            'pageid': page.get('pageid'), 'revid': page.get('lastrevid'),
            'source_url': page.get('fullurl') or 'https://ar.wiktionary.org/wiki/سلام',
            'extract': str(page.get('extract') or '')[:600],
            'license': 'CC BY-SA 4.0 / GFDL per entry; verify entry and media terms',
            'retrieved_at': now(), 'http_status': status}


def source_health(source):
    try:
        status, headers, _ = fetch(source['url'])
        return {'id': source['id'], 'url': source['url'], 'kind': source['kind'],
                'license': source['license'], 'ok': 200 <= status < 400,
                'http_status': status, 'retrieved_at': now(),
                'etag': headers.get('ETag', ''), 'last_modified': headers.get('Last-Modified', '')}
    except Exception as e:
        return {'id': source['id'], 'url': source['url'], 'kind': source['kind'],
                'license': source['license'], 'ok': False, 'retrieved_at': now(),
                'error': str(e)[:240]}


def main():
    started = now()
    health = []
    for i, source in enumerate(SOURCES):
        if i:
            time.sleep(1.1)  # conservative single queue; not an official quota
        health.append(source_health(source))
    sample = None
    try:
        time.sleep(1.1)
        sample = wiktionary_sample()
        atomic_json(CACHE / 'wiktionary-sample.json', sample)
    except Exception as e:
        sample = {'ok': False, 'error': str(e)[:240], 'retrieved_at': now()}
    report = {'job': 'public-source-sync', 'started_at': started, 'finished_at': now(),
              'policy': {'allowlist_only': True, 'max_response_bytes': MAX_BYTES,
                         'request_spacing_seconds': 1.1, 'bulk_downloads': False,
                         'overwrites_user_data': False},
              'sources': health, 'wiktionary_sample': sample}
    atomic_json(CACHE / 'status.json', report)
    print(json.dumps({'ok': True, 'finished_at': report['finished_at'],
                      'healthy_sources': sum(1 for x in health if x.get('ok')),
                      'wiktionary_sample': bool(sample and sample.get('extract'))}, ensure_ascii=False))


if __name__ == '__main__':
    main()
