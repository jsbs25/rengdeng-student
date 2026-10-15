#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""六大部圣训全集构建器。

数据源：fawazahmed0/hadith-api（公开、CDN 直取，editions: ara-bukhari 等）
产出：data/hadith/index.json + data/hadith/<key>.json
用法：python3 harvest/build_hadith.py
"""
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'data' / 'hadith'
CDN = 'https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/ara-%s.min.json'

BOOKS = [
    ('bukhari', 'صحيح البخاري', '布哈里圣训实录', 'Sahih al-Bukhari'),
    ('muslim', 'صحيح مسلم', '穆斯林圣训实录', 'Sahih Muslim'),
    ('abudawud', 'سنن أبي داود', '艾布·达乌德圣训集', 'Sunan Abu Dawud'),
    ('tirmidhi', 'جامع الترمذي', '提尔密济圣训集', 'Jami at-Tirmidhi'),
    ('nasai', 'سنن النسائي', '奈萨仪圣训集', 'Sunan an-Nasai'),
    ('ibnmajah', 'سنن ابن ماجه', '伊本·马哲圣训集', 'Sunan Ibn Majah'),
]


def fetch(url, dst):
    if dst.exists() and dst.stat().st_size > 1000:
        return
    print('  ↓', url)
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=180) as r, dst.open('wb') as f:
        f.write(r.read())


def main():
    raw = ROOT / 'harvest' / 'raw'
    raw.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    index = {'books': [], 'total': 0}

    for key, ar, cn, en in BOOKS:
        fp = raw / f'hadith_{key}.json'
        fetch(CDN % key, fp)
        d = json.loads(fp.read_text(encoding='utf-8'))
        meta = d.get('metadata', {})
        CN = {}
        try:
            CN = json.loads((OUT / 'sections.json').read_text(encoding='utf-8'))
        except Exception:
            CN = {}
        sections = {}
        for k, v in (meta.get('sections') or {}).items():
            v = (v or '').strip()
            if v:
                sections[str(k)] = {'en': v, 'cn': CN.get(v, v)}
        rows = []
        for h in d.get('hadiths', []):
            txt = (h.get('text') or '').strip()
            if not txt:
                continue
            sec = h.get('reference', {}).get('book')
            rows.append({'n': h.get('hadithnumber'), 'ar': txt, 's': str(sec) if sec is not None else ''})
        payload = {'key': key, 'name_ar': ar, 'name_cn': cn, 'name_en': en, 'sections': sections, 'hadiths': rows}
        (OUT / f'{key}.json').write_text(json.dumps(payload, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
        size = (OUT / f'{key}.json').stat().st_size
        index['books'].append({'key': key, 'ar': ar, 'cn': cn, 'en': en, 'n': len(rows), 'mb': round(size / 1048576, 1)})
        index['total'] += len(rows)
        print(f'  ✅ {key:<10} {len(rows):>6} 段  {size/1048576:.1f} MB')

    index['books'].sort(key=lambda b: b['n'], reverse=True)
    (OUT / 'index.json').write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"\n六大部合计: {index['total']} 段")
    for b in index['books']:
        print(f"   {b['cn']:<18} {b['n']:>6}")


if __name__ == '__main__':
    main()
