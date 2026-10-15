#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""构建「可读书库」：以可读全文源为主体，再并入不可读的目录条目。

可读源：
  A. Shamela4_Full_DB（HF）—— 8,589 本，逐页正文 pages.jsonl
  B. shamela-waqfeya-library（HF）—— 4,652 本，整本 txt
产出：data/islamic_catalog.json（含 r 字段标记可读来源）
用法：python3 harvest/build_readable.py
"""
import csv
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / 'harvest' / 'raw'
LIB = ROOT / 'data' / 'library'
CAT = ROOT / 'data' / 'islamic_catalog.json'

AR_DIAC = re.compile(r'[\u0610-\u061A\u064B-\u0652\u0670\u06D6-\u06ED\u0640]')

# 分类中文名映射（Shamela4 目录名 -> 中文）
CAT_CN = {
    'العقيدة': '教义 / 认主学', 'الفرق-والردود': '教派 / 驳论', 'التفسير': '经注 / 古兰学',
    'علوم-القرآن-وأصول-التفسير': '古兰学 / 经注原理', 'التجويد-والقراءات': '诵读学 / 读法',
    'كتب-السنة': '圣训 / 圣训学', 'شروح-الحديث': '圣训注释', 'التخريج-والأطراف': '圣训出处学',
    'العلل-والسؤلات-الحديثية': '圣训隐疾学', 'علوم-الحديث': '圣训学',
    'أصول-الفقه': '法源学', 'علوم-الفقه-والقواعد-الفقهية': '法理学 / 教法规则',
    'المنطق': '逻辑学', 'الفقه-الحنفي': '哈乃斐教法', 'الفقه-المالكي': '马立克教法',
    'الفقه-الشافعي': '沙斐仪教法', 'الفقه-الحنبلي': '罕百里教法', 'الفقه-العام': '教法总论',
    'مسائل-فقهية': '教法问题', 'السياسة-الشرعية-والقضاء': '教法司法', 'الفرائض-والوصايا': '遗产与遗嘱',
    'الفتاوى': '教法判例', 'الرقائق-والآداب-والأذكار': '劝诫 / 礼仪 / 记主',
    'السيرة-النبوية': '先知传记', 'التاريخ': '历史', 'التراجم-والطبقات': '人物志 / 传记',
    'الأنساب': '谱系学', 'البلدان-والرحلات': '地理 / 游记', 'كتب-اللغة': '阿拉伯语',
    'الغريب-والمعاجم': '词典 / 辞书', 'النحو-والصرف': '语法 / 词法', 'الأدب': '文学',
    'العروض-والقوافي': '韵律学', 'الشعر-ودواوينه': '诗歌 / 诗集', 'البلاغة': '修辞学',
    'الجوامع': '文集 / 期刊', 'فهارس-الكتب-والأدلة': '书目 / 索引', 'الطب': '医学',
    'كتب-عامة': '综合', 'علوم-أخرى': '其他学科',
}


def key(s):
    s = unicodedata.normalize('NFKC', str(s or ''))
    s = AR_DIAC.sub('', s)
    s = re.sub(r'[إأآا]', 'ا', s)
    s = re.sub(r'[ىي]', 'ي', s)
    s = re.sub(r'[ةه]', 'ه', s)
    s = re.sub(r'\s+', ' ', s)
    return s.strip()[:70]


def cat_of_shamela4(dirname):
    first = str(dirname or '').split('/')[0]          # 01__العقيدة
    base = first.split('__', 1)[-1] if '__' in first else first
    return CAT_CN.get(base, base.replace('-', ' '))


def load_shamela4():
    fp = LIB / 'shamela_index.json'
    d = json.loads(fp.read_text(encoding='utf-8'))['books']
    out = []
    for bid, info in d.items():
        slug = info.get('slug', '').replace('-', ' ').strip()
        if not slug:
            continue
        out.append({
            's': 'shamela', 'id': bid, 't': slug, 'a': '', 'y': '',
            'c': cat_of_shamela4(info.get('dir', '')), 'c_ar': '', 'pub': '', 'ed': '',
            'pg': '', 'vol': '', 'u': '',
            'r': {'t': 'shamela', 'id': bid},
        })
    return out


def load_waqfeya():
    fp = RAW / 'waqfeya_index.tsv'
    if not fp.exists():
        return []
    out = []
    with fp.open(encoding='utf-8', newline='') as f:
        for r in csv.DictReader(f, delimiter='\t'):
            title = (r.get('title') or '').strip()
            if not title:
                continue
            m = re.findall(r"'(\./txt/[^']+)'", r.get('txt_paths') or '')
            if not m:
                continue
            out.append({
                's': 'waqfeya', 'id': '', 't': title, 'a': (r.get('author') or '').strip(), 'y': '',
                'c': (r.get('category') or '').strip() or '其他 / 综合', 'c_ar': '', 'pub': '', 'ed': '',
                'pg': (r.get('pages') or '').strip(), 'vol': (r.get('volumes') or '').strip(), 'u': '',
                'r': {'t': 'waqfeya', 'p': m[0][2:]},
            })
    return out


def main():
    old = json.loads(CAT.read_text(encoding='utf-8'))
    old_books = old['books']

    merged, seen = [], set()
    n_sham = n_waq = n_other = 0

    for b in load_shamela4():
        k = key(b['t'])
        if not k or k in seen:
            continue
        seen.add(k); merged.append(b); n_sham += 1

    for b in load_waqfeya():
        k = key(b['t'])
        if not k:
            continue
        if k in seen:
            continue
        seen.add(k); merged.append(b); n_waq += 1

    for b in old_books:
        k = key(b['t'])
        if not k or k in seen:
            continue
        seen.add(k)
        b.pop('r', None)
        merged.append(b); n_other += 1

    counts = {}
    for b in merged:
        counts[b['c']] = counts.get(b['c'], 0) + 1

    out = {
        'meta': {
            'total': len(merged),
            'readable': n_sham + n_waq,
            'readable_shamela': n_sham,
            'readable_waqfeya': n_waq,
            'catalog_only': n_other,
            'categories': dict(sorted(counts.items(), key=lambda x: -x[1])),
        },
        'books': merged,
    }
    CAT.write_text(json.dumps(out, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    print(f"✅ 书库总计 {len(merged)} 部")
    print(f"   可读全文 {n_sham + n_waq} 部（Shamela {n_sham} + waqfeya {n_waq}）")
    print(f"   仅目录 {n_other} 部")
    print(f"   分类 {len(counts)} 项")
    print(f"   文件 {CAT.stat().st_size/1048576:.1f} MB")


if __name__ == '__main__':
    main()
