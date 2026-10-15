#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把圣训篇章名（英文/阿拉伯转写）批量翻译成中文，产出 data/hadith/sections.json

用 App 自带的 DeepSeek key（data/ai_key.txt），分批调用。
用法：python3 harvest/translate_sections.py
"""
import json
import os
import re
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / 'harvest' / 'raw'
OUT = ROOT / 'data' / 'hadith' / 'sections.json'
BOOKS = ['bukhari', 'muslim', 'abudawud', 'tirmidhi', 'nasai', 'ibnmajah']


def api_key():
    fp = ROOT / 'data' / 'ai_key.txt'
    k = fp.read_text(encoding='utf-8').strip()
    return k


def collect():
    names = []
    for b in BOOKS:
        fp = RAW / f'hadith_{b}.json'
        if not fp.exists():
            continue
        d = json.loads(fp.read_text(encoding='utf-8'))
        for sid, v in (d.get('metadata', {}).get('sections', {}) or {}).items():
            v = (v or '').strip()
            if v and v not in names:
                names.append(v)
    return names


def translate(batch, key, model='deepseek-chat'):
    prompt = ('把下面这些伊斯兰圣训篇章名翻译成简洁中文（每行一条，格式：英文|中文）。'
              '用中国穆斯林通行译法，例如 Belief→信仰篇、Knowledge→知识篇、Ablutions (Wudu\')→小净篇、'
              'Prayers (Salat)→礼拜篇、Obligatory Charity Tax (Zakat)→天课篇、Fasting→斋戒篇、'
              'Hajj (Pilgrimage)→朝觐篇、Funeral→殡葬篇。只输出结果行，不要解释。\n\n' + '\n'.join(batch))
    body = json.dumps({
        'model': model,
        'messages': [{'role': 'user', 'content': prompt}],
        'temperature': 0,
        'max_tokens': 2000,
    }).encode('utf-8')
    req = urllib.request.Request('https://api.deepseek.com/chat/completions', data=body,
                                 headers={'Content-Type': 'application/json',
                                          'Authorization': 'Bearer ' + key})
    with urllib.request.urlopen(req, timeout=120) as r:
        d = json.loads(r.read().decode('utf-8'))
    txt = d['choices'][0]['message']['content']
    out = {}
    for line in txt.split('\n'):
        if '|' in line:
            a, b = line.split('|', 1)
            a, b = a.strip(), b.strip()
            if a and b:
                out[a] = b
    return out


def main():
    key = api_key()
    names = collect()
    mapping = {}
    if OUT.exists():
        try:
            mapping = json.loads(OUT.read_text(encoding='utf-8'))
        except Exception:
            mapping = {}
    todo = [n for n in names if n not in mapping]
    print(f'篇章名 {len(names)} 个，待翻译 {len(todo)}')
    B = 20
    for i in range(0, len(todo), B):
        batch = todo[i:i + B]
        for attempt in range(3):
            try:
                got = translate(batch, key)
                mapping.update(got)
                print(f'  批 {i//B+1}: +{len(got)}')
                break
            except Exception as e:
                print(f'  批 {i//B+1} 失败({attempt+1}): {e}')
                time.sleep(2 + attempt * 3)
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(mapping, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'✅ 已翻译 {len(mapping)}/{len(names)} -> {OUT}')


if __name__ == '__main__':
    main()
