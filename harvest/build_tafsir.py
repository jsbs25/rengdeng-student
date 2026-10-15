#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""为古兰经每一章生成中文「经注」（简介/降示背景/主题/重点），写入 data/tafsir.json。

用法：python3 harvest/build_tafsir.py
"""
import json
import re
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KEY = (ROOT / 'data' / 'ai_key.txt').read_text(encoding='utf-8').strip()
OUT = ROOT / 'data' / 'tafsir.json'
SRC = ROOT / 'data' / 'quranData.js'


def surahs():
    txt = SRC.read_text(encoding='utf-8', errors='ignore')
    m = re.search(r'(\[.*\])', txt, re.S)
    try:
        d = json.loads(m.group(1))
        out = []
        for s in d:
            out.append({'id': s.get('id'), 'n': s.get('n') or s.get('name'), 'tz': s.get('tz') or s.get('arabic') or ''})
        return out
    except Exception:
        return []


def gen(s):
    prompt = ('请为《古兰经》第%s章「%s」写一段简体中文经注，包含：①降示背景与地点（麦加/麦地那）②本章主题与结构 '
              '③重要经文与教义要点 ④诵读与践行建议。180-260字，只输出正文，不要标题、不要"经注："前缀。'
              % (s['id'], s['n']))
    body = json.dumps({'model': 'deepseek-chat', 'messages': [{'role': 'user', 'content': prompt}],
                       'temperature': 0.4, 'max_tokens': 700}).encode('utf-8')
    req = urllib.request.Request('https://api.deepseek.com/chat/completions', data=body,
                                 headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + KEY})
    with urllib.request.urlopen(req, timeout=150) as r:
        d = json.loads(r.read().decode('utf-8'))
    return (d['choices'][0]['message']['content'] or '').strip()


def main():
    ss = surahs()
    print('章数:', len(ss))
    done = []
    if OUT.exists():
        try:
            done = json.loads(OUT.read_text(encoding='utf-8'))
        except Exception:
            done = []
    have = {x['surah'] for x in done}
    todo = [s for s in ss if s['id'] not in have]
    print('待生成:', len(todo))

    def work(s):
        try:
            t = gen(s)
            return {'surah': s['id'], 'name': s['n'], 'ar': s['tz'], 'text': t}
        except Exception as e:
            print('fail', s['id'], e)
            return None

    with ThreadPoolExecutor(max_workers=4) as ex:
        for i, r in enumerate(ex.map(work, todo)):
            if r:
                done.append(r)
            if i % 10 == 0:
                OUT.write_text(json.dumps(done, ensure_ascii=False, indent=1), encoding='utf-8')
                print('  进度', i, '/', len(todo), flush=True)
    done.sort(key=lambda x: x['surah'])
    OUT.write_text(json.dumps(done, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'✅ 经注 {len(done)} 章 → {OUT} ({OUT.stat().st_size/1024:.0f}KB)')


if __name__ == '__main__':
    main()
