#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从阿拉伯语维基文库下载公版书籍 → data/books.json（v2：links API + 延时重试）"""
import json, re, sys, time, urllib.request, urllib.parse
from pathlib import Path

DIR = Path(__file__).parent
UA = {'User-Agent': 'Mozilla/5.0 (ArabicLearning/1.0)'}

def api_get(params, retries=4):
    url = 'https://ar.wikisource.org/w/api.php?' + urllib.parse.urlencode(params)
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read())
        except Exception as e:
            if i == retries - 1:
                raise
            time.sleep(3 + i * 2)

def fetch_wikitext(page):
    d = api_get({'action': 'parse', 'page': page, 'format': 'json', 'prop': 'wikitext'})
    return d['parse']['wikitext']['*']

def get_chapter_pages(book_page):
    """用 links API 获取子页面"""
    pages = []
    cont = None
    while True:
        params = {'action': 'query', 'titles': book_page, 'prop': 'links',
                  'plnamespace': '0', 'pllimit': '500', 'format': 'json'}
        if cont:
            params['plcontinue'] = cont
        d = api_get(params)
        q = d['query']['pages']
        for pid, page in q.items():
            for l in page.get('links', []):
                title = l['title']
                if title.startswith(book_page + '/'):
                    pages.append(title.split('/', 1)[1])
        if 'continue' in d and 'plcontinue' in d['continue']:
            cont = d['continue']['plcontinue']
            time.sleep(1.2)
        else:
            break
    # 去重保序
    seen, out = set(), []
    for p in pages:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out

def clean_text(wt):
    t = wt
    t = re.sub(r'\{\{[\s\S]*?\}\}', '', t)
    t = re.sub(r'\[\[([^\]|]*\|)?([^\]]*)\]\]', r'\2', t)
    t = re.sub(r"'''?", '', t)
    t = re.sub(r'<[^>]+>', '', t)
    t = re.sub(r'^[ \t]*[-=#*]+\s*', '', t, flags=re.M)
    t = re.sub(r'^[ \t]*:[ \t]*', '', t, flags=re.M)
    t = re.sub(r'[ \t]+', ' ', t)
    t = re.sub(r'\n{3,}', '\n\n', t)
    return t.strip()

def download_book(book_page, title, author, intro_cn, intro_en, max_chapters=14):
    print(f'📖 抓取《{title}》...')
    slugs = get_chapter_pages(book_page)
    print(f'   子页面 {len(slugs)} 个')
    chapters = []
    for slug in slugs[:max_chapters]:
        try:
            wt = fetch_wikitext(f'{book_page}/{slug}')
            body = clean_text(wt)
            if len(body) > 150:
                chapters.append({'t': slug, 'body': body})
                print(f'   ✓ {slug} ({len(body)}字)')
            else:
                print(f'   - 跳过(过短): {slug}')
        except Exception as e:
            print(f'   ✗ {slug}: {e}')
        time.sleep(1.2)
    return {
        'title': title, 'author': author,
        'intro_cn': intro_cn, 'intro_en': intro_en,
        'chapters': chapters,
    }

def main():
    books = []
    books.append(download_book(
        'كليلة ودمنة',
        'كليلة ودمنة（卡里来和笛木乃）',
        'ابن المقفع（伊本·穆加法）',
        '阿拉伯古典寓言集，通过狮子、公牛、狐狸等动物的故事讲述治国与处世智慧，源自印度《五卷书》，公元8世纪由伊本·穆加法译为阿拉伯语，是阿拉伯散文的奠基之作。',
        'Kalila wa-Dimna, the classic Arabic collection of animal fables adapted from the Indian Panchatantra by Ibn al-Muqaffa.',
        max_chapters=14,
    ))
    json.dump(books, open(DIR / 'data' / 'books.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    total = sum(len(b['chapters']) for b in books)
    print(f'✅ 完成: {len(books)} 本书 / {total} 章 → data/books.json')

if __name__ == '__main__':
    main()
