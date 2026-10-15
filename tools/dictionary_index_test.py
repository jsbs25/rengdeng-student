#!/usr/bin/env python3
"""Offline integrity contract for the local Arabic dictionary index."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = Path(os.environ.get('NOUR_DICTIONARY_DATA_DIR', str(ROOT / 'data')))
INDEX = Path(os.environ.get('NOUR_DICTIONARY_INDEX_PATH', str(DATA / 'dictionary_index.json')))

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def main() -> int:
    d = json.loads(INDEX.read_text(encoding='utf-8'))
    assert d.get('version') == 1
    source = d['source']
    for key, filename in [('vocab_meanings', 'vocab_meanings.json'), ('sentences', 'data.json')]:
        p = DATA / filename
        assert p.exists() and source[key]['sha256'] == sha256(p), key
        assert source[key]['size'] == p.stat().st_size, key + ':size'
    meanings = d['meanings']; examples = d['examples']; prefix = d['prefix']
    sentences = json.loads((DATA / 'data.json').read_text(encoding='utf-8'))
    assert meanings and examples and prefix
    assert isinstance(examples, dict)
    for token, ids in list(examples.items())[:200]:
        assert len(ids) == len(set(ids)) <= 6
        assert all(isinstance(i, int) and 0 <= i < len(sentences) for i in ids)
    for key, values in list(prefix.items())[:200]:
        assert 1 <= len(key) <= 3
        assert len(values) <= 120 and len(values) == len(set(values))
        assert all(v.startswith(key) for v in values)
    assert 'كتاب' in meanings or 'كتاب' in examples
    assert 'كتاب' in prefix.get('ك', []) or 'كتاب' in prefix.get('كت', []) or 'كتاب' in prefix.get('كتا', [])
    print(json.dumps({'ok': True, 'meaning_count': len(meanings),
                      'unique_tokens': len(examples), 'prefixes': len(prefix),
                      'sentence_count': len(sentences)}, ensure_ascii=False))

if __name__ == '__main__':
    main()
