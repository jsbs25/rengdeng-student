#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""抓取中文小说/文学 → 并入「书籍」（data/cn_books）。

来源：中文维基文库（zh.wikisource.org，公有领域）的小说/诗词/文集/戏曲等分类。
产出：data/cn_books/t/<id>.txt + index.json（追加入 literary 条目）
用法：python3 harvest/build_cn_literature.py [每类上限]
"""
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CBDIR = ROOT / 'data' / 'cn_books'
TDIR = CBDIR / 't'
API = 'https://zh.wikisource.org/w/api.php'

CATS = [
    ('章回小說', '小说'), ('筆記小說', '笔记小说'), ('志怪', '志怪小说'),
    ('傳奇', '传奇小说'), ('話本', '话本'), ('宋代筆記', '笔记随笔'),
    ('明代筆記', '笔记随笔'), ('清代筆記', '笔记随笔'), ('唐五代筆記', '笔记随笔'),
]
LIMIT = int(sys.argv[1]) if len(sys.argv) > 1 else 400


def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'nur/1.0'})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode('utf-8'))


def cat_members(cat, limit):
    out, cont = [], None
    while len(out) < limit:
        u = (API + '?action=query&list=categorymembers&cmtitle=' + urllib.parse.quote('Category:' + cat) +
             '&cmnamespace=0&cmlimit=500&format=json')
        if cont:
            u += '&cmcontinue=' + cont
        try:
            d = get(u)
        except Exception:
            break
        out += [m['title'] for m in d.get('query', {}).get('categorymembers', [])]
        cont = d.get('continue', {}).get('cmcontinue')
        if not cont:
            break
        time.sleep(0.3)
    return out[:limit]


def extracts(titles):
    res = {}
    for i in range(0, len(titles), 20):
        batch = titles[i:i + 20]
        u = (API + '?action=query&prop=extracts&explaintext=1&exlimit=20&format=json&titles=' +
             urllib.parse.quote('|'.join(batch)))
        try:
            d = get(u)
        except Exception:
            continue
        for p in d.get('query', {}).get('pages', {}).values():
            t = (p.get('extract') or '').strip()
            if t:
                res[p.get('title')] = t
        time.sleep(0.25)
    return res


def main():
    TDIR.mkdir(parents=True, exist_ok=True)
    idxp = CBDIR / 'index.json'
    idx = json.loads(idxp.read_text(encoding='utf-8')) if idxp.exists() else {'total': 0, 'books': []}
    have = {b.get('title') for b in idx['books']}
    n_new = 0
    for cat, genre in CATS:
        titles = [t for t in cat_members(cat, LIMIT) if t not in have]
        if not titles:
            print('  -', cat, '无新增')
            continue
        got = extracts(titles)
        for title, text in got.items():
            if title in have or len(text) < 300:
                continue
            bid = 'lit' + str(abs(hash(title)) % 10**9)
            (TDIR / (bid + '.txt')).write_text(text[:120000], encoding='utf-8')
            idx['books'].append({'id': bid, 'title': title, 'category': genre,
                                 'path': 'data/cn_books/t/%s.txt' % bid, 'size': len(text)})
            have.add(title)
            n_new += 1
        print(f'  ✓ {cat} → {genre}: +{len(got)}（累计新 {n_new}）', flush=True)
        idxp.write_text(json.dumps(idx, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    idx['total'] = len(idx['books'])
    idxp.write_text(json.dumps(idx, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    print(f'✅ 中文文学新增 {n_new} 部，书籍总数 {idx["total"]}')


if __name__ == '__main__':
    main()
