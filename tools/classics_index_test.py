#!/usr/bin/env python3
"""Offline integrity checks for the additive classics discovery index."""
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / 'data' / 'library'
idx = json.loads((LIB / 'classics_index.json').read_text(encoding='utf-8'))
shamela = json.loads((LIB / 'shamela_index.json').read_text(encoding='utf-8')).get('books', {})
items = idx.get('items') or []
assert len(items) >= 1500, len(items)
ids = [str(x.get('id') or '') for x in items]
assert all(ids), 'empty id'
assert len(ids) == len(set(ids)), 'duplicate id'
assert all(x in shamela for x in ids), 'non-Shamela id present'
assert all(x.get('rt') == 'shamela' and x.get('readable') is True for x in items)
assert all(x.get('read_entry') == 'openReadById' for x in items)
assert all(not re.search(r'[\u4e00-\u9fff]', str(x.get('title_ar') or '')) for x in items)
assert all(x.get('classification_basis') and x.get('rights_notice') for x in items)
assert set((idx.get('meta') or {}).get('counts', {})) >= {'language', 'literature', 'fiqh', 'usul'}
for path in idx.get('reading_paths') or []:
    assert path.get('id') and path.get('title') and path.get('steps')
    assert set(path.get('collections') or []) <= set((idx.get('meta') or {}).get('counts', {}))
assert (idx.get('meta') or {}).get('total') == len(items)
print(json.dumps({'ok': True, 'total': len(items), 'unique_ids': len(set(ids)), 'shamela_readable': True, 'paths': len(idx.get('reading_paths') or []), 'counts': (idx.get('meta') or {}).get('counts', {})}, ensure_ascii=False))
