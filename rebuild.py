#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一键重建：categorized.json → app/src/data.js + 网页版 arabic_learning.html"""
import json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).parent

def build_app_data():
    d = json.load(open(ROOT / 'data' / 'categorized.json', encoding='utf-8'))
    dialogues = []
    dp = ROOT / 'data' / 'dialogues.json'
    if dp.exists():
        dialogues = json.load(open(dp, encoding='utf-8'))
    history = []
    hp = ROOT / 'data' / 'history.json'
    if hp.exists():
        history = json.load(open(hp, encoding='utf-8'))
    hadith = []
    hdp = ROOT / 'data' / 'hadith_all.json'
    if hdp.exists():
        hadith = json.load(open(hdp, encoding='utf-8'))
    elif (ROOT / 'data' / 'hadith.json').exists():
        hadith = json.load(open(ROOT / 'data' / 'hadith.json', encoding='utf-8'))
    cats = {}
    for it in d:
        c = it.get('cat', 'other')
        cats.setdefault(c, []).append({
            'a': it.get('ar', ''), 'e': it.get('en', ''), 'c': it.get('cn', ''), 'py': it.get('py', ''),
        })
    meta = {
        'greeting': {'icon': '👋', 'cn': '问候', 'ar': 'مرحبا'}, 'daily': {'icon': '🌅', 'cn': '日常', 'ar': 'يومي'},
        'food': {'icon': '🍽', 'cn': '饮食', 'ar': 'طعام'}, 'travel': {'icon': '✈️', 'cn': '旅行', 'ar': 'سفر'},
        'family': {'icon': '👨👩👧', 'cn': '家庭', 'ar': 'عائلة'}, 'work': {'icon': '💼', 'cn': '工作', 'ar': 'عمل'},
        'study': {'icon': '📚', 'cn': '学习', 'ar': 'دراسة'}, 'religion': {'icon': '🕌', 'cn': '宗教', 'ar': 'دين'},
        'health': {'icon': '🏥', 'cn': '健康', 'ar': 'صحة'}, 'weather': {'icon': '🌤', 'cn': '天气', 'ar': 'طقس'},
        'shopping': {'icon': '🛍', 'cn': '购物', 'ar': 'تسوق'}, 'hobby': {'icon': '🎨', 'cn': '爱好', 'ar': 'هواية'},
        'other': {'icon': '📖', 'cn': '其他', 'ar': 'أخرى'},
        'jordan_greet': {'icon': '✈️', 'cn': '旅途问候', 'ar': 'تحيات'}, 'jordan_airport': {'icon': '🛫', 'cn': '机场交通', 'ar': 'المطار'},
        'jordan_hotel': {'icon': '🏨', 'cn': '住宿租房', 'ar': 'السكن'}, 'jordan_food': {'icon': '🍽', 'cn': '餐厅饮食', 'ar': 'المطاعم'},
        'jordan_shop': {'icon': '🛍', 'cn': '购物讲价', 'ar': 'التسوق'}, 'jordan_dir': {'icon': '🧭', 'cn': '问路方位', 'ar': 'الاتجاهات'},
        'jordan_campus': {'icon': '🎓', 'cn': '校园学习', 'ar': 'الجامعة'}, 'jordan_emerg': {'icon': '🚨', 'cn': '紧急情况', 'ar': 'طوارئ'},
        'jordan_social': {'icon': '👥', 'cn': '社交文化', 'ar': 'تواصل'}, 'jordan_daily': {'icon': '☕', 'cn': '日常表达', 'ar': 'عبارات'},
    }
    out = '// 自动生成 - 全部句子（含旅途 200 句）+ 日常对话\nmodule.exports = ' + json.dumps(
        {'cats': cats, 'meta': meta, 'dialogues': dialogues, 'history': history, 'hadith': hadith,
         'stats': {'sentences': len(d), 'words': sum(len(it.get('ar', '').split()) for it in d), 'cats': len(cats)}},
        ensure_ascii=False) + ';\n'
    (ROOT / 'app' / 'src' / 'data.js').write_text(out, encoding='utf-8')
    print(f'app/src/data.js: {len(d)} 句 / {len(cats)} 分类')

def build_web():
    subprocess.run([sys.executable, str(ROOT / 'build_home.py')], cwd=str(ROOT), check=True)

if __name__ == '__main__':
    build_app_data()
    build_web()
    print('✅ 全部重建完成')
