#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""抓取「伊斯兰文明」细节数据（中文维基百科正文 + 阿拉伯语标题）。

产出：data/civ.json  —— {scholars:[], dynasties:[], cities:[], events:[], subjects:[]}
用法：python3 harvest/build_civ.py
"""
import json
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'data' / 'civ.json'
ZH = 'https://zh.wikipedia.org/w/api.php'

SCHOLARS = [
    '伊本·西那', '花拉子米', '比鲁尼', '伊本·赫勒敦', '拉齐', '伊本·鲁世德', '安萨里', '法拉比',
    '伊本·白图泰', '穆罕默德·伊德里西', '贾比尔·伊本·哈扬', '肯迪', '伊本·海赛姆', '伊本·纳菲斯',
    '穆罕默德·布哈里', '穆斯林·本·哈贾吉', '塔巴里', '伊本·凯西尔', '苏尤蒂', '伊本·泰米叶',
    '伊本·哈杰尔·阿斯卡拉尼', '叶海亚·本·沙拉夫·纳瓦维', '西伯维', '哈利勒·本·艾哈迈德',
    '伊本·马利克', '沙斐仪', '阿布·哈尼法', '马立克·本·阿纳斯', '艾哈迈德·本·罕百勒', '贾希兹',
    '伊斯法哈尼', '伊本·穆格法', '比斯塔米', '哈拉智', '鲁米', '伊本·阿拉比'
]
DYNASTIES = [
    '伍麦叶王朝', '阿拔斯王朝', '法蒂玛王朝', '塞尔柱帝国', '阿尤布王朝', '马穆鲁克王朝', '奥斯曼帝国',
    '后伍麦叶王朝', '萨曼王朝', '布韦希王朝', '伽色尼王朝', '古尔王朝', '花剌子模王朝', '帖木儿帝国',
    '莫卧儿帝国', '萨法维王朝', '伊德里斯王朝', '阿格拉布王朝', '图伦王朝', '哈姆丹王朝', '穆拉比特王朝',
    '穆瓦希德王朝', '阿曼帝国', '宰德派', '卡拉汗国'
]
CITIES = [
    '麦加', '麦地那', '大马士革', '巴格达', '开罗', '科尔多瓦', '撒马尔罕', '布哈拉', '伊斯坦布尔',
    '非斯', '突尼斯市', '萨那', '摩苏尔', '阿勒颇', '伊斯法罕', '设拉子', '赫拉特', '加兹尼',
    '凯鲁万', '马拉喀什', '格拉纳达', '塞维利亚', '哈拉布', '巴士拉', '库法'
]
EVENTS = [
    '伊斯兰教历史', '希吉拉', '征服麦加', '伊斯兰教对耶路撒冷的征服', '倭马亚哈里发国', '阿拔斯革命',
    '巴格达围城 (1258年)', '君士坦丁堡的陷落', '格拉纳达战役', '十字军东征', '哈丁战役',
    '怛罗斯战役', '智慧之家', '翻译运动', '伊斯兰黄金时代', '伊斯兰教传播', '阿拉伯征服',
    '信德征服', '安达卢斯', '收复失地运动', '蒙古西征', '奥斯曼帝国的崛起', '萨法维王朝', '什叶派',
    '逊尼派', '四大哈里发', '阿里·本·阿比·塔利卜', '欧麦尔·本·哈塔卜', '阿布·伯克尔', '奥斯曼·本·阿凡',
    '哈立德·本·瓦利德', '萨拉丁', '穆罕默德二世', '苏莱曼一世', '哈伦·拉希德', '马蒙', '帖木儿'
]


def get(url, retry=2):
    for i in range(retry + 1):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'nur/1.0'})
            with urllib.request.urlopen(req, timeout=45) as r:
                return json.loads(r.read().decode('utf-8'))
        except Exception:
            time.sleep(1 + i)
    return {}


def fetch(titles, kind):
    out = []
    for i in range(0, len(titles), 20):
        batch = titles[i:i + 20]
        u = (ZH + '?action=query&prop=extracts|langlinks&explaintext=1&exintro=1&exlimit=20'
             '&lllang=ar&lllimit=5&format=json&redirects=1&titles=' + urllib.parse.quote('|'.join(batch)))
        d = get(u)
        pages = d.get('query', {}).get('pages', {})
        for p in pages.values():
            t = (p.get('extract') or '').strip()
            if len(t) < 80:
                continue
            ar = ''
            for ll in (p.get('langlinks') or []):
                if ll.get('lang') == 'ar':
                    ar = ll.get('*') or ''
                    break
            out.append({'name': p.get('title'), 'ar': ar, 'text': t[:1500], 'kind': kind})
        time.sleep(0.3)
    return out


def main():
    data = {}
    with ThreadPoolExecutor(max_workers=4) as ex:
        f1 = ex.submit(fetch, SCHOLARS, 'scholar')
        f2 = ex.submit(fetch, DYNASTIES, 'dynasty')
        f3 = ex.submit(fetch, CITIES, 'city')
        f4 = ex.submit(fetch, EVENTS, 'event')
        data['scholars'] = f1.result()
        data['dynasties'] = f2.result()
        data['cities'] = f3.result()
        data['events'] = f4.result()
    data['counts'] = {k: len(v) for k, v in data.items()}
    OUT.write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    print('✅', data['counts'], '→', OUT, f'({OUT.stat().st_size/1024:.0f}KB)')


if __name__ == '__main__':
    main()
