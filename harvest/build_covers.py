#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""真书封爬虫（Open Library）→ data/covers/<slug>.jpg
产出 data/covers.json : {书名: 图片相对路径}
"""
import json, re, time, unicodedata, urllib.parse, urllib.request
from pathlib import Path

DIR = Path(__file__).resolve().parent.parent
COV = DIR / 'data' / 'covers'
OUT = DIR / 'data' / 'covers.json'
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36'

# 书名 → 候选搜索词
WANT = [
    ('三国演义', ['三国演义 罗贯中', '三国演义', 'Romance of the Three Kingdoms']),
    ('水浒传', ['水浒传 施耐庵', '水浒传', 'Water Margin']),
    ('西游记', ['西游记 吴承恩', '西游记', 'Journey to the West']),
    ('红楼梦', ['红楼梦 曹雪芹', '红楼梦', 'Dream of the Red Chamber']),
    ('聊斋志异', ['聊斋志异', '聊斋志异 蒲松龄', 'Strange Tales from a Chinese Studio']),
    ('封神演义', ['封神演义', 'Investiture of the Gods']),
    ('隋唐演义', ['隋唐演义']),
    ('儒林外史', ['儒林外史', 'The Scholars']),
    ('镜花缘', ['镜花缘']),
    ('东周列国志', ['东周列国志']),
    ('三字经', ['三字经', 'Three Character Classic']),
    ('孙子兵法', ['孙子兵法', 'The Art of War Sun Tzu']),
    ('史记', ['史记 司马迁', 'Records of the Grand Historian']),
    ('论语', ['论语', 'The Analects Confucius']),
    ('صحيح البخاري', ['Sahih al-Bukhari', 'صحيح البخاري']),
    ('صحيح مسلم', ['Sahih Muslim', 'صحيح مسلم']),
    ('سنن أبي داود', ['Sunan Abu Dawud']),
    ('جامع الترمذي', ['Jami at-Tirmidhi', 'Sunan al-Tirmidhi']),
    ('سنن النسائي', ['Sunan an-Nasai']),
    ('سنن ابن ماجه', ['Sunan Ibn Majah']),
    ('القرآن الكريم', ['The Holy Quran', 'Quran']),
]


def get(url, timeout=14, binary=False):
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': '*/*'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read()
    return raw if binary else raw.decode('utf-8', 'ignore')


def slug(s):
    s = unicodedata.normalize('NFKC', s)
    return (re.sub(r'[^0-9A-Za-z\u0600-\u06FF\u4e00-\u9fff]+', '_', s).strip('_'))[:40] or 'book'


def find_cover(queries):
    for q in queries:
        url = 'https://openlibrary.org/search.json?q=' + urllib.parse.quote(q, safe='') + \
              '&limit=6&fields=title,author_name,cover_i,first_publish_year'
        try:
            d = json.loads(get(url))
        except Exception as e:
            print('    搜索失败', q[:20], e)
            time.sleep(0.5)
            continue
        for x in (d.get('docs') or []):
            if x.get('cover_i'):
                return x['cover_i']
        time.sleep(0.4)
    return None


def main():
    COV.mkdir(parents=True, exist_ok=True)
    res = {}
    try:
        res = json.load(open(OUT, encoding='utf-8'))
    except Exception:
        res = {}
    # 清掉指向不存在文件的旧记录
    res = {k: v for k, v in res.items() if (DIR / v).exists()}
    ok = miss = 0
    for title, queries in WANT:
        if title in res and (DIR / res[title]).exists():
            print('  已有', title, (DIR / res[title]).stat().st_size, 'B')
            continue
        cid = find_cover(queries)
        if not cid:
            print('  ✗ 未找到', title)
            miss += 1
            continue
        fn = COV / (slug(title) + '.jpg')
        try:
            data = get('https://covers.openlibrary.org/b/id/%s-L.jpg' % cid, binary=True)
        except Exception as e:
            print('  ✗ 下载失败', title, e)
            miss += 1
            continue
        if not data or len(data) < 3000:
            print('  ✗ 图太小', title, len(data or b''))
            miss += 1
            continue
        fn.write_bytes(data)
        res[title] = 'data/covers/' + fn.name
        ok += 1
        print('  ✓', title, len(data), 'B')
        time.sleep(0.6)
    json.dump(res, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('完成：新增 %d 张，未找到 %d 张，共 %d 条' % (ok, miss, len(res)))


if __name__ == '__main__':
    main()
