#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""爬取完整六大部圣训 v2（fawazahmed0/hadith-api：每段一个文件）
阿拉伯语原文 + 英文翻译，约 3 万段。
"""
import json, time, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = 'https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions'
BOOKS = ['bukhari', 'muslim', 'abudawud', 'tirmidhi', 'nasai', 'ibnmajah']
BOOK_CN = {
    'bukhari': '布哈里圣训', 'muslim': '穆斯林圣训', 'abudawud': '艾布达伍德圣训',
    'tirmidhi': '提尔密济圣训', 'nasai': '奈萨仪圣训', 'ibnmajah': '伊本马哲圣训',
}
OUT = 'data/hadith6.json'

def fetch_one(lang, book, num):
    url = f'{BASE}/{lang}-{book}/{num}.json'
    for i in range(3):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=20) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            time.sleep(1.5)
        except Exception:
            time.sleep(1.5)
    return None

INFO_CACHE = 'data/hadith_info.json'

def load_section_map(book):
    """从 info.json 拿 段号→章节名 映射（本地缓存 + 重试）"""
    info = None
    try:
        info = json.load(open(INFO_CACHE, encoding='utf-8'))
    except Exception:
        pass
    if info is None:
        for i in range(4):
            try:
                req = urllib.request.Request('https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/info.json', headers={'User-Agent': 'Mozilla/5.0'})
                info = json.loads(urllib.request.urlopen(req, timeout=60).read())
                json.dump(info, open(INFO_CACHE, 'w', encoding='utf-8'), ensure_ascii=False)
                print(f'✅ info.json 已缓存（{len(info)} 部书）', flush=True)
                break
            except Exception as e:
                print(f'  info.json 重试 {i+1}: {e}', flush=True)
                time.sleep(3)
    try:
        meta = info.get(book, {}).get('metadata', {})
        sec_names = meta.get('sections', {})
        sd = meta.get('section_details') or meta.get('section_detail') or {}
        num2sec = {}
        for sec_id, d in sd.items():
            first = d.get('hadithnumber_first', 0)
            last = d.get('hadithnumber_last', 0)
            for n in range(first, last + 1):
                num2sec[n] = (sec_id, sec_names.get(str(sec_id), ''))
        return num2sec, meta.get('last_hadithnumber', 0)
    except Exception as e:
        print('section map 失败:', e)
        return {}, 0

def main():
    print('=' * 50)
    print('🕌 六大部圣训全量爬取 v2（每段一文件，约 3 万段）')
    print('=' * 50)
    results = {}
    for book in BOOKS:
        num2sec, last_num = load_section_map(book)
        if not num2sec or not last_num:
            # 兜底：探测段数（每 100 段试一次，找到最后存在的段）
            print(f'⚠️ {book} 无映射，改为探测段数...', flush=True)
            lo, hi = 1, 1
            while fetch_one('ara', book, hi) is not None:
                lo, hi = hi, hi * 2
                if hi > 20000: break
            print(f'  {book} 探测区间 {lo}-{hi}', flush=True)
            last_num = lo
            num2sec = {n: ('', '') for n in range(1, lo + 1)}
        max_num = int(last_num)
        print(f'📖 {BOOK_CN[book]}: 共 {max_num} 段', flush=True)
        done = 0
        with ThreadPoolExecutor(max_workers=8) as ex:
            futs = {}
            # 阿语
            for n in range(1, max_num + 1):
                futs[ex.submit(fetch_one, 'ara', book, n)] = ('ara', book, n)
            # 英文
            for n in range(1, max_num + 1):
                futs[ex.submit(fetch_one, 'eng', book, n)] = ('eng', book, n)
            for f in as_completed(futs):
                lang, bk, n = futs[f]
                d = f.result()
                if d:
                    key = f'{bk}|{n}'
                    rec = results.setdefault(key, {'book': bk, 'book_cn': BOOK_CN[bk], 'number': n, 'ar': '', 'en': ''})
                    sec = num2sec.get(n, ('', ''))
                    rec['section'] = sec[0]
                    rec['section_name'] = sec[1]
                    txt = (d.get('hadiths') or [{}])[0].get('text', '')
                    if lang == 'ara':
                        rec['ar'] = txt
                    else:
                        rec['en'] = txt
                done += 1
                if done % 500 == 0:
                    print(f'  {book}: 处理 {done}/{max_num*2}，累计 {len(results)} 条', flush=True)
        print(f'✅ {BOOK_CN[book]} 完成，当前累计 {len(results)} 条', flush=True)
    final = list(results.values())
    final.sort(key=lambda x: (BOOKS.index(x['book']), x['number']))
    json.dump(final, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False)
    print(f'🎉 全部完成！共 {len(final)} 条 → {OUT}')

if __name__ == '__main__':
    main()
