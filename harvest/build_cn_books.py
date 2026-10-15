#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从「殆知阁古代文献」生成中国书籍索引与正文副本。

输入：harvest/cn/daizhige/<藏>/…/<书名>.txt
产物：
  data/cn_books/index.json   {total, books:[{id,title,category,size}]}
  data/cn_books/t/<id>.txt   正文副本（体积大，已在 .gitignore 中忽略，不入库）

用法：python3 harvest/build_cn_books.py
"""
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'harvest' / 'cn' / 'daizhige'
OUT = ROOT / 'data' / 'cn_books'
TDIR = OUT / 't'

# 顶层藏名（只收录这十藏，顺序用于稳定排序与前端展示）
CAT_ORDER = ['儒藏', '史藏', '子藏', '集藏', '诗藏', '医藏', '易藏', '艺藏', '佛藏', '道藏']
CAT_IDX = {c: i for i, c in enumerate(CAT_ORDER)}


def main():
    if not SRC.exists():
        raise SystemExit('源目录不存在：%s' % SRC)
    OUT.mkdir(parents=True, exist_ok=True)
    TDIR.mkdir(parents=True, exist_ok=True)

    txts = sorted(SRC.rglob('*.txt'))
    rows = []
    for p in txts:
        rel = p.relative_to(SRC)
        cat = rel.parts[0] if rel.parts else ''
        if cat not in CAT_IDX:
            continue
        rows.append((CAT_IDX[cat], cat, p.stem, p))

    # 稳定排序：先按藏序，再按书名
    rows.sort(key=lambda r: (r[0], r[2]))

    books = []
    for n, (_, cat, title, p) in enumerate(rows, 1):
        bid = '%06d' % n
        dst = TDIR / (bid + '.txt')
        if not dst.exists() or dst.stat().st_size != p.stat().st_size:
            shutil.copyfile(p, dst)
        books.append({'id': bid, 'title': title, 'category': cat, 'size': p.stat().st_size})

    idx = {'total': len(books), 'books': books}
    (OUT / 'index.json').write_text(json.dumps(idx, ensure_ascii=False), encoding='utf-8')

    # 统计各藏分布
    dist = {}
    for b in books:
        dist[b['category']] = dist.get(b['category'], 0) + 1
    print('收录 %d 部' % len(books))
    for c in CAT_ORDER:
        if c in dist:
            print('  %s %d' % (c, dist[c]))
    print('索引：%s' % (OUT / 'index.json'))
    print('正文：%s（%d 个文件）' % (TDIR, len(books)))


if __name__ == '__main__':
    main()
