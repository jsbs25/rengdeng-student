# -*- coding: utf-8 -*-
"""爬取阿拉伯语听力视频（YouTube 搜索 → 分类目录 data/videos.json）"""
import json, os, re, time, urllib.parse, urllib.request

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'videos.json')

CATS = [
    {'id': 'basic',   'name': '入门基础',  'icon': '📗', 'q': ['تعلم العربية للمبتدئين', 'تعلم اللغة العربية الدرس الأول', '阿拉伯语 入门 教学']},
    {'id': 'talk',    'name': '日常会话',  'icon': '🗣', 'q': ['محادثة عربية يومية', 'عبارات عربية شائعة', '阿拉伯语 日常对话 教学']},
    {'id': 'quran',   'name': '古兰经诵读', 'icon': '🕌', 'q': ['تلاوة القرآن الكريم', 'سورة البقرة تلاوة', 'quran recitation beautiful']},
    {'id': 'news',    'name': '新闻听力',  'icon': '📰', 'q': ['أخبار بالعربية الفصحى', 'نشرة الأخبار العربية', 'Arabic news listening']},
    {'id': 'kids',    'name': '儿童动画',  'icon': '🧸', 'q': ['قصص الأطفال بالعربية', 'كرتون عربي تعليمي', 'Arabic cartoon for kids']},
    {'id': 'hadith',  'name': '圣训讲座',  'icon': '📜', 'q': ['شرح الأحاديث النبوية', 'دروس الحديث الشريف', '圣训 讲解 中文']},
    {'id': 'grammar', 'name': '阿语语法',  'icon': '✏️', 'q': ['قواعد اللغة العربية', 'النحو العربي للمبتدئين', '阿拉伯语 语法 教学']},
    {'id': 'listen',  'name': '听力训练',  'icon': '🎧', 'q': ['Arabic listening practice', 'استماع العربية للمبتدئين', '阿拉伯语 听力 练习']},
]

UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'

def fetch(u):
    req = urllib.request.Request(u, headers={'User-Agent': UA, 'Accept-Language': 'ar,zh-CN;q=0.9,en;q=0.8'})
    return urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'ignore')

def walk(o, key):
    if isinstance(o, dict):
        if key in o:
            yield o[key]
        for v in o.values():
            for x in walk(v, key):
                yield x
    elif isinstance(o, list):
        for v in o:
            for x in walk(v, key):
                yield x

def search(q, limit=12):
    h = fetch('https://www.youtube.com/results?search_query=' + urllib.parse.quote(q))
    m = re.search(r'var ytInitialData\s*=\s*(\{.*?\});</script>', h, re.S)
    if not m:
        return []
    try:
        data = json.loads(m.group(1))
    except Exception:
        return []
    out = []
    for r in walk(data, 'videoRenderer'):
        try:
            vid = r.get('videoId')
            if not vid:
                continue
            t = ''.join(x.get('text', '') for x in (r.get('title', {}).get('runs') or [])) or r.get('title', {}).get('simpleText', '')
            ch = ''.join(x.get('text', '') for x in ((r.get('ownerText') or r.get('longBylineText') or {}).get('runs') or []))
            dur = (r.get('lengthText') or {}).get('simpleText', '')
            views = (r.get('viewCountText') or {}).get('simpleText', '')
            if not t:
                continue
            out.append({'id': vid, 't': t.strip(), 'ch': ch.strip(), 'dur': dur, 'views': views})
        except Exception:
            continue
        if len(out) >= limit:
            break
    return out

def main():
    seen, videos = set(), []
    for c in CATS:
        got = 0
        for q in c['q']:
            for v in search(q, 12):
                if v['id'] in seen:
                    continue
                seen.add(v['id'])
                v['cat'] = c['id']
                videos.append(v)
                got += 1
                if got >= 14:
                    break
            if got >= 14:
                break
            time.sleep(1)
        print('%-8s %-10s 抓取 %d 条（累计 %d）' % (c['id'], c['name'], got, len(videos)))
    data = {'cats': [{k: c[k] for k in ('id', 'name', 'icon')} for c in CATS],
            'videos': videos, 'updated': time.strftime('%Y-%m-%d %H:%M')}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(data, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('✅ 写入', OUT, '共', len(videos), '个视频')

if __name__ == '__main__':
    main()
