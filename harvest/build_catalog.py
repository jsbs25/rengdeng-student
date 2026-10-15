#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""伊斯兰书籍/经著目录库构建器。

数据源（全部为公开可下载的批量数据，不是逐页爬取）：
  1. Shamela（المكتبة الشاملة）书目元数据 CSV —— 含书名/作者/分类/出版社/页数
  2. OpenITI RELEASE 元数据 TSV —— 约 1.4 万部阿拉伯语文本（含作者/年代/标签）

产出：data/islamic_catalog.json（统一结构 + 分类统计）
用法：python3 harvest/build_catalog.py
"""
import csv
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / 'harvest' / 'raw'
OUT = ROOT / 'data' / 'islamic_catalog.json'

AR_DIAC = re.compile(r'[\u0610-\u061A\u064B-\u0652\u0670\u06D6-\u06ED\u0640]')


def norm(s):
    if not s:
        return ''
    s = unicodedata.normalize('NFKC', str(s))
    s = AR_DIAC.sub('', s)
    s = re.sub(r'[إأآا]', 'ا', s)
    s = re.sub(r'[ىي]', 'ي', s)
    s = re.sub(r'[ةه]', 'ه', s)
    s = re.sub(r'\s+', ' ', s)
    return s.strip()


def clean(s):
    if s is None:
        return ''
    s = str(s).strip()
    return '' if s.lower() in ('null', 'nan', 'none') else s


# 归类：把各源杂乱分类归并到统一的伊斯兰学科分类
CANON = [
    ('حديث', '圣训 / 圣训学', 'الحديث وعلومه'),
    ('سنة', '圣训 / 圣训学', 'الحديث وعلومه'),
    ('تخريج', '圣训 / 圣训学', 'الحديث وعلومه'),
    ('أجزاء حديثية', '圣训 / 圣训学', 'الحديث وعلومه'),
    ('علل', '圣训 / 圣训学', 'الحديث وعلومه'),
    ('تفسير', '经注 / 古兰学', 'التفسير وعلوم القرآن'),
    ('قرآن', '经注 / 古兰学', 'التفسير وعلوم القرآن'),
    ('قراءات', '经注 / 古兰学', 'التفسير وعلوم القرآن'),
    ('تجويد', '经注 / 古兰学', 'التفسير وعلوم القرآن'),
    ('عقيدة', '教义 / 认主学', 'العقيدة'),
    ('توحيد', '教义 / 认主学', 'العقيدة'),
    ('أصول الدين', '教义 / 认主学', 'العقيدة'),
    ('فرق', '教派 / 学派', 'الفرق والردود'),
    ('ردود', '教派 / 学派', 'الفرق والردود'),
    ('ملل', '教派 / 学派', 'الفرق والردود'),
    ('أصول الفقه', '法源学', 'أصول الفقه'),
    ('قواعد فقهية', '法源学', 'أصول الفقه'),
    ('فقه', '教法 / 法学', 'الفقه وأصوله'),
    ('فتاوى', '教法判例', 'الفتاوى'),
    ('فرائض', '遗产与遗嘱', 'الفرائض والوصايا'),
    ('وصايا', '遗产与遗嘱', 'الفرائض والوصايا'),
    ('قضاء', '教法司法', 'السياسة الشرعية والقضاء'),
    ('سياسة شرعية', '教法司法', 'السياسة الشرعية والقضاء'),
    ('سيرة', '先知传记', 'السيرة النبوية'),
    ('تراجم', '人物志 / 传记', 'التاريخ والتراجم'),
    ('طبقات', '人物志 / 传记', 'التاريخ والتراجم'),
    ('أنساب', '谱系学', 'الأنساب'),
    ('تاريخ', '历史', 'التاريخ'),
    ('بلدان', '地理 / 游记', 'البلدان والرحلات'),
    ('رحلات', '地理 / 游记', 'البلدان والرحلات'),
    ('لغة', '阿拉伯语 / 语言学', 'اللغة العربية'),
    ('نحو', '语法学', 'النحو والصرف'),
    ('صرف', '语法学', 'النحو والصرف'),
    ('معاجم', '词典 / 辞书', 'الغريب والمعاجم'),
    ('غريب', '词典 / 辞书', 'الغريب والمعاجم'),
    ('بلاغة', '修辞学', 'البلاغة'),
    ('عروض', '韵律学', 'العروض والقوافي'),
    ('قوافي', '韵律学', 'العروض والقوافي'),
    ('أدب', '文学 / 诗文', 'الأدب'),
    ('شعر', '诗歌', 'الشعر ودواوينه'),
    ('دواوين', '诗歌', 'الشعر ودواوينه'),
    ('رقائق', '苦修 / 劝诫', 'الرقائق والآداب'),
    ('زهد', '苦修 / 劝诫', 'الرقائق والآداب'),
    ('آداب', '礼仪 / 修养', 'الآداب والأذكار'),
    ('أذكار', '记主与祈祷', 'الأذكار'),
    ('خطب', '演讲 / 劝词', 'الأخلاق والآداب'),
    ('تصوف', '苏非 / 修行', 'التصوف والزهد'),
    ('تزكية', '苏非 / 修行', 'التصوف والزهد'),
    ('أخلاق', '伦理 / 修养', 'الأخلاق والآداب'),
    ('دعوة', '宣教 / 劝化', 'الدعوة والفكر'),
    ('فكر', '思想', 'الدعوة والفكر'),
    ('منطق', '逻辑学', 'الفلسفة والمنطق'),
    ('فلسفة', '哲学', 'الفلسفة والمنطق'),
    ('طب', '医学', 'الطب'),
    ('فلك', '天文', 'الفلك'),
    ('رياضيات', '数学', 'الرياضيات'),
    ('فهارس', '书目 / 索引', 'الفهارس'),
    ('جوامع', '文集 / 期刊', 'الجوامع والمجلات'),
    ('مجلات', '文集 / 期刊', 'الجوامع والمجلات'),
]


def _tag_cats(tags):
    """OpenITI 的标签里有 Shamela@التفسير 这种分类信息，抽出来。"""
    out = []
    for t in (tags or '').split('::'):
        t = t.strip()
        if '@' in t:
            out.append(t.split('@', 1)[1])
    return out


def canon_cat(*cands):
    joined = ' '.join(c for c in cands if c)
    for key, cn, ar in CANON:
        if key in joined:
            return cn, ar
    return '其他 / 综合', 'متنوع'


def load_shamela():
    fp = RAW / 'shamela_books_info.csv'
    if not fp.exists():
        return []
    out = []
    with fp.open(encoding='utf-8', newline='') as f:
        for r in csv.DictReader(f):
            title = clean(r.get('book_title'))
            if not title:
                continue
            cn, ar = canon_cat(r.get('category'), title)
            out.append({
                's': 'shamela',
                'id': clean(r.get('book_id')) or clean(r.get('sn')),
                't': title,
                'a': clean(r.get('author_name')) or clean(r.get('nickname')),
                'y': clean(r.get('author_year')).replace('ه', '').replace('هـ', ''),
                'c': cn, 'c_ar': ar,
                'pub': clean(r.get('publisher')), 'ed': clean(r.get('edition')),
                'pg': clean(r.get('pages')), 'vol': clean(r.get('volumes')),
                'u': clean(r.get('book_link')),
            })
    return out


def load_openiti():
    fp = RAW / 'openiti_metadata.tsv'
    if not fp.exists():
        return []
    out = []
    with fp.open(encoding='utf-8', newline='') as f:
        rd = csv.DictReader(f, delimiter='\t')
        for r in rd:
            title = clean(r.get('title_ar'))
            if not title:
                continue
            cn, ar = canon_cat(' '.join(_tag_cats(r.get('tags'))) + ' ' + clean(r.get('tags')), r.get('subcorpus'), title)
            out.append({
                's': 'openiti',
                'id': clean(r.get('id')),
                't': title,
                'a': clean(r.get('author_ar')),
                'y': clean(r.get('date')),
                'c': cn, 'c_ar': ar,
                'tags': clean(r.get('tags'))[:120],
                'tk': clean(r.get('tok_length')),
                'u': '',
            })
    return out


def main():
    sham = load_shamela()
    oit = load_openiti()
    print(f'Shamela 条目: {len(sham)}')
    print(f'OpenITI 条目: {len(oit)}')

    seen = set()
    merged = []
    for b in sham + oit:
        k = (norm(b['t'])[:60], norm(b['a'])[:40])
        if k in seen:
            continue
        seen.add(k)
        merged.append(b)

    print(f'去重后总计: {len(merged)}')

    by_cat = defaultdict(int)
    for b in merged:
        by_cat[b['c']] += 1
    print('分类分布（Top 20）:')
    for cn, n in sorted(by_cat.items(), key=lambda x: -x[1])[:20]:
        print(f'   {cn:<16} {n}')

    src = Counter(b['s'] for b in merged)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        'meta': {
            'total': len(merged),
            'sources': dict(src),
            'categories': dict(sorted(by_cat.items(), key=lambda x: -x[1])),
        },
        'books': merged,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    print(f'✅ 写出 {OUT} ({OUT.stat().st_size/1024/1024:.1f} MB)')


if __name__ == '__main__':
    main()
