#!/usr/bin/env python3
"""Offline integrity contract for the local Arabic dictionary index."""
from __future__ import annotations
import hashlib
import json
import os
import subprocess
import sys
import tempfile
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


def rebuild_index() -> dict:
    """Build into a temporary path so this test never rewrites project data."""
    env = os.environ.copy()
    env['NOUR_DICTIONARY_DATA_DIR'] = str(DATA)
    with tempfile.TemporaryDirectory(prefix='dictionary-index-test-') as tmp:
        output = Path(tmp) / 'dictionary_index.json'
        env['NOUR_DICTIONARY_INDEX_OUT'] = str(output)
        subprocess.run(
            [sys.executable, str(ROOT / 'tools' / 'build_dictionary_index.py')],
            cwd=ROOT,
            env=env,
            check=True,
            stdout=subprocess.PIPE,
            text=True,
        )
        return json.loads(output.read_text(encoding='utf-8'))


def main() -> int:
    d = json.loads(INDEX.read_text(encoding='utf-8'))
    assert d.get('version') == 1
    source = d['source']
    for key, filename in [('vocab_meanings', 'vocab_meanings.json'), ('sentences', 'data.json')]:
        p = DATA / filename
        assert p.is_file(), f'{key}: missing source file {p}'
        meta = source[key]
        assert meta['sha256'] == sha256(p), f'{key}:sha256'
        assert meta['size'] == p.stat().st_size, f'{key}:size'

    meanings = d['meanings']
    examples = d['examples']
    prefix = d['prefix']
    sentences = json.loads((DATA / 'data.json').read_text(encoding='utf-8'))
    assert isinstance(meanings, dict) and meanings
    assert isinstance(examples, dict) and examples
    assert isinstance(prefix, dict) and prefix
    assert isinstance(sentences, list)

    stats = d['stats']
    assert stats['meaning_count'] == len(meanings)
    assert stats['unique_tokens'] == len(examples)
    assert stats['sentence_count'] == len(sentences)
    assert stats['example_postings'] == sum(len(ids) for ids in examples.values())
    assert stats['max_examples_per_term'] == 6
    assert stats['max_suggestions_per_prefix'] == 120

    terms = set(meanings) | set(examples)
    for token, ids in examples.items():
        assert isinstance(token, str) and token
        assert isinstance(ids, list) and 1 <= len(ids) <= 6, token
        assert len(ids) == len(set(ids)), token
        assert all(type(i) is int and 0 <= i < len(sentences) for i in ids), token
    for key, values in prefix.items():
        assert isinstance(key, str) and 1 <= len(key) <= 3, key
        assert isinstance(values, list)
        assert len(values) <= 120 and len(values) == len(set(values)), key
        assert all(isinstance(v, str) and v.startswith(key) and v in terms for v in values), key
    assert 'كتاب' in meanings or 'كتاب' in examples
    assert any('كتاب' in prefix.get(key, []) for key in ('ك', 'كت', 'كتا'))

    # Compare the checked-in artifact with a fresh build, ignoring only volatile
    # generation time and source mtime. Content, source hashes/sizes, and stats
    # must all come from the current project inputs.
    rebuilt = rebuild_index()
    for field in ('version', 'stats', 'meanings', 'examples', 'prefix'):
        assert d[field] == rebuilt[field], f'{field}: differs from a fresh build'
    for key in ('vocab_meanings', 'sentences'):
        for field in ('sha256', 'size'):
            assert source[key][field] == rebuilt['source'][key][field], f'{key}:{field}: differs from a fresh build'

    print(json.dumps({'ok': True, 'meaning_count': len(meanings),
                      'unique_tokens': len(examples), 'prefixes': len(prefix),
                      'sentence_count': len(sentences), 'fresh_build_match': True},
                     ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
