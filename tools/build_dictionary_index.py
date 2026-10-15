#!/usr/bin/env python3
"""Build a bounded local Arabic dictionary/example index from project data only."""
from __future__ import annotations
import hashlib
import json
import os
import re
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = Path(os.environ.get('NOUR_DICTIONARY_DATA_DIR', str(ROOT / 'data')))
OUT = Path(os.environ.get('NOUR_DICTIONARY_INDEX_OUT', str(DATA / 'dictionary_index.json')))
MARKS = re.compile(r'[\u0610-\u061A\u064B-\u0652\u0670\u0640]')
AR_TOKEN = re.compile(r'[\u0600-\u06ff]+')
PUNCT = '،؛,.!?؟:()[]{}<>"\'“”‘’/\\|'

def normalize(value: object) -> str:
    value = MARKS.sub('', re.sub(r'\s+', ' ', str(value or '')).strip())
    return value

def tokens(text: str) -> list[str]:
    out = []
    for raw in AR_TOKEN.findall(text or ''):
        token = normalize(raw).strip(PUNCT)
        if token:
            out.append(token)
    return out

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def source_meta(path: Path) -> dict:
    st = path.stat()
    return {'sha256': sha256(path), 'size': st.st_size, 'mtime_ns': st.st_mtime_ns}

def load_meanings(path: Path) -> dict[str, dict]:
    raw = json.loads(path.read_text(encoding='utf-8'))
    out = {}
    if isinstance(raw, dict):
        rows = raw.items()
        for original, value in rows:
            if not isinstance(value, dict):
                continue
            key = normalize(original)
            if key:
                out[key] = {'w': str(original), 'cn': str(value.get('cn') or ''),
                            'en': str(value.get('en') or '')}
    elif isinstance(raw, list):
        for value in raw:
            if not isinstance(value, dict) or not value.get('w'):
                continue
            original = str(value['w'])
            key = normalize(original)
            if key:
                out[key] = {'w': original, 'cn': str(value.get('cn') or ''),
                            'en': str(value.get('en') or '')}
    return out

def main() -> int:
    meanings_path = DATA / 'vocab_meanings.json'
    sentences_path = DATA / 'data.json'
    meanings = load_meanings(meanings_path)
    sentences = json.loads(sentences_path.read_text(encoding='utf-8'))
    if not isinstance(sentences, list):
        raise SystemExit('data.json must contain a list')

    example_ids: dict[str, list[int]] = {}
    frequency: dict[str, int] = {}
    for idx, row in enumerate(sentences):
        if not isinstance(row, dict):
            continue
        for token in tokens(str(row.get('ar') or '')):
            frequency[token] = frequency.get(token, 0) + 1
            ids = example_ids.setdefault(token, [])
            if idx not in ids and len(ids) < 6:
                ids.append(idx)

    # Suggestions cover fixed dictionary heads plus real sentence tokens. Keep
    # each prefix bounded so one-character input cannot create a huge response.
    terms = set(example_ids) | set(meanings)
    prefix: dict[str, list[str]] = {}
    for term in terms:
        if not term:
            continue
        for n in range(1, min(3, len(term)) + 1):
            prefix.setdefault(term[:n], []).append(term)
    for key, values in prefix.items():
        values.sort(key=lambda x: (-frequency.get(x, 0), 0 if x in meanings else 1, x))
        prefix[key] = values[:120]

    postings = sum(len(v) for v in example_ids.values())
    index = {
        'version': 1,
        'generated_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'source': {
            'vocab_meanings': source_meta(meanings_path),
            'sentences': source_meta(sentences_path),
        },
        'stats': {
            'meaning_count': len(meanings),
            'unique_tokens': len(example_ids),
            'suggestion_terms': len(terms),
            'sentence_count': len(sentences),
            'example_postings': postings,
            'max_examples_per_term': 6,
            'max_suggestions_per_prefix': 120,
        },
        'meanings': meanings,
        'examples': example_ids,
        'prefix': prefix,
    }
    OUT.write_text(json.dumps(index, ensure_ascii=False, separators=(',', ':')) + '\n',
                   encoding='utf-8')
    print(json.dumps({'output': str(OUT), **index['stats']}, ensure_ascii=False))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
