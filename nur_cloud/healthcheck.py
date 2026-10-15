#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""通宵巡检：服务器/数据/文件一致性/磁盘 一键健康检查"""
import json, os, socket, subprocess, sys
from pathlib import Path

ROOT = Path('/Users/mafucheng/Desktop/arabic-learning')
ok = True

def check(name, cond, detail=''):
    global ok
    mark = '✅' if cond else '❌'
    if not cond:
        ok = False
    print(f'{mark} {name} {detail}')

# 1. 服务器
try:
    s = socket.create_connection(('127.0.0.1', 8080), timeout=3)
    s.close()
    check('服务器 8080', True)
except Exception:
    check('服务器 8080', False, '(未运行!)')

# 2. ASR 服务
try:
    import urllib.request
    r = json.loads(urllib.request.urlopen('http://localhost:8080/api/asr/status', timeout=5).read())
    check('语音识别服务', r.get('asr'), f"model={r.get('model_ready')}")
except Exception as e:
    check('语音识别服务', False, str(e))

# 3. 数据完整性
d = json.load(open(ROOT / 'data' / 'categorized.json', encoding='utf-8'))
missing = sum(1 for it in d if not it.get('en', '').strip() or not it.get('cn', '').strip())
check('句子数据', len(d) > 2000, f'{len(d)} 句, 缺翻译 {missing}')
dlg = json.load(open(ROOT / 'data' / 'dialogues.json', encoding='utf-8'))
check('对话数据', len(dlg) >= 30, f'{len(dlg)} 场景')
books = json.load(open(ROOT / 'data' / 'books.json', encoding='utf-8'))
check('书籍数据', len(books) >= 5, f'{len(books)} 本')

# 4. 文件一致性
sizes = {}
for f in ['arabic_learning.html']:
    sizes[f] = (ROOT / f).stat().st_size
desktop = Path.home() / 'Desktop' / 'arabic_learning.html'
check('桌面副本一致', desktop.exists() and desktop.stat().st_size == sizes['arabic_learning.html'])
app_dist = Path.home() / 'Desktop/Nur Al-Arabiyya.app/Contents/Resources/app/electron/dist/index.html'
check('桌面App dist一致', app_dist.exists() and app_dist.stat().st_size == sizes['arabic_learning.html'])

# 5. 磁盘
st = os.statvfs('/')
free = st.f_bavail * st.f_frsize / 1e9
check('磁盘空间', free > 20, f'{free:.1f}GB 可用')

# 6. 爬虫日志（最近一次运行）
logf = ROOT / 'scraper.log'
if logf.exists():
    check('爬虫日志', True, f'更新于 {logf.stat().st_mtime}')

# 7. 圣训数据
try:
    h = json.load(open(ROOT / 'data' / 'hadith_all.json', encoding='utf-8'))
    full = sum(1 for x in h if x.get('source') == 'hadeethenc' and len(x.get('cn', '')) > 30)
    check('圣训数据', len(h) >= 2000, f'{len(h)} 则（正文完整 {full}）')
except Exception as e:
    check('圣训数据', False, str(e))

# 8. 网页版功能测试（jsdom）
try:
    out = subprocess.run(['node', '/tmp/test_web_jsdom.js'], capture_output=True, text=True, timeout=90, cwd='/tmp')
    last = [l for l in out.stdout.split('\n') if l.startswith('TEST')]
    if last:
        detail = last[-1].split(':', 1)[1] if ':' in last[-1] else last[-1]
        check('网页功能', 'MISS' not in detail and 'ERR' not in detail, detail[:120])
    else:
        check('网页功能', False, out.stderr[-100:])
except Exception as e:
    check('网页功能', False, str(e))
print('\n' + ('✅ 全部正常' if ok else '⚠️ 存在问题，需处理'))
sys.exit(0 if ok else 1)


# 7. 网页版功能测试（jsdom）
try:
    out = subprocess.run(['node', '/tmp/test_web_jsdom.js'], capture_output=True, text=True, timeout=90, cwd='/tmp')
    last = [l for l in out.stdout.split('\n') if l.startswith('TEST')]
    if last:
        detail = last[-1].split(':', 1)[1] if ':' in last[-1] else last[-1]
        check('网页功能', 'MISS' not in detail and 'ERR' not in detail, detail[:120])
    else:
        check('网页功能', False, out.stderr[-100:])
except Exception as e:
    check('网页功能', False, str(e))
