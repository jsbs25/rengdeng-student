#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""重建「历史」书库：只保留 中文 + 阿拉伯语（删除全部英文/国外书）。

来源：
  中文 —— 殆知阁 data/cn_books/index.json（史藏=历史；集藏/诗藏/子藏=文学）
  阿拉伯语 —— data/islamic_catalog.json 中分类含「历史/传记/人物志/先知传记」的书
产出：data/history/index.json
用法：python3 harvest/build_history_v2.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'data' / 'history' / 'index.json'

CN_HIST = {'史藏'}
CN_LIT = {'集藏', '诗藏', '子藏'}


def main():
    books = []

    # 1) 中文：史藏 → 历史；集藏/诗藏/子藏 → 文学/小说
    cn = json.loads((ROOT / 'data' / 'cn_books' / 'index.json').read_text(encoding='utf-8'))
    n_cn_hist = n_cn_lit = 0
    for b in cn.get('books', []):
        cat = b.get('category', '')
        if cat in CN_HIST:
            kind = '中国历史'
            n_cn_hist += 1
        elif cat in CN_LIT:
            kind = '中国文学 / 小说'
            n_cn_lit += 1
        else:
            continue
        books.append({
            'id': 'cn:' + str(b.get('id')),
            'title': b.get('title', ''),
            'lang': 'zh',
            'cat': kind,
            'src': 'cn',
            'path': b.get('path') or ('data/cn_books/t/%s.txt' % b.get('id')),
        })

    # 2) 阿拉伯语：伊斯兰目录里历史/传记类的书
    n_ar = 0
    try:
        cat = json.loads((ROOT / 'data' / 'islamic_catalog.json').read_text(encoding='utf-8'))
        for b in cat.get('books', []):
            c = b.get('c', '') or ''
            if any(k in c for k in ('历史', '传记', '人物志', '先知传记', '谱系', '地理')):
                books.append({
                    'id': 'ar:' + str(b.get('id') or b.get('t')),
                    'title': b.get('t', ''),
                    'lang': 'ar',
                    'cat': '阿拉伯语历史 / 传记',
                    'src': 'ar',
                    'rid': b.get('r') or None,
                    'u': b.get('u', ''),
                })
                n_ar += 1
    except Exception as e:
        print('ar skip:', e)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({'total': len(books), 'books': books}, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    print(f'✅ 历史/文学库重建：{len(books)} 部')
    print(f'   中文历史 {n_cn_hist} · 中文文学小说 {n_cn_lit} · 阿拉伯语历史传记 {n_ar}')
    print(f'   （已删除全部英文/国外历史书）')


if __name__ == '__main__':
    main()
