#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一带一路 · 中阿合作 —— 真新闻爬虫（RSS 源，标准库实现）
每 1 小时由 crontab 调用；产出 data/beltroad.json
"""
import json, re, sys, time, urllib.request, xml.etree.ElementTree as ET
from pathlib import Path
from email.utils import parsedate_to_datetime

DIR = Path(__file__).resolve().parent.parent
OUT = DIR / 'data' / 'beltroad.json'
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36'

FEEDS = [
    ('中阿合作', 'https://news.google.com/rss/search?q=%E4%B8%AD%E9%98%BF%E5%90%88%E4%BD%9C+when:1d&hl=zh-CN&gl=CN&ceid=CN:zh-Hans'),
    ('中国·阿拉伯', 'https://news.google.com/rss/search?q=%E4%B8%AD%E5%9B%BD+%E9%98%BF%E6%8B%89%E4%BC%AF+when:2d&hl=zh-CN&gl=CN&ceid=CN:zh-Hans'),
    ('一带一路·阿拉伯', 'https://news.google.com/rss/search?q=%E4%B8%80%E5%B8%A6%E4%B8%80%E8%B7%AF+%E9%98%BF%E6%8B%89%E4%BC%AF+when:2d&hl=zh-CN&gl=CN&ceid=CN:zh-Hans'),
    ('中国·沙特', 'https://news.google.com/rss/search?q=%E4%B8%AD%E5%9B%BD+%E6%B2%99%E7%89%B9+when:2d&hl=zh-CN&gl=CN&ceid=CN:zh-Hans'),
    ('中国·阿联酋', 'https://news.google.com/rss/search?q=%E4%B8%AD%E5%9B%BD+%E9%98%BF%E8%81%94%E9%85%8B+when:2d&hl=zh-CN&gl=CN&ceid=CN:zh-Hans'),
    ('中国·埃及', 'https://news.google.com/rss/search?q=%E4%B8%AD%E5%9B%BD+%E5%9F%83%E5%8F%8A+when:2d&hl=zh-CN&gl=CN&ceid=CN:zh-Hans'),
    ('中东·中国', 'https://news.google.com/rss/search?q=%E4%B8%AD%E4%B8%9C+%E4%B8%AD%E5%9B%BD+when:2d&hl=zh-CN&gl=CN&ceid=CN:zh-Hans'),
    ('阿盟', 'https://news.google.com/rss/search?q=%E9%98%BF%E7%9B%9F+when:2d&hl=zh-CN&gl=CN&ceid=CN:zh-Hans'),
    ('中新网·滚动', 'https://www.chinanews.com.cn/rss/scroll-news.xml'),
]

# 中阿相关关键词
KW = ['阿拉伯', '中阿', '阿盟', '海湾', '沙特', '阿联酋', '迪拜', '埃及', '伊拉克', '卡塔尔',
      '科威特', '巴林', '阿曼', '也门', '约旦', '黎巴嫩', '叙利亚', '摩洛哥', '突尼斯',
      '阿尔及利亚', '利比亚', '苏丹', '吉布提', '毛里塔尼亚', '巴勒斯坦', '一带一路',
      '丝绸之路', '丝路', '中东', '利雅得', '阿布扎比', '开罗', '多哈']


def fetch(url, timeout=25):
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': '*/*'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def strip_tags(s):
    s = re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', s or '', flags=re.S)
    s = re.sub(r'<[^>]+>', '', s)
    s = re.sub(r'&nbsp;|&#160;', ' ', s)
    s = re.sub(r'&amp;', '&', s)
    return re.sub(r'\s+', ' ', s).strip()


def parse_feed(name, url):
    items = []
    try:
        raw = fetch(url)
    except Exception as e:
        print('  取源失败', name, e)
        return items
    try:
        root = ET.fromstring(raw)
    except Exception:
        try:
            root = ET.fromstring(raw.decode('utf-8', 'ignore'))
        except Exception as e:
            print('  解析失败', name, e)
            return items
    for it in root.iter('item'):
        def g(tag):
            e = it.find(tag)
            return (e.text or '') if e is not None else ''
        title = strip_tags(g('title'))
        title = re.sub(r'\s+-\s+[^-]{2,20}$', '', title)
        if len(title) < 8:
            continue
        link = (g('link') or '').strip()
        desc = strip_tags(g('description'))[:220]
        pub = (g('pubDate') or '').strip()
        ts = 0
        try:
            ts = int(parsedate_to_datetime(pub).timestamp())
        except Exception:
            ts = int(time.time())
        if not title:
            continue
        blob = title + ' ' + desc
        if any(k in blob for k in KW):
            items.append({'title': title, 'link': link, 'desc': desc,
                          'source': name, 'pub': pub, 'ts': ts})
    print('  %s → %d 条命中' % (name, len(items)))
    return items


def _mm(text, src='zh-CN', dst='ar'):
    """免费翻译兜底：MyMemory（无需密钥）"""
    try:
        u = ('https://api.mymemory.translated.net/get?q=' + urllib.parse.quote(text[:420]) +
             '&langpair=' + src + '%7C' + dst)
        req = urllib.request.Request(u, headers={'User-Agent': UA})
        with urllib.request.urlopen(req, timeout=25) as r:
            d = json.loads(r.read().decode('utf-8'))
        t = ((d.get('responseData') or {}).get('translatedText') or '').strip()
        if t and 'INVALID' not in t.upper():
            return t
    except Exception:
        pass
    return ''


def translate_fallback(news, cap=40):
    n = 0
    for x in news[:cap]:
        if x.get('ar'):
            continue
        t = _mm(x.get('title', ''))
        if t:
            x['ar'] = t
            n += 1
        time.sleep(0.35)
    print('  免费翻译兜底 %d 条' % n)
    return news


def _key():
    try:
        return (DIR / 'data' / 'ai_key.txt').read_text(encoding='utf-8').strip()
    except Exception:
        return ''


def translate_titles(news, cap=20):
    key = _key()
    if not key:
        print('  无 AI 密钥，跳过阿语翻译')
        return news
    todo = [x for x in news if not x.get('ar')][:cap]
    if not todo:
        print('  无需翻译（都已缓存）')
        return news
    NL = chr(10)
    lines = [str(i + 1) + '. ' + x['title'] for i, x in enumerate(todo)]
    prompt = ('把下面每条中文新闻标题翻译成地道的现代标准阿拉伯语（新闻传媒用语，简洁准确）。'
              '严格输出 JSON 数组，每项形如 {"i":序号,"ar":"阿语标题"}，不要任何多余文字、不要代码块。'
              + NL + NL + NL.join(lines))
    body = json.dumps({
        'model': 'deepseek-chat',
        'messages': [{'role': 'user', 'content': prompt}],
        'temperature': 0.3,
    }, ensure_ascii=False).encode('utf-8')
    try:
        req = urllib.request.Request('https://api.deepseek.com/chat/completions', data=body,
                                     headers={'Content-Type': 'application/json',
                                              'Authorization': 'Bearer ' + key})
        with urllib.request.urlopen(req, timeout=180) as r:
            d = json.loads(r.read().decode('utf-8'))
        txt = d['choices'][0]['message']['content'] or ''
    except Exception as e:
        print('  翻译调用失败', e)
        return news
    a, b = txt.find('['), txt.rfind(']')
    if a < 0 or b <= a:
        print('  翻译结果解析失败')
        return news
    try:
        arr = json.loads(txt[a:b + 1])
    except Exception as e:
        print('  翻译 JSON 解析失败', e)
        return news
    m = {}
    for it in arr:
        try:
            m[int(it.get('i'))] = str(it.get('ar') or '').strip()
        except Exception:
            pass
    n = 0
    for i, x in enumerate(todo, 1):
        if m.get(i):
            x['ar'] = m[i]
            n += 1
    print('  阿语翻译完成 %d 条' % n)
    return news


def main():
    allitems = []
    print('开始爬取中阿合作新闻…')
    for name, url in FEEDS:
        allitems += parse_feed(name, url)
    _now = int(time.time())
    allitems = [x for x in allitems if x.get('ts') and (_now - x['ts']) < 3 * 86400]
    # 去重（按标题）
    seen, uniq = set(), []
    for x in sorted(allitems, key=lambda t: -t['ts']):
        k = x['title'][:24]
        if k in seen:
            continue
        seen.add(k)
        uniq.append(x)
    uniq = uniq[:40]
    out = {'updated': time.strftime('%Y-%m-%d %H:%M'), 'count': len(uniq), 'items': uniq}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    old = {}
    try:
        old = json.load(open(OUT, encoding='utf-8'))
    except Exception:
        pass
    # 保留已有阿语翻译
    tr = {}
    for x in (old.get('items') or []):
        if x.get('ar'):
            tr[x['title'][:24]] = x['ar']
    for x in uniq:
        if x['title'][:24] in tr:
            x['ar'] = tr[x['title'][:24]]
    translate_titles(uniq, cap=20)
    translate_fallback(uniq, cap=40)
    out = {'updated': time.strftime('%Y-%m-%d %H:%M'), 'count': len(uniq), 'items': uniq}
    json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('写入', OUT, '共', len(uniq), '条')


if __name__ == '__main__':
    main()
