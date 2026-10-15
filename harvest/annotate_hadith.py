#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""后台批量生成圣训「译文 + 经注」，写入 data/hadith/an/<book>.json（可断点续跑）。

用法：python3 harvest/annotate_hadith.py [--workers 6] [--limit 0]
"""
import argparse
import json
import os
import threading
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AN = ROOT / 'data' / 'hadith' / 'an'
IDX = ROOT / 'data' / 'hadith' / 'index.json'
KEY = (ROOT / 'data' / 'ai_key.txt').read_text(encoding='utf-8').strip()

lock = threading.Lock()
stats = {'ok': 0, 'fail': 0, 'skip': 0}
_cache = {}


def load(book):
    if book not in _cache:
        try:
            _cache[book] = json.loads((AN / (book + '.json')).read_text(encoding='utf-8'))
        except Exception:
            _cache[book] = {}
    return _cache[book]


def save(book):
    AN.mkdir(parents=True, exist_ok=True)
    p = AN / (book + '.json')
    with lock:
        tmp = str(p) + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(_cache[book], f, ensure_ascii=False)
        os.replace(tmp, p)


def annotate(ar):
    prompt = ('下面是一段阿拉伯语圣训。请完成两件事，严格按 JSON 输出（不要代码块、不要多余文字）：\n'
              '{"cn":"中文译文","note":"简要经注（讲的是什么、教法或信仰要点、传述背景，80-160字）"}\n\n'
              '圣训原文：\n' + ar)
    body = json.dumps({'model': 'deepseek-chat', 'messages': [{'role': 'user', 'content': prompt}],
                       'temperature': 0.2, 'max_tokens': 900}).encode('utf-8')
    req = urllib.request.Request('https://api.deepseek.com/chat/completions', data=body,
                                 headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + KEY})
    with urllib.request.urlopen(req, timeout=180) as r:
        d = json.loads(r.read().decode('utf-8'))
    txt = d['choices'][0]['message']['content'].strip()
    s, e = txt.find('{'), txt.rfind('}')
    if s >= 0 and e > s:
        try:
            j = json.loads(txt[s:e + 1])
            return {'cn': (j.get('cn') or '').strip(), 'note': (j.get('note') or '').strip()}
        except Exception:
            pass
    return {'cn': txt[:800], 'note': ''}


def work(book, item):
    n = str(item.get('n'))
    ar = item.get('ar') or ''
    if not ar:
        return
    d = load(book)
    if n in d and d[n].get('cn'):
        with lock:
            stats['skip'] += 1
        return
    try:
        got = annotate(ar)
        with lock:
            _cache[book][n] = got
            stats['ok'] += 1
        if stats['ok'] % 20 == 0:
            save(book)
    except Exception as e:
        with lock:
            stats['fail'] += 1
        if stats['fail'] % 10 == 1:
            print('  fail:', e, flush=True)
        time.sleep(1.0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--workers', type=int, default=6)
    ap.add_argument('--limit', type=int, default=0)
    args = ap.parse_args()

    idx = json.loads(IDX.read_text(encoding='utf-8'))['books']
    tasks = []
    for b in idx:
        book = b['key']
        bj = json.loads((ROOT / 'data' / 'hadith' / (book + '.json')).read_text(encoding='utf-8'))
        for it in bj.get('hadiths', []):
            tasks.append((book, it))
    d = load(idx[0]['key'])
    print(f'总段数 {len(tasks)}，已有缓存（首部 {len(d)}）', flush=True)
    if args.limit:
        tasks = tasks[:args.limit]

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        for i, (book, it) in enumerate(tasks):
            ex.submit(work, book, it)
            if i % 200 == 0:
                print(f'  提交 {i}/{len(tasks)}  ok={stats["ok"]} skip={stats["skip"]} fail={stats["fail"]}', flush=True)
    for b in idx:
        save(b['key'])
    print(f'✅ 完成 ok={stats["ok"]} skip={stats["skip"]} fail={stats["fail"]}')


if __name__ == '__main__':
    main()
