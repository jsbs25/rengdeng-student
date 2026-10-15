#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成留学生日常对话数据（30 场景 × 5 轮，每天 10 场景 = 100 句轮换）"""
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
        "max_tokens": 4000,
        "temperature": 0.7,
    }, ensure_ascii=False).encode('utf-8')
    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                "https://api.deepseek.com/chat/completions", data=body,
                headers={"Content-Type": "application/json", "Authorization": "Bearer " + key},
                method="POST")
            with urllib.request.urlopen(req, timeout=90) as r:
                d = json.loads(r.read())
            return d['choices'][0]['message']['content']
        except Exception as e:
            print(f'  重试 {attempt+1}: {e}')
            time.sleep(3)
    return None

SCENES = [
    ("报到注册", "التسجيل في الجامعة", "🏫"),
    ("选课咨询", "اختيار المواد", "📋"),
    ("图书馆借书", "المكتبة", "📚"),
    ("宿舍入住", "السكن الجامعي", "🛏"),
    ("食堂点餐", "المطعم الجامعي", "🍽"),
    ("校园问路", "السؤال عن الطريق", "🗺"),
    ("超市购物", "التسوق في السوبرماركت", "🛒"),
    ("银行开户", "فتح حساب بنكي", "🏦"),
    ("手机办卡", "شريحة الهاتف", "📱"),
    ("医院挂号", "المستشفى", "🏥"),
    ("打车出行", "سيارة الأجرة", "🚕"),
    ("咖啡店闲聊", "المقهى", "☕"),
    ("小组讨论", "النقاش الجماعي", "👥"),
    ("认识新朋友", "أصدقاء جدد", "🤝"),
    ("健身房", "النادي الرياضي", "🏋"),
    ("洗衣房", "غسيل الملابس", "🧺"),
    ("取快递", "استلام الطرد", "📦"),
    ("换钱", "صرافة العملة", "💱"),
    ("签证续签", "تجديد الإقامة", "🛂"),
    ("周末旅行", "رحلة نهاية الأسبوع", "🎒"),
    ("餐厅订座", "حجز طاولة", "🍴"),
    ("网购退货", "إرجاع المنتج", "📮"),
    ("天气闲聊", "الطقس", "🌤"),
    ("假期安排", "خطة العطلة", "🗓"),
    ("社团活动", "النشاط الطلابي", "🎭"),
    ("考试周", "أسبوع الامتحانات", "📝"),
    ("找兼职", "عمل جزئي", "💼"),
    ("室友相处", "زميل الغرفة", "🏠"),
    ("毕业答辩", "مناقشة التخرج", "🎓"),
    ("告别回国", "الوداع", "✈️"),
]

PROMPT_TMPL = """你是阿拉伯语教材编写者。为以下 {n} 个"留学生日常"场景各编写 5 轮对话（共 {total} 句），要求：
1. 口语化、地道、带完整音符（تشكيل），符合该场景真实语境（阿语国家大学留学生视角）
2. 每轮是"有来有往"的两句：A 说一句，B 回应一句，各带中文翻译
3. 语言简单实用，适合中级学习者
4. 只输出 JSON（不要任何其他文字），格式：
[{{"scene": "场景中文名", "scene_ar": "场景阿语名", "icon": "emoji", "dialogue": [{{"a": "A的阿语句子", "a_cn": "A的中文", "b": "B的阿语句子", "b_cn": "B的中文"}}, ...5轮...]}}, ...]

场景列表：
{scenes}"""

def gen_batch(key, batch):
    scenes_desc = '\n'.join(f"- {s[0]} ({s[1]})" for s in batch)
    prompt = PROMPT_TMPL.format(n=len(batch), total=len(batch) * 10, scenes=scenes_desc)
    out = chat(prompt, key)
    if not out:
        return None
    m = re.search(r'\[.*\]', out, re.S)
    if not m:
        return None
    try:
        data = json.loads(m.group(0))
        return data
    except Exception as e:
        print('  JSON 解析失败:', e)
        return None

def main():
    key = get_key()
    if not key:
        print('没有 API key')
        sys.exit(1)
    all_data = []
    BATCH = 5
    for i in range(0, len(SCENES), BATCH):
        batch = SCENES[i:i + BATCH]
        print(f'生成 {i+1}-{i+len(batch)}/{len(SCENES)}...')
        data = None
        for _ in range(3):
            data = gen_batch(key, batch)
            if data:
                break
            print('  重试整批...')
            time.sleep(2)
        if data:
            all_data.extend(data)
            json.dump(all_data, open(DIR / 'data' / 'dialogues.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
            print(f'  ✓ 已生成 {len(data)} 场景，累计 {len(all_data)}')
        else:
            print(f'  ✗ 批次失败，跳过')
        time.sleep(1)
    # 校验完整性
    total_sent = sum(len(d['dialogue']) * 2 for d in all_data)
    print(f'完成：{len(all_data)} 场景 / {total_sent} 句')
    json.dump(all_data, open(DIR / 'data' / 'dialogues.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('已保存 data/dialogues.json')

if __name__ == '__main__':
    main()
