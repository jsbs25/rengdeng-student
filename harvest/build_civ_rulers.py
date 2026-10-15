#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""抓取「王朝 → 君主」数据（中文维基）。

产出：data/civ_rulers.json  —— {"伍麦叶王朝": [{name, ar, text}], ...}
用法：python3 harvest/build_civ_rulers.py
"""
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'data' / 'civ_rulers.json'
ZH = 'https://zh.wikipedia.org/w/api.php'

DYN_CATS = {
    '正统哈里发': ['正统哈里发', '四大哈里发'],
    '倭马亚王朝': ['倭马亚王朝哈里发', '倭马亚王朝', '伍麦叶王朝哈里发'],
    '阿拔斯王朝': ['阿拔斯王朝哈里发', '阿拔斯王朝'],
    '后倭马亚王朝': ['后倭马亚王朝哈里发', '科尔多瓦哈里发', '后伍麦叶王朝'],
    '法蒂玛王朝': ['法蒂玛王朝哈里发', '法蒂玛王朝'],
    '奥斯曼帝国': ['奥斯曼帝国苏丹', '奥斯曼帝国'],
    '塞尔柱帝国': ['塞尔柱君主', '塞尔柱帝国', '塞爾柱王朝'],
    '阿尤布王朝': ['阿尤布王朝苏丹', '阿尤布王朝'],
    '马穆鲁克王朝': ['马穆鲁克苏丹', '马穆鲁克苏丹国', '巴赫里王朝苏丹'],
    '萨曼王朝': ['萨曼王朝', '萨曼王朝埃米尔'],
    '布韦希王朝': ['布韦希王朝', '白益王朝'],
    '伽色尼王朝': ['伽色尼王朝', '伽色尼王朝君主'],
    '古尔王朝': ['古尔王朝'],
    '花剌子模王朝': ['花剌子模王朝', '花剌子模沙阿'],
    '帖木儿帝国': ['帖木儿帝国君主', '帖木儿王朝人物', '帖木儿帝国'],
    '莫卧儿帝国': ['莫卧儿帝国皇帝', '莫卧儿帝国'],
    '萨法维王朝': ['萨法维王朝', '萨法维王朝君主'],
    '伊德里斯王朝': ['伊德里斯王朝'],
    '穆拉比特王朝': ['穆拉比特王朝', '阿尔摩拉维德王朝'],
    '穆瓦希德王朝': ['穆瓦希德王朝', '阿尔摩哈德王朝'],
    '阿格拉布王朝': ['阿格拉布王朝'],
    '图伦王朝': ['图伦王朝'],
    '哈姆丹王朝': ['哈姆丹王朝'],
    '卡拉汗国': ['喀喇汗国', '卡拉汗国'],
    '德里苏丹国': ['德里苏丹国苏丹', '德里苏丹国'],
    '阿曼帝国': ['阿曼苏丹', '阿曼君主'],
}


def get(u):
    for i in range(3):
        try:
            rq = urllib.request.Request(u, headers={'User-Agent': 'nur/1.0'})
            with urllib.request.urlopen(rq, timeout=45) as r:
                return json.loads(r.read().decode('utf-8'))
        except Exception:
            time.sleep(1 + i)
    return {}


def members(cat, limit=80):
    out, cont = [], None
    while len(out) < limit:
        u = (ZH + '?action=query&list=categorymembers&cmtitle=' + urllib.parse.quote('Category:' + cat) +
             '&cmnamespace=0&cmlimit=500&format=json')
        if cont:
            u += '&cmcontinue=' + cont
        d = get(u)
        out += [m['title'] for m in d.get('query', {}).get('categorymembers', [])]
        cont = d.get('continue', {}).get('cmcontinue')
        if not cont:
            break
        time.sleep(0.25)
    return out[:limit]


def extracts(titles):
    res = []
    for i in range(0, len(titles), 20):
        u = (ZH + '?action=query&prop=extracts|langlinks&explaintext=1&exintro=1&exlimit=20&lllang=ar&redirects=1&format=json&titles=' +
             urllib.parse.quote('|'.join(titles[i:i + 20])))
        d = get(u)
        for p in d.get('query', {}).get('pages', {}).values():
            t = (p.get('extract') or '').strip()
            if len(t) < 60:
                continue
            import re as _re
            if not _re.search(r'哈里发|苏丹|埃米尔|沙阿|可汗|君主|国王|帕迪沙|伊玛目', t):
                continue
            ar = ''
            for ll in (p.get('langlinks') or []):
                if ll.get('lang') == 'ar':
                    ar = ll.get('*') or ''
                    break
            res.append({'name': p.get('title'), 'ar': ar, 'text': t[:1200]})
        time.sleep(0.25)
    return res


def main():
    data = {}
    total = 0
    for dyn, cats in DYN_CATS.items():
        titles = []
        for c in cats:
            for t in members(c):
                if t not in titles:
                    titles.append(t)
        if not titles:
            print('  -', dyn, '（无分类命中）')
            continue
        rs = extracts(titles)
        if rs:
            data[dyn] = rs
            total += len(rs)
            print(f'  ✓ {dyn}: {len(rs)} 位')
        OUT.write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    print(f'✅ 王朝 {len(data)} 个，君主共 {total} 位 → {OUT}')
    print('   总数统计已写入')


if __name__ == '__main__':
    main()
