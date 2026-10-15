#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成古兰经精选经注（塔巴里/伊本·凯西尔/赛尔迪/贾拉莱因风格）"""
import json, os, re, sys, time, urllib.request
from pathlib import Path

DIR = Path(__file__).parent
KEY_FILE = DIR / 'data' / 'ai_key.txt'

def get_key():
    k = ''
    if KEY_FILE.exists():
        k = open(KEY_FILE, encoding='utf-8').read().strip()
    if not k:
        k = os.environ.get('DEEPSEEK_API_KEY') or os.environ.get('LOBSTER_APIKEY_DEEPSEEK') or ''
    return k

def chat(prompt, key, retries=3):
    body = json.dumps({
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 2200,
        "temperature": 0.3,
    }, ensure_ascii=False).encode('utf-8')
    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                "https://api.deepseek.com/chat/completions", data=body,
                headers={"Content-Type": "application/json", "Authorization": "Bearer " + key},
                method="POST")
            with urllib.request.urlopen(req, timeout=120) as r:
                d = json.loads(r.read())
            return d['choices'][0]['message']['content']
        except Exception as e:
            print(f'  重试 {attempt+1}: {e}')
            time.sleep(4)
    return None

# 精选经文：(章号, 节号, 章中文名, 经注来源)
VERSES = [
    (1, 1, '开端章', '伊本·凯西尔'),
    (1, 2, '开端章', '塔巴里'),
    (1, 5, '开端章', '赛尔迪'),
    (2, 2, '黄牛章', '塔巴里'),
    (2, 152, '黄牛章', '伊本·凯西尔'),
    (2, 153, '黄牛章', '赛尔迪'),
    (2, 255, '黄牛章', '伊本·凯西尔'),
    (2, 286, '黄牛章', '贾拉莱因'),
    (3, 8, '伊姆兰的家属章', '塔巴里'),
    (4, 36, '妇女章', '赛尔迪'),
    (5, 3, '筵席章', '伊本·凯西尔'),
    (8, 46, '战利品章', '贾拉莱因'),
    (24, 35, '光明章', '塔巴里'),
    (30, 21, '罗马人章', '伊本·凯西尔'),
    (55, 1, '至仁主章', '赛尔迪'),
    (103, 1, '时光章', '伊本·凯西尔'),
    (112, 1, '忠诚章', '贾拉莱因'),
]

PROMPT = """你是古兰经经注学者。请为以下经文编写一段经注（约150-200字中文），要求：
1. 结合{source}经注传统，说明经文背景（如有降示背景）、关键词含义、教法或信仰要点
2. 语言通俗准确，适合学习者
3. 只输出 JSON：{{"tafsir": "经注内容"}}

经文（第{surah_cn}第{ayah}节）：
阿语：{ar}
中文：{cn}"""

def load_quran():
    qf = DIR / 'data' / 'quranData.js'
    s = open(qf, encoding='utf-8').read()
    data = json.loads(s.split('module.exports = ')[1].rstrip().rstrip(';'))
    return data

def main():
    key = get_key()
    if not key:
        print('没有 API key')
        sys.exit(1)
    quran = load_quran()
    # 章索引
    surah_map = {}
    for ch in quran:
        surah_map[ch['id']] = ch
    out_file = DIR / 'data' / 'tafsir.json'
    all_data = []
    if out_file.exists():
        all_data = json.load(open(out_file, encoding='utf-8'))
    done = {(d['surah'], d['ayah']) for d in all_data}
    for i, (sid, aidx, scn, source) in enumerate(VERSES):
        if (sid, aidx) in done:
            print(f'跳过: {scn} {aidx}')
            continue
        ch = surah_map.get(sid)
        if not ch or aidx > len(ch.get('vs', [])):
            print(f'✗ 章{ sid }节{aidx}不存在')
            continue
        ayah = ch['vs'][aidx - 1]
        ar = ayah.get('ar', '')
        cn = ayah.get('zh', '') or ayah.get('cn', '')
        print(f'[{i+1}/{len(VERSES)}] {scn} {aidx}...')
        body = None
        for _ in range(3):
            reply = chat(PROMPT.format(source=source, surah_cn=scn, ayah=aidx, ar=ar, cn=cn), key)
            if reply:
                m = re.search(r'\{[\s\S]*\}', reply)
                if m:
                    try:
                        d = json.loads(m.group(0))
                        if d.get('tafsir'):
                            body = d['tafsir']
                            break
                    except Exception:
                        pass
            print('  重试...')
            time.sleep(3)
        if body:
            all_data.append({
                'surah': sid, 'ayah': aidx, 'surah_cn': scn, 'source': source,
                'ar': ar, 'cn': cn, 'tafsir': body,
            })
            json.dump(all_data, open(out_file, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
            print(f"  ✓ {body[:40]}...")
        else:
            print('  ✗ 失败')
        time.sleep(1.5)
    print(f'完成：{len(all_data)} 节经注')
    json.dump(all_data, open(out_file, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

if __name__ == '__main__':
    main()
