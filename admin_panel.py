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
    m = re.search(r'SYSTEM = (""".*?"""|\'\'\'.*?\'\'\'|"(?:[^"\\]|\\.)*")', src, re.S)
    cfg = {}
    sys_str = ''
    if m:
        v = m.group(1)
        if v.startswith('"""') or v.startswith("'''"):
            sys_str = v[3:-3]
        else:
            try:
                sys_str = json.loads(v)
            except Exception:
                sys_str = v[1:-1]
    for k in ['AI_KEY', 'AI_MODEL', 'AI_URL']:
        m2 = re.search(rf'^{k}\s*=\s*["\']([^"\']*)["\']', src, re.M)
        if m2: cfg[k] = m2.group(1)
    m3 = re.search(r'AI_CFG\s*=\s*\{[^}]*\}', src, re.S)
    if m3: cfg['AI_CFG'] = m3.group(0)
    m4 = re.search(r'"max_tokens": (\d+)', src)
    if m4: cfg['max_tokens'] = m4.group(1)
    return {'system': sys_str, **cfg}

def set_ai_config(new_system=None, max_tokens=None):
    p = ROOT / 'server.py'
    src = p.read_text(encoding='utf-8')
    if new_system is not None:
        import re as _re
        m = _re.search(r'SYSTEM = """.*?"""', src, re.S) or _re.search(r"SYSTEM = '''.*?'''", src, re.S)
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

KINDS = {
    'sentences':  {'file': 'categorized.json',      'label': '💬 句子库',        'note': '阿拉伯语句子（含中/英译文与分类）'},
    'vocab':      {'file': 'vocab_meanings.json',   'label': '📚 词汇释义',      'note': '单词的中英文释义'},
    'articles':   {'file': 'articles.json',         'label': '📝 阿语文章',      'note': '分级阅读文章'},
    'dialogues':  {'file': 'dialogues.json',        'label': '🎙 会话场景',      'note': '日常对话场景'},
    'quotes':     {'file': 'quotes.json',           'label': '✨ 名言警句',      'note': '阿语名言 + 翻译'},
    'tafsir':     {'file': 'tafsir.json',           'label': '🕌 古兰经经注',    'note': '114 章中文经注'},
    'hadith':     {'file': 'hadith_all.json',       'label': '📜 圣训（全库）',  'note': '带译文与注释的圣训'},
    'hadith_api': {'file': 'hadith_api.json',       'label': '📜 圣训（分类库）', 'note': '按主题分类的圣训'},
    'history':    {'file': 'history.json',          'label': '🏛 历史与文学',    'note': '中文历史/文学 + 阿语历史'},
    'civ':        {'file': 'civ.json',              'label': '🌍 文明图谱',      'note': '学者 / 王朝 / 城市'},
    'rulers':     {'file': 'civ_rulers.json',       'label': '👑 历代君主',      'note': '各王朝君主列表'},
    'islamic':    {'file': 'islamic_catalog.json',  'label': '📖 伊斯兰书库',    'note': '书目总表（Shamela / waqfeya）'},
    'books':      {'file': 'books.json',            'label': '📗 精选书（带章节）', 'note': '内置完整书籍'},
    'covers':     {'file': 'covers.json',           'label': '🖼 书封映射',      'note': '书名 → 封面图'},
}

def _row(key, obj, cat=''):
    if not isinstance(obj, dict):
        return {'key': str(key), 'ar': '', 'zh': str(obj)[:120], 'cat': str(cat)[:30]}
    ar = str(obj.get('ar', obj.get('a', obj.get('topic', obj.get('scene_ar', obj.get('name_ar', ''))))))[:120]
    zh = str(obj.get('cn', obj.get('zh', obj.get('z', obj.get('t', obj.get('title', obj.get('name', obj.get('scene', ''))))))))[:120]
    c = str(cat or obj.get('cat_cn', obj.get('cat', obj.get('book_cn', obj.get('c', obj.get('tag', obj.get('grade', '')))))))[:30]
    if not zh and not ar:
        zh = str(obj)[:120]
    return {'key': str(key), 'ar': ar, 'zh': zh, 'cat': c}

def _flatten(d):
    """把各种结构统一成 [{key, ar, zh, cat}]"""
    out = []
    if isinstance(d, list):
        for i, x in enumerate(d):
            out.append(_row(x.get('id', i) if isinstance(x, dict) else i, x))
    elif isinstance(d, dict):
        SKIP = {'meta', 'total', 'readable', 'readable_shamela', 'readable_waqfeya', 'catalog_only'}
        for k, v in d.items():
            if k in SKIP and not isinstance(v, list):
                continue
            if isinstance(v, dict):
                vals = list(v.values())[:3]
                if vals and all(isinstance(x, list) for x in vals):
                    for cat, arr in v.items():
                        for i, it in enumerate(arr if isinstance(arr, list) else []):
                            out.append(_row(it.get('id', i) if isinstance(it, dict) else i, it, cat))
                elif vals and all(isinstance(x, dict) for x in vals):
                    for k2, v2 in v.items():
                        out.append(_row(k2, v2, k))
                else:
                    out.append(_row(k, v))
            elif isinstance(v, list):
                if v and isinstance(v[0], dict):
                    for i, it in enumerate(v):
                        out.append(_row(it.get('id', i), it, k))
                else:
                    out.append({'key': str(k), 'ar': '', 'zh': ('%d 条' % len(v)), 'cat': ''})
            else:
                out.append({'key': str(k), 'ar': '', 'zh': str(v)[:120], 'cat': ''})
    return out

def kinds():
    res = []
    for k, meta in KINDS.items():
        n = '?'
        try:
            d = json.load(open(DATA / meta['file'], encoding='utf-8'))
            if isinstance(d, list):
                n = len(d)
            elif isinstance(d, dict):
                n = 0
                for kk, v in d.items():
                    if kk in ('meta', 'total', 'readable', 'readable_shamela', 'readable_waqfeya', 'catalog_only'):
                        continue
                    if isinstance(v, list):
                        n += len(v)
                    elif isinstance(v, dict):
                        tot = sum(len(vv) for vv in v.values() if isinstance(vv, list))
                        n += tot if tot else len(v)
                    else:
                        n += 1
        except Exception:
            pass
        res.append({'id': k, 'label': meta['label'], 'note': meta['note'], 'file': meta['file'], 'count': n})
    return {'ok': True, 'kinds': res}

def data_list(kind, page=0, size=30, q=''):
    """内容列表：支持全部在用内容类型"""
    meta = KINDS.get(kind)
    if not meta:
        return {'error': '未知类型: %s' % kind}
    try:
        d = json.load(open(DATA / meta['file'], encoding='utf-8'))
    except Exception as e:
        return {'error': str(e)}
    items = _flatten(d)
    if q:
        ql = q.lower()
        items = [x for x in items if ql in x['ar'].lower() or ql in x['zh'].lower() or ql in x['cat'].lower()]
    total = len(items)
    return {'total': total, 'items': items[page * size:(page + 1) * size], 'page': page, 'size': size, 'label': meta['label']}
