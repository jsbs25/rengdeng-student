#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Shamela4 全文库索引构建器（可读全文）。

数据源：HuggingFace `AuthenticIlm/Shamela4_Full_DB`
  目录结构：<分类>/<图书id>__<书名slug>/{book_metadata.json, toc.jsonl, pages.jsonl}
产出：data/library/shamela_index.json  —— id -> {cat, dir, slug}
用法：python3 harvest/build_shamela_index.py
"""
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'data' / 'library'
API = 'https://huggingface.co/api/datasets/AuthenticIlm/Shamela4_Full_DB/tree/main'


def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read().decode('utf-8')), dict(r.headers)


def get_all(url):
    """跟随 Link: rel=next 分页，拿完一个目录下的全部条目。"""
    out = []
    nxt = url
    seen = 0
    while nxt and seen < 20:
        data, hdr = get(nxt)
        out.extend(data)
        link = hdr.get('Link') or hdr.get('link') or ''
        m = re.search(r'<([^>]+)>;\s*rel="next"', link)
        nxt = m.group(1) if m else None
        seen += 1
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    top, _ = get(API)
    cats = [x['path'] for x in top if x.get('type') == 'directory' and not x['path'].startswith('_')]
    print('分类数:', len(cats))
    index = {}
    for cat in cats:
        path = urllib.parse.quote(cat)
        try:
            items = get_all(API + '/' + path)
        except Exception as e:
            print('  ✗', cat, e)
            continue
        n = 0
        for it in items:
            if it.get('type') != 'directory':
                continue
            name = it['path'].rsplit('/', 1)[-1]
            m = re.match(r'^(\d+)__(.+)$', name)
            if not m:
                continue
            bid, slug = m.group(1), m.group(2)
            index[bid] = {'cat': cat, 'dir': f'{cat}/{name}', 'slug': slug}
            n += 1
        print(f'  {cat:<40} {n} 本')
    (OUT / 'shamela_index.json').write_text(
        json.dumps({'total': len(index), 'books': index}, ensure_ascii=False, separators=(',', ':')),
        encoding='utf-8')
    print(f'\n✅ 可读全文图书: {len(index)} 本 -> {OUT / "shamela_index.json"} ({(OUT / "shamela_index.json").stat().st_size/1048576:.1f} MB)')


if __name__ == '__main__':
    main()
