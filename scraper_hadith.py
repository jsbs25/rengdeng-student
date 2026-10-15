#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""圣训爬虫：自动获取圣训（hadeethenc API）+ 补全正文 + 质量校验 + 重建同步

运行：python3 scraper_hadith.py
调度：每小时半点（openclaw cron），断点续传，多轮完成全部正文
"""
import json, os, re, sys, time, urllib.request
from pathlib import Path
from collections import Counter

DIR = Path(__file__).parent
API_LIST = 'https://hadeethenc.com/api/v1/hadeeths/list/'
API_ONE = 'https://hadeethenc.com/api/v1/hadeeths/one/'
HADITH_JSON = DIR / 'data' / 'hadith.json'        # 37 则阿语版（人工精选）
API_JSON = DIR / 'data' / 'hadith_api.json'        # API 拉取库
ALL_JSON = DIR / 'data' / 'hadith_all.json'        # 合并库（App/网页数据源）
LOG = DIR / 'data' / 'hadith_crawler.log'

def log(msg):
    line = f'[{time.strftime("%H:%M:%S")}] {msg}'
    print(line, flush=True)
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(f'[{time.strftime("%Y-%m-%d %H:%M:%S")}] {msg}\n')

def fetch(url, timeout=30, retries=2):
    # 用 curl 子进程（比 urllib 稳定，curl 直连响应 1-2s）
    import subprocess
    for attempt in range(retries):
        try:
            r = subprocess.run(['curl', '-s', '--max-time', str(timeout), '-H', 'User-Agent: Mozilla/5.0', url],
                               capture_output=True, text=True, timeout=timeout + 10)
            if r.returncode != 0 or not r.stdout.strip():
                raise RuntimeError(f'curl exit {r.returncode}')
            return json.loads(r.stdout)
        except Exception as e:
            if isinstance(e, json.JSONDecodeError):
                return None
            wait = 4 + attempt * 4
            log(f'  API 请求失败({attempt+1}/{retries}): {e}，等待 {wait}s')
            time.sleep(wait)
    return None

def load_api():
    if API_JSON.exists():
        return json.load(open(API_JSON, encoding='utf-8'))
    return []

def save_api(d):
    json.dump(d, open(API_JSON, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# ===== 1. list 拉取（增量，50 个主题分类）=====
def pull_list(api):
    seen = {h['id'] for h in api}
    new = 0
    for cid in range(1, 51):
        page = 1
        while page <= 8:
            d = fetch(f'{API_LIST}?language=zh&category_id={cid}&page={page}&per_page=100')
            if not d:
                break  # 404 或失败 → 该类结束
            data = d.get('data', [])
            if not data:
                break
            for h in data:
                hid = h.get('id')
                if hid in seen:
                    continue
                seen.add(hid)
                api.append({
                    'id': hid,
                    'title': h.get('title', ''),
                    'cn': h.get('title', ''),  # 标题兜底，正文由 one 接口补
                    'attribution': '',
                    'grade': '',
                    'explanation': '',
                    'hints': [],
                    'book': 'other',
                    'source': 'hadeethenc',
                })
                new += 1
            if len(data) < 100:
                break
            page += 1
            time.sleep(0.8)
        time.sleep(0.5)
    if new:
        save_api(api)
        log(f'list 拉取新增 {new} 则（累计 {len(api)}）')
    else:
        log(f'list 无新增（累计 {len(api)}）')
    return new

# ===== 2. one 接口补正文（断点续传，稳定速率）=====
def fill_bodies(api, limit=None):
    todo = [h for h in api if not h.get('full')]
    if limit:
        todo = todo[:limit]
    if not todo:
        log('正文已全部补齐 ✅')
        return 0
    log(f'本轮补正文：{len(todo)} 则')
    done = 0
    for i, h in enumerate(todo):
        d = fetch(f'{API_ONE}?id={h["id"]}&language=zh')
        if not d:
            log(f'  {h["id"]} 多次失败，跳过（下轮续跑）')
            continue
        h['full'] = 1
        if d.get('hadeeth'):
            h['cn'] = d['hadeeth']
        if d.get('attribution'):
            h['attribution'] = d['attribution']
        if d.get('explanation'):
            h['explanation'] = d['explanation']
        if d.get('grade'):
            h['grade'] = d['grade']
        if d.get('hints'):
            h['hints'] = d['hints']
        done += 1
        if (i + 1) % 20 == 0:
            save_api(api)
            log(f'  已补 {i + 1}/{len(todo)}')
        time.sleep(2.0)
    save_api(api)
    log(f'本轮补正文完成：{done} 则')
    return done

# ===== 3. 主题打标 =====
TAGS = [
    ('古兰', ['古兰', '诵读古兰', '黄牛章', '开端章', '忠诚章', '读经']),
    ('礼拜', ['礼拜', '晨礼', '晡礼', '宵礼', '晌礼', '主麻', '拜功', '祈祷', '叩头', '宣礼']),
    ('斋戒', ['斋戒', '斋月', '封斋', '开斋']),
    ('朝觐', ['朝觐', '天房', '麦加', '朝圣']),
    ('洁净', ['洁净', '小净', '大净', '净下', '清洁']),
    ('施舍', ['施舍', '天课', '济贫', '布施', '慈善', '财物']),
    ('婚姻', ['婚姻', '结婚', '妻子', '丈夫', '嫁妆', '离婚', '聘礼']),
    ('商业', ['商业', '买卖', '交易', '经商', '利息', '债务', '称量']),
    ('知识', ['知识', '求知', '学者', '学习', '教育', '传授']),
    ('饮食', ['饮食', '食物', '吃喝', '用餐', '进餐']),
    ('美德', ['美德', '善良', '诚实', '诚信', '仁爱', '宽容', '忍耐', '温和', '谦虚', '慷慨', '善待', '兄弟']),
    ('末日', ['末日', '后世', '审判', '复活', '天堂', '火狱', '乐园', '清算']),
    ('举意', ['举意', '意图', '意念']),
]
def tag_of(h):
    text = (h.get('topic', '') + ' ' + h.get('cn', ''))[:500]
    for tag, kws in TAGS:
        for kw in kws:
            if kw in text:
                return tag
    return '其他'

def apply_tags(api):
    for h in api:
        h['tag'] = tag_of(h)
    save_api(api)

# ===== 4. 合并 + 质量校验 =====
def merge_and_check():
    hadith = json.load(open(HADITH_JSON, encoding='utf-8')) if HADITH_JSON.exists() else []
    api = load_api()
    merged = list(hadith)
    seen_id = {h.get('id') for h in hadith if h.get('id')}
    added = 0
    for h in api:
        if h.get('id') in seen_id:
            continue
        seen_id.add(h.get('id'))
        merged.append({
            'id': h.get('id'),
            'topic': h.get('title', '圣训'),
            'cn': h.get('cn', ''),
            'attribution': h.get('attribution', ''),
            'grade': h.get('grade', ''),
            'explanation': h.get('explanation', ''),
            'hints': h.get('hints', []),
            'tag': h.get('tag', '其他'),
            'book': h.get('book', 'other'),
            'book_cn': '综合圣训' if h.get('book') == 'other' else '',
            'source': 'hadeethenc',
        })
        added += 1
    json.dump(merged, open(ALL_JSON, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    # 质量统计
    no_cn = sum(1 for h in merged if not h.get('cn', '').strip())
    empty = sum(1 for h in merged if not h.get('topic', '').strip())
    books = Counter(h.get('book', 'other') for h in merged)
    log(f'合并 {len(merged)} 则（新增 {added}）| 空标题 {empty} | 无正文 {no_cn} | 分布 {dict(books)}')
    if empty or no_cn > len(merged) * 0.1:
        log('⚠️ 质量告警：存在空数据条目')
    return merged

# ===== 5. 重建 + 同步 =====
def rebuild_all():
    log('重建 data.js + 网页版...')
    import subprocess, sys
    subprocess.run([sys.executable, str(DIR / 'rebuild.py')], cwd=str(DIR), check=False)
    # 同步桌面 App
    app_e = Path.home() / 'Desktop/Nur Al-Arabiyya.app/Contents/Resources/app/electron'
    if app_e.exists():
        subprocess.run(['cp', str(DIR / 'build_home.py'), str(app_e / 'build_home.py')], check=False)
        subprocess.run(['cp', str(ALL_JSON), str(app_e / 'data' / 'hadith_all.json')], check=False)
        subprocess.run([sys.executable, 'build_home.py', 'dist/index.html'], cwd=str(app_e), check=False)
        subprocess.run(['codesign', '--force', '--deep', '--sign', '-', str(Path.home() / 'Desktop/Nur Al-Arabiyya.app')], check=False)
        log('桌面 App 已同步')
    log('重建完成')

def main():
    import sys
    do_list = '--full' in sys.argv  # 默认仅补正文；--full 才拉取列表
    log(f'===== 圣训爬虫启动（{"完整模式" if do_list else "仅补正文"}）=====')
    api = load_api()
    if do_list:
        pull_list(api)
    filled = fill_bodies(api, limit=100)  # 每轮 100 则（约 10 分钟），稳定防限流
    apply_tags(api)
    merged = merge_and_check()
    if filled > 0 or True:
        rebuild_all()
    log(f'===== 本轮完成：补正文 {filled} 则，库共 {len(merged)} 则 =====')

if __name__ == '__main__':
    main()
