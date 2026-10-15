#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""抓取「历史」书库（Archive.org 世界史书，元数据 + 按需正文）。

产出：data/history/index.json（{id,title,lang,year,creator,subject,src}）
用法：python3 harvest/build_history.py [目标条数，默认 20000]
"""
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'data' / 'history'
API = 'https://archive.org/advancedsearch.php'
TARGET = int(sys.argv[1]) if len(sys.argv) > 1 else 20000

QUERIES = [
    'mediatype:texts AND subject:(history) AND -collection:newspapers AND -collection:magazine_rack',
    'mediatype:texts AND subject:("world history")',
    'mediatype:texts AND subject:("ancient history")',
    'mediatype:texts AND subject:("中国历史" OR "历史")',
    'mediatype:texts AND subject:("Islamic history" OR "تاريخ")',
]


def fetch(q, page, rows=1000):
    params = {
        'q': q, 'rows': str(rows), 'page': str(page), 'output': 'json',
        'sort[]': 'downloads desc',
    }
    url = API + '?' + urllib.parse.urlencode(params) + \
        '&fl%5B%5D=identifier&fl%5B%5D=title&fl%5B%5D=language&fl%5B%5D=year&fl%5B%5D=creator&fl%5B%5D=subject'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode('utf-8'))['response']['docs']


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    books, seen = [], set()
    for q in QUERIES:
        if len(books) >= TARGET:
            break
        page = 1
        while len(books) < TARGET and page <= 25:
            try:
                docs = fetch(q, page)
            except Exception as e:
                print('  ✗', str(e)[:60]); break
            if not docs:
                break
            for d in docs:
                i = d.get('identifier')
                t0 = d.get('title') or ''
                if isinstance(t0, list):
                    t0 = t0[0] if t0 else ''
                t = str(t0 or '').strip()
                if not i or not t or i in seen:
                    continue
                seen.add(i)
                lang = d.get('language')
                if isinstance(lang, list):
                    lang = lang[0] if lang else ''
                cr = d.get('creator')
                if isinstance(cr, list):
                    cr = cr[0] if cr else ''
                books.append({
                    'id': i, 'title': t[:180], 'lang': (lang or '')[:12],
                    'year': str(d.get('year') or '')[:6], 'creator': (cr or '')[:80],
                    'src': 'archive',
                })
            print(f'  {q[:40]}… 第{page}页 → 累计 {len(books)}', flush=True)
            page += 1
            time.sleep(0.4)
    (OUT / 'index.json').write_text(json.dumps({'total': len(books), 'books': books}, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    print(f'✅ 历史书库: {len(books)} 部 → {OUT}/index.json ({(OUT/"index.json").stat().st_size/1048576:.1f} MB)')


if __name__ == '__main__':
    main()
