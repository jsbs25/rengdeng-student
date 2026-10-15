# -*- coding: utf-8 -*-
"""燃灯者管理控制台：系统状态 + 内容管理 + AI 设置 + 系统控制"""
import json, os, subprocess, sys, time, re
from pathlib import Path

ROOT = Path(__file__).parent
DATA = ROOT / 'data'

def status():
    out = {'time': time.strftime('%Y-%m-%d %H:%M:%S'), 'root': str(ROOT)}
    # 磁盘
    try:
        st = os.statvfs(str(ROOT))
        out['disk_free_gb'] = round(st.f_bavail * st.f_frsize / 1073741824, 1)
    except Exception: out['disk_free_gb'] = '?'
    # 数据规模
    for name in ['categorized.json', 'hadith_all.json', 'history.json', 'dialogues.json', 'hadith.json']:
        f = DATA / name
        try:
            d = json.load(open(f, encoding='utf-8'))
            n = len(d) if isinstance(d, list) else sum(len(v) for v in d.values() if isinstance(v, list))
            out[name.replace('.json', '')] = n
        except Exception:
            out[name.replace('.json', '')] = '?'
    # 模型/服务
    out['asr_model'] = os.path.isdir(os.path.expanduser('~/.cache/huggingface/hub/models--Systran--faster-whisper-small'))
    m1 = os.path.isdir(str(ROOT / 'models_musicgen'))
    m2 = os.path.isdir('/Users/mafucheng/Desktop/arabic-learning/models_musicgen')
    out['music_model'] = m1 or m2
    return out

def get_ai_config():
    src = (ROOT / 'server.py').read_text(encoding='utf-8')
    m = re.search(r'SYSTEM = (".*?"|\'\'\'.*?\'\'\'|""".*?""")', src, re.S)
    cfg = {}
    for k in ['AI_KEY', 'AI_MODEL', 'AI_URL']:
        m2 = re.search(rf'^{k}\s*=\s*["\']([^"\']*)["\']', src, re.M)
        if m2: cfg[k] = m2.group(1)
    m3 = re.search(r'AI_CFG\s*=\s*\{[^}]*\}', src, re.S)
    if m3: cfg['AI_CFG'] = m3.group(0)
    m4 = re.search(r'"max_tokens": (\d+)', src)
    if m4: cfg['max_tokens'] = m4.group(1)
    return {'system': (m.group(1)[1:-1] if m else ''), **cfg}

def set_ai_config(new_system=None, max_tokens=None):
    p = ROOT / 'server.py'
    src = p.read_text(encoding='utf-8')
    if new_system is not None:
        import re as _re
        m = _re.search(r'SYSTEM = (".*?"|\'\'\'.*?\'\'\'|""".*?""")', src, re.S)
        if m:
            src = src[:m.start()] + 'SYSTEM = ' + json.dumps(new_system, ensure_ascii=False) + src[m.end():]
    if max_tokens:
        src = re.sub(r'"max_tokens": \d+', f'"max_tokens": {int(max_tokens)}', src)
    p.write_text(encoding='utf-8', data=src)
    return True

def rebuild():
    r = subprocess.run([sys.executable, str(ROOT / 'rebuild.py')], capture_output=True, text=True, timeout=600)
    return {'ok': r.returncode == 0, 'out': (r.stdout + r.stderr)[-800:]}

def run_scraper():
    r = subprocess.run([sys.executable, str(ROOT / 'scraper_hourly.py')], capture_output=True, text=True, timeout=900)
    return {'ok': r.returncode == 0, 'out': (r.stdout + r.stderr)[-800:]}

def data_list(kind, page=0, size=30, q=''):
    """kind: sentences|hadith|history|dialogues"""
    f = {'sentences': 'categorized.json', 'hadith': 'hadith_all.json', 'history': 'history.json', 'dialogues': 'dialogues.json'}[kind]
    try:
        d = json.load(open(DATA / f, encoding='utf-8'))
    except Exception as e:
        return {'error': str(e)}
    items = []
    if kind == 'sentences':
        flat = []
        for i, s in enumerate(d):
            flat.append({'key': str(i), 'ar': s.get('ar', s.get('a', '')), 'zh': s.get('cn', s.get('c', '')), 'cat': s.get('cat', '')})
        items = flat
    elif kind == 'hadith':
        items = [{'key': str(x.get('id', i)), 'ar': x.get('topic', x.get('cn', ''))[:80], 'zh': x.get('cn', x.get('topic', ''))[:80]} for i, x in enumerate(d)]
    elif kind == 'history':
        items = [{'key': str(x.get('id', i)), 'ar': '', 'zh': x.get('title', x.get('body', ''))[:80]} for i, x in enumerate(d)]
    elif kind == 'dialogues':
        items = [{'key': str(i), 'ar': '', 'zh': str(x)[:80]} for i, x in enumerate(d)]
    if q:
        items = [x for x in items if q in x.get('ar', '') or q in x.get('zh', '')]
    total = len(items)
    return {'total': total, 'items': items[page * size:(page + 1) * size], 'page': page, 'size': size}
