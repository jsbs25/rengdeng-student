#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""批量下载公版阿拉伯语书籍（扩充图书馆）"""
import json, re, time, urllib.request, urllib.parse
from pathlib import Path

DIR = Path(__file__).parent
UA = {'User-Agent': 'Mozilla/5.0 (ArabicLearning/1.0)'}

def api(params, retries=4):
    url = 'https://ar.wikisource.org/w/api.php?' + urllib.parse.urlencode(params)
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=45) as r:
                return json.loads(r.read())
        except Exception:
            time.sleep(4 + i * 3)
    return None

def fetch_wikitext(page):
    d = api({'action': 'parse', 'page': page, 'format': 'json', 'prop': 'wikitext'})
    return d['parse']['wikitext']['*'] if d else None

def clean_text(wt):
    t = wt
    t = re.sub(r'\{\{[\s\S]*?\}\}', '', t)
    t = re.sub(r'\[\[([^\]|]*\|)?([^\]]*)\]\]', r'\2', t)
    t = re.sub(r"'''?", '', t)
    t = re.sub(r'<[^>]+>', '', t)
    t = re.sub(r'^[ \t]*[-=#*:]+\s*', '', t, flags=re.M)
    # 删除含 == 的标题行
    t = re.sub(r'^[ \t]*[^=\n]{0,60}==+[^=\n]*[ \t]*$', '', t, flags=re.M)
    t = re.sub(r'[ \t]+', ' ', t)
    t = re.sub(r'\n{3,}', '\n\n', t)
    return t.strip()

def get_subpages(book_page, limit=500):
    pages, cont = [], None
    while True:
        params = {'action': 'query', 'titles': book_page, 'prop': 'links',
                  'plnamespace': '0', 'pllimit': '500', 'format': 'json'}
        if cont:
            params['plcontinue'] = cont
        d = api(params)
        if not d:
            break
        for pid, page in d['query']['pages'].items():
            for l in page.get('links', []):
                title = l['title']
                if title.startswith(book_page + '/'):
                    pages.append(title.split('/', 1)[1])
        if 'continue' in d and 'plcontinue' in d['continue']:
            cont = d['continue']['plcontinue']
            time.sleep(1.2)
        else:
            break
        if len(pages) > limit:
            break
    seen, out = set(), []
    for p in pages:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out

def download_book(book_page, title, author, intro_cn, intro_en, max_chapters=12, min_len=150):
    print(f'📖 {title}')
    try:
        slugs = get_subpages(book_page)
    except Exception as e:
        print(f'   ✗ 页面查询失败: {e}')
        return None
    if not slugs:
        # 可能是单页书籍
        try:
            wt = fetch_wikitext(book_page)
            if wt and len(wt) > 3000:
                body = clean_text(wt)
                if len(body) > 2000:
                    # 按小节切分
                    sections = re.split(r'\n==\s*([^=]+?)\s*==\n', body)
                    chs = []
                    if sections and len(sections[0].strip()) > 100:
                        chs.append({'t': 'مقدمة（引言）', 'body': sections[0].strip()})
                    for i in range(1, len(sections) - 1, 2):
                        b = sections[i + 1].strip()
                        if len(b) > 200:
                            chs.append({'t': sections[i].strip(), 'body': b})
                    if not chs:
                        chs.append({'t': 'الكتاب（全书）', 'body': body})
                    print(f'   ✓ 单页书，{len(chs)} 节')
                    return {'title': title, 'author': author, 'intro_cn': intro_cn, 'intro_en': intro_en, 'chapters': chs}
        except Exception as e:
            print(f'   ✗ {e}')
        return None
    chapters = []
    for slug in slugs[:max_chapters]:
        try:
            wt = fetch_wikitext(f'{book_page}/{slug}')
            body = clean_text(wt) if wt else ''
            if len(body) > min_len:
                chapters.append({'t': slug, 'body': body})
                print(f'   ✓ {slug} ({len(body)}字)')
            else:
                print(f'   - 跳过: {slug}')
        except Exception as e:
            print(f'   ✗ {slug}: {e}')
        time.sleep(1.2)
    if not chapters:
        return None
    print(f'   ✅ {len(chapters)} 章')
    return {'title': title, 'author': author, 'intro_cn': intro_cn, 'intro_en': intro_en, 'chapters': chapters}

def main():
    catalog = [
        # (页面名, 标题, 作者, 中文简介, 英文简介, 章节数上限)
        ('مقامات الحريري', 'مقامات الحريري（哈里里玛卡梅）', 'الحريري（哈里里）',
         '11世纪阿拉伯文学杰作，以韵文散文讲述流浪才子艾布·扎伊德的奇遇，语言精妙、双关机锋，被誉为"韵文圣经"。',
         'The Maqamat of al-Hariri, a masterpiece of rhymed prose featuring the roguish Abu Zayd.', 12),
        ('نهج البلاغة', 'نهج البلاغة（雄辩之道）', 'الشريف الرضي（谢里夫·拉迪）',
         '伊斯兰经典文集，汇集阿里·本·阿比·塔利卜的演讲、书信与格言，阿拉伯散文的巅峰之作。',
         'Nahj al-Balagha, the peak of Arabic eloquence: sermons, letters and sayings of Ali ibn Abi Talib.', 12),
        ('البخلاء', 'البخلاء（吝啬鬼）', 'الجاحظ（贾希兹）',
         '阿拔斯时期文学大师贾希兹的幽默讽刺集，刻画形形色色的守财奴，笔调机智辛辣。',
         'The Book of Misers by al-Jahiz, a witty satire of the avaricious.', 12),
        ('رسالة الغفران', 'رسالة الغفران（宽恕书）', 'أبو العلاء المعري（阿布·阿拉·马阿里）',
         '马阿里的奇幻之作：诗人梦中游历天堂地狱，与历代诗人文豪对话，阿拉伯文学的奇书。',
         'The Epistle of Forgiveness by al-Ma\'arri, a visionary journey through heaven and hell.', 10),
        ('ألف ليلة وليلة', 'ألف ليلة وليلة（一千零一夜·选）', 'ألف ليلة وليلة（佚名）',
         '世界文学瑰宝：山鲁佐德夜夜讲故事以化解杀机，阿里巴巴、阿拉丁、渔夫与精灵等故事皆出此典。',
         'One Thousand and One Nights: Scheherazade\'s tales of wonder.', 10),
    ]
    books = json.load(open(DIR / 'data' / 'books.json', encoding='utf-8')) if (DIR / 'data' / 'books.json').exists() else []
    have = {b['title'] for b in books}
    for page, title, author, ic, ie, mx in catalog:
        if title in have:
            print(f'⏭ 已有: {title}')
            continue
        time.sleep(2)
        b = download_book(page, title, author, ic, ie, max_chapters=mx)
        if b and len(b['chapters']) >= 3:
            books.append(b)
            json.dump(books, open(DIR / 'data' / 'books.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
            print(f'💾 已保存: {title} ({len(b["chapters"])} 章)，累计 {len(books)} 本')
    total_ch = sum(len(b['chapters']) for b in books)
    print(f'✅ 全部完成: {len(books)} 本书 / {total_ch} 章')
    json.dump(books, open(DIR / 'data' / 'books.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

if __name__ == '__main__':
    main()
