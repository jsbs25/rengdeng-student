#!/usr/bin/env python3
import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
import server
for name in ('grammar.json', 'morphology.json'):
    p = root / 'data' / name
    assert p.exists() and p.stat().st_size > 0, name
    raw = json.loads(p.read_text(encoding='utf-8'))
    assert isinstance(raw, list) and raw, name

d = server._dictionary_lesson_links('كتاب', 6)
assert d['ok'] and d['offline'] and d['source'] == '本地语法与词法课程'
assert 1 <= len(d['items']) <= 6
ids = {(x['kind'], x['id']) for x in d['items']}
assert len(ids) == len(d['items'])
assert all(x['kind'] in ('grammar', 'morph') for x in d['items'])
assert all(x['id'] and x['title'] and x['match_type'] for x in d['items'])
assert any(x['matched_terms'] for x in d['items'])
assert not server._dictionary_lesson_links('غيرموجودكلمة')['items']
assert len(server._dictionary_lesson_links('كتاب كتاب كتاب كتاب كتاب كتاب كتاب كتاب كتاب')['items']) <= 6
assert not server._dictionary_lesson_links('book')['items']
print('DICTIONARY_LESSON_TEST_OK', len(d['items']), sorted(ids))
