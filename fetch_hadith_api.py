#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""批量收录圣训（hadeethenc 免费 API，中文翻译 + 出处 + 注解）"""
import json, os, sys, time, urllib.request, urllib.parse
from pathlib import Path

DIR = Path(__file__).parent
OUT = DIR / 'data' / 'hadith_api.json'
API = 'https://hadeethenc.com/api/v1/hadeeths/list/'

def fetch(url, retries=3):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read())
        except Exception as e:
            print(f'  重试 {attempt+1}: {e}')
            time.sleep(3)
    return None

# 出处 → 六大部映射（从 attribution 文本解析）
def map_book(attr):
    a = attr or ''
    if '布哈里' in a and '穆斯林' in a:
        return 'bukhari'  # 布哈里与穆斯林（教规学家认可的两位）
    if '布哈里' in a:
        return 'bukhari'
    if '穆斯林' in a:
        return 'muslim'
    if '铁密济' in a or '提尔米济' in a:
        return 'tirmidhi'
    if '艾布·达乌德' in a or '达伍德' in a or '达乌德' in a:
        return 'abudawud'
    if '奈萨仪' in a or '奈萨伊' in a:
        return 'nasai'
    if '伊本·马哲' in a or '伊本·马贾' in a:
        return 'ibnmajah'
    return 'other'

def main():
    out_file = OUT
    all_data = []
    if out_file.exists():
        all_data = json.load(open(out_file, encoding='utf-8'))
    seen_ids = {d.get('id') for d in all_data}
    total_new = 0
    # 主题分类 1-50 逐类分页拉取
    for cid in range(1, 51):
        page = 1
        while page <= 10:  # 每类最多 10 页（1000 则）
            url = f'{API}?language=zh&category_id={cid}&page={page}&per_page=100'
            d = fetch(url)
            if not d:
                break
            data = d.get('data', [])
            if not data:
                break
            new = 0
            for h in data:
                hid = h.get('id')
                if hid in seen_ids:
                    continue
                seen_ids.add(hid)
                book = map_book(h.get('attribution', ''))
                all_data.append({
                    'id': hid,
                    'title': h.get('title', ''),
                    'cn': h.get('hadeeth', ''),
                    'attribution': h.get('attribution', ''),
                    'grade': h.get('grade', ''),
                    'explanation': h.get('explanation', ''),
                    'hints': h.get('hints', []),
                    'book': book,
                    'source': 'hadeethenc',
                })
                new += 1
            total_new += new
            print(f'cat {cid} page {page}: +{new}（累计 {len(all_data)}）', flush=True)
            if len(data) < 100:
                break
            page += 1
            time.sleep(0.5)
        json.dump(all_data, open(out_file, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)  # 每类即存
        time.sleep(0.5)
    json.dump(all_data, open(out_file, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'完成：{len(all_data)} 则（新增 {total_new}）')

if __name__ == '__main__':
    main()
