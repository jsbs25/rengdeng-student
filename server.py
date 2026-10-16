#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""阿拉伯语学习 - 网页 + DeepSeek AI + 文章 + 本地语音识别 (端口8080)"""
import gzip, json, os, random, re, urllib.request, urllib.parse, threading, tempfile
# 语音识别离线加载优先（模型已下载则不走网络）
os.environ.setdefault('HF_HUB_OFFLINE', '1')
os.environ.setdefault('HF_ENDPOINT', 'https://hf-mirror.com')
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, quote, urlencode
from urllib.error import HTTPError
from datetime import datetime
from email.utils import formatdate
from pathlib import Path
import time
try:
    import music_gen
except Exception:
    music_gen = None
try:
    import admin_panel
except Exception:
    admin_panel = None
import hashlib, hmac as _hmac, base64

# ===== 用户 / 会员系统 =====
USERS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'users.json')
try:
    import sys as _sys
    _sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass

def _load_secret():
    """SECRET：优先环境变量 → data/secret.txt（gitignore）→ 首次自动生成并持久化。"""
    v = (os.environ.get('NUR_SECRET') or '').strip()
    if v:
        return v
    _sp = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'secret.txt')
    try:
        v = open(_sp, encoding='utf-8').read().strip()
        if v:
            return v
    except Exception:
        pass
    import secrets as _secrets
    v = _secrets.token_hex(24)
    try:
        open(_sp, 'w', encoding='utf-8').write(v)
        os.chmod(_sp, 0o600)
    except Exception:
        pass
    return v

SECRET = _load_secret()
FREE_AI_DAILY = 20  # 普通用户每日 AI 次数

# ===== 简易 IP 限流（防滥用高成本接口；每 IP 每分钟上限）=====
_RATE = {}
_RATE_LOCK = threading.Lock()
_RATE_RULES = {
    '/api/tts': 10,
    '/api/image': 5,
    '/api/music': 3,
    '/api/asr': 10,
    '/api/chat/message': 30,
    '/api/chat/stream_voice': 10,
    '/api/page/analyze': 20,
    '/api/search': 60,
}

def _rate_limited(ip, path):
    """命中限流规则则返回需等待秒数；否则返回 None（放行）。"""
    lim = None
    for pref, n in _RATE_RULES.items():
        if path == pref or path.startswith(pref + '/'):
            lim = n
            break
    if lim is None:
        return None
    now = time.time()
    key = ip + '|' + path
    with _RATE_LOCK:
        hits = [t for t in _RATE.get(key, []) if now - t < 60]
        if len(hits) >= lim:
            _RATE[key] = hits
            return int(60 - (now - hits[0])) + 1
        hits.append(now)
        _RATE[key] = hits
        return None

# ===== 静态文件安全：禁止通过 HTTP 直接下载的敏感文件 =====
# 说明：_serve 会返回项目根目录下的静态文件，这里显式拒绝密钥/用户库/后台密码/源码等，
# 防止类似 GET /data/ai_key.txt、/data/users.json、/server.py 的裸奔下载。
SENSITIVE_STATIC_NAMES = {
    'users.json', 'codes.json', 'pays.json', 'unlocks.json', 'wx_users.json',
    'admin_pw.txt', 'ai_key.txt', 'ai_keys.json', 'ai_config.json', 'secret.txt',
    'openai_realtime_key.txt', 'openai_api_key.txt', 'dict_cn_cache.json',
}
SENSITIVE_STATIC_PREFIXES = ('ai_key', 'admin_pw', 'secret', 'server', 'cloud_server', 'admin_panel')
SENSITIVE_STATIC_SUFFIXES = ('.py', '.pyc', '.sh', '.keystore', '.jks', '.pem', '.key', '.db', '.sqlite', '.log')

def _load_users():
    try:
        if os.path.exists(USERS_FILE):
            return json.load(open(USERS_FILE, encoding='utf-8'))
    except Exception:
        pass
    return {}

def _save_users(u):
    os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
    json.dump(u, open(USERS_FILE, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

def _hash(pw):
    return hashlib.sha256((pw + SECRET).encode()).hexdigest()

def _mk_token(username):
    raw = f'{username}:{time.time():.0f}'
    sig = _hmac.new(SECRET.encode(), raw.encode(), hashlib.sha256).hexdigest()[:16]
    return base64.b64encode(f'{username}|{sig}'.encode()).decode()

def _check_token(token):
    try:
        raw = base64.b64decode(token.encode()).decode()
        u, sig = raw.split('|')
        users = _load_users()
        if u in users and users[u].get('token') == token:
            return u
    except Exception:
        pass
    return None

def _vip_info(username):
    users = _load_users()
    u = users.get(username, {})
    vip = bool(u.get('vip'))
    until = u.get('vip_until', '')
    if vip and until and until < time.strftime('%Y-%m-%d'):
        vip = False
    return vip, until

def _check_ai_quota(username):
    """普通用户每日次数限制：返回 (允许, 剩余, 提示)"""
    users = _load_users()
    u = users.setdefault(username, {})
    today = time.strftime('%Y-%m-%d')
    q = u.setdefault('ai_quota', {})
    if q.get('date') != today:
        q['date'] = today
        q['count'] = 0
    vip, _ = _vip_info(username)
    if vip:
        return True, -1, ''
    if q['count'] >= FREE_AI_DAILY:
        return False, 0, f'今日免费额度已用完（{FREE_AI_DAILY} 次）。开通会员可无限使用。'
    return True, FREE_AI_DAILY - q['count'], ''

CODES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'codes.json')

def _load_codes():
    try:
        if os.path.exists(CODES_FILE):
            return json.load(open(CODES_FILE, encoding='utf-8'))
    except Exception:
        pass
    return {'codes': {}}

def _save_codes(c):
    os.makedirs(os.path.dirname(CODES_FILE), exist_ok=True)
    json.dump(c, open(CODES_FILE, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

ADMIN_PW_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'admin_pw.txt')

def _admin_pw():
    """管理员密码：首次运行自动生成，存在 data/admin_pw.txt"""
    try:
        if os.path.exists(ADMIN_PW_FILE):
            pw = open(ADMIN_PW_FILE, encoding='utf-8').read().strip()
            if pw:
                return pw
    except Exception:
        pass
    pw = ''.join(random.choices('abcdefghijkmnpqrstuvwxyz23456789', k=12))
    os.makedirs(os.path.dirname(ADMIN_PW_FILE), exist_ok=True)
    open(ADMIN_PW_FILE, 'w', encoding='utf-8').write(pw)
    return pw

def _is_admin(h):
    """校验管理端密钥（Header X-Admin-Key 或 ?key=）"""
    try:
        key = (h.headers.get('X-Admin-Key') or '').strip()
        if not key:
            from urllib.parse import parse_qs
            key = (parse_qs(urlparse(h.path).query).get('key') or [''])[0]
        return bool(key) and key == _admin_pw()
    except Exception:
        return False

def _admin_codes_payload():
    c = _load_codes()
    items = [dict(v, code=k) for k, v in c.get('codes', {}).items()]
    items.sort(key=lambda x: (x.get('created', ''), x.get('used_at', '')), reverse=True)
    return {'ok': True, 'codes': items[:500], 'total': len(items),
            'used': sum(1 for i in items if i.get('used')),
            'active': sum(1 for i in items if not i.get('used') and i.get('enabled') is not False)}

def gen_code(days=30, batch=1, note='', plan=None, charge=None):
    """生成激活码（days 天会员）"""
    c = _load_codes()
    made = []
    for _ in range(batch):
        code = ''.join(random.choices('ABCDEFGHJKLMNPQRSTUVWXYZ23456789', k=12))
        code = code[:4] + '-' + code[4:8] + '-' + code[8:]
        if charge:
            code = ''.join(random.choices('ABCDEFGHJKLMNPQRSTUVWXYZ23456789', k=12))
            code = 'R' + code[:3] + '-' + code[3:7] + '-' + code[7:11]
            _amt = float(charge)
            _q = round(_amt * _pay_ratio(), 2)
            c['codes'][code] = {'days': 0, 'used': False, 'used_by': '', 'used_at': '',
                                'created': time.strftime('%Y-%m-%d'), 'enabled': True, 'note': note or ('充值码 ¥%.0f' % _amt),
                                'type': 'charge', 'amount': _amt, 'quota': _q, 'price': _amt}
            made.append(code)
            continue
        _pl = _plan(plan) if plan else None
        if _pl:
            days = int(_pl.get('days') or days)
        c['codes'][code] = {'days': days, 'used': False, 'used_by': '', 'used_at': '', 'created': time.strftime('%Y-%m-%d'),
                            'enabled': True, 'note': note, 'plan': (_pl or {}).get('id', 'free'),
                            'price': (_pl or {}).get('price', 0), 'quota': (_pl or {}).get('quota', 0)}
        made.append(code)
    _save_codes(c)
    return made

PRICING_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'pricing.json')
DEFAULT_PRICING = {
    'plans': [
        {'id': 'activate', 'name': '开通（一次性）', 'days': 3650, 'price': 100, 'quota': 0},
        {'id': 'topup', 'name': '充值', 'days': 0, 'price': 40, 'quota': 20},
    ],
    'pay': {'ratio': 1.0, 'amounts': [10, 20, 30], 'monthly_free': 0, 'auto_approve': True, 'sub_days': 30, 'sub_min': 10, 'entry_price': 10, 'entry_quota': 5, 'don_amounts': [10, 20, 40, 100],
            'activate_price': 100, 'topup_price': 40,
            'note': '首次付 ¥100 开通（一码一台设备）；AI 每月免费 ¥5；充值 ¥40 → 到账 ¥20 额度'},
    'rates': {'in_hit': 0.5, 'in_miss': 2.0, 'out': 8.0},
    'note': 'rates = 人民币元/百万 token；quota = 该套餐赠送的 AI 额度（元）'
}

def _load_pricing():
    try:
        if os.path.exists(PRICING_FILE):
            d = json.load(open(PRICING_FILE, encoding='utf-8'))
            if d.get('plans'):
                return d
    except Exception:
        pass
    _save_pricing(DEFAULT_PRICING)
    return DEFAULT_PRICING

def _save_pricing(d):
    try:
        os.makedirs(os.path.dirname(PRICING_FILE), exist_ok=True)
        json.dump(d, open(PRICING_FILE, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        return True
    except Exception:
        return False

def _plan(pid):
    plans = _load_pricing().get('plans', [])
    for p in plans:
        if p.get('id') == pid:
            return p
    return plans[0] if plans else {'id': 'month', 'name': '月卡', 'days': 30, 'price': 15, 'quota': 10}

def _cost_cny(usage):
    """按 DeepSeek 返回的 usage 折算人民币成本"""
    r = _load_pricing().get('rates', {})
    hit = usage.get('prompt_cache_hit_tokens', 0) or 0
    miss = usage.get('prompt_cache_miss_tokens')
    if miss is None:
        miss = max(0, (usage.get('prompt_tokens', 0) or 0) - hit)
    out = usage.get('completion_tokens', 0) or 0
    return (hit * r.get('in_hit', 0.5) + miss * r.get('in_miss', 2.0) + out * r.get('out', 8.0)) / 1000000.0

SPEND_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'ai_spend.json')

def _global_spend():
    """全站本月 AI 成本（元）"""
    try:
        d = json.load(open(SPEND_FILE, encoding='utf-8'))
    except Exception:
        d = {}
    p = time.strftime('%Y-%m')
    if d.get('period') != p:
        return 0.0
    return float(d.get('cny', 0) or 0)

def _add_global_spend(cost):
    try:
        p = time.strftime('%Y-%m')
        d = {}
        try:
            d = json.load(open(SPEND_FILE, encoding='utf-8'))
        except Exception:
            d = {}
        if d.get('period') != p:
            d = {'period': p, 'cny': 0.0}
        d['cny'] = round(float(d.get('cny', 0) or 0) + float(cost), 6)
        os.makedirs(os.path.dirname(SPEND_FILE), exist_ok=True)
        json.dump(d, open(SPEND_FILE, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    except Exception:
        pass

def _monthly_free():
    try:
        return float(_load_pricing().get('pay', {}).get('monthly_free', 5) or 5)
    except Exception:
        return 5.0

def _user_bal(u, save=False):
    """余额：本月免费额度 + 充值余额。返回 dict"""
    users = _load_users()
    v = users.get(u, {})
    period = time.strftime('%Y-%m')
    free = _monthly_free()
    if v.get('free_period') != period:
        v['free_period'] = period
        v['free_used'] = 0.0
        if save or True:
            users[u] = v
            _save_users(users)
    f_rem = max(0.0, free - float(v.get('free_used', 0) or 0))
    p_rem = max(0.0, float(v.get('paid_total', 0) or 0) - float(v.get('paid_used', 0) or 0))
    return {'ok': True, 'period': period, 'monthly_free': free,
            'free_left': round(f_rem, 4), 'paid_left': round(p_rem, 4),
            'paid_total': round(float(v.get('paid_total', 0) or 0), 2),
            'left': round(f_rem + p_rem, 4),
            'used_total': round(float(v.get('ai_used_cny', 0) or 0), 4),
            'calls': int(v.get('ai_calls', 0) or 0)}

def _user_quota(u):
    b = _user_bal(u)
    return b['left'], b['used_total']

def _ensure_entry_quota(u):
    """每个设备送一次欢迎额度（默认 ¥5）"""
    try:
        users = _load_users()
        v = users.setdefault(u, {})
        if v.get('welcome_granted'):
            return
        eq = float(_load_pricing().get('pay', {}).get('entry_quota', 5) or 5)
        v['paid_total'] = round(float(v.get('paid_total', 0) or 0) + eq, 2)
        v['welcome_granted'] = True
        _save_users(users)
        print(f'[欢迎额度] {u} +{eq:.0f} 元')
    except Exception:
        pass

def _charge_ai(username, usage):
    """AI 调用后扣额度：先扣本月免费额度，再扣充值余额"""
    try:
        cost = _cost_cny(usage or {})
        users = _load_users()
        v = users.setdefault(username, {})
        period = time.strftime('%Y-%m')
        if v.get('free_period') != period:
            v['free_period'] = period
            v['free_used'] = 0.0
        free = _monthly_free()
        f_used = float(v.get('free_used', 0) or 0)
        f_room = max(0.0, free - f_used)
        take_free = min(cost, f_room)
        v['free_used'] = round(f_used + take_free, 6)
        rest = cost - take_free
        if rest > 0:
            v['paid_used'] = round(float(v.get('paid_used', 0) or 0) + rest, 6)
        v['ai_used_cny'] = round(float(v.get('ai_used_cny', 0) or 0) + cost, 6)
        v['ai_calls'] = int(v.get('ai_calls', 0) or 0) + 1
        _save_users(users)
        _add_global_spend(cost)
        if cost > 0:
            print(f'[AI计费] {username} +{cost:.4f}元 / 累计 {v["ai_used_cny"]:.4f} 元')
    except Exception as e:
        print('[AI计费错误]', e)

def _pay_ratio():
    try:
        return float(_load_pricing().get('pay', {}).get('ratio', 0.5))
    except Exception:
        return 0.5

_SEARCH_IDX = {'data': None, 'ts': 0}

def _search_index():
    """懒加载全站内容索引（10 分钟缓存）"""
    now = time.time()
    if _SEARCH_IDX['data'] is not None and now - _SEARCH_IDX['ts'] < 600:
        return _SEARCH_IDX['data']
    idx = []
    try:
        import admin_panel as _ap
        for kind in _ap.KINDS:
            if kind in ('covers',):
                continue
            try:
                rows = _ap.data_list(kind, 0, 10 ** 9)
            except Exception:
                continue
            for r in rows.get('items', []):
                idx.append({'k': kind, 'key': r.get('key', ''), 'ar': r.get('ar', '')[:200],
                            'zh': r.get('zh', '')[:200], 'cat': r.get('cat', '')[:40]})
    except Exception as e:
        print('[搜索索引错误]', e)
    _SEARCH_IDX.update({'data': idx, 'ts': now})
    print(f'[搜索索引] 已建立 {len(idx)} 条')
    return idx

CLASSICS_INDEX_PATH = Path(__file__).parent / 'data' / 'library' / 'classics_index.json'
_CLASSICS_INDEX_CACHE = {'mtime': 0.0, 'data': None}

def _classics_index():
    """经典扩展索引：只读元数据，正文仍由现有 Shamela 按需入口读取。"""
    try:
        mt = CLASSICS_INDEX_PATH.stat().st_mtime
        if _CLASSICS_INDEX_CACHE['data'] is not None and _CLASSICS_INDEX_CACHE['mtime'] == mt:
            return _CLASSICS_INDEX_CACHE['data']
        d = json.loads(CLASSICS_INDEX_PATH.read_text(encoding='utf-8'))
        if not isinstance(d, dict):
            raise ValueError('classics index must be an object')
        d.setdefault('items', [])
        d.setdefault('reading_paths', [])
        d.setdefault('meta', {})
        _CLASSICS_INDEX_CACHE.update({'mtime': mt, 'data': d})
        return d
    except Exception as e:
        print('[经典索引]', e)
        return {'meta': {'total': 0}, 'items': [], 'reading_paths': []}


def _search_books(q, limit=60):
    """搜索书名：中文古籍 + 阿拉伯典籍 + 六大部"""
    ql = (q or '').strip().lower()
    if len(ql) < 1:
        return []
    out = []
    try:
        d = json.load(open(DIR / 'data' / 'cn_books' / 'index.json', encoding='utf-8'))
        for b in (d.get('books') or []):
            t = b.get('title') or ''
            if ql in t.lower():
                out.append({'k': 'cnbook', 'key': b.get('id', ''), 'ar': '', 'zh': t,
                            'cat': b.get('category', ''), 'rt': 'cn'})
                if len(out) >= limit:
                    return out
    except Exception:
        pass
    try:
        d = json.load(open(DIR / 'data' / 'islamic_catalog.json', encoding='utf-8'))
        for b in (d.get('items') or d.get('books') or []):
            t = b.get('t') or b.get('title') or ''
            if ql in t.lower():
                r = b.get('r') or {}
                out.append({'k': 'arbook', 'key': r.get('id') or b.get('id', ''), 'ar': t,
                            'zh': '', 'cat': b.get('cat', ''), 'rt': r.get('t') or 'shamela'})
                if len(out) >= limit:
                    return out
    except Exception:
        pass
    # 经典扩展索引：只收本地 Shamela 可读条目，不把外部正文伪装成站内内容。
    try:
        existing = {str(x.get('key') or '') for x in out}
        for b in (_classics_index().get('items') or []):
            t = str(b.get('title_ar') or b.get('title') or '')
            hay = ' '.join(str(b.get(k) or '') for k in ('title_ar', 'title', 'collection_label', 'source_pool'))
            bid = str(b.get('id') or '')
            if bid and bid not in existing and ql in hay.lower():
                out.append({'k': 'arbook', 'key': bid, 'ar': t,
                            'zh': b.get('collection_label', ''),
                            'cat': b.get('collection_label', ''), 'rt': 'shamela',
                            'source': 'classics_index'})
                existing.add(bid)
                if len(out) >= limit:
                    return out
    except Exception:
        pass
    try:
        d = json.load(open(DIR / 'data' / 'hadith' / 'index.json', encoding='utf-8'))
        for b in (d.get('books') or []):
            if ql in (b.get('cn') or '').lower() or ql in (b.get('ar') or '').lower():
                out.append({'k': 'hadith', 'key': b.get('key', ''), 'ar': b.get('ar', ''),
                            'zh': b.get('cn', ''), 'cat': '六大部', 'rt': 'h6'})
    except Exception:
        pass
    return out


def _search(q, limit=120):
    ql = (q or '').strip().lower()
    if len(ql) < 1:
        return []
    out = _search_books(q, limit)
    for it in _search_index():
        if ql in it['ar'].lower() or ql in it['zh'].lower() or ql in it['cat'].lower():
            out.append(it)
            if len(out) >= limit:
                break
    return out

SUB_DAYS_DEFAULT = 30

def _sub_until():
    try:
        d = int(_load_pricing().get('pay', {}).get('sub_days', 30) or 30)
    except Exception:
        d = 30
    return time.strftime('%Y-%m-%d', time.localtime(time.time() + d * 86400))

def _sub_status(u):
    """返回 (是否有效, 到期日, 剩余天数)"""
    users = _load_users()
    v = users.get(u, {})
    until = (v.get('sub_until') or '').strip()
    today = time.strftime('%Y-%m-%d')
    if not until:
        return False, '', 0
    try:
        left = int((time.mktime(time.strptime(until, '%Y-%m-%d')) - time.mktime(time.strptime(today, '%Y-%m-%d'))) / 86400)
    except Exception:
        left = 0
    return (left >= 0), until, max(0, left)

UNLOCK_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'unlocks.json')

def _load_unlocks():
    try:
        if os.path.exists(UNLOCK_FILE):
            d = json.load(open(UNLOCK_FILE, encoding='utf-8'))
            if isinstance(d, dict) and 'codes' in d:
                return d
    except Exception:
        pass
    return {'codes': {}}

def _save_unlocks(d):
    try:
        os.makedirs(os.path.dirname(UNLOCK_FILE), exist_ok=True)
        json.dump(d, open(UNLOCK_FILE, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        return True
    except Exception:
        return False

PAY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'payments.json')

VIDEOS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'videos.json')

def _home_stats():
    """首页实时统计：所有数字都从数据文件现算"""
    D = os.path.join(DIR, 'data')
    out = {'time': time.strftime('%Y-%m-%d %H:%M:%S')}

    def _n(f, key=None):
        try:
            d = json.load(open(os.path.join(D, f), encoding='utf-8'))
            if key:
                return len(d.get(key, {}))
            return len(d) if hasattr(d, '__len__') else 0
        except Exception:
            return 0

    try:
        c = json.load(open(os.path.join(D, 'islamic_catalog.json'), encoding='utf-8'))
        m = c.get('meta', {}) if isinstance(c, dict) else {}
        out['islamic_total'] = int(m.get('total') or 0)
        out['islamic_readable'] = int(m.get('readable') or 0)
        out['islamic_shamela'] = int(m.get('readable_shamela') or 0)
        out['islamic_waqfeya'] = int(m.get('readable_waqfeya') or 0)
    except Exception:
        pass
    h = _n('hadith_all.json') + _n('hadith_api.json')
    try:
        hi = json.load(open(os.path.join(D, 'hadith_info.json'), encoding='utf-8'))
        if isinstance(hi, dict):
            for _k, v in hi.items():
                if isinstance(v, dict):
                    for _kk, vv in v.items():
                        if isinstance(vv, list):
                            h += len(vv)
                elif isinstance(v, list):
                    h += len(v)
    except Exception:
        pass
    out['hadith'] = h
    out['quran'] = _n('tafsir.json')
    out['sentences'] = _n('categorized.json')
    out['articles'] = _n('articles.json')
    out['dialogues'] = _n('dialogues.json')
    out['quotes'] = _n('quotes.json')
    out['history_articles'] = _n('history.json')
    out['videos'] = _n('videos.json', 'videos')
    out['vocab_meanings'] = _n('vocab_meanings.json')
    try:
        out['cn_books'] = len(_cn_books().get('books', []))
    except Exception:
        pass
    try:
        hb = _history().get('books', [])
        out['history_books'] = len(hb)
        langs = {}
        for b in hb:
            langs[b.get('lang') or '?'] = langs.get(b.get('lang') or '?', 0) + 1
        out['history_langs'] = langs
    except Exception:
        pass
    try:
        cv = json.load(open(os.path.join(D, 'civ.json'), encoding='utf-8'))
        for k, v in cv.items():
            n = len(v) if isinstance(v, list) else (sum(len(x) for x in v.values() if isinstance(x, list)) if isinstance(v, dict) else 0)
            out['civ_' + k] = n
    except Exception:
        pass
    try:
        rl = json.load(open(os.path.join(D, 'civ_rulers.json'), encoding='utf-8'))
        n = 0
        for _k, v in rl.items():
            if isinstance(v, list):
                n += len(v)
            elif isinstance(v, dict):
                n += sum(len(x) for x in v.values() if isinstance(x, list)) or 1
        out['rulers'] = n
    except Exception:
        out['rulers'] = _n('civ_rulers.json')
    out['covers'] = _n('covers.json')
    try:
        bs = json.load(open(os.path.join(D, 'stats.json'), encoding='utf-8'))
        for k, v in bs.items():
            out.setdefault(k, v)
    except Exception:
        pass
    return out

def _load_videos():
    try:
        return json.load(open(VIDEOS_FILE, encoding='utf-8'))
    except Exception:
        return {'cats': [], 'videos': []}

def _load_pays():
    try:
        if os.path.exists(PAY_FILE):
            d = json.load(open(PAY_FILE, encoding='utf-8'))
            if isinstance(d, dict) and 'items' in d:
                return d
    except Exception:
        pass
    return {'items': []}

def _save_pays(d):
    try:
        os.makedirs(os.path.dirname(PAY_FILE), exist_ok=True)
        json.dump(d, open(PAY_FILE, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        return True
    except Exception:
        return False

def _norm_code(c):
    """激活码归一化：去空格/横杠、转大写，12 位自动补横杠"""
    raw = (c or '').strip().upper()
    alnum = ''.join(ch for ch in raw if ch.isalnum())
    if len(alnum) == 12:
        return f'{alnum[:4]}-{alnum[4:8]}-{alnum[8:]}'
    return raw

def activate_code(username, code):
    """兑换激活码：开通会员"""
    code = _norm_code(code)
    c = _load_codes()
    if code not in c['codes']:
        print(f'[激活失败] 用户={username} 码={code!r} 原因=不存在 (可用码数={len(c["codes"])})')
        return False, '激活码不存在'
    cd = c['codes'][code]
    if cd.get('enabled') is False:
        return False, '激活码已停用，请联系管理员'
    if cd.get('used'):
        print(f'[激活失败] 用户={username} 码={code} 原因=已被使用 by {cd.get("used_by")}')
        return False, '激活码已被使用'
    cd['used'] = True
    cd['used_by'] = username
    cd['used_at'] = time.strftime('%Y-%m-%d %H:%M')
    _save_codes(c)
    print(f'[激活成功] 用户={username} 码={code} {cd.get("days")}天')
    users = _load_users()
    u = users.setdefault(username, {})
    _q = cd.get('quota')
    # 充值码：只加额度，不改会员期
    if cd.get('type') == 'charge':
        amt = float(cd.get('amount') or _q or 0)
        u['ai_quota_cny'] = round(float(u.get('ai_quota_cny', 0) or 0) + amt, 2)
        _save_users(users)
        print(f'[充值成功] 用户={username} 码={code} +{amt:.2f}元')
        return True, f'充值成功！已到账 {amt:.2f} 元 AI 额度'
    u['vip'] = True
    if _q is None:
        _q = 0
    u['ai_quota_cny'] = round(float(u.get('ai_quota_cny', 0) or 0) + float(_q or 0), 2)
    u['vip_until'] = time.strftime('%Y-%m-%d', time.localtime(time.time() + cd['days'] * 86400))
    _save_users(users)
    print(f'[激活成功] 用户={username} 配额+{_q}元 会员至{u["vip_until"]}')
    if float(_q or 0) > 0:
        return True, f'开通成功！会员至 {u["vip_until"]}（{cd["days"]} 天），含 AI 额度 {float(_q):.2f} 元'
    return True, f'激活成功！（{cd["days"]} 天）基础功能已开通，AI 需另外开通'

def _consume_quota(username):
    users = _load_users()
    u = users.setdefault(username, {})
    q = u.setdefault('ai_quota', {})
    today = time.strftime('%Y-%m-%d')
    if q.get('date') != today:
        q['date'] = today
        q['count'] = 0
    q['count'] += 1
    _save_users(users)

DIR = Path(__file__).parent

# ===== 首页今日一句：只读真实句子源，按文件mtime缓存 =====
_SENTENCE_SOURCE = DIR / 'data' / 'categorized.json'
_SENTENCE_CACHE = {'mtime_ns': None, 'items': [], 'total': 0}
_SENTENCE_CACHE_LOCK = threading.Lock()

def _sentence_daily_payload():
    """返回有界的今日句子摘要；不改变 categorized.json。"""
    stat = _SENTENCE_SOURCE.stat()
    with _SENTENCE_CACHE_LOCK:
        if _SENTENCE_CACHE['mtime_ns'] != stat.st_mtime_ns:
            raw = json.loads(_SENTENCE_SOURCE.read_text(encoding='utf-8'))
            items = []
            for item in raw if isinstance(raw, list) else []:
                if not isinstance(item, dict):
                    continue
                items.append({'a': str(item.get('ar') or ''),
                              'e': str(item.get('en') or ''),
                              'c': str(item.get('cn') or ''),
                              'cat': str(item.get('cat') or 'other')})
            _SENTENCE_CACHE.update({'mtime_ns': stat.st_mtime_ns,
                                    'items': items, 'total': len(items)})
        total = int(_SENTENCE_CACHE['total'] or 0)
        date = datetime.now().strftime('%Y-%m-%d')
        index = int(datetime.now().strftime('%Y%m%d')) % total if total else 0
        item = dict(_SENTENCE_CACHE['items'][index]) if total else {'a': '', 'e': '', 'c': '', 'cat': 'other'}
    return {'ok': True, 'date': date, 'index': index, 'total': total, 'item': item}

# ===== 右侧来源监测台：只读白名单同步缓存，不接受任意 URL =====
_PUBLIC_SOURCE_CATALOG = [
    {'id': 'ar-wiktionary', 'title': 'Arabic Wiktionary', 'title_zh': '阿拉伯语词典', 'kind': 'dictionary', 'kind_label': '词典', 'url': 'https://ar.wiktionary.org/w/api.php', 'license': 'CC BY-SA 4.0 / GFDL；逐条核验词条和媒体许可', 'action': '只读取词条样例'},
    {'id': 'tatoeba', 'title': 'Tatoeba', 'title_zh': '阿语例句库', 'kind': 'sentences', 'kind_label': '例句', 'url': 'https://api.tatoeba.org/', 'license': '逐句 CC BY 2.0 FR 或 CC0；音频另行核验', 'action': '只读取句子元数据'},
    {'id': 'openiti-release', 'title': 'OpenITI RELEASE', 'title_zh': 'OpenITI 典籍', 'kind': 'texts', 'kind_label': '典籍', 'url': 'https://github.com/OpenITI/RELEASE', 'license': 'CC BY-NC-SA 4.0；非商业、署名、相同方式共享', 'action': '按需读取公开原文'},
    {'id': 'arabic-wikipedia', 'title': 'Arabic Wikipedia', 'title_zh': '阿拉伯语百科', 'kind': 'reading', 'kind_label': '阅读', 'url': 'https://ar.wikipedia.org/w/api.php', 'license': '通常 CC BY-SA 4.0；逐页核验页面和媒体来源', 'action': '只读取页面摘要'},
    {'id': 'common-voice-mdc', 'title': 'Mozilla Common Voice', 'title_zh': '阿拉伯语语音元数据', 'kind': 'audio-metadata', 'kind_label': '语音', 'url': 'https://mozilladatacollective.com/datasets/cmu5wom3z00ceo107guxtg4xa', 'license': 'CC0 数据集标记；遵循 Mozilla/MDC 分发条款', 'action': '只读取数据集元数据'},
]

def _public_source_feed(query='', kind='', status='all', limit=20):
    """把每周同步留下的来源状态变成可审计、可过滤的右侧记录。
    该函数不发起网络请求、不执行爬虫；网络工作只由白名单 systemd job 完成。
    """
    try:
        limit = max(1, min(int(limit or 20), 20))
    except Exception:
        limit = 20
    query = str(query or '').strip().lower()
    kind = str(kind or '').strip().lower()
    status = str(status or 'all').strip().lower()
    cache_dir = DIR / 'data' / 'public_source_cache'
    report = {}
    sample = {}
    try:
        report = json.loads((cache_dir / 'status.json').read_text(encoding='utf-8'))
    except Exception:
        report = {}
    try:
        sample = json.loads((cache_dir / 'wiktionary-sample.json').read_text(encoding='utf-8'))
    except Exception:
        sample = {}
    health = {str(x.get('id')): x for x in (report.get('sources') or []) if isinstance(x, dict)}
    rows = []
    for base in _PUBLIC_SOURCE_CATALOG:
        row = dict(base)
        observed = health.get(base['id'], {})
        row.update({k: observed[k] for k in ('ok', 'http_status', 'retrieved_at', 'etag', 'last_modified', 'error') if k in observed})
        row['ok'] = bool(observed.get('ok'))
        row['status'] = 'healthy' if row['ok'] else ('pending' if not observed else 'review')
        row['status_label'] = {'healthy': '可用', 'pending': '待同步', 'review': '需复核'}[row['status']]
        row['allowlisted'] = True
        row['bounded'] = True
        haystack = ' '.join(str(row.get(k) or '') for k in ('id', 'title', 'title_zh', 'kind', 'kind_label', 'license', 'action')).lower()
        if kind not in ('', 'all') and kind not in (row['kind'], row['kind_label'].lower()):
            continue
        if status not in ('', 'all') and status != row['status']:
            continue
        if query and query not in haystack:
            continue
        rows.append(row)
    healthy = sum(1 for x in rows if x['status'] == 'healthy')
    review = sum(1 for x in rows if x['status'] == 'review')
    pending = sum(1 for x in rows if x['status'] == 'pending')
    return {
        'ok': True, 'mode': 'cached-allowlist', 'job': report.get('job', 'public-source-sync'),
        'started_at': report.get('started_at', ''), 'finished_at': report.get('finished_at', ''), 'last_sync': report.get('finished_at', ''),
        'policy': report.get('policy') or {'allowlist_only': True, 'max_response_bytes': 2 * 1024 * 1024, 'request_spacing_seconds': 1.1, 'bulk_downloads': False, 'overwrites_user_data': False},
        'filters': {'q': query, 'kind': kind or 'all', 'status': status or 'all'}, 'total': len(_PUBLIC_SOURCE_CATALOG), 'visible': len(rows), 'healthy': healthy, 'review': review, 'pending': pending, 'filtered_out': len(_PUBLIC_SOURCE_CATALOG) - len(rows),
        'sample': {'title': sample.get('title', ''), 'source_url': sample.get('source_url', ''), 'retrieved_at': sample.get('retrieved_at', ''), 'extract': sample.get('extract', '')[:220]} if sample else None,
        'sources': rows[:limit],
    }
# ===== 应用内音频资料库：只索引项目已有文件，不抓取外部音频 =====
AUDIO_EXTENSIONS = {'.flac', '.wav', '.m4a', '.mp3', '.ogg', '.aac'}
AUDIO_CONTENT_TYPES = {
    '.flac': 'audio/flac', '.wav': 'audio/wav', '.m4a': 'audio/mp4',
    '.mp3': 'audio/mpeg', '.ogg': 'audio/ogg', '.aac': 'audio/aac'
}

def _audio_roots():
    """资料库根目录白名单；不允许通过请求路径访问任意文件。"""
    music_dir = Path(getattr(music_gen, 'OUT_DIR', '') or (DIR / 'music_out'))
    return {
        'athan': (DIR / 'athan', '宣礼与礼拜'),
        'music': (music_dir, 'AI 生成与语音'),
    }

def _audio_resolve(root, name):
    roots = _audio_roots()
    if root not in roots:
        raise ValueError('unknown audio root')
    raw = str(name or '').replace('\\', '/').lstrip('/')
    rel = Path(raw)
    if not raw or rel.is_absolute() or '..' in rel.parts:
        raise ValueError('bad audio name')
    base = roots[root][0].resolve()
    fp = (base / rel).resolve()
    try:
        if os.path.commonpath([str(base), str(fp)]) != str(base):
            raise ValueError('audio path outside allowlist')
    except ValueError:
        raise ValueError('audio path outside allowlist')
    if not fp.is_file() or fp.suffix.lower() not in AUDIO_EXTENSIONS:
        raise FileNotFoundError('audio file not found')
    return fp

def _audio_title(root, fp):
    stem = fp.stem.replace('_', ' ').replace('-', ' ').strip()
    if root == 'athan':
        names = {
            'abdulbasit': '阿卜杜勒·巴西特', 'alafasy': '阿法西',
            'amade': '阿马迪', 'aqsa': '阿克萨古城', 'awad': '阿瓦德',
            'dahbe': '达赫贝', 'kassab': '卡萨布', 'madinah': '麦地那圣寺',
            'makkah': '麦加禁寺', 'minshawi': '明沙维', 'riyadh': '利雅得',
            'saadoun': '萨阿敦', 'saleh': '萨利赫', 'surehi': '苏莱希',
            'trabulsi': '特拉布勒西'
        }
        return names.get(fp.stem.lower(), stem)
    return stem or fp.name

def _audio_library(query='', fmt='', limit=240):
    q = str(query or '').strip().lower()
    fmt = str(fmt or '').strip().lower().lstrip('.')
    try:
        limit = max(1, min(int(limit or 240), 500))
    except Exception:
        limit = 240
    items = []
    for root, (base, category) in _audio_roots().items():
        if not base.is_dir():
            continue
        try:
            files = sorted(base.rglob('*'), key=lambda p: (p.suffix.lower(), p.name.lower()))
        except Exception:
            files = []
        for fp in files:
            if not fp.is_file() or fp.suffix.lower() not in AUDIO_EXTENSIONS:
                continue
            try:
                rel = fp.relative_to(base).as_posix()
                ext = fp.suffix.lower().lstrip('.')
                title = _audio_title(root, fp)
                hay = ' '.join((title, rel, category, ext)).lower()
                if q and q not in hay:
                    continue
                if fmt and ext != fmt:
                    continue
                items.append({
                    'id': hashlib.sha1((root + ':' + rel).encode('utf-8')).hexdigest()[:16],
                    'root': root, 'name': rel, 'title': title, 'category': category,
                    'ext': ext, 'size': fp.stat().st_size,
                    'modified': datetime.fromtimestamp(fp.stat().st_mtime).isoformat(timespec='seconds'),
                    'codec': '无损 / 原生播放' if ext in ('flac', 'wav') else '浏览器原生播放',
                    'url': '/api/audio/file?root=' + quote(root, safe='') + '&name=' + quote(rel, safe='')
                })
            except (OSError, ValueError):
                continue
    items.sort(key=lambda x: (x['category'], x['title'].lower(), x['name'].lower()))
    return items[:limit]

# ===== 古兰经经注：按章请求、短期缓存、来源显式标注 =====
TAFSIR_CACHE_DIR = DIR / 'cache' / 'tafsir'
TAFSIR_EDITIONS = {
    'ar.muyassar': {'name': 'تفسير المیسر', 'label': '阿拉伯语 · 经注 المیسر'},
    'ar.jalalayn': {'name': 'تفسير الجلالين', 'label': '阿拉伯语 · 经注 الجلالين'},
}

def _quran_tafsir( surah, edition='ar.muyassar'):
    """从 AlQuran.Cloud 按章取经注；不抓网页，缓存时间有限并返回来源。"""
    try:
        sid = max(1, min(int(surah), 114))
    except Exception:
        raise ValueError('invalid surah')
    edition = edition if edition in TAFSIR_EDITIONS else 'ar.muyassar'
    TAFSIR_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    fp = TAFSIR_CACHE_DIR / (edition.replace('.', '_') + '_' + str(sid) + '.json')
    # 6 小时短缓存：避免重复请求，同时不把上游内容做成永久镜像。
    if fp.exists() and time.time() - fp.stat().st_mtime < 6 * 3600:
        try:
            return json.loads(fp.read_text(encoding='utf-8'))
        except Exception:
            pass
    url = 'https://api.alquran.cloud/v1/surah/%d/%s' % (sid, edition)
    req = urllib.request.Request(url, headers={'User-Agent': 'NourArabicLearning/1.0'})
    with urllib.request.urlopen(req, timeout=20) as resp:
        payload = json.loads(resp.read().decode('utf-8'))
    if payload.get('code') != 200 or not isinstance(payload.get('data'), dict):
        raise RuntimeError('tafsir upstream returned an invalid response')
    data = payload['data']
    out = {
        'surah': sid,
        'edition': edition,
        'edition_name': (data.get('edition') or {}).get('name') or TAFSIR_EDITIONS[edition]['name'],
        'source_name': 'AlQuran.Cloud',
        'source_url': url,
        'retrieved_at': datetime.utcnow().isoformat() + 'Z',
        'ayahs': [{'number': int(x.get('numberInSurah') or 0), 'text': str(x.get('text') or '')}
                  for x in (data.get('ayahs') or [])]
    }
    try:
        tmp = Path(str(fp) + '.tmp')
        tmp.write_text(json.dumps(out, ensure_ascii=False), encoding='utf-8')
        tmp.replace(fp)
    except Exception:
        pass
    return out

# ===== 圣训「译文 + 经注」生成与缓存 =====
_AN = {}


def _an_path(book):
    return DIR / 'data' / 'hadith' / 'an' / (book + '.json')


def _an_get(book):
    if book not in _AN:
        try:
            _AN[book] = json.loads(_an_path(book).read_text(encoding='utf-8'))
        except Exception:
            _AN[book] = {}
    return _AN[book]


def _an_save(book):
    p = _an_path(book)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = str(p) + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(_AN.get(book, {}), f, ensure_ascii=False)
    os.replace(tmp, p)


def _lingva(text, src='zh', dst='ar'):
    """免费翻译：Lingva（开源、无需密钥）"""
    try:
        u = 'https://lingva.ml/api/v1/' + src + '/' + dst + '/' + urllib.parse.quote(text[:480])
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=25) as r:
            d = json.loads(r.read().decode('utf-8'))
        return (d.get('translation') or '').strip()
    except Exception as e:
        print('[Lingva 失败]', e)
        return ''


def _wiktionary(word):
    """免费词典：Wiktionary（无需密钥）"""
    try:
        titles = [str(word or '').strip()]
        base = 'https://ar.wiktionary.org/w/api.php'
        def query_titles(ts):
            u = base + '?' + urllib.parse.urlencode({
                'action': 'query', 'prop': 'extracts', 'explaintext': '1',
                'format': 'json', 'titles': '|'.join(ts)
            })
            req = urllib.request.Request(u, headers={'User-Agent': 'NourArabicLearning/1.0'})
            with urllib.request.urlopen(req, timeout=20) as r:
                return json.loads(r.read().decode('utf-8'))
        d = query_titles(titles)
        for _, pg in ((d.get('query') or {}).get('pages') or {}).items():
            t = (pg.get('extract') or '').strip()
            if t:
                return t[:900]
        # Arabic entries often store the fully vocalized headword separately.
        # One bounded search recovers it without crawling or enumerating pages.
        if titles[0]:
            su = base + '?' + urllib.parse.urlencode({
                'action': 'query', 'list': 'search', 'srsearch': titles[0],
                'srlimit': '3', 'format': 'json'
            })
            req = urllib.request.Request(su, headers={'User-Agent': 'NourArabicLearning/1.0'})
            with urllib.request.urlopen(req, timeout=20) as r:
                sd = json.loads(r.read().decode('utf-8'))
            hits = [x.get('title') for x in ((sd.get('query') or {}).get('search') or []) if x.get('title')]
            if hits:
                d = query_titles(hits)
                for _, pg in ((d.get('query') or {}).get('pages') or {}).items():
                    t = (pg.get('extract') or '').strip()
                    if t:
                        return t[:900]
                for title in hits[:3]:
                    d = query_titles([title])
                    for _, pg in ((d.get('query') or {}).get('pages') or {}).items():
                        t = (pg.get('extract') or '').strip()
                        if t:
                            return t[:900]
    except Exception:
        pass
    return ''


_AR_DICT_MARKS = re.compile(r'[\u0610-\u061A\u064B-\u0652\u0670\u0640]')
_LOCAL_DICT_CACHE = {
    'mtime': 0, 'sent_mtime': 0, 'index_mtime': 0,
    'lesson_mtimes': (), 'lessons': [],
    'meanings': {}, 'sentences': [], 'index': {}
}
def _dict_norm(word):
    """规范化阿拉伯单词，只去除音符、伸展符和多余空白，不改动原词。"""
    s = re.sub(r'\s+', ' ', str(word or '')).strip()
    s = _AR_DICT_MARKS.sub('', s)
    return s

def _dictionary_index():
    """Load the generated local index once; an invalid/missing index never blocks lookup."""
    path = DIR / 'data' / 'dictionary_index.json'
    try:
        mt = path.stat().st_mtime_ns if path.exists() else 0
        if mt and _LOCAL_DICT_CACHE.get('index_mtime') == mt:
            return _LOCAL_DICT_CACHE.get('index') or {}
        raw = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
        if not isinstance(raw, dict) or raw.get('version') != 1:
            raw = {}
        _LOCAL_DICT_CACHE.update({'index_mtime': mt, 'index': raw})
        return raw
    except Exception:
        return _LOCAL_DICT_CACHE.get('index') or {}

def _local_dict_lookup(word):
    """本地优先查词：固定数据、无模型、无账号、可离线使用。"""
    q = str(word or '').strip()[:80]
    key = _dict_norm(q)
    if not key:
        return {'ok': True, 'found': False, 'word': q, 'normalized': ''}
    mf = DIR / 'data' / 'vocab_meanings.json'
    sf = DIR / 'data' / 'data.json'
    try:
        mt = mf.stat().st_mtime_ns if mf.exists() else 0
        st = sf.stat().st_mtime_ns if sf.exists() else 0
        if (_LOCAL_DICT_CACHE.get('mtime') != mt or
                _LOCAL_DICT_CACHE.get('sent_mtime') != st):
            raw = json.loads(mf.read_text(encoding='utf-8')) if mf.exists() else {}
            meanings = {}
            if isinstance(raw, dict):
                for k, v in raw.items():
                    if isinstance(v, dict):
                        meanings[_dict_norm(k)] = {
                            'w': k, 'cn': str(v.get('cn') or ''),
                            'en': str(v.get('en') or '')
                        }
            elif isinstance(raw, list):
                for v in raw:
                    if isinstance(v, dict) and v.get('w'):
                        meanings[_dict_norm(v['w'])] = dict(v)
            sentences = []
            if sf.exists():
                data = json.loads(sf.read_text(encoding='utf-8'))
                if isinstance(data, list):
                    sentences = data
            _LOCAL_DICT_CACHE.update({'mtime': mt, 'sent_mtime': st,
                                      'meanings': meanings, 'sentences': sentences})
    except Exception:
        pass
    meanings = _LOCAL_DICT_CACHE.get('meanings') or {}
    exact = meanings.get(key)
    examples = []
    sentence_rows = _LOCAL_DICT_CACHE.get('sentences') or []
    index = _dictionary_index()
    indexed_ids = ((index.get('examples') or {}).get(key) if index else None) or []
    for idx in indexed_ids:
        if not isinstance(idx, int) or idx < 0 or idx >= len(sentence_rows):
            continue
        item = sentence_rows[idx] or {}
        examples.append({'ar': str(item.get('ar') or ''),
                         'cn': str(item.get('cn') or ''),
                         'en': str(item.get('en') or '')})
    if not examples:
        for item in sentence_rows:
            ar = str((item or {}).get('ar') or '')
            if key and _dict_norm(ar).find(key) >= 0:
                examples.append({'ar': ar, 'cn': str((item or {}).get('cn') or ''),
                                 'en': str((item or {}).get('en') or '')})
                if len(examples) >= 6:
                    break
    matches = []
    for nk, item in meanings.items():
        # Prefix/substring suggestions are useful for a short inflected ending,
        # but a long unrelated query must not match a tiny dictionary head.
        close = bool(nk and nk != key and (key in nk or
                    (key.startswith(nk) and len(key) - len(nk) <= 2)))
        if close:
            matches.append(item)
            if len(matches) >= 12:
                break
    return {'ok': True, 'found': bool(exact or examples or matches), 'word': q,
            'normalized': key, 'meaning': exact or {}, 'examples': examples,
            'matches': matches, 'source': '本地固定词库与句子库',
            'offline': True}

def _dict_suggest(word, limit=8):
    """Return short prefix suggestions from local real data, bounded for mobile input."""
    q = str(word or '').strip()[:80]
    key = _dict_norm(q)
    try:
        limit = max(1, min(int(limit), 12))
    except Exception:
        limit = 8
    if not key or any(ord(c) < 0x0600 or ord(c) > 0x06ff for c in key):
        return {'ok': True, 'query': q, 'normalized': key, 'items': [],
                'source': '本地阿语词头索引', 'offline': True}
    index = _dictionary_index()
    meanings = index.get('meanings') or {}
    prefixes = index.get('prefix') or {}
    bucket = prefixes.get(key[:min(3, len(key))], []) if prefixes else []
    candidates = []
    for term in bucket:
        if term.startswith(key) and term not in candidates:
            candidates.append(term)
        if len(candidates) >= limit:
            break
    if key in meanings and key not in candidates:
        candidates.insert(0, key)
    items = []
    for term in candidates[:limit]:
        m = meanings.get(term) or {}
        items.append({'w': str(m.get('w') or term),
                      'normalized': term, 'cn': str(m.get('cn') or ''),
                      'en': str(m.get('en') or '')})
    return {'ok': True, 'query': q, 'normalized': key, 'items': items,
            'source': '本地阿语词头索引', 'offline': True}

def _dictionary_lesson_links(word, limit=6):
    """Return bounded links to existing grammar/morphology lessons only."""
    q = str(word or '').strip()[:80]
    key = _dict_norm(q)
    try:
        limit = max(1, min(int(limit), 12))
    except Exception:
        limit = 6
    if not key or len(key) < 2 or any(ord(c) < 0x0600 or ord(c) > 0x06ff for c in key):
        return {'ok': True, 'query': q, 'normalized': key, 'items': [],
                'source': '本地语法与词法课程', 'offline': True}
    paths = (DIR / 'data' / 'grammar.json', DIR / 'data' / 'morphology.json')
    mtimes = tuple(p.stat().st_mtime_ns if p.exists() else 0 for p in paths)
    if _LOCAL_DICT_CACHE.get('lesson_mtimes') != mtimes:
        lessons = []
        for kind, path in zip(('grammar', 'morph'), paths):
            try:
                raw = json.loads(path.read_text(encoding='utf-8')) if path.exists() else []
            except Exception:
                raw = []
            if not isinstance(raw, list):
                raw = []
            for row in raw:
                if isinstance(row, dict):
                    lessons.append((kind, row))
        _LOCAL_DICT_CACHE.update({'lesson_mtimes': mtimes, 'lessons': lessons})
    hits = []
    for kind, row in _LOCAL_DICT_CACHE.get('lessons') or []:
        points = row.get('points') if isinstance(row.get('points'), list) else []
        matched = []
        for point in points:
            if not isinstance(point, dict):
                continue
            ar = str(point.get('ar') or '').strip()
            if ar and key in _dict_norm(ar) and ar not in matched:
                matched.append(ar)
        title_ar = str(row.get('title_ar') or '')
        intro = str(row.get('intro') or '')
        tip = str(row.get('tip') or '')
        title_hit = bool(key in _dict_norm(title_ar))
        text_hit = bool(key in _dict_norm(intro + ' ' + tip))
        if not matched and not title_hit and not text_hit:
            continue
        score = (5 if matched else 0) + (3 if title_hit else 0) + (1 if text_hit else 0)
        hits.append({'kind': kind, 'id': str(row.get('id') or ''),
                     'title': str(row.get('title') or ''),
                     'title_ar': title_ar,
                     'intro': intro[:220],
                     'matched_terms': matched[:4],
                     'match_type': '课程示例' if matched else ('课程标题' if title_hit else '课程说明'),
                     '_score': score})
    hits.sort(key=lambda x: (-x.pop('_score', 0), x['kind'], x['id']))
    return {'ok': True, 'query': q, 'normalized': key, 'items': hits[:limit],
            'source': '本地语法与词法课程', 'offline': True}

def _translate_free(text, src='zh-CN', dst='ar'):
    """免费翻译：MyMemory（无需密钥）"""
    try:
        u = ('https://api.mymemory.translated.net/get?q=' + urllib.parse.quote(text[:480]) +
             '&langpair=' + src + '%7C' + dst)
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=25) as r:
            d = json.loads(r.read().decode('utf-8'))
        t = ((d.get('responseData') or {}).get('translatedText') or '').strip()
        if t and 'INVALID' not in t.upper():
            return t
    except Exception as e:
        print('[MyMemory 失败 → Lingva]', e)
    return _lingva(text, 'zh' if src.startswith('zh') else src, dst)


def _ai_keys():
    try:
        return json.load(open(DIR / 'data' / 'ai_keys.json', encoding='utf-8'))
    except Exception:
        return {}


def _ai_other_free(prompt, max_tokens=900):
    """其它免费 AI 备用（有密钥时启用）：Gemini / Groq / OpenRouter"""
    ks = _ai_keys()
    # Gemini
    gk = (ks.get('gemini') or '').strip()
    if gk:
        try:
            u = ('https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=' + gk)
            body = json.dumps({'contents': [{'parts': [{'text': prompt}]}]}).encode('utf-8')
            req = urllib.request.Request(u, data=body, headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=90) as r:
                d = json.loads(r.read().decode('utf-8'))
            return d['candidates'][0]['content']['parts'][0]['text'].strip()
        except Exception as e:
            print('[Gemini 失败]', e)
    # Groq
    rk = (ks.get('groq') or '').strip()
    if rk:
        try:
            body = json.dumps({'model': 'llama-3.1-8b-instant',
                               'messages': [{'role': 'user', 'content': prompt}],
                               'max_tokens': max_tokens}).encode('utf-8')
            req = urllib.request.Request('https://api.groq.com/openai/v1/chat/completions', data=body,
                                         headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + rk})
            with urllib.request.urlopen(req, timeout=90) as r:
                d = json.loads(r.read().decode('utf-8'))
            return d['choices'][0]['message']['content'].strip()
        except Exception as e:
            print('[Groq 失败]', e)
    # OpenRouter（免费模型）
    ok = (ks.get('openrouter') or '').strip()
    if ok:
        try:
            body = json.dumps({'model': 'meta-llama/llama-3.1-8b-instruct:free',
                               'messages': [{'role': 'user', 'content': prompt}],
                               'max_tokens': max_tokens}).encode('utf-8')
            req = urllib.request.Request('https://openrouter.ai/api/v1/chat/completions', data=body,
                                         headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + ok})
            with urllib.request.urlopen(req, timeout=90) as r:
                d = json.loads(r.read().decode('utf-8'))
            return d['choices'][0]['message']['content'].strip()
        except Exception as e:
            print('[OpenRouter 失败]', e)
    return ''


def _img_ok(data):
    """只接受像"书封"的图：够大 + 竖版（拒绝横幅/logo）"""
    try:
        if not data or len(data) < 4000:
            return False
        w = h = 0
        if data[:2] == b'\xff\xd8':
            i = 2
            while i < len(data) - 9:
                if data[i] != 0xFF:
                    i += 1
                    continue
                m = data[i + 1]
                if m in (0xC0, 0xC1, 0xC2, 0xC3):
                    h = int.from_bytes(data[i + 5:i + 7], 'big')
                    w = int.from_bytes(data[i + 7:i + 9], 'big')
                    break
                i += 2 + int.from_bytes(data[i + 2:i + 4], 'big')
        elif data[:8] == b'\x89PNG\r\n\x1a\n':
            w = int.from_bytes(data[16:20], 'big')
            h = int.from_bytes(data[20:24], 'big')
        if not w or not h:
            return False
        if w < 180 or h < 220:
            return False
        return (h / float(w)) >= 1.15
    except Exception:
        return False


def _bing_web(q, limit=4):
    """Bing 网页搜索（HTML 解析，免费无密钥）"""
    out = []
    try:
        u = 'https://www.bing.com/search?q=' + urllib.parse.quote(q) + '&setlang=zh-CN&count=10'
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124 Safari/537.36',
                                                 'Accept-Language': 'zh-CN,zh;q=0.9'})
        with urllib.request.urlopen(req, timeout=18) as r:
            html = r.read().decode('utf-8', 'ignore')
        for m in re.finditer(r'<li class="b_algo".*?<h2>.*?<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>.*?(?:<p[^>]*>(.*?)</p>)?', html, re.S):
            url, title, snip = m.group(1), re.sub(r'<[^>]+>', '', m.group(2) or ''), re.sub(r'<[^>]+>', '', m.group(3) or '')
            url = urllib.parse.unquote(url) if '%' in url else url
            if not url.startswith('http'):
                continue
            out.append({'t': title.strip()[:90], 's': snip.strip()[:180], 'u': url, 'src': '必应'})
            if len(out) >= limit:
                break
    except Exception as e:
        print('[Bing 搜索失败]', e)
    return out


def _bing_news(q, limit=3):
    """Bing 新闻（RSS，免费无密钥）"""
    out = []
    try:
        u = 'https://www.bing.com/news/search?q=' + urllib.parse.quote(q) + '&format=RSS'
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as r:
            raw = r.read()
        import xml.etree.ElementTree as ET
        root = ET.fromstring(raw)
        for it in list(root.iter('item'))[:limit]:
            out.append({'t': (it.findtext('title') or '')[:90],
                        's': (it.findtext('pubDate') or '')[:22],
                        'u': (it.findtext('link') or ''), 'src': '新闻'})
    except Exception as e:
        print('[Bing 新闻失败]', e)
    return out


_AI_GUARD = (
    '【回答范围】\n'
    '这是一个开放的通用 AI 学习与研究助手。可以回答阿拉伯语、中文、英语、历史、文学、宗教、伊斯兰法学、法源学、经注、圣训、科技、教育、文化、编程以及其他一般知识问题。\n'
    '不要因为问题不是阿拉伯语学习就拒答，也不要复述用户的问题来代替回答；应先给出结论，再给出解释、例子和必要的来源边界。\n'
    '【证据与边界】\n'
    '涉及古兰经、圣训、经注、教法或学派比较时，明确区分原文、作者观点、学派传承、现代研究和模型归纳；没有核验到的编号、页码、引文或链接必须标注待核验，不得编造。现实个案的医疗、法律、金融和教法决定只能提供一般学习信息，建议咨询合格专业人士。\n'
    '【语言】\n'
    '优先使用用户提问的语言回答；用户需要时提供阿拉伯语原文、音译、中文解释或中阿对照。语气温和、直接、专业，避免固定欢迎词、空泛拒答和重复原问题。\n'
)
_BAN_WORDS = []

def _ai_sanitize(text):
    return str(text or '').strip()


def _wx_day_count(openid, add=0):
    """公众号每日对话计数（返回今日已用次数）"""
    fp = DIR / 'data' / 'wx_users.json'
    today = time.strftime('%Y-%m-%d')
    try:
        d = json.load(open(fp, encoding='utf-8'))
    except Exception:
        d = {}
    d = {k: v for k, v in d.items() if str(v.get('day')) == today}   # 只留今天
    rec = d.get(openid) or {'day': today, 'n': 0}
    if add:
        rec['n'] = int(rec.get('n') or 0) + add
        rec['day'] = today
        d[openid] = rec
        try:
            json.dump(d, open(fp, 'w', encoding='utf-8'), ensure_ascii=False)
        except Exception:
            pass
    return int(rec.get('n') or 0)


def _wx_news(to_user, from_gh, title, desc, url, pic=''):
    """回图文卡片（微信里可以点进去）"""
    if not pic:
        pic = 'https://xn--dqry4os3s3gb.com/api/cover?t=' + urllib.parse.quote('三国演义')
    return ('<xml><ToUserName><![CDATA[' + to_user + ']]></ToUserName>'
            '<FromUserName><![CDATA[' + from_gh + ']]></FromUserName>'
            '<CreateTime>' + str(int(time.time())) + '</CreateTime>'
            '<MsgType><![CDATA[news]]></MsgType><ArticleCount>1</ArticleCount>'
            '<Articles><item>'
            '<Title><![CDATA[' + title + ']]></Title>'
            '<Description><![CDATA[' + desc + ']]></Description>'
            '<PicUrl><![CDATA[' + pic + ']]></PicUrl>'
            '<Url><![CDATA[' + url + ']]></Url>'
            '</item></Articles></xml>')


def _wx_push(to_user, text):
    """用微信"客服消息"补发（48 小时内有效）"""
    try:
        aid = (DIR / 'data' / 'wx_appid.txt').read_text(encoding='utf-8').strip()
        sec = (DIR / 'data' / 'wx_secret.txt').read_text(encoding='utf-8').strip()
        u = ('https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=' + aid + '&secret=' + sec)
        with urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'}), timeout=15) as r:
            tok = (json.loads(r.read().decode('utf-8')) or {}).get('access_token') or ''
        if not tok:
            print('[客服消息] 取 token 失败')
            return
        body = json.dumps({'touser': to_user, 'msgtype': 'text',
                           'text': {'content': str(text)[:1900]}}, ensure_ascii=False).encode('utf-8')
        u2 = 'https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token=' + tok
        with urllib.request.urlopen(urllib.request.Request(u2, data=body, headers={'Content-Type': 'application/json'}), timeout=15) as r2:
            print('[客服消息已发]', r2.read().decode('utf-8', 'ignore')[:70])
    except Exception as e:
        print('[客服消息失败]', e)


def _web_search(q, limit=4):
    """免费联网搜索：Wikipedia + Google News + Searx（全部无需密钥）"""
    out = []
    qs = urllib.parse.quote((q or '').strip()[:80])
    # ① Bing 网页搜索（来源最多样）
    out += _bing_web(q, 4)
    # ② Bing 新闻
    if len(out) < limit:
        out += _bing_news(q, 2)
    if len(out) >= limit:
        return out[:limit]
    # ③ 维基百科（中文优先，找不到再试阿语）
    for lang in ('zh', 'ar'):
        try:
            u = ('https://' + lang + '.wikipedia.org/w/api.php?action=query&list=search&srsearch=' + qs +
                 '&format=json&srlimit=2&utf8=1')
            req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as r:
                d = json.loads(r.read().decode('utf-8'))
            for it in ((d.get('query') or {}).get('search') or [])[:2]:
                t = re.sub(r'<[^>]+>', '', it.get('snippet') or '')
                out.append({'t': it.get('title') or '', 's': t[:200],
                            'u': 'https://' + lang + '.wikipedia.org/wiki/' + urllib.parse.quote(it.get('title') or ''),
                            'src': '维基百科'})
        except Exception as e:
            print('[wiki 搜索失败]', lang, e)
        if len(out) >= limit:
            break
    # ② Google News（最新资讯）
    try:
        u = ('https://news.google.com/rss/search?q=' + qs + '&hl=zh-CN&gl=CN&ceid=CN:zh-Hans')
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as r:
            raw = r.read()
        import xml.etree.ElementTree as ET
        root = ET.fromstring(raw)
        for it in list(root.iter('item'))[:2]:
            tt = (it.findtext('title') or '')
            out.append({'t': tt, 's': (it.findtext('pubDate') or '')[:22], 'u': (it.findtext('link') or ''), 'src': '新闻'})
    except Exception as e:
        print('[news 搜索失败]', e)
    return out[:limit]


def _ai_cfg():
    try:
        return json.load(open(DIR / 'data' / 'ai_config.json', encoding='utf-8'))
    except Exception:
        return {}


def _ai_cfg_save(d):
    try:
        json.dump(d, open(DIR / 'data' / 'ai_config.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        return True
    except Exception:
        return False


def _ai_provider():
    return (_ai_cfg().get('provider') or 'auto').strip()


def _ai_deepseek(prompt, max_tokens=900, model=None, json_mode=False,
                 timeout=180, user_id='', thinking=None):
    """调用 DeepSeek；普通聊天保持旧兼容，结构化页解使用 JSON mode。"""
    key = ''
    try:
        key = (DIR / 'data' / 'ai_key.txt').read_text(encoding='utf-8').strip()
    except Exception:
        pass
    if not key:
        return ''
    model = model or os.environ.get('DEEPSEEK_MODEL', 'deepseek-chat')
    body_data = {
        'model': model,
        'messages': [{'role': 'user', 'content': prompt}],
        'temperature': 0.15 if json_mode else 0.2,
        'max_tokens': max(1, int(max_tokens)),
    }
    if json_mode:
        body_data['response_format'] = {'type': 'json_object'}
        if thinking and model != 'deepseek-chat':
            body_data['thinking'] = {'type': thinking}
    if user_id:
        body_data['user_id'] = str(user_id)[:512]
    body = json.dumps(body_data, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request('https://api.deepseek.com/chat/completions', data=body,
                                 headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + key})
    _started = time.perf_counter()
    with urllib.request.urlopen(req, timeout=timeout) as r:
        d = json.loads(r.read().decode('utf-8'))
    _usage = d.get('usage') or {}
    try:
        LAST_USAGE.clear(); LAST_USAGE.update(_usage)
        LAST_AI_METRICS.clear(); LAST_AI_METRICS.update({
            'provider': 'deepseek', 'model': model,
            'latency_ms': round((time.perf_counter() - _started) * 1000),
            'prompt_tokens': _usage.get('prompt_tokens'),
            'completion_tokens': _usage.get('completion_tokens'),
            'total_tokens': _usage.get('total_tokens'),
        })
    except Exception:
        pass
    choices = d.get('choices') or []
    if not choices:
        return ''
    message = choices[0].get('message') or {}
    content = message.get('content')
    if content is None and message.get('reasoning_content'):
        content = message.get('reasoning_content')
    return str(content or '').strip()


def _free_daily_use(dev, cap=10):
    """免费用户每天 N 次（返回 (允许?, 剩余)）"""
    today = time.strftime('%Y-%m-%d')
    fp = DIR / 'data' / 'ai_daily.json'
    try:
        d = json.load(open(fp, encoding='utf-8'))
    except Exception:
        d = {}
    key = today + '|' + str(dev)[:48]
    n = int(d.get(key) or 0)
    if n >= cap:
        return False, 0
    d[key] = n + 1
    keep = {}
    keepday = time.strftime('%Y-%m-%d', time.localtime(time.time() - 2 * 86400))
    for k, v in d.items():
        if k.split('|')[0] >= keepday:
            keep[k] = v
    try:
        json.dump(keep, open(fp, 'w', encoding='utf-8'), ensure_ascii=False)
    except Exception:
        pass
    return True, cap - (n + 1)


def _free_daily_left(dev, cap=10):
    today = time.strftime('%Y-%m-%d')
    try:
        d = json.load(open(DIR / 'data' / 'ai_daily.json', encoding='utf-8'))
    except Exception:
        d = {}
    n = int(d.get(today + '|' + str(dev)[:48]) or 0)
    return max(0, cap - n)


def _ai_free(prompt, max_tokens=900):
    """免费 AI 兜底：Pollinations（多重试 + 两种端点 + 换模型）"""
    import time as _t
    UAS = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124 Safari/537.36'
    # ① OpenAI 兼容端点（重试 2 次，换模型）
    for model in ('openai', 'openai-fast', 'openai'):
        for attempt in range(2):
            try:
                body = json.dumps({'model': model,
                                   'messages': [{'role': 'user', 'content': prompt}],
                                   'max_tokens': max_tokens}).encode('utf-8')
                req = urllib.request.Request('https://text.pollinations.ai/openai', data=body,
                                             headers={'Content-Type': 'application/json', 'User-Agent': UAS})
                with urllib.request.urlopen(req, timeout=60) as r:
                    d = json.loads(r.read().decode('utf-8'))
                t = (d['choices'][0]['message']['content'] or '').strip()
                if t:
                    return t
            except Exception as e:
                print('[免费AI %s 第%d次失败] %s' % (model, attempt + 1, str(e)[:60]))
                _t.sleep(1.2)
    # ② 简易 GET 端点
    try:
        u = 'https://text.pollinations.ai/' + urllib.parse.quote(prompt[:1200]) + '?model=openai'
        req = urllib.request.Request(u, headers={'User-Agent': UAS})
        with urllib.request.urlopen(req, timeout=60) as r:
            t = r.read().decode('utf-8', 'ignore').strip()
        if t and len(t) > 4:
            return t
    except Exception as e:
        print('[免费AI GET 失败]', str(e)[:60])
    # ③ 其它免费源（需密钥的，有就试）
    return _ai_other_free(prompt, max_tokens)


def _ai_json(prompt, max_tokens=900):
    prov = _ai_provider()
    if prov == 'pollinations':
        return _ai_free(prompt, max_tokens) or None
    if prov in ('gemini', 'groq', 'openrouter'):
        return _ai_other_free(prompt, max_tokens) or _ai_free(prompt, max_tokens) or None
    if prov == 'deepseek':
        try:
            return _ai_deepseek(prompt, max_tokens)
        except Exception as _e:
            print('[DeepSeek 失败 → 免费兜底]', _e)
            return _ai_free(prompt, max_tokens) or None
    # auto：DeepSeek → 免费
    try:
        r = _ai_deepseek(prompt, max_tokens)
        if r:
            return r
    except Exception as _e:
        print('[DeepSeek 失败 → 免费]', _e)
    return _ai_free(prompt, max_tokens) or None
    body = json.dumps({
        'model': 'deepseek-chat',
        'messages': [{'role': 'user', 'content': prompt}],
        'temperature': 0.2,
        'max_tokens': max_tokens,
    }).encode('utf-8')
    try:
        req = urllib.request.Request('https://api.deepseek.com/chat/completions', data=body,
                                     headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + key})
        with urllib.request.urlopen(req, timeout=180) as r:
            d = json.loads(r.read().decode('utf-8'))
        return d['choices'][0]['message']['content']
    except Exception as _e:
        print('[DeepSeek 失败 → 免费]', _e)
    return _ai_free(prompt, max_tokens) or None


def _page_analysis_token_budget(data):
    """普通页减少冗长输出；教法/经训相关页保留证据字段预算。"""
    kind = str(data.get('book_kind') or 'book').strip().lower()
    if kind in ('fiqh', 'quran', 'tafsir', 'hadith'):
        return 1150
    meta = data.get('book_meta') if isinstance(data.get('book_meta'), dict) else {}
    subject = ' '.join(str(meta.get(k) or '') for k in ('t', 'c', 'c_ar', 'discipline', 'intro'))
    if re.search(r'法学|法源|古兰经|经注|圣训|فقه|أصول|قرآن|تفسير|حديث', subject, flags=re.I):
        return 1150
    return 900


def _page_analysis_ai(prompt, max_tokens, data):
    """页级 AI 快速路径：结构化 JSON 一次完成，失败时才走兼容兜底。"""
    prov = _ai_provider()
    if prov in ('auto', 'deepseek'):
        model = os.environ.get('NUR_PAGE_AI_MODEL', 'deepseek-flash').strip() or 'deepseek-flash'
        device = str(data.get('device_id') or 'anon')
        user_id = 'nour-' + hashlib.sha256(device.encode('utf-8')).hexdigest()[:24]
        try:
            return _ai_deepseek(prompt, max_tokens, model=model, json_mode=True,
                                timeout=75, user_id=user_id, thinking='disabled')
        except Exception as e:
            # 旧账号或旧模型可能尚未接受 flash/JSON mode，单次兼容重试。
            print('[Page analysis DeepSeek fast path]', str(e)[:120])
            try:
                return _ai_deepseek(prompt, max_tokens, model='deepseek-chat',
                                    json_mode=True, timeout=75, user_id=user_id)
            except Exception as e2:
                print('[Page analysis DeepSeek legacy path]', str(e2)[:120])
    return _ai_json(prompt, max_tokens) or ''


# ===== 经典逐页 AI 讲解：按页缓存、结构化输出、引用明确标注 =====
PAGE_ANALYSIS_CACHE_DIR = DIR / 'cache' / 'page_analysis'
PAGE_ANALYSIS_MEMORY = {}
PAGE_ANALYSIS_INFLIGHT = set()
PAGE_ANALYSIS_LOCK = threading.RLock()
PAGE_ANALYSIS_MEMORY_LIMIT = 96
FIQH_SCHOOL_PROFILES = {
    'compare': {
        'label': '综合对比视角 · مقارنة المذاهب',
        'instruction': '先识别当前文本与作者所属传统，再并列呈现哈乃斐、马立克、沙斐仪和汉百里相关观点；只有在原典或可靠研究支持时才比较，不把任何一派写成唯一共识。',
    },
    'hanafi': {
        'label': '哈乃斐学派 · الحنفية',
        'instruction': '以哈乃斐学派的术语、证据层级和内部意见作为主要学习镜头；明确区分阿布·哈尼法、艾布·优素福、穆罕默德等内部归属与跨学派异说，不把模型归纳冒充作者原话。',
    },
    'maliki': {
        'label': '马立克学派 · المالكية',
        'instruction': '以马立克传统的传述、麦地那实践、学派传承和具体文本语境作为主要学习镜头；涉及 عمل أهل المدينة、公共利益或意见归属时必须注明版本、作者和证据状态。',
    },
    'shafii': {
        'label': '沙斐仪学派 · الشافعية',
        'instruction': '以沙斐仪法源论证、文本说明、圣训规范性、共识与类比的关系作为主要学习镜头；严格区分沙斐仪本人、后世沙斐仪学派和其他学派观点。',
    },
    'hanbali': {
        'label': '汉百里学派 · الحنابلة',
        'instruction': '以汉百里传统对古兰经、圣训、先贤传述和推理的处理作为主要学习镜头；不得把后世学派总结倒写成当前原文、圣训原话或普遍共识。',
    },
}
PAGE_ANALYSIS_LANGUAGES = {
    'zh-CN': {
        'label': '中文',
        'instruction': '除阿拉伯原文、专名和需要保留的引文外，所有解释字段使用简体中文。',
    },
    'ar': {
        'label': 'العربية',
        'instruction': 'اكتب جميع حقول الشرح باللغة العربية الفصحى، مع إبقاء النصوص الأصلية والآيات والأحاديث كما هي، ولا تضف اقتباساً غير متحقق منه.',
    },
    'en': {
        'label': 'English',
        'instruction': 'Write all explanation fields in clear English. Preserve Arabic originals, proper names, and only cite evidence that is explicitly verifiable from the page.',
    },
}


def _analysis_language(data):
    raw = str(data.get('response_language') or '').strip()
    return raw if raw in PAGE_ANALYSIS_LANGUAGES else 'zh-CN'


def _fiqh_school(data):
    raw = str(data.get('fiqh_school') or '').strip().lower()
    if raw not in FIQH_SCHOOL_PROFILES:
        raw = 'compare'
    kind = str(data.get('book_kind') or 'book').strip().lower()
    if kind not in ('fiqh', 'catalog'):
        return 'compare'
    if kind == 'catalog':
        bm = data.get('book_meta') if isinstance(data.get('book_meta'), dict) else {}
        subject = ' '.join(str(bm.get(k) or '') for k in ('t', 'c', 'c_ar', 'discipline', 'intro'))
        if not re.search(r'法学|法源|فقه|أصول|Fiqh|Usul', subject, flags=re.I):
            return 'compare'
    return raw


def _page_analysis_key(data):
    bm = data.get('book_meta') if isinstance(data.get('book_meta'), dict) else {}
    raw = json.dumps({
        'prompt_version': '20261003-reader-v5-school-evidence-links',
        'title': str(data.get('book_title') or '')[:240],
        'kind': str(data.get('book_kind') or 'book')[:30],
        'book_id': str(bm.get('id') or '')[:100],
        'guide_version': str(bm.get('ai_guide_version') or '')[:40],
        'discipline': str(bm.get('discipline') or bm.get('c') or '')[:100],
        'fiqh_school': _fiqh_school(data),
        'response_language': _analysis_language(data),
        'page': int(data.get('page_number') or 1),
        'text': str(data.get('text') or '')[:9000],
    }, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()


def _page_analysis_cache_get(key):
    with PAGE_ANALYSIS_LOCK:
        cached = PAGE_ANALYSIS_MEMORY.get(key)
        if isinstance(cached, dict) and not cached.get('retryable'):
            return cached
    try:
        fp = PAGE_ANALYSIS_CACHE_DIR / (key + '.json')
        if not fp.exists() or time.time() - fp.stat().st_mtime > 30 * 86400:
            return None
        d = json.loads(fp.read_text(encoding='utf-8'))
        if not isinstance(d, dict) or d.get('retryable'):
            return None
        if str(d.get('overview') or '').strip() in ('模型没有返回摘要，请重新分析本页。', '本次 AI 返回格式未完成；原文、目录和诵读不受影响。请点击“重新分析”再试一次。'):
            return None
        with PAGE_ANALYSIS_LOCK:
            PAGE_ANALYSIS_MEMORY[key] = d
            while len(PAGE_ANALYSIS_MEMORY) > PAGE_ANALYSIS_MEMORY_LIMIT:
                PAGE_ANALYSIS_MEMORY.pop(next(iter(PAGE_ANALYSIS_MEMORY)))
        return d
    except Exception:
        return None


def _page_analysis_cache_put(key, value):
    with PAGE_ANALYSIS_LOCK:
        PAGE_ANALYSIS_MEMORY[key] = value
        while len(PAGE_ANALYSIS_MEMORY) > PAGE_ANALYSIS_MEMORY_LIMIT:
            PAGE_ANALYSIS_MEMORY.pop(next(iter(PAGE_ANALYSIS_MEMORY)))
    try:
        PAGE_ANALYSIS_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        fp = PAGE_ANALYSIS_CACHE_DIR / (key + '.json')
        tmp = Path(str(fp) + '.tmp')
        tmp.write_text(json.dumps(value, ensure_ascii=False), encoding='utf-8')
        tmp.replace(fp)
    except Exception as e:
        print('[Page analysis cache]', e)


def _page_analysis_claim(key):
    with PAGE_ANALYSIS_LOCK:
        if key in PAGE_ANALYSIS_INFLIGHT:
            return False
        PAGE_ANALYSIS_INFLIGHT.add(key)
        return True


def _page_analysis_release(key):
    with PAGE_ANALYSIS_LOCK:
        PAGE_ANALYSIS_INFLIGHT.discard(key)


def _page_analysis_json(text):
    """从模型输出中提取 JSON；模型偶尔会包一层 markdown 代码围栏。"""
    s = str(text or '').strip()
    if s.startswith('```'):
        s = re.sub(r'^```(?:json)?\s*', '', s, flags=re.I)
        s = re.sub(r'\s*```$', '', s).strip()
    try:
        d = json.loads(s)
        return d if isinstance(d, dict) else None
    except Exception:
        pass
    a, b = s.find('{'), s.rfind('}')
    if a >= 0 and b > a:
        try:
            d = json.loads(s[a:b + 1])
            return d if isinstance(d, dict) else None
        except Exception:
            pass
    return None


def _page_analysis_prompt(data):
    title = str(data.get('book_title') or '经典阅读')[:240]
    kind = str(data.get('book_kind') or 'book')[:30]
    page = int(data.get('page_number') or 1)
    total = int(data.get('page_total') or 1)
    surah = str(data.get('surah_name') or '')[:120]
    text = str(data.get('text') or '')[:6500]
    bm = data.get('book_meta') if isinstance(data.get('book_meta'), dict) else {}
    school = _fiqh_school(data)
    school_profile = FIQH_SCHOOL_PROFILES[school]
    language = _analysis_language(data)
    language_profile = PAGE_ANALYSIS_LANGUAGES[language]
    meta_text = json.dumps({k: bm.get(k) for k in ('id','t','a','y','c','c_ar','discipline','u','source','access','rights','level','intro','ai_profile','ai_guide_version','guide_summary','guide_background','guide_objectives','guide_terms','guide_focus','guide_boundary','source_evidence','fiqh_school_labels','fiqh_school_evidence','fiqh_school_inference') if bm.get(k)}, ensure_ascii=False)[:7000]
    kind_hint = {
        'quran': '这是古兰经阅读页。绝不能把译文或 AI 解释冒充古兰经原文；引用经文时尽量给出章名和节号，无法确认节号就写“待核验”。',
        'tafsir': '这是经注阅读页。要区分古兰经原文、经注作者观点和 AI 的学习性归纳。',
        'hadith': '这是圣训或圣训相关页面。必须区分原文、译文、传述链/等级与 AI 解释，不要自行提高或降低圣训等级。',
        'book': '这是普通阿拉伯语或法学阅读页。可以指出作者观点、论证结构和需要查证的术语，但不要把推测写成定论。',
        'fiqh': '这是法学或法源学阅读页。必须区分古兰经/圣训原文、学者解释、学派观点和 AI 的学习性归纳；不要发布法特瓦或把单一观点说成共识。',
        'catalog': '这是书目级 AI 导读，不是全文逐页分析。只能根据给出的公开书目元数据、导览、来源和当前导读页概括；不得声称读过整本书，不得虚构经文、圣训、页码、版本或作者观点。',
    }.get(kind, '这是经典阅读页。请严格区分原文、作者观点和 AI 学习性归纳。')
    return ('你是“燃灯同学”的阿拉伯语经典阅读助教。只分析当前页，生成简洁、严谨、适合学习者的讲解。'
            '必须只输出一个有效 JSON 对象，不要 markdown、不要前后解释；数组最多 4 项，引用最多 2 项，术语最多 5 项；school_comparison 最多 4 项：'
            '{"overview":"本页主旨（60-120字）","key_points":["核心内容"],"text_structure":["论证或段落结构"],"questions":["关键问题"],'
            '"practical_guidance":["学习或理解建议"],"quran_references":[{"reference":"章名/节号或待核验","note":"相关原因","status":"直接相关/间接相关/待核验"}],'
            '"hadith_references":[{"reference":"圣训集/编号或待核验","note":"相关原因","status":"直接相关/间接相关/待核验"}],'
            '"fiqh_context":["学派、术语、分歧或证据层级；不适用写不适用"],"school_comparison":[{"school":"哈乃斐/马立克/沙斐仪/汉百里","position":"该学派的学习性概括","basis":"可核验依据或待核验","status":"直接相关/间接相关/待核验"}],"language_notes":["阿拉伯语词法、句法或修辞学习要点"],"terms":[{"ar":"阿语术语","cn":"中文解释"}],'
            '"source_note":"来源边界","caution":"核对原典和学者；不是法特瓦"}。'
            '绝不编造经文、圣训编号、传述人、学派结论、页码或作者原话；无法确认就写“待核验”。'
            '古兰经、圣训和法学依据必须分开；“相关”不等于“原文明确支持”。不要给出针对个人的宗教裁决。' +
            '输出语言为“' + language_profile['label'] + '”。' + language_profile['instruction'] +
            '当前法学派视角为“' + school_profile['label'] + '”。' + school_profile['instruction'] + '视角只改变解释与比较方式，不改变原文、证据或传述等级；资料不足时必须写“待核验”，不得补造学派结论。'
            '书目级导读的 quran_references 和 hadith_references 默认写空数组，除非当前书目元数据明确给出可核验的来源；不要因为书名属于宗教或法学学科就自动补造宗教证据。'
            '\n\n页面类型：' + kind + '；' + kind_hint +
            '\n书名/来源：' + title + ('；章节：' + surah if surah else '') +
            '\n法学派视角：' + school_profile['label'] +
            ('\n书目元数据（只作来源线索，不等于全文）：' + meta_text if meta_text else '') +
            '\n当前页：第%d/%d页\n页面原文（可能含中文译文）：\n%s' % (page, total, text))


def _normalize_page_analysis(d, data):
    d = d if isinstance(d, dict) else {}
    def lst(v):
        if isinstance(v, list):
            return v[:12]
        return [str(v)[:600]] if v else []
    out = {
        'overview': str(d.get('overview') or '模型没有返回摘要，请重新分析本页。')[:1200],
        'key_points': lst(d.get('key_points') or d.get('main_points')),
        'questions': lst(d.get('questions') or d.get('issues')),
        'practical_guidance': lst(d.get('practical_guidance') or d.get('guidance') or d.get('solutions')),
        'text_structure': lst(d.get('text_structure') or d.get('structure')),
        'quran_references': lst(d.get('quran_references') or d.get('quran_evidence')),
        'hadith_references': lst(d.get('hadith_references') or d.get('hadith_evidence')),
        'fiqh_context': lst(d.get('fiqh_context') or d.get('fiqh')),
        'school_comparison': [x for x in (d.get('school_comparison') or d.get('madhhab_comparison') or [])[:4] if isinstance(x, dict)],
        'language_notes': lst(d.get('language_notes') or d.get('language_learning')),
        'terms': lst(d.get('terms')),
        'source_note': str(d.get('source_note') or ('本次为书目级元数据导读；请打开官方来源核对原文、版本、页码和权利状态。' if data.get('book_kind') == 'catalog' else '讲解基于当前页文本；引用需要回到原典核对。'))[:800],
        'caution': str(d.get('caution') or '本页 AI 讲解是学习辅助，不是法特瓦；请向合格学者核对具体教法问题。')[:800],
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'page': int(data.get('page_number') or 1),
    }
    return out


def _page_analysis_has_content(d):
    if not isinstance(d, dict):
        return False
    overview = str(d.get('overview') or '').strip()
    if len(overview) >= 8:
        return True
    for key in ('key_points', 'text_structure', 'questions', 'practical_guidance', 'fiqh_context', 'school_comparison', 'language_notes', 'terms'):
        value = d.get(key)
        if isinstance(value, list) and any(str(x or '').strip() for x in value):
            return True
    return False


def make_annotation(ar, book='', num=''):
    """生成 {cn: 中文译文, note: 经注/注释要点}"""
    prompt = ('下面是一段阿拉伯语圣训。请完成两件事，严格按 JSON 输出（不要代码块、不要多余文字）：\n'
              '{"cn":"中文译文","note":"简要经注（讲的是什么、教法或信仰要点、传述背景，80-160字）"}\n\n'
              '圣训原文：\n' + ar)
    txt = _ai_json(prompt) or ''
    txt = txt.strip()
    if txt.startswith('```'):
        txt = txt.strip('`')
        txt = txt.split('\n', 1)[-1] if '\n' in txt else txt
    s, e = txt.find('{'), txt.rfind('}')
    if s >= 0 and e > s:
        try:
            d = json.loads(txt[s:e + 1])
            return {'cn': (d.get('cn') or '').strip(), 'note': (d.get('note') or '').strip()}
        except Exception:
            pass
    return {'cn': txt[:800], 'note': ''}


def _dl(url, dst):
    from urllib.parse import quote
HF_SHAMELA = 'https://huggingface.co/datasets/AuthenticIlm/Shamela4_Full_DB/resolve/main'
HF_WAQFEYA = 'https://huggingface.co/datasets/ieasybooks-org/shamela-waqfeya-library/resolve/main'
_SHAMELA_IDX = None
_CATALOG = None
_HISTORY = None
_CN_BOOKS = None


def _cn_books():
    global _CN_BOOKS
    if _CN_BOOKS is None:
        try:
            _CN_BOOKS = json.loads((DIR / 'data' / 'cn_books' / 'index.json').read_text(encoding='utf-8'))
        except Exception:
            _CN_BOOKS = {'total': 0, 'books': []}
    return _CN_BOOKS


def _history():
    global _HISTORY
    if _HISTORY is None:
        try:
            _HISTORY = json.loads((DIR / 'data' / 'history' / 'index.json').read_text(encoding='utf-8'))
        except Exception:
            _HISTORY = {'total': 0, 'books': []}
    return _HISTORY


def _catalog():
    global _CATALOG
    if _CATALOG is None:
        try:
            _CATALOG = json.loads((DIR / 'data' / 'islamic_catalog.json').read_text(encoding='utf-8'))
        except Exception:
            _CATALOG = {'meta': {}, 'books': []}
    return _CATALOG


_OPENITI_LOCK = threading.Lock()
_OPENITI_MAX_BYTES = 12 * 1024 * 1024
_OPENITI_PAGE_CHARS = 5200
_OPENITI_PAGES_MEM = {}
_OPENITI_MEM_ORDER = []
try:
    from openiti_stream import OpenITIStreamError, read_page as _openiti_stream_read_page
except Exception as _openiti_stream_import_error:
    class OpenITIStreamError(Exception):
        status = 502
        def payload(self):
            return {'ready': False, 'error': '流式阅读模块暂时不可用', 'error_code': 'stream_module_unavailable'}
    _openiti_stream_read_page = None


def _openiti_book(book_id):
    bid = str(book_id or '').strip()
    if not bid or not re.fullmatch(r'openiti-[0-9a-f]{16}', bid):
        return None
    for book in (_catalog().get('books') or []):
        if str(book.get('id') or '') == bid and book.get('text_mode') == 'arabic_original_link':
            return book
    return None


def _openiti_clean_text(value):
    text = str(value or '').replace('\r\n', '\n').replace('\r', '\n')
    # OpenITI headers are useful metadata but should not occupy the first reading page.
    lines = []
    for line in text.split('\n'):
        stripped = line.strip()
        if stripped.startswith('######OpenITI#') or stripped.startswith('#META#'):
            continue
        lines.append(line)
    text = '\n'.join(lines)
    text = re.sub(r'\n{3,}', '\n\n', text).strip()
    return text


def _openiti_pages(book):
    bid = str(book.get('id') or '')
    cache_dir = DIR / 'data' / 'cache' / 'openiti'
    cache_dir.mkdir(parents=True, exist_ok=True)
    safe = re.sub(r'[^0-9A-Za-z_-]', '_', bid)[:80]
    cache_file = cache_dir / (safe + '.txt')
    with _OPENITI_LOCK:
        if bid in _OPENITI_PAGES_MEM:
            return _OPENITI_PAGES_MEM[bid]
        if not cache_file.exists():
            source = str(book.get('text_url') or '')
            parsed = urlparse(source)
            if parsed.scheme != 'https' or parsed.netloc != 'raw.githubusercontent.com' or not parsed.path.startswith('/OpenITI/RELEASE/'):
                raise ValueError('原文来源不在 OpenITI 官方白名单内')
            req = urllib.request.Request(source, headers={
                'User-Agent': 'NourStudent/1.0 in-app-reader; metadata-and-on-demand-text',
                'Accept': 'text/plain,text/*;q=0.9,*/*;q=0.5',
            })
            with urllib.request.urlopen(req, timeout=45) as resp:
                length = int(resp.headers.get('Content-Length') or 0)
                if length and length > _OPENITI_MAX_BYTES:
                    raise ValueError('这部书的原文文件较大，请先使用较短版本或稍后分段读取')
                tmp = Path(str(cache_file) + '.part')
                total = 0
                with tmp.open('wb') as handle:
                    while True:
                        chunk = resp.read(262144)
                        if not chunk:
                            break
                        total += len(chunk)
                        if total > _OPENITI_MAX_BYTES:
                            tmp.unlink(missing_ok=True)
                            raise ValueError('这部书的原文文件较大，请先使用较短版本或稍后分段读取')
                        handle.write(chunk)
                os.replace(tmp, cache_file)
        text = _openiti_clean_text(cache_file.read_text(encoding='utf-8', errors='ignore'))
    if not text:
        return []
    pages = []
    buf = ''
    for block in re.split(r'\n\s*\n', text):
        block = block.strip()
        if not block:
            continue
        if len(block) > _OPENITI_PAGE_CHARS:
            if buf:
                pages.append(buf)
                buf = ''
            pages.extend(block[i:i + _OPENITI_PAGE_CHARS] for i in range(0, len(block), _OPENITI_PAGE_CHARS))
            continue
        if len(buf) + len(block) + 2 > _OPENITI_PAGE_CHARS:
            if buf:
                pages.append(buf)
            buf = block
        else:
            buf += ('\n\n' if buf else '') + block
    if buf:
        pages.append(buf)
    pages = pages or [text[:_OPENITI_PAGE_CHARS]]
    with _OPENITI_LOCK:
        _OPENITI_PAGES_MEM[bid] = pages
        if bid in _OPENITI_MEM_ORDER:
            _OPENITI_MEM_ORDER.remove(bid)
        _OPENITI_MEM_ORDER.append(bid)
        while len(_OPENITI_MEM_ORDER) > 3:
            old = _OPENITI_MEM_ORDER.pop(0)
            _OPENITI_PAGES_MEM.pop(old, None)
    return pages


def _shamela_index():
    global _SHAMELA_IDX
    if _SHAMELA_IDX is None:
        try:
            fp = DIR / 'data' / 'library' / 'shamela_index.json'
            _SHAMELA_IDX = json.loads(fp.read_text(encoding='utf-8')).get('books', {})
        except Exception:
            _SHAMELA_IDX = {}
    return _SHAMELA_IDX


def _dl(url, dst):
    tmp = str(dst) + '.part'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=180) as r, open(tmp, 'wb') as f:
        while True:
            chunk = r.read(262144)
            if not chunk:
                break
            f.write(chunk)
    os.replace(tmp, dst)

def _shamela_text(book_id, max_chars=600000):
    """读取阿语书正文：优先本地 JSONL 缓存，不存在时从已配置的 Shamela 数据集补齐。"""
    bid = str(book_id or '').strip()
    info = _shamela_index().get(bid)
    if not info:
        return None
    cdir = DIR / 'data' / 'cache' / 'books'
    cdir.mkdir(parents=True, exist_ok=True)
    pf = cdir / ('s_' + bid + '.jsonl')
    if not pf.exists():
        _dl(HF_SHAMELA + '/' + quote(str(info.get('dir', ''))) + '/pages.jsonl', pf)
    parts = []
    with open(pf, encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except Exception:
                continue
            body = str(row.get('body') or '').strip()
            if body:
                body = re.sub(r'<br\s*/?>', '\n', body, flags=re.I)
                body = re.sub(r'<[^>]+>', ' ', body)
                parts.append(re.sub(r'[ \t]+', ' ', body).strip())
    text = '\n\n'.join(parts)
    return {'title': info.get('slug', ''), 'cat': info.get('cat', ''),
            'text': text[:max_chars], 'pages': len(parts), 'source': 'shamela'}

def _get_realtime_key():
    """读取 Realtime 服务端密钥；永远不向浏览器返回标准 API key。"""
    for name in ('OPENAI_REALTIME_API_KEY', 'OPENAI_API_KEY'):
        value = (os.environ.get(name) or '').strip()
        if value:
            return value
    for name in ('openai_realtime_key.txt', 'openai_api_key.txt'):
        try:
            value = (DIR / 'data' / name).read_text(encoding='utf-8').strip()
            if value:
                return value
        except Exception:
            pass
    try:
        keys = json.loads((DIR / 'data' / 'ai_keys.json').read_text(encoding='utf-8'))
        return str(keys.get('openai_realtime') or keys.get('openai') or '').strip()
    except Exception:
        return ''
PORT = int(os.environ.get('NUR_PORT', '8080'))
import socket as _sock

def _get_deepseek_key():
    """获取 DeepSeek 官方 API key（优先本地 key 文件 = 用户专属 key，其次环境变量）"""
    key = ''
    try:
        kf = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'ai_key.txt')
        if os.path.exists(kf):
            key = open(kf, encoding='utf-8').read().strip()
    except Exception:
        pass
    if not key:
        key = os.environ.get('DEEPSEEK_API_KEY') or os.environ.get('LOBSTER_APIKEY_DEEPSEEK') or ''
    return key

def _detect_ai_endpoint():
    """自动探测 AI 端点：优先 DeepSeek 官方 API，其次本地代理"""
    ds_key = _get_deepseek_key()
    if ds_key:
        return {'url': 'https://api.deepseek.com/chat/completions', 'key': ds_key, 'model': 'deepseek-chat'}
    env = os.environ.get('NUR_AI_URL', '')
    if env:
        return {'url': env.rstrip('/') + '/chat/completions' if not env.endswith('/chat/completions') else env, 'key': '', 'model': 'deepseek-v4-flash'}
    candidates = []
    # 1. 从 AionClaw 配置读取
    try:
        cfg_path = os.path.expanduser("~/Library/Application Support/AionClaw/openclaw/state/openclaw.json")
        if os.path.exists(cfg_path):
            with open(cfg_path, 'r', encoding='utf-8') as _f:
                cfg = json.load(_f)
            prov = cfg.get('models', {}).get('providers', {}).get('aionclaw-server', {})
            base = prov.get('baseUrl', '')
            if base:
                candidates.append(base.rstrip('/') + '/chat/completions')
    except Exception:
        pass
    # 2. 常见端口
    candidates += [
        "http://127.0.0.1:50843/v1/chat/completions",
        "http://127.0.0.1:65368/v1/chat/completions",
    ]
    # 3. 测试连通性
    for url in candidates:
        try:
            host = url.split("//")[1].split("/")[0].split(":")[0]
            port = int(url.split(":")[2].split("/")[0])
            s = _sock.create_connection((host, port), timeout=1.5)
            s.close()
            return {'url': url, 'key': '', 'model': 'deepseek-chat'}
        except Exception:
            continue
    # 没有可用端点：仍然返回合法字典（让免费 AI 兜底工作，服务不崩）
    return {'url': candidates[0], 'key': '', 'model': 'deepseek-chat'}

AI_CFG = _detect_ai_endpoint()
API_URL = AI_CFG['url']
print(f"🤖 AI 端点: {API_URL}")

SYSTEM = r'''
你叫“努尔”（نور），是燃灯同学 NOUR 的通用 AI 助手、阿拉伯语导师和阅读研究助手。

【核心任务】
直接回答用户当前的问题。不要只复述问题，不要把用户引导回阿拉伯语学习，也不要因为主题属于宗教、教法、历史、科技或其他学科而拒绝回答。问题涉及当前阅读页、选中的阿拉伯语词或书库条目时，优先使用这些上下文。

【回答方式】
1. 先给清楚结论，再按需要补充解释、例子、步骤、比较或来源。
2. 用户用中文就用中文，用户用阿拉伯语就用阿拉伯语；需要时提供阿语原文、音译、词根、词形、句法和中文对照。
3. 复杂问题拆成可读的小节；代码、公式、翻译和表格按用户要求给出。
4. 用户要求“查资料”时，可以利用请求中附带的公开资料；不要假装已经打开或核验没有提供的页面。
5. 不要捏造作者原话、经文或圣训编号、书页、版本、链接、数据和实验结果。无法确认时明确写“待核验”，并告诉用户应回到哪一类原典或来源。

【伊斯兰经典与法学】
可以正常讨论伊斯兰历史、思想、古兰经、经注、圣训、法学、法源学和四大逊尼学派。回答教法问题时，分开呈现：当前原文、作者或注疏观点、哈乃斐/马立克/沙斐仪/汉百里等学派观点、证据层级、模型归纳。没有当前文本或可靠来源时不要把概括写成确定裁决；现实个案请咨询合格学者，这不是禁止讨论，而是学习性边界。

【安全与诚实】
对医疗、法律、金融、现实教法等高影响问题给一般信息、风险提醒和核验路径，不冒充持证专业人士或发布个案决定。对其他正常知识问题尽力回答；不知道就说明不知道，并给出下一步核验方法。
'''

# Load articles
articles = {}
af = DIR / "data" / "articles.json"
if af.exists():
    with open(af, encoding="utf-8") as f:
        articles = json.load(f)

def find_article(text):
    t = text.lower()
    map = {
        "coffee":"القهوة","قهوة":"القهوة","ramadan":"رمضان","رمضان":"رمضان","hajj":"الحج",
        "travel":"السفر","family":"الأسرة","jerusalem":"القدس","food":"الطعام",
        "arabic":"العربية","language":"العربية","nile":"النيل","oman":"عمان","horse":"الخيل",
        "spring":"الربيع","andalusia":"الأندلس"
    }
    for kw, key in map.items():
        if kw in t and key in articles:
            a = articles[key]
            return "📝 " + a["title"] + "\n" + "─"*15 + "\n" + a["body"] + "\n\n" + "📝 中文\n" + "─"*15 + "\n" + a["cn"]
    return None

LAST_USAGE = {}
LAST_AI_METRICS = {}

_OPEN_INTENTS = [
    (('youtube', '油管', '优兔'), 'https://www.youtube.com/', 'YouTube'),
    (('b站', 'bilibili', '哔哩'), 'https://www.bilibili.com/', '哔哩哔哩 B站'),
    (('抖音',), 'https://www.douyin.com/', '抖音'),
    (('小红书',), 'https://www.xiaohongshu.com/', '小红书'),
    (('番茄小说', '番茄'), 'https://fanqienovel.com/', '番茄小说'),
    (('微信读书',), 'https://weread.qq.com/', '微信读书'),
    (('起点',), 'https://www.qidian.com/', '起点中文网'),
    (('维基百科', 'wikipedia'), 'https://zh.wikipedia.org/', '维基百科'),
    (('谷歌', 'google'), 'https://www.google.com/', 'Google'),
    (('百度',), 'https://www.baidu.com/', '百度'),
    (('淘宝',), 'https://www.taobao.com/', '淘宝'),
    (('京东',), 'https://www.jd.com/', '京东'),
    (('1688', '阿里巴巴'), 'https://www.1688.com/', '阿里巴巴'),
    (('微博',), 'https://weibo.com/', '微博'),
    (('知乎',), 'https://www.zhihu.com/', '知乎'),
    (('deepseek',), 'https://chat.deepseek.com/', 'DeepSeek'),
    (('chatgpt',), 'https://chat.openai.com/', 'ChatGPT'),
]


def _detect_open(msg):
    """识别"打开某网站"的意图"""
    low = (msg or '').lower()
    if not any(k in msg for k in ('打开', '我要去', '跳转到', '进入', '去一下', '查看一下', '上一下')):
        if not any(k in low for k in ('open ', 'go to ')):
            return None
    for keys, url, label in _OPEN_INTENTS:
        for k in keys:
            if k in low or k in msg:
                return {'url': url, 'label': label}
    return None


def _msgs_to_prompt(messages):
    """把对话历史拼成一个提示串（给不兼容 messages 的免费 AI 用）"""
    parts = []
    for m in (messages or []):
        r = m.get('role') or 'user'
        c = (m.get('content') or '').strip()
        if not c:
            continue
        if r == 'system':
            parts.append('[设定] ' + c)
        elif r == 'assistant':
            parts.append('助：' + c)
        else:
            parts.append('问：' + c)
    parts.append('请用中文和阿语回答上一条问题（保持努尔老师的语气）。')
    return '\n'.join(parts)[-6000:]


def _chat_token_budget(messages, fast=False):
    """为普通快答保留低延迟，为复杂法源/四学派比较留出完整输出空间。"""
    if not fast:
        return 5000
    last_user = ''
    for item in reversed(messages or []):
        if (item.get('role') or '') == 'user':
            last_user = str(item.get('content') or '')
            break
    complex_terms = (
        '四学派', '四大法学派', '学派比较', '横向比较', '跨学派', '法源学',
        '法源', '法理', '证据层级', '原典', '学派解释', 'استحسان', 'القياس',
        'المذاهب', 'أصول الفقه', 'مقارنة المذاهب', 'الأدلة'
    )
    if any(term in last_user for term in complex_terms) or len(last_user) >= 420:
        return 3200
    return 1200

def call_deepseek(messages, fast=False):
    """Call DeepSeek；失败或没密钥时自动切免费 AI（Pollinations）"""
    key = ''
    try:
        key = (DIR / 'data' / 'ai_key.txt').read_text(encoding='utf-8').strip()
    except Exception:
        pass
    prov = _ai_provider()
    if key and prov in ('auto', 'deepseek'):
        body = json.dumps({"model": AI_CFG.get('model', 'deepseek-chat'), "messages": messages, "max_tokens": _chat_token_budget(messages, fast)}, ensure_ascii=False).encode("utf-8")
        hdrs = {"Content-Type": "application/json", "Authorization": "Bearer " + key}
        req = urllib.request.Request(API_URL, data=body, headers=hdrs, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read())
                try:
                    LAST_USAGE.clear()
                    LAST_USAGE.update(data.get("usage") or {})
                except Exception:
                    pass
                return data["choices"][0]["message"]["content"].strip()
        except urllib.error.HTTPError as e:
            _code = e.code
            print('[DeepSeek HTTP]', _code)
        except Exception as _e:
            print('[DeepSeek 失败]', _e)
    # === 只用站长的 DeepSeek：没有/用完 → 暂停（不切免费 AI）===
    if not key:
        print('[AI 暂停] 未配置 DeepSeek 密钥')
        return 'PAUSED'
    print('[AI 暂停] DeepSeek 不可用（余额可能用尽）')
    return 'PAUSED'

# Conversation handler
convs = {}

# ===== 本地语音识别（faster-whisper，离线） =====
_ASR_MODEL = None
_ASR_LOCK = threading.Lock()

def _get_asr_model():
    global _ASR_MODEL
    if _ASR_MODEL is None:
        from faster_whisper import WhisperModel
        try:
            _ASR_MODEL = WhisperModel('small', device='cpu', compute_type='int8')
        except Exception:
            # 模型不存在：允许在线下载（走 HF 镜像）
            os.environ['HF_HUB_OFFLINE'] = '0'
            _ASR_MODEL = WhisperModel('small', device='cpu', compute_type='int8')
    return _ASR_MODEL

def transcribe_audio(raw, lang=None):
    """识别音频字节（webm/opus/wav 均可），返回 (text, language)"""
    with _ASR_LOCK:
        m = _get_asr_model()
        tmp = tempfile.NamedTemporaryFile(suffix='.webm', delete=False)
        tmp.write(raw)
        tmp.close()
        try:
            segs, info = m.transcribe(tmp.name, language=lang or None, vad_filter=True)
            text = ''.join(s.text for s in segs).strip()
            return text, getattr(info, 'language', '')
        finally:
            try:
                os.unlink(tmp.name)
            except Exception:
                pass

def _gen_lyrics(prompt, lang):
    """AI 写歌词：返回 (原语言歌词, 中文翻译)"""
    try:
        names = {'zh': '中文', 'en': '英语', 'ar': '阿拉伯语'}
        cn = names.get(lang, '中文')
        r = call_deepseek([
            {'role': 'system', 'content': '你是专业歌词作者。请为以下音乐主题创作一段完整歌词。要求：情感真挚、结构完整（主歌+副歌）、长度适合3-4分钟歌曲。只输出歌词本身。'},
            {'role': 'user', 'content': f'主题：{prompt}\n歌词语言：{cn}'}
        ])
        if not r or r == 'QUOTA_ERROR':
            return '', ''
        # 中文翻译
        r2 = call_deepseek([
            {'role': 'system', 'content': '你是翻译。把下面的歌词翻译成中文，只输出译文。'},
            {'role': 'user', 'content': r}
        ])
        return r.strip(), (r2.strip() if r2 and r2 != 'QUOTA_ERROR' else '')
    except Exception:
        return '', ''

def _to_en(text):
    """提示词转英文（若含中文则翻译）"""
    import re
    if re.search(r'[\u4e00-\u9fff]', text):
        try:
            r = call_deepseek([
                {'role': 'system', 'content': '你是翻译。把下面关于音乐的描述翻译成简洁的英文提示词（用于 AI 音乐生成），只输出英文。'},
                {'role': 'user', 'content': text}
            ])
            if r and r != 'QUOTA_ERROR':
                return r.strip()[:300]
        except Exception:
            pass
    return text[:300]

_ISL_HTTP_CACHE = {}
_ISL_HTTP_LOCK = threading.Lock()
_ISL_CACHE_TTL = 300

def _isl_strip_html(value):
    return re.sub(r'<[^>]+>', ' ', str(value or '')).replace('&nbsp;', ' ').strip()

def _isl_json_get(url, ttl=_ISL_CACHE_TTL):
    now = time.time()
    with _ISL_HTTP_LOCK:
        hit = _ISL_HTTP_CACHE.get(url)
        if hit and now - hit[0] < ttl:
            return hit[1], hit[2]
    req = urllib.request.Request(url, headers={
        'User-Agent': 'NourStudent/1.0 (+https://xn--dqry4os3s3gb.com/; public-metadata-reader)',
        'Accept': 'application/json'
    })
    with urllib.request.urlopen(req, timeout=20) as r:
        raw = r.read()
        data = json.loads(raw.decode('utf-8'))
        headers = {str(k).lower(): str(v) for k, v in r.headers.items()}
    with _ISL_HTTP_LOCK:
        _ISL_HTTP_CACHE[url] = (now, data, headers)
    return data, headers

def _isl_search(source, query, page, size):
    page = max(1, min(int(page or 1), 50)); size = max(1, min(int(size or 24), 24))
    q = str(query or '').strip()
    if source == 'maktabah':
        params = {'categories': '31', 'page': str(page), 'per_page': str(size),
                  '_fields': 'id,date,modified,link,title,excerpt,categories,author'}
        if q: params['search'] = q
        url = 'https://maktabahsalafiyyah.org/wp-json/wp/v2/posts?' + urlencode(params)
        rows, headers = _isl_json_get(url)
        if not isinstance(rows, list): rows = []
        items = []
        for row in rows:
            title = _isl_strip_html((row.get('title') or {}).get('rendered', ''))
            excerpt = _isl_strip_html((row.get('excerpt') or {}).get('rendered', ''))
            items.append({'id': row.get('id'), 'title': title, 'excerpt': excerpt,
                          'url': row.get('link', ''), 'source_name': 'Maktabah Salafiyyah',
                          'category': 'Books · 公开 WordPress 元数据',
                          'modified': row.get('modified', ''), 'rights': '按官方版权页使用'})
        if not items:
            items.append({'title': ('在 Maktabah Salafiyyah 官方目录查找：' + q) if q else 'Maktabah Salafiyyah 官方图书目录',
                          'excerpt': '该站当前未向本站返回可同步的书目元数据；请打开官方目录浏览，本站不会复制受保护正文。',
                          'url': 'https://maktabahsalafiyyah.org/category/books/',
                          'source_name': 'Maktabah Salafiyyah', 'category': '官方目录回退入口',
                          'rights': '以来源网站版权页为准'})
        return {'items': items, 'page': page, 'total': int(headers.get('x-wp-total', len(items)) or len(items)),
                'total_pages': int(headers.get('x-wp-totalpages', page) or page),
                'source_url': 'https://maktabahsalafiyyah.org/wp-json/wp/v2/posts'}
    if source == 'archive':
        term = q or 'Islamic'
        query = 'mediatype:texts AND (title:(' + term + ') OR subject:(' + term + '))'
        params = {'q': query, 'fl[]': ['identifier', 'title', 'creator', 'description', 'subject', 'rights', 'licenseurl'],
                  'rows': str(size), 'page': str(page), 'output': 'json'}
        # urlencode with doseq keeps IA's repeated fl[] fields intact.
        url = 'https://archive.org/advancedsearch.php?' + urlencode(params, doseq=True)
        data, _headers = _isl_json_get(url, 900)
        docs = ((data or {}).get('response') or {}).get('docs') or []
        items = []
        for row in docs:
            ident = row.get('identifier', '')
            items.append({'id': ident, 'title': row.get('title', ''), 'author': row.get('creator', ''),
                          'excerpt': row.get('description', ''), 'rights': row.get('rights', ''),
                          'url': 'https://archive.org/details/' + quote(str(ident)),
                          'source_name': 'Internet Archive / Open Library', 'category': '按条目核验权利'})
        total = int(((data or {}).get('response') or {}).get('numFound') or len(items))
        return {'items': items, 'page': page, 'total': total, 'source_url': 'https://archive.org/advancedsearch.php'}
    if source == 'sunnah':
        rows = [
            ('Sahih al-Bukhari · صحيح البخاري', 'https://sunnah.com/bukhari', '97 书 · 六大部'),
            ('Sahih Muslim · صحيح مسلم', 'https://sunnah.com/muslim', '57 书 · 六大部'),
            ('Sunan Abi Dawud · سنن أبي داود', 'https://sunnah.com/abudawud', '43 书 · 六大部'),
            ('Jami at-Tirmidhi · جامع الترمذي', 'https://sunnah.com/tirmidhi', '46 书 · 六大部'),
            ("Sunan an-Nasa'i · سنن النسائي", 'https://sunnah.com/nasai', '52 书 · 六大部'),
            ('Sunan Ibn Majah · سنن ابن ماجه', 'https://sunnah.com/ibnmajah', '37 书 · 六大部')]
        if q: rows = [x for x in rows if q.lower() in x[0].lower()]
        return {'items': [{'title': x[0], 'meta': x[2], 'url': x[1], 'source_name': 'Sunnah.com · 六大部圣训', 'category': '官方书目与原文链接'} for x in rows], 'page': 1, 'total': len(rows), 'source_url': 'https://sunnah.com/developers'}
    if source == 'quran':
        return {'items': [{'title': ('在 Quran.com 搜索：' + q) if q else '古兰经与经注学习中心',
                           'excerpt': '原文、译文、经注、逐词和诵读；本站已有 114 章内置内容。',
                           'url': 'https://quran.com/search?q=' + quote(q) if q else 'https://quran.com/',
                           'source_name': 'Quran.com / AlQuran.Cloud', 'category': '官方 API 与阅读入口'}], 'page': 1, 'total': 1, 'source_url': 'https://api.alquran.cloud/api'}
    if source == 'shamela':
        return {'items': [{'title': ('在 Shamela 官方站查找：' + q) if q else 'المكتبة الشاملة · 官方阿拉伯语书库',
                           'excerpt': '法学、法源学、经注、圣训、信仰、传记和语言等学科；使用官方只读网页或 MCP 按需阅读。',
                           'url': 'https://shamela.ws/', 'source_name': 'Shamela', 'category': '官方只读目录 / MCP'}], 'page': 1, 'total': 1, 'source_url': 'https://shamela.ws/mcp'}
    return {'items': [], 'page': page, 'total': 0}

class Handler(BaseHTTPRequestHandler):
    def _json(self, data, status=200):
        raw = json.dumps(data, ensure_ascii=False).encode("utf-8")
        use_gz = len(raw) > 40000 and 'gzip' in (self.headers.get('Accept-Encoding') or '').lower()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-store")
        if use_gz:
            raw = gzip.compress(raw, 6)
            self.send_header("Content-Encoding", "gzip")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)
    
    def _admin_page(self):
        try:
            fp = Path(DIR) / 'admin.html'
            if not fp.exists():
                fp = Path(__file__).parent / 'admin.html'
            data = fp.read_bytes()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            self._json({'error': str(e)}, 500)

    def _serve_local_audio(self, fp):
        """服务项目内音频，支持浏览器 Range 请求和 inline 播放。"""
        try:
            total = fp.stat().st_size
            rng = self.headers.get('Range', '')
            start, end, status = 0, total - 1, 200
            if rng.startswith('bytes=') and total:
                spec = rng[6:].split(',', 1)[0].strip()
                a, b = (spec.split('-', 1) + [''])[:2]
                if a == '':
                    length = int(b or 0)
                    start = max(0, total - length)
                else:
                    start = int(a)
                end = int(b) if b else total - 1
                if start < 0 or start >= total or end < start:
                    self.send_response(416)
                    self.send_header('Content-Range', 'bytes */%d' % total)
                    self.end_headers()
                    return
                end = min(end, total - 1)
                status = 206
            length = max(0, end - start + 1)
            self.send_response(status)
            self.send_header('Content-Type', AUDIO_CONTENT_TYPES.get(fp.suffix.lower(), 'application/octet-stream'))
            self.send_header('Content-Length', str(length))
            self.send_header('Accept-Ranges', 'bytes')
            if status == 206:
                self.send_header('Content-Range', 'bytes %d-%d/%d' % (start, end, total))
            self.send_header('Content-Disposition', 'inline; filename="%s"' % fp.name.replace('"', ''))
            self.send_header('Cache-Control', 'public, max-age=86400')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            with fp.open('rb') as f:
                f.seek(start)
                remain = length
                while remain:
                    chunk = f.read(min(65536, remain))
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    remain -= len(chunk)
        except (BrokenPipeError, ConnectionResetError):
            return
        except Exception as e:
            print('[本地音频服务错误]', e)
            try:
                self.send_error(404)
            except Exception:
                pass

    def _serve(self, path):
        try:
            from urllib.parse import unquote as _uq2
            path = _uq2(path)
        except Exception:
            pass
        if '..' in path:
            return self._json({'error': 'bad path'}, 400)
        # 先解析特殊媒体根目录，再做存在性检查；旧实现先检查 DIR/music，
        # 导致 music_out 里的 WAV/MP3 被错误回退成首页 HTML。
        if path.startswith('/music/'):
            _music_dir = getattr(music_gen, 'OUT_DIR', None) if music_gen else None
            fp = Path(_music_dir or (DIR / 'music_out')) / path[len('/music/'):]
        elif path.startswith('/images/'):
            fp = Path(DIR) / 'images' / path[len('/images/'):]
        elif path == '/pay_qr.png':
            fp = Path(DIR) / 'data' / 'pay_qr.png'
        else:
            fp = DIR / path.lstrip("/")
        if '..' in str(fp.relative_to(fp.anchor)):
            return self._json({'error': 'bad path'}, 400)
        # ===== 安全：拒绝下载敏感文件 =====
        _nm = fp.name.lower()
        if (_nm in SENSITIVE_STATIC_NAMES
                or _nm.startswith(SENSITIVE_STATIC_PREFIXES)
                or fp.suffix.lower() in SENSITIVE_STATIC_SUFFIXES):
            return self._json({'error': 'forbidden'}, 403)
        if fp.is_dir():
            fp = DIR / "arabic_learning.html"
        if not fp.exists():
            # 静态/数据文件缺失时不要回退成网页（否则前端拿到 HTML 解析 JSON 必崩）
            _suffix = Path(path).suffix.lower()
            if path.startswith('/api/') or _suffix in ('.json', '.js', '.css', '.webmanifest', '.txt', '.png', '.jpg', '.svg', '.ico'):
                self.send_response(404)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Content-Length', '2')
                self.end_headers()
                self.wfile.write(b'{}')
                return
            fp = DIR / "arabic_learning.html"
        if fp.suffix.lower() in AUDIO_EXTENSIONS:
            return self._serve_local_audio(fp)
        ct = {".html": "text/html; charset=utf-8", ".json": "application/json", ".flac": "audio/flac", ".wav": "audio/wav", ".m4a": "audio/mp4", ".mp3": "audio/mpeg", ".ogg": "audio/ogg", ".aac": "audio/aac", ".png": "image/png", ".jpg": "image/jpeg", ".js": "application/javascript; charset=utf-8", ".mjs": "application/javascript; charset=utf-8", ".webmanifest": "application/manifest+json", ".css": "text/css; charset=utf-8", ".svg": "image/svg+xml", ".ico": "image/x-icon", ".ttf": "font/ttf", ".otf": "font/otf", ".woff2": "font/woff2"}.get(fp.suffix, "application/octet-stream")
        try:
            suffix = fp.suffix.lower()
            static_suffixes = ('.json', '.js', '.mjs', '.css', '.webmanifest', '.svg', '.png', '.jpg', '.jpeg', '.ico', '.ttf', '.otf', '.woff2')
            is_cacheable = suffix in static_suffixes
            query = urlparse(self.path).query
            is_versioned = is_cacheable and bool(re.search(r'(?:^|&)v=[^&]+(?:&|$)', query))
            st = fp.stat()
            etag = '"%x-%x"' % (int(st.st_mtime_ns), int(st.st_size))
            # HTML and unversioned data stay revalidated; versioned assets can be immutable.
            if self.headers.get('If-None-Match', '').strip() == etag:
                self.send_response(304)
                self.send_header('ETag', etag)
                self.send_header('Cache-Control', 'public, max-age=31536000, immutable' if is_versioned else 'no-cache, must-revalidate, max-age=0')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Vary', 'Accept-Encoding')
                self.send_header('Content-Length', '0')
                self.end_headers()
                return
            data = fp.read_bytes()
            cache_control = ('public, max-age=31536000, immutable' if is_versioned else
                             ('public, max-age=86400' if suffix not in static_suffixes and suffix != '.html' else
                              'no-cache, must-revalidate, max-age=0'))
            # 大文本：gzip 压缩后传输，并缓存压缩结果。ETag 指向源文件版本。
            if suffix in (".html", ".json", ".js", ".css") and len(data) > 60000 and 'gzip' in (self.headers.get('Accept-Encoding') or '').lower():
                try:
                    gz = str(fp) + '.gz'
                    if (not os.path.exists(gz)) or os.path.getmtime(gz) < os.path.getmtime(fp):
                        with gzip.open(gz, 'wb', 6) as f:
                            f.write(data)
                    cdata = open(gz, 'rb').read()
                    self.send_response(200)
                    self.send_header("Content-Type", ct)
                    self.send_header("Content-Encoding", "gzip")
                    self.send_header("Content-Length", str(len(cdata)))
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.send_header("Cache-Control", cache_control)
                    self.send_header("ETag", etag)
                    self.send_header("Last-Modified", formatdate(st.st_mtime, usegmt=True))
                    self.send_header("Vary", "Accept-Encoding")
                    self.end_headers()
                    self.wfile.write(cdata)
                    return
                except Exception as e:
                    print('[gzip 失败]', e)
            self.send_response(200)
            self.send_header("Content-Type", ct)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", cache_control)
            self.send_header("ETag", etag)
            self.send_header("Last-Modified", formatdate(st.st_mtime, usegmt=True))
            if not is_versioned and (suffix in static_suffixes or suffix == '.html'):
                self.send_header("Pragma", "no-cache")
                self.send_header("Expires", "0")
            self.end_headers()
            self.wfile.write(data)
        except:
            self.send_error(404)
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
    
    def do_GET(self):
        p = urlparse(self.path).path
        # URL 解码（支持中文/阿语文件名，如 data/covers/三国演义.jpg）
        try:
            from urllib.parse import unquote as _uq
            p = _uq(p)
        except Exception:
            pass
        if '..' in p:
            return self._json({'error': 'bad path'}, 400)
        # 全新地址入口（绕过任何历史缓存）：/n/ 、 /app/ 、 /v2/
        if p in ('/n', '/n/', '/app', '/app/', '/v2', '/v2/', '/new'):
            return self._serve('/arabic_learning.html')
        # 根路径直接返回最新页面（不再 302；避免浏览器把旧跳转缓存住）
        if p in ('/', '/index.html'):
            return self._serve('/arabic_learning.html')
        # 统一域名：从 IP 或 www 进来的一律跳回 燃灯同学.com（保持同一路径）
        _host = (self.headers.get('Host') or '').split(':')[0].lower()
        if _host and _host not in ('xn--dqry4os3s3gb.com', 'localhost', '127.0.0.1') and not _host.endswith('.hstgr.cloud'):
            self.send_response(301)
            self.send_header('Location', 'https://xn--dqry4os3s3gb.com' + self.path)
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            return
        if (p.startswith('/api/admin/') or p == '/api/deploy_node') and p != '/api/admin/login' and not _is_admin(self):
            return self._json({'ok': False, 'msg': '需要管理员密码', 'need_admin': True}, 401)
        if p == '/admin':
            return self._admin_page()
        if p == '/api/auth/me':
            from urllib.parse import parse_qs
            qs = parse_qs(urlparse(self.path).query)
            token = (qs.get('token') or [''])[0]
            u = _check_token(token)
            if not u:
                return self._json({'ok': False, 'msg': '未登录或登录已过期'})
            vip, until = _vip_info(u)
            return self._json({'ok': True, 'username': u, 'vip': vip, 'vip_until': until})
        if p == '/api/admin/users':
            users = _load_users()
            today = time.strftime('%Y-%m-%d')
            out = []
            for k, v in users.items():
                until = v.get('vip_until', '')
                left = 0
                if until:
                    try:
                        left = max(0, int((time.mktime(time.strptime(until, '%Y-%m-%d')) - time.mktime(time.strptime(today, '%Y-%m-%d'))) / 86400))
                    except Exception:
                        left = 0
                q = v.get('ai_quota', {}) or {}
                out.append({'username': k, 'device': k[4:] if k.startswith('dev:') else k,
                            'vip': bool(v.get('vip')) and left > 0, 'vip_until': until,
                            'days_left': left, 'created': v.get('created', ''),
                            'ai_today': q.get('count', 0) if q.get('date') == today else 0,
                            'ai_used_cny': round(float(v.get('ai_used_cny', 0) or 0), 4),
                            'ai_quota_cny': round(float(v.get('ai_quota_cny', 0) or 0), 2),
                            'free_left': round(max(0.0, _monthly_free() - float(v.get('free_used', 0) or 0)), 2) if v.get('free_period') == today else _monthly_free(),
                            'paid_left': round(max(0.0, float(v.get('paid_total', 0) or 0) - float(v.get('paid_used', 0) or 0)), 2)})
            out.sort(key=lambda x: (str(x['created']), x['username']), reverse=True)
            return self._json({'ok': True, 'users': out, 'total': len(out), 'vip': sum(1 for x in out if x['vip'])})
        if p == '/api/admin/status':
            return self._json(admin_panel.status())
        if p == '/api/admin/kinds':
            try:
                return self._json(admin_panel.kinds())
            except Exception as e:
                return self._json({'ok': False, 'error': str(e)}, 500)
        if p == '/api/admin/data':
            from urllib.parse import parse_qs
            qs = parse_qs(urlparse(self.path).query)
            kind = (qs.get('kind') or ['sentences'])[0]
            page = int((qs.get('page') or ['0'])[0])
            q = (qs.get('q') or [''])[0]
            return self._json(admin_panel.data_list(kind, page, q=q))
        if p == '/api/admin/ai':
            return self._json(admin_panel.get_ai_config())
        if p == '/api/admin/codes':
            return self._json(_admin_codes_payload())
        if p == '/api/pay/status':
            from urllib.parse import parse_qs
            qs = parse_qs(urlparse(self.path).query)
            dev = (qs.get('device_id') or [''])[0].strip()
            tok = (qs.get('token') or [''])[0].strip()
            u = _check_token(tok) if tok else ('dev:' + dev if dev else '')
            d = _load_pays()
            mine = [x for x in d['items'] if (x.get('user') == u or (dev and x.get('device') == dev))]
            mine.sort(key=lambda x: str(x.get('ts', '')), reverse=True)
            top = mine[0] if mine else None
            return self._json({'ok': True, 'status': (top or {}).get('status', 'none'),
                               'code': (top or {}).get('unlock_code') or (top or {}).get('code') or '',
                               'amount': (top or {}).get('amount', 0)})
        if p == '/api/home_stats':
            return self._json(_home_stats())
        if p == '/api/videos':
            from urllib.parse import parse_qs
            qs = parse_qs(urlparse(self.path).query)
            cat = (qs.get('cat') or [''])[0]
            q = (qs.get('q') or [''])[0].strip().lower()
            d = _load_videos()
            vs = d.get('videos', [])
            if cat:
                vs = [v for v in vs if v.get('cat') == cat]
            if q:
                vs = [v for v in vs if q in ((v.get('t') or '') + (v.get('ch') or '')).lower()]
            return self._json({'ok': True, 'cats': d.get('cats', []), 'total': len(vs), 'videos': vs[:120], 'updated': d.get('updated', '')})
        if p == '/api/thumb':
            from urllib.parse import parse_qs
            qs = parse_qs(urlparse(self.path).query)
            vid = re.sub(r'[^A-Za-z0-9_-]', '', (qs.get('id') or [''])[0])[:16]
            if not vid:
                return self._json({'error': 'bad id'}, 400)
            try:
                cdir = os.path.join(DIR, 'cache', 'thumb')
                os.makedirs(cdir, exist_ok=True)
                fp = os.path.join(cdir, vid + '.jpg')
                if not os.path.exists(fp) or os.path.getsize(fp) < 500:
                    u = 'https://i.ytimg.com/vi/%s/mqdefault.jpg' % vid
                    req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
                    open(fp, 'wb').write(urllib.request.urlopen(req, timeout=20).read())
                data = open(fp, 'rb').read()
                self.send_response(200)
                self.send_header('Content-Type', 'image/jpeg')
                self.send_header('Content-Length', str(len(data)))
                self.send_header('Cache-Control', 'public, max-age=604800')
                self.end_headers()
                self.wfile.write(data)
                return
            except Exception as e:
                return self._json({'error': str(e)}, 502)
        if p == '/api/plans':
            try:
                pr = _load_pricing()
                return self._json({'ok': True, 'pay': pr.get('pay', {}), 'plans': pr.get('plans', []),
                                   'pay_qr': os.path.exists(os.path.join(DIR, 'data', 'pay_qr.png'))})
            except Exception as e:
                return self._json({'ok': False, 'error': str(e)}, 500)
        if p == '/api/access/status':
            # 站长的设备（unlimited_devices 里）永久解锁，不受门禁影响
            try:
                from urllib.parse import parse_qs as _pq
                _q = _pq(urlparse(self.path).query)
                _dv = (_q.get('device_id') or [''])[0].strip()
                _ip = (self.headers.get('X-Forwarded-For') or '').split(',')[0].strip()
                _ul = _ai_cfg().get('unlimited_devices') or []
                if (_dv and _dv in _ul) or (_ip and _ip in _ul):
                    return self._json({'ok': True, 'active': True, 'until': '2099-12-31', 'days_left': 9999, 'owner': True})
            except Exception as _e:
                print('[门禁-站长判定失败]', _e)
            from urllib.parse import parse_qs
            qs = parse_qs(urlparse(self.path).query)
            dev = (qs.get('device_id') or [''])[0].strip()
            tok = (qs.get('token') or [''])[0].strip()
            u = _check_token(tok) if tok else ('dev:' + dev if dev else '')
            ok, until, left = _sub_status(u) if u else (False, '', 0)
            return self._json({'ok': True, 'active': ok, 'until': until, 'days_left': left})
        if p == '/api/me/usage':
            from urllib.parse import parse_qs
            qs = parse_qs(urlparse(self.path).query)
            token = (qs.get('token') or [''])[0]
            u = _check_token(token) if token else None
            if not u:
                return self._json({'ok': False, 'msg': '未激活'})
            b = _user_bal(u)
            vip, until = _vip_info(u)
            b.update({'username': u, 'vip': vip, 'until': until})
            b['quota'] = b['left']            # 兼容旧前端
            b['used'] = b['used_total']
            return self._json(b)
        if p == '/api/admin/pricing':
            return self._json({'ok': True, 'pricing': _load_pricing()})
        if p == '/api/admin/payments':
            d = _load_pays()
            items = sorted(d['items'], key=lambda x: (x.get('status') != 'pending', str(x.get('ts', ''))), reverse=False)
            pend = [x for x in items if x.get('status') == 'pending']
            return self._json({'ok': True, 'items': items[:200], 'pending': len(pend), 'total': len(items)})
        if p == '/api/admin/stats':
            users = _load_users()
            c = _load_codes()
            today = time.strftime('%Y-%m-%d')
            _rec = [{'code': k, 'by': v.get('used_by', ''), 'at': v.get('used_at', ''), 'days': v.get('days')} for k, v in c.get('codes', {}).items() if v.get('used')]
            _rec.sort(key=lambda x: str(x['at']), reverse=True)
            _ai_used = round(sum(float(u.get('ai_used_cny', 0) or 0) for u in users.values()), 4)
            _ai_quota = round(sum(float(u.get('ai_quota_cny', 0) or 0) for u in users.values()), 2)
            _pl = _load_pays().get('items', [])
            _pend = len([x for x in _pl if x.get('status') == 'pending'])
            _today = time.strftime('%Y-%m-%d')
            _pay_today = [x for x in _pl if str(x.get('ts', '')).startswith(_today)]
            _pay_all = [x for x in _pl if x.get('status') in ('auto', 'approved')]
            _pay_today_ok = [x for x in _pay_today if x.get('status') in ('auto', 'approved')]
            _income_today = round(sum(float(x.get('amount', 0) or 0) for x in _pay_today_ok), 2)
            _income_total = round(sum(float(x.get('amount', 0) or 0) for x in _pay_all), 2)
            _income_ai = round(sum(float(x.get('quota', 0) or 0) for x in _pay_all), 2)
            return self._json({'ai_spend_month': round(_global_spend(), 4), 'pay_pending': _pend, 'pay_today_count': len(_pay_today), 'pay_today_income': _income_today, 'pay_total_income': _income_total, 'pay_total_count': len(_pay_all), 'pay_ai_granted': _income_ai, 'ai_used_total': _ai_used, 'ai_quota_total': _ai_quota, 'recent': _rec[:8], 'new_users_today': sum(1 for u in users.values() if u.get('created') == today), 'ok': True, 'users': len(users),
                               'vip': sum(1 for u in users.values() if u.get('vip')),
                               'codes_total': len(c.get('codes', {})),
                               'codes_used': sum(1 for v in c.get('codes', {}).values() if v.get('used')),
                               'codes_today': sum(1 for v in c.get('codes', {}).values() if v.get('created') == today),
                               'today': today})

        p = urlparse(self.path).path
        if p == '/api/recite':
            # 古兰经诵读中转：小文件缓存、大文件流式（边下边播 + 支持断点续传）
            try:
                from urllib.parse import parse_qs, urlparse as _up
                qs = parse_qs(urlparse(self.path).query)
                u = (qs.get('u') or [''])[0]
                host = (_up(u).hostname or '').lower()
                ALLOW = ('mp3quran.net', 'quran.com', 'everyayah.com', 'islamic.network', 'qurancdn.com', 'quranicaudio.com')
                if not u or not any(host == d or host.endswith('.' + d) for d in ALLOW):
                    return self._json({'error': 'domain not allowed'}, 403)
                key = hashlib.md5(u.encode()).hexdigest()
                cdir = os.path.join(DIR, 'cache', 'recite')
                os.makedirs(cdir, exist_ok=True)
                fp = os.path.join(cdir, key + '.mp3')
                rng = self.headers.get('Range')
                # 1) 命中缓存（客户端没有 Range 请求时）
                if os.path.exists(fp) and os.path.getsize(fp) > 1000 and not rng:
                    data = open(fp, 'rb').read()
                    self.send_response(200)
                    self.send_header('Content-Type', 'audio/mpeg')
                    self.send_header('Content-Length', str(len(data)))
                    self.send_header('Accept-Ranges', 'bytes')
                    self.send_header('Cache-Control', 'public, max-age=604800')
                    self.end_headers()
                    self.wfile.write(data)
                    return
                req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
                if rng:
                    req.add_header('Range', rng)
                resp = urllib.request.urlopen(req, timeout=30)
                clen = resp.headers.get('Content-Length')
                crange = resp.headers.get('Content-Range')
                code = 206 if (rng and crange) else 200
                # 2) 小文件：整段读取 + 落盘缓存
                if clen and int(clen) < 6 * 1024 * 1024 and not rng:
                    blob = resp.read()
                    try:
                        open(fp, 'wb').write(blob)
                    except Exception:
                        pass
                    self.send_response(200)
                    self.send_header('Content-Type', 'audio/mpeg')
                    self.send_header('Content-Length', str(len(blob)))
                    self.send_header('Accept-Ranges', 'bytes')
                    self.send_header('Cache-Control', 'public, max-age=604800')
                    self.end_headers()
                    self.wfile.write(blob)
                    return
                # 3) 大文件：流式转发（边下边播）
                self.send_response(code)
                self.send_header('Content-Type', 'audio/mpeg')
                if clen:
                    self.send_header('Content-Length', clen)
                if crange:
                    self.send_header('Content-Range', crange)
                self.send_header('Accept-Ranges', 'bytes')
                self.send_header('Cache-Control', 'public, max-age=604800')
                self.end_headers()
                try:
                    while True:
                        chunk = resp.read(65536)
                        if not chunk:
                            break
                        self.wfile.write(chunk)
                except Exception:
                    pass
                return
            except Exception as e:
                print('[诵读中转错误]', e)
                return self._json({'error': str(e)}, 502)
        if p == '/api/asr/status':
            try:
                import importlib.util
                fw = importlib.util.find_spec('faster_whisper') is not None
                md = os.path.expanduser('~/.cache/huggingface/hub/models--Systran--faster-whisper-small')
                self._json({'asr': fw and os.path.isdir(md), 'model_ready': os.path.isdir(md), 'lib_ready': fw})
            except Exception as e:
                self._json({'asr': False, 'error': str(e)})
            return
        if p == '/api/nodes':
            # 高速节点列表（App 用）：只读最近成功缓存，刷新由后台单飞worker执行
            try:
                state = _sub_start_refresh()
                y = state['data']
                import re as _re
                names = _re.findall(r'  - name: (.+)', y)
                servers = _re.findall(r'    server: (.+)', y)
                ports = _re.findall(r'    port: (\d+)', y)
                nodes = [{'name': names[i] if i < len(names) else '?', 'server': servers[i] if i < len(servers) else '', 'port': int(ports[i]) if i < len(ports) else 0} for i in range(min(len(names), 20))]
                return self._json({'ok': True, 'count': len(names), 'nodes': nodes,
                                   'sub': f'http://{self.headers.get("Host", "127.0.0.1")}/sub',
                                   'refreshing': bool(state['refreshing']),
                                   'stale': bool(state['stale']),
                                   'age_seconds': state['age_seconds'],
                                   'last_success': state['last_success'],
                                   'last_error': state['last_error']})
            except Exception as e:
                return self._json({'error': str(e)}, 500)
        if p == '/sub':
            # 免费节点订阅：只读缓存；任何外部刷新都在后台执行，不能阻塞订阅请求
            try:
                state = _sub_start_refresh()
                data = state['data'] or _SUB_EMPTY_YAML
                self.send_response(200)
                self.send_header('Content-Type', 'text/yaml; charset=utf-8')
                self.send_header('Content-Length', str(len(data)))
                self.send_header('Cache-Control', 'no-store')
                self.send_header('X-Nour-Sub-Refreshing', '1' if state['refreshing'] else '0')
                self.send_header('X-Nour-Sub-Stale', '1' if state['stale'] else '0')
                self.end_headers()
                self.wfile.write(data.encode('utf-8'))
            except Exception as e:
                print(f'[Sub Error] {e}')
                try:
                    self.send_response(500)
                    self.send_header('Content-Type', 'text/plain')
                    self.end_headers()
                    self.wfile.write(('订阅生成失败: ' + str(e)).encode())
                except Exception:
                    pass
            return
        if p == '/api/quran/proxy':
            # 代理远程古兰经音频（解决国外源访问慢/被墙）：手机 → 本地服务器 → mp3quran
            try:
                from urllib.parse import parse_qs
                import shutil
                qs = parse_qs(urlparse(self.path).query)
                u = (qs.get('u') or [''])[0]
                if not u:
                    return self._json({'error': 'no url'}, 400)
                req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'})
                resp = urllib.request.urlopen(req, timeout=20)
                self.send_response(200)
                self.send_header('Content-Type', resp.headers.get('Content-Type', 'audio/mpeg'))
                cl = resp.headers.get('Content-Length')
                if cl:
                    self.send_header('Content-Length', cl)
                self.end_headers()
                shutil.copyfileobj(resp, self.wfile)
                return
            except Exception as e:
                try:
                    self.send_response(502)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(('{\"error\":\"proxy fail: ' + str(e) + '\"}').encode())
                except Exception:
                    pass
                return
        if p == '/api/catalog/meta':
            catdata = _catalog()
            meta = dict(catdata.get('meta') or {})
            books = catdata.get('books') or []
            counts = {}
            for book in books:
                labels = book.get('disciplines') if isinstance(book.get('disciplines'), list) else [book.get('c')]
                labels = [str(x or '未分类') for x in labels] or ['未分类']
                for label in labels:
                    counts[label] = counts.get(label, 0) + 1
            meta['total'] = len(books)
            meta['categories'] = counts
            meta['series_counts'] = counts
            return self._json(meta)
        if p == '/api/theme/source-feed':
            try:
                from urllib.parse import parse_qs
                qs = parse_qs(urlparse(self.path).query)
                return self._json(_public_source_feed(
                    (qs.get('q') or [''])[0], (qs.get('kind') or [''])[0],
                    (qs.get('status') or ['all'])[0], (qs.get('limit') or ['20'])[0],
                ))
            except Exception as e:
                return self._json({'ok': False, 'error': str(e)[:240]}, 500)
        if p == '/api/library/classics':
            # 经典扩展只读元数据 API；size 有界，正文复用 /api/read?t=shamela。
            try:
                from urllib.parse import parse_qs
                qs = parse_qs(urlparse(self.path).query)
                collection = (qs.get('collection') or [''])[0].strip().lower()
                query = (qs.get('q') or [''])[0].strip().lower()
                page = max(0, int((qs.get('page') or ['0'])[0]))
                size = max(1, min(100, int((qs.get('size') or ['24'])[0])))
                d = _classics_index()
                items = d.get('items') or []
                if collection and collection not in ('all', '全部'):
                    items = [x for x in items if str(x.get('collection') or '').lower() == collection]
                if query:
                    items = [x for x in items if query in ' '.join(str(x.get(k) or '') for k in ('title_ar', 'title', 'collection_label', 'source_pool')).lower()]
                total = len(items)
                return self._json({
                    'ok': True, 'total': total, 'page': page, 'size': size,
                    'items': items[page * size:(page + 1) * size],
                    'reading_paths': d.get('reading_paths') or [],
                    'meta': d.get('meta') or {},
                    'reading_entry': "openReadById(id, 'shamela')",
                })
            except Exception as e:
                return self._json({'ok': False, 'error': str(e)[:240]}, 500)
        if p == '/api/library/fiqh-schools':
            # 四学派导航只返回有界元数据；正文仍复用现有站内阅读/官方来源入口。
            try:
                from urllib.parse import parse_qs
                qs = parse_qs(urlparse(self.path).query)
                size = max(2, min(8, int((qs.get('size') or ['6'])[0])))
                catalog = _catalog()
                books = catalog.get('books') or []
                school_defs = [
                    ('hanafi', '哈乃斐学派', 'الحنفية', '追踪文本、类比、法学偏好与学派内部诸师意见。'),
                    ('maliki', '马立克学派', 'المالكية', '追踪传述、麦地那实践、公共利益与学派传承。'),
                    ('shafii', '沙斐仪学派', 'الشافعية', '追踪文本说明、圣训规范性、共识与类比的关系。'),
                    ('hanbali', '汉百里学派', 'الحنابلة', '追踪经文、圣训、先贤传述与推理的具体处理。'),
                ]
                pinned = {
                    'hanafi': ['fiqh-quduri', 'usul-sarakhsi', 'openiti-7720a0688601b8a6', 'openiti-2ea95ce78970567f'],
                    'maliki': ['fiqh-bidaya', 'fiqh-muwatta'],
                    'shafii': ['fiqh-risala', 'usul-risala'],
                    'hanbali': ['fiqh-mughni'],
                }
                def _school_item(b):
                    bid = str(b.get('id') or '')
                    guide = b.get('ai_guide') if isinstance(b.get('ai_guide'), dict) else {}
                    # 《مختصر القدوري》 has a verified local Shamela index entry 8220.
                    # Keep the catalog identity for the guide/evidence chain, but open
                    # the complete pages.jsonl inside the existing reader on demand.
                    reader_type = ''
                    read_id = ''
                    reader_source_url = ''
                    if bid == 'fiqh-quduri':
                        reader_type = 'shamela'
                        read_id = '8220'
                        reader_source_url = 'https://shamela.ws/book/8220'
                    in_app = bool(reader_type or b.get('text_mode') == 'arabic_original_link' or b.get('text_url') or bid.startswith('openiti-') or b.get('r'))
                    return {
                        'id': bid, 't': b.get('t', ''), 'a': b.get('a', ''),
                        'y': b.get('y', ''), 'c': b.get('c', ''), 'c_ar': b.get('c_ar', ''),
                        'source': b.get('source', ''), 'access': b.get('access', ''),
                        'rights': b.get('rights', ''), 'u': b.get('u', ''),
                        'text_url': b.get('text_url', ''), 'text_mode': b.get('text_mode', ''),
                        'reader_type': reader_type, 'read_id': read_id,
                        'reader_source_url': reader_source_url,
                        'fiqh_schools': (b.get('fiqh_schools') or [])[:4],
                        'fiqh_school_labels': (b.get('fiqh_school_labels') or [])[:4],
                        'fiqh_school_inference': b.get('fiqh_school_inference', ''),
                        'intro': b.get('intro', ''), 'level': b.get('level', ''),
                        'ai_profile': b.get('ai_profile', ''), 'ai_guide_version': b.get('ai_guide_version', ''),
                        'ai_guide': {
                            'summary': guide.get('summary', ''),
                            'historical_context': guide.get('historical_context', ''),
                            'study_objectives': (guide.get('study_objectives') or [])[:4],
                            'reading_route': (guide.get('reading_route') or [])[:4],
                            'key_terms': (guide.get('key_terms') or [])[:8],
                            'comparative_focus': (guide.get('comparative_focus') or [])[:4],
                            'evidence_boundary': guide.get('evidence_boundary', ''),
                            'sources': (guide.get('sources') or [])[:6],
                        },
                        'in_app': in_app,
                        'reading_label': ('站内全文（Shamela）' if reader_type == 'shamela' else ('站内原文' if in_app else '书目导读 / 官方入口')),
                    }
                out = []
                for sid, name, ar, lens in school_defs:
                    rows = [b for b in books if sid in (b.get('fiqh_schools') or [])]
                    pins = pinned.get(sid, [])
                    rows.sort(key=lambda b: (
                        pins.index(str(b.get('id'))) if str(b.get('id')) in pins else 99,
                        0 if (b.get('text_mode') == 'arabic_original_link' or str(b.get('id') or '').startswith('openiti-')) else 1,
                        str(b.get('t') or ''),
                    ))
                    out.append({
                        'id': sid, 'name': name, 'ar': ar, 'count': len(rows), 'lens': lens,
                        'items': [_school_item(b) for b in rows[:size]],
                    })
                return self._json({
                    'ok': True,
                    'schools': out,
                    'notice': '学派标签依据公开书目、作者与作品线索推断；具体主张、版本、页码与证据必须回到原典核验。',
                })
            except Exception as e:
                return self._json({'ok': False, 'error': str(e)[:240]}, 500)
        if p == '/api/catalog':
            # 服务端分页：手机端一次只取一小页，避免爆内存
            try:
                from urllib.parse import parse_qs
                qs = parse_qs(urlparse(self.path).query)
                cat = (qs.get('cat') or [''])[0]
                tag = (qs.get('tag') or [''])[0].strip().lower()
                school = (qs.get('school') or [''])[0].strip().lower()
                q = (qs.get('q') or [''])[0].strip().lower()
                page = max(0, int((qs.get('page') or ['0'])[0]))
                size = max(1, min(200, int((qs.get('size') or ['60'])[0])))
                books = _catalog().get('books', [])
                if q:
                    books = [b for b in books if q in ' '.join(str(b.get(k) or '') for k in ('t', 'a', 'c', 'c_ar', 'source', 'intro', 'openiti')).lower()]
                if cat and cat not in ('', '全部'):
                    books = [b for b in books if b.get('c') == cat or cat in (b.get('disciplines') or [])]
                if tag:
                    books = [b for b in books if tag in (b.get('catalog_tags') or [])]
                if school:
                    books = [b for b in books if school in (b.get('fiqh_schools') or [])]
                total = len(books)
                items = books[page * size:(page + 1) * size]
                return self._json({'total': total, 'page': page, 'size': size, 'items': items})
            except Exception as e:
                return self._json({'error': str(e)}, 500)
        if p == '/api/catalog/read':
            # OpenITI/KITAB：仅允许固定 release 的官方 raw 文本，首次按需缓存，正文按页返回。
            try:
                from urllib.parse import parse_qs
                qs = parse_qs(urlparse(self.path).query)
                book = _openiti_book((qs.get('id') or [''])[0])
                if not book:
                    return self._json({'error': '书目不存在或不是可内置阅读的 OpenITI 原文'}, 404)
                # 大型 OpenITI 书目使用流式 Range + 增量 UTF-8 分页；
                # 小型旧缓存仍由旧实现兼容，避免一次升级清空已有阅读缓存。
                if _openiti_stream_read_page is not None:
                    page = max(0, int((qs.get('page') or ['0'])[0]))
                    payload, status = _openiti_stream_read_page(
                        book, page, DIR / 'data' / 'cache' / 'openiti_stream'
                    )
                    return self._json(payload, status)
                pages = _openiti_pages(book)
                page = max(0, int((qs.get('page') or ['0'])[0]))
                if page >= len(pages):
                    return self._json({'error': '页码超出范围', 'total': len(pages)}, 416)
                return self._json({
                    't': 'openiti', 'id': book.get('id'), 'title': book.get('t', ''),
                    'author': book.get('a', ''), 'page': page, 'total': len(pages),
                    'text': pages[page], 'source': book.get('source', 'OpenITI/KITAB'),
                    'source_url': book.get('u', ''), 'text_url': book.get('text_url', ''),
                    'rights': book.get('rights', ''), 'cached': True,
                })
            except OpenITIStreamError as e:
                payload = e.payload()
                payload.setdefault('streaming', True)
                return self._json(payload, e.status)
            except ValueError as e:
                return self._json({'error': str(e)}, 413)
            except Exception as e:
                print('[OpenITI read]', e)
                return self._json({'error': '原文暂时无法载入，请稍后重试。'}, 502)
        if p == '/api/read':
            # 可读全文：Shamela4（逐页 pages.jsonl） / waqfeya（整本 txt）
            try:
                from urllib.parse import parse_qs, quote
                qs = parse_qs(urlparse(self.path).query)
                t = (qs.get('t') or ['shamela'])[0]
                cdir = DIR / 'data' / 'cache' / 'books'
                cdir.mkdir(parents=True, exist_ok=True)
                if t == 'shamela':
                    bid = str((qs.get('id') or [''])[0])
                    info = _shamela_index().get(bid)
                    if not info:
                        return self._json({'error': 'book not found', 'id': bid}, 404)
                    pf = cdir / ('s_' + bid + '.jsonl')
                    if not pf.exists():
                        _dl(HF_SHAMELA + '/' + quote(info['dir']) + '/pages.jsonl', pf)
                    pages = []
                    with open(pf, encoding='utf-8') as f:
                        for line in f:
                            line = line.strip()
                            if not line:
                                continue
                            try:
                                pages.append(json.loads(line))
                            except Exception:
                                pass
                    return self._json({'t': 'shamela', 'id': bid, 'title': info.get('slug', ''), 'cat': info.get('cat', ''), 'pages': pages})
                else:
                    rp = (qs.get('p') or [''])[0]
                    if not rp or '..' in rp:
                        return self._json({'error': 'bad path'}, 400)
                    safe = re.sub(r'[^0-9A-Za-z_.-]', '_', rp)[-140:]
                    cf = cdir / ('w_' + safe + '.txt')
                    if not cf.exists():
                        _dl(HF_WAQFEYA + '/' + quote(rp), cf)
                    txt = cf.read_text(encoding='utf-8', errors='ignore')
                    return self._json({'t': 'waqfeya', 'text': txt})
            except Exception as e:
                return self._json({'error': 'read fail: ' + str(e)}, 500)
        if p == '/api/hnote':
            # 圣训：译文 + 经注（有缓存直接返回，无则生成并缓存）
            try:
                from urllib.parse import parse_qs
                qs = parse_qs(urlparse(self.path).query)
                book = (qs.get('b') or ['bukhari'])[0]
                num = str((qs.get('n') or [''])[0])
                ar = (qs.get('ar') or [''])[0]
                d = _an_get(book)
                if num and num in d and d[num].get('cn'):
                    return self._json(d[num])
                if not ar and num:
                    # 服务端自己从书中取原文，避免 URL 过长
                    try:
                        bf = DIR / 'data' / 'hadith' / (book + '.json')
                        bj = json.loads(bf.read_text(encoding='utf-8'))
                        for x in bj.get('hadiths', []):
                            if str(x.get('n')) == num:
                                ar = x.get('ar', '')
                                break
                    except Exception:
                        pass
                if not ar:
                    return self._json({'error': 'no text'}, 400)
                got = make_annotation(ar, book, num)
                if num:
                    d[num] = got
                    _an_save(book)
                return self._json(got)
            except Exception as e:
                return self._json({'error': 'annotate fail: ' + str(e)}, 500)
        if p == '/api/hnote/status':
            total = 0
            done = 0
            try:
                idx = DIR / 'data' / 'hadith' / 'index.json'
                if idx.exists():
                    for b in json.loads(idx.read_text(encoding='utf-8'))['books']:
                        total += b['n']
                        f = DIR / 'data' / 'hadith' / 'an' / (b['key'] + '.json')
                        if f.exists():
                            try:
                                done += len(json.loads(f.read_text(encoding='utf-8')))
                            except Exception:
                                pass
            except Exception:
                pass
            return self._json({'total': total, 'done': done})
        if p == '/api/history':
            # 世界史书（Archive.org）目录，服务端分页
            try:
                from urllib.parse import parse_qs
                qs = parse_qs(urlparse(self.path).query)
                lang = (qs.get('cat') or [''])[0]
                q = (qs.get('q') or [''])[0].strip().lower()
                page = max(0, int((qs.get('page') or ['0'])[0]))
                size = max(1, min(200, int((qs.get('size') or ['60'])[0])))
                idx = _history()
                books = idx.get('books', [])
                cats = {}
                for b in books:
                    k = (b.get('lang') or '未知')
                    cats[k] = cats.get(k, 0) + 1
                if q:
                    books = [b for b in books if q in (b.get('title') or '').lower() or q in (b.get('creator') or '').lower()]
                if lang and lang not in ('', '全部'):
                    books = [b for b in books if (b.get('lang') or '未知') == lang]
                total = len(books)
                items = books[page * size:(page + 1) * size]
                top = dict(sorted(cats.items(), key=lambda x: -x[1])[:40])
                return self._json({'total': total, 'categories': top, 'page': page, 'size': size, 'items': items})
            except Exception as e:
                return self._json({'error': str(e)}, 500)
        if p == '/api/histbook':
            # 按需取正文：中文（殆知阁本地 txt） / 阿拉伯语（原书链接）
            try:
                from urllib.parse import parse_qs, quote
                qs = parse_qs(urlparse(self.path).query)
                bid = (qs.get('id') or [''])[0]
                if not bid:
                    return self._json({'error': 'bad id'}, 400)
                meta = {}
                for b in _history().get('books', []):
                    if b.get('id') == bid:
                        meta = b
                        break
                if bid.startswith('cn:'):
                    cid = bid[3:]
                    fp = DIR / 'data' / 'cn_books' / 't' / (cid + '.txt')
                    if not fp.exists():
                        return self._json({'error': 'file not found'}, 404)
                    txt = fp.read_text(encoding='utf-8', errors='ignore')
                    return self._json({'id': bid, 'title': meta.get('title', ''), 'lang': 'zh', 'text': txt[:400000]})
                # 阿拉伯语：优先从 Shamela4 本地缓存/数据集恢复正文；不可读时再跳转原书
                rid = (meta.get('rid') or {}).get('id')
                got = _shamela_text(rid)
                if got and got.get('text'):
                    return self._json({'id': bid, 'title': meta.get('title', '') or got.get('title', ''),
                                       'lang': 'ar', 'text': got['text'],
                                       'pages': got.get('pages', 0), 'source': got.get('source', 'shamela')})
                external = meta.get('u', '') or ('https://shamela.ws/book/' + str(rid)) if rid else meta.get('u', '')
                return self._json({'id': bid, 'title': meta.get('title', ''), 'lang': 'ar',
                                   'text': '', 'url': external, 'source': 'external'})
            except Exception as e:
                return self._json({'error': 'hist fail: ' + str(e)}, 500)
        if p == '/api/cnbooks':
            # 中国古籍（殆知阁）目录，服务端分页 + 全量分类计数
            try:
                from urllib.parse import parse_qs
                qs = parse_qs(urlparse(self.path).query)
                cat = (qs.get('cat') or [''])[0]
                q = (qs.get('q') or [''])[0].strip().lower()
                page = max(0, int((qs.get('page') or ['0'])[0]))
                size = max(1, min(200, int((qs.get('size') or ['60'])[0])))
                books = _cn_books().get('books', [])
                cats = {}
                for b in books:
                    k = b.get('category') or '其他'
                    cats[k] = cats.get(k, 0) + 1
                if q:
                    books = [b for b in books if q in (b.get('title') or '').lower()]
                if cat and cat not in ('', '全部'):
                    books = [b for b in books if b.get('category') == cat]
                total = len(books)
                items = books[page * size:(page + 1) * size]
                slim = [{'id': b.get('id'), 'title': b.get('title', ''), 'category': b.get('category', '')} for b in items]
                return self._json({'total': total, 'categories': cats, 'page': page, 'size': size, 'items': slim})
            except Exception as e:
                return self._json({'error': str(e)}, 500)
        if p == '/api/cnbook':
            # 取中国古籍正文（本地副本；超大书只返回前 30 万字符）
            try:
                from urllib.parse import parse_qs
                qs = parse_qs(urlparse(self.path).query)
                bid = (qs.get('id') or [''])[0]
                if not bid or not bid.isdigit():
                    return self._json({'error': 'bad id'}, 400)
                info = None
                for b in _cn_books().get('books', []):
                    if b.get('id') == bid:
                        info = b
                        break
                if not info:
                    return self._json({'error': 'book not found', 'id': bid}, 404)
                tf = DIR / 'data' / 'cn_books' / 't' / (bid + '.txt')
                if not tf.exists():
                    return self._json({'error': 'text missing', 'id': bid}, 404)
                txt = tf.read_text(encoding='utf-8', errors='ignore')
                return self._json({'id': bid, 'title': info.get('title', ''), 'category': info.get('category', ''), 'chars': len(txt), 'text': txt})
            except Exception as e:
                return self._json({'error': 'cnbook fail: ' + str(e)}, 500)
        if p == '/api/cover':
            try:
                from urllib.parse import parse_qs, quote
                qs = parse_qs(urlparse(self.path).query)
                title = (qs.get('t') or [''])[0].strip()
                if not title:
                    return self.send_error(404)
                import hashlib as _hl
                h = _hl.md5(title.encode('utf-8')).hexdigest()[:16]
                cdir = DIR / 'data' / 'covers'
                cdir.mkdir(parents=True, exist_ok=True)
                cf = cdir / ('q_' + h + '.jpg')
                missf = cdir / ('q_' + h + '.miss')
                if cf.exists() and cf.stat().st_size > 3000:
                    data = cf.read_bytes()
                elif missf.exists():
                    return self.send_error(404)
                else:
                    data = b''
                    try:
                        # ① 先试 Archive.org（有大量扫描真封面，无需密钥）
                        try:
                            au = ('https://archive.org/advancedsearch.php?q=title%3A(' + quote(title, safe='') +
                                  ')&fl%5B%5D=identifier&fl%5B%5D=title&rows=6&output=json')
                            areq = urllib.request.Request(au, headers={'User-Agent': 'Mozilla/5.0'})
                            with urllib.request.urlopen(areq, timeout=14) as ar:
                                aj = json.loads(ar.read().decode('utf-8'))
                            for _doc in (((aj.get('response') or {}).get('docs')) or []):
                                _id = _doc.get('identifier')
                                if not _id:
                                    continue
                                # 书名必须对得上（archive 里 title 字段要含查询词的核心部分）
                                _dt = str(_doc.get('title') or '') + ' ' + str(_id)
                                _core = title.replace(' ', '')[:6]
                                if _core and (_core not in _dt.replace(' ', '')):
                                    continue
                                iu2 = 'https://archive.org/services/img/' + _id
                                try:
                                    r3 = urllib.request.Request(iu2, headers={'User-Agent': 'Mozilla/5.0'})
                                    with urllib.request.urlopen(r3, timeout=14) as r4:
                                        _d2 = r4.read()
                                    if _d2 and _img_ok(_d2):
                                        data = _d2
                                        break
                                except Exception:
                                    continue
                        except Exception as _ae:
                            print('[archive.org 失败]', title[:18], _ae)
                        u = ('https://openlibrary.org/search.json?q=' + quote(title, safe='') +
                             '&limit=5&fields=cover_i,title,language')
                        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(req, timeout=14) as r:
                            j = json.loads(r.read().decode('utf-8'))
                        if data and len(data) > 3500:
                            pass
                        cid = None
                        for doc in (j.get('docs') or []):
                            if doc.get('cover_i'):
                                cid = doc['cover_i']
                                break
                        if cid and not (data and _img_ok(data)):
                            iu = 'https://covers.openlibrary.org/b/id/%s-L.jpg' % cid
                            req2 = urllib.request.Request(iu, headers={'User-Agent': 'Mozilla/5.0'})
                            with urllib.request.urlopen(req2, timeout=14) as r2:
                                data = r2.read()
                    except Exception as _e:
                        print('[封面抓取失败]', title[:20], _e)
                    if data and _img_ok(data):
                        cf.write_bytes(data)
                    else:
                        try:
                            missf.write_text('1')
                        except Exception:
                            pass
                        return self.send_error(404)
                self.send_response(200)
                self.send_header('Content-Type', 'image/jpeg')
                self.send_header('Cache-Control', 'public, max-age=604800')
                self.send_header('Content-Length', str(len(data)))
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(data)
            except Exception as e:
                print('[cover 出错]', e)
                self.send_error(404)
            return
        if p == '/api/websearch':
            try:
                from urllib.parse import parse_qs
                qs2 = parse_qs(urlparse(self.path).query)
                q2 = (qs2.get('q') or [''])[0]
                return self._json({'ok': True, 'q': q2, 'items': _web_search(q2, 6)})
            except Exception as e:
                return self._json({'ok': False, 'error': str(e)}, 500)
        # ===== 微信公众号接入（被动回复：用户发消息 → 努尔老师回答）=====
        if p == '/wechat' or p == '/wechat/':
            try:
                from urllib.parse import parse_qs
                import hashlib as _hl
                qs = parse_qs(urlparse(self.path).query)
                wxtok = ''
                try:
                    wxtok = (DIR / 'data' / 'wx_token.txt').read_text(encoding='utf-8').strip()
                except Exception:
                    wxtok = 'randeng2026'
                _sig = (qs.get('signature') or [''])[0]
                _ts = (qs.get('timestamp') or [''])[0]
                _nc = (qs.get('nonce') or [''])[0]
                _echo = (qs.get('echostr') or [''])[0]
                _chk = ''.join(sorted([wxtok, _ts, _nc]))
                if _hl.sha1(_chk.encode('utf-8')).hexdigest() == _sig and _echo:
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/plain')
                    self.end_headers()
                    self.wfile.write(_echo.encode('utf-8'))
                    return
                # 收到用户消息（明文 XML）
                _ln = int(self.headers.get('Content-Length', 0) or 0)
                _body = self.rfile.read(_ln).decode('utf-8', 'ignore') if _ln else ''
                _msg = ''
                import re as _re
                _m = _re.search(r'<Content><!\[CDATA\[(.*?)\]\]></Content>', _body, _re.S) or _re.search(r'<Content>(.*?)</Content>', _body, _re.S)
                _from = ''
                _m2 = _re.search(r'<FromUserName><!\[CDATA\[(.*?)\]\]></FromUserName>', _body, _re.S)
                if _m2:
                    _from = _m2.group(1)
                _to = ''
                _m3 = _re.search(r'<ToUserName><!\[CDATA\[(.*?)\]\]></ToUserName>', _body, _re.S)
                if _m3:
                    _to = _m3.group(1)
                if _m:
                    _msg = _m.group(1).strip()
                # 关注/取关等事件
                _is_sub = ('<Event><![CDATA[subscribe]]></Event>' in _body) or ('subscribe' in _body and '<Event>' in _body)
                if _is_sub:
                    _welcome = (  # (保留，卡片里用的是新文案)'欢迎来到【燃灯同学】🪔\n\n'
                                '这是一个阿拉伯语学习平台：\n'
                                '📚 23,835 部世界典籍 · 15,699 部中文古籍\n'
                                '📖 查词典（中文/阿语 · 含词根/近义词/反义词/例句）\n'
                                '🎧 听力训练 · 🗣 日常口语 · 📝 句子库\n'
                                '🤖 还有你的 AI 阿拉伯语老师「努尔」\n\n'
                                '👉 点这里进站：https://燃灯同学.com\n'
                                '（¥20 可用 30 天 ✓ 直接回复"开通"了解）\n\n'
                                '也可以现在就在这儿问我：\n'
                                '比如「教我一句阿拉伯语问候」✓')
                    _xml0 = _wx_news(_from, _to or 'gh_',
                        '🪔 欢迎来到燃灯同学 · 阿拉伯学习平台',
                        '23,835 部世界典籍 · 查词典 · 听力 · 口语 · AI 老师「努尔」\n'
                        '点上面这张卡片直接进站 ✓\n'
                        '———\n'
                        '想开通会员（¥99 用 3 个月）：\n'
                        '扫码付款后，就在这里私信我一声 ✓\n'
                        '博主看到会马上帮你确认开通 ^_^\n'
                        '———\n'
                        '也可以现在就问我，比如「教我一句阿拉伯语问候」🌙',
                        'https://xn--dqry4os3s3gb.com/')
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/xml; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(_xml0.encode('utf-8'))
                    return
                # 关键词"开通/价格/买" → 直接回价格与方式
                if any(k in (_msg or '') for k in ('开通', '价格', '多少钱', '怎么买', '购买', '付费', '解锁')):
                    _pay = ('【燃灯同学 · 开通说明】\n\n'
                            '💰 ¥20 = 30 天（全部内容 + AI 无限）\n\n'
                            '开通方式：\n'
                            '1. 进网站 https://燃灯同学.com 点「付费进入」\n'
                            '2. 或直接联系站长（回复"联系站长"）\n\n'
                            '开通后你的设备 30 天内免解锁码进入 ✓')
                    _xml1 = _wx_news(_from, _to or 'gh_',
                        '📖 燃灯同学 · 开通说明（¥99 / 3 个月）',
                        '付款方式见图（或回复「联系站长」）✓\n'
                        '付完后请在这里私信我一声（发个截图/说一句"付好了"）\n'
                        '博主看到会马上确认开通 ^_^\n'
                        '开通后 3 个月免解锁码 · 全部内容 + AI 无限 ✓',
                        'https://xn--dqry4os3s3gb.com/')
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/xml; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(_xml1.encode('utf-8'))
                    return
                if not _msg:
                    _msg = '你好'
                # === 公众号：每天免费聊 10 句，超过提醒开通 VIP ===
                try:
                    _used = _wx_day_count(_from, add=1)
                    if _used > 10:
                        _tip = ('今天已经陪你聊了 10 句啦\n'
                                '想继续深入学的话 可以开通会员\n'
                                '99 元 用 3 个月 全部内容加 AI 不限量\n'
                                '点下面这张卡片进站开通')
                        _xmlL = _wx_news(_from, _to or 'gh_',
                                         '📖 燃灯同学 · 开通会员（99 元 / 3 个月）',
                                         _tip + '\n\n开通后免解锁码 全部功能加 AI 无限 有问题随时私信我',
                                         'https://xn--dqry4os3s3gb.com/')
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/xml; charset=utf-8')
                        self.end_headers()
                        self.wfile.write(_xmlL.encode('utf-8'))
                        return
                except Exception as _le:
                    print('[公众号限额检查失败]', _le)
                # 微信限 5 秒 → AI 线程最多等 4.2 秒，拿到就回；没拿到回一句提示
                _ans = ''
                try:
                    import threading as _th
                    _st = {'a': ''}
                    def _call_ai(_m=_msg):
                        try:
                            _st['a'] = _ai_sanitize((_ai_json(_AI_GUARD + '你是"努尔老师"，一个温和的阿拉伯语老师。要求：1) 标点要少用，只用必要的，句子短一点，像口语说话；2) 不要加网址或宣传语；3) 用中文，必要时附阿拉伯语。用户说：' + _m, 600) or '').strip())
                        except Exception as _ae:
                            print('[公众号 AI 失败]', _ae)
                    _t = _th.Thread(target=_call_ai)
                    _t.daemon = True
                    _t.start()
                    _t.join(4.2)
                    _ans = _st['a']
                except Exception as _te:
                    print('[公众号线程失败]', _te)
                if not _ans:
                    _ans = '稍等一下，努尔老师有点忙，再发一次试试 🌙'
                else:
                    _ans = _ans
                _xml = ('<xml><ToUserName><![CDATA[' + _from + ']]></ToUserName>'
                        '<FromUserName><![CDATA[' + (_to or 'gh_') + ']]></FromUserName>'
                        '<CreateTime>' + str(int(time.time())) + '</CreateTime>'
                        '<MsgType><![CDATA[text]]></MsgType><Content><![CDATA[' + _ans.replace(']]>', ']]') + ']]></Content></xml>')
                self.send_response(200)
                self.send_header('Content-Type', 'application/xml; charset=utf-8')
                self.end_headers()
                self.wfile.write(_xml.encode('utf-8'))
            except Exception as e:
                print('[wechat 出错]', e)
                self.send_error(200)
            return
        if p == '/api/ai/quota':
            try:
                from urllib.parse import parse_qs
                qs = parse_qs(urlparse(self.path).query)
                _dev3 = (qs.get('device_id') or [''])[0].strip() or 'anon'
                _tk3 = (qs.get('token') or [''])[0].strip()
                _vip3 = False
                try:
                    _u3 = _check_token(_tk3) if _tk3 else None
                    if _u3:
                        _r3 = (_load_users().get(_u3) or {})
                        _un3 = str(_r3.get('sub_until') or _r3.get('vip_until') or '')
                        if _un3 and _un3 >= time.strftime('%Y-%m-%d'):
                            _vip3 = True
                except Exception:
                    pass
                try:
                    _ul3 = (_ai_cfg().get('unlimited_devices') or [])
                    if _dev3 and (_dev3 in _ul3):
                        _vip3 = True
                except Exception:
                    pass
                return self._json({'ok': True, 'vip': _vip3, 'cap': 10,
                                   'left': (999 if _vip3 else _free_daily_left(_dev3, 10))})
            except Exception as e:
                return self._json({'ok': False, 'error': str(e)}, 500)
        if p == '/api/dict/cn':
            try:
                from urllib.parse import parse_qs
                qs = parse_qs(urlparse(self.path).query)
                w = (qs.get('w') or [''])[0].strip()
                if not w:
                    return self._json({'ok': False, 'msg': '缺参数'})
                prompt = ('请解释中文词语「' + w + '」。严格按 JSON 输出（不要代码块、不要多余文字）：\n'
                          '{"word":"词","pinyin":"拼音","pos":"词性","meaning":"简明释义(60字内)",'
                          '"detail":"详细解释(120-200字，含用法/感情色彩/常见搭配)",'
                          '"syn":["近义词1","近义词2","近义词3"],"ant":["反义词1","反义词2"],'
                          '"sent":["例句1（含该词）","例句2"],"note":"易错点或辨析（可选）"}')
                txt = _ai_json(prompt, 900) or ''
                txt = txt.strip()
                if txt.startswith('```'):
                    txt = txt.strip('`')
                    txt = txt.split('\n', 1)[-1] if '\n' in txt else txt
                a, b = txt.find('{'), txt.rfind('}')
                if a >= 0 and b > a:
                    return self._json({'ok': True, 'w': w, 'data': json.loads(txt[a:b + 1])})
                return self._json({'ok': True, 'w': w, 'data': {'meaning': txt[:200]}})
            except Exception as e:
                return self._json({'ok': False, 'error': str(e)}, 500)
        if p == '/api/dict/suggest':
            try:
                from urllib.parse import parse_qs
                qs = parse_qs(urlparse(self.path).query)
                w = (qs.get('q') or qs.get('w') or [''])[0].strip()
                limit = (qs.get('limit') or ['8'])[0]
                return self._json(_dict_suggest(w, limit))
            except Exception as e:
                return self._json({'ok': False, 'error': str(e)}, 500)
        if p == '/api/dict/lesson':
            try:
                from urllib.parse import parse_qs
                qs = parse_qs(urlparse(self.path).query)
                w = (qs.get('w') or qs.get('q') or [''])[0].strip()
                limit = (qs.get('limit') or ['6'])[0]
                return self._json(_dictionary_lesson_links(w, limit))
            except Exception as e:
                return self._json({'ok': False, 'error': str(e)}, 500)
        if p == '/api/dict/lookup':
            try:
                from urllib.parse import parse_qs
                qs = parse_qs(urlparse(self.path).query)
                w = (qs.get('w') or [''])[0].strip()
                if not w:
                    return self._json({'ok': False, 'msg': '缺参数'})
                return self._json(_local_dict_lookup(w))
            except Exception as e:
                return self._json({'ok': False, 'error': str(e)}, 500)
        if p == '/api/dict/free':
            try:
                from urllib.parse import parse_qs
                qs = parse_qs(urlparse(self.path).query)
                w = (qs.get('w') or [''])[0].strip()
                if not w:
                    return self._json({'ok': False, 'msg': '缺参数'})
                return self._json({'ok': True, 'w': w, 'wiki': _wiktionary(w)})
            except Exception as e:
                return self._json({'ok': False, 'error': str(e)}, 500)
        if p == '/api/audio/library':
            try:
                from urllib.parse import parse_qs
                qs = parse_qs(urlparse(self.path).query)
                q = (qs.get('q') or [''])[0]
                fmt = (qs.get('format') or [''])[0]
                limit = (qs.get('limit') or ['240'])[0]
                items = _audio_library(q, fmt, limit)
                return self._json({'ok': True, 'items': items, 'total': len(items),
                                   'supported_formats': sorted(x.lstrip('.') for x in AUDIO_EXTENSIONS),
                                   'roots': [{'id': 'athan', 'title': '宣礼与礼拜'},
                                             {'id': 'music', 'title': 'AI 生成与语音'}],
                                   'in_app': True})
            except Exception as e:
                return self._json({'ok': False, 'error': str(e)}, 500)
        if p == '/api/audio/file':
            try:
                from urllib.parse import parse_qs
                qs = parse_qs(urlparse(self.path).query)
                fp = _audio_resolve((qs.get('root') or [''])[0], (qs.get('name') or [''])[0])
                return self._serve_local_audio(fp)
            except FileNotFoundError:
                return self._json({'ok': False, 'error': 'audio file not found'}, 404)
            except ValueError as e:
                return self._json({'ok': False, 'error': str(e)}, 400)
            except Exception as e:
                return self._json({'ok': False, 'error': str(e)}, 500)
        if p == '/api/audio':
            # 有声书：按书名到 Archive.org 的 LibriVox 合集找真人朗读
            try:
                from urllib.parse import parse_qs, quote
                qs = parse_qs(urlparse(self.path).query)
                q = (qs.get('q') or [''])[0].strip()
                if not q:
                    return self._json({'error': 'no q'}, 400)
                s1 = 'https://archive.org/advancedsearch.php?q=' + quote('collection:librivoxaudio AND title:("' + q + '")') + \
                     '&fl%5B%5D=identifier&fl%5B%5D=title&rows=5&output=json'
                req = urllib.request.Request(s1, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=60) as r:
                    docs = json.loads(r.read().decode('utf-8'))['response']['docs']
                if not docs:
                    return self._json({'found': False})
                best = docs[0]
                bid = best['identifier']
                mreq = urllib.request.Request('https://archive.org/metadata/' + quote(bid), headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(mreq, timeout=60) as r:
                    md = json.loads(r.read().decode('utf-8'))
                files = [f for f in md.get('files', []) if str(f.get('name', '')).lower().endswith('.mp3')]
                if not files:
                    return self._json({'found': False})
                files.sort(key=lambda f: str(f.get('name')))
                items = [{'n': str(f.get('name')), 'u': 'https://archive.org/download/' + quote(bid) + '/' + quote(str(f.get('name')))} for f in files]
                return self._json({'found': True, 'id': bid, 'title': (best.get('title') or '')[:120], 'files': items})
            except Exception as e:
                return self._json({'error': 'audio fail: ' + str(e)}, 500)
        if p == '/api/cover':
            # 按书名找真实封面（Open Library，带本地缓存）
            try:
                from urllib.parse import parse_qs, quote
                qs = parse_qs(urlparse(self.path).query)
                t = (qs.get('t') or [''])[0].strip()
                if not t:
                    return self._json({'url': ''})
                cf = DIR / 'data' / 'covers.json'
                try:
                    cache = json.loads(cf.read_text(encoding='utf-8'))
                except Exception:
                    cache = {}
                if t in cache:
                    return self._json({'url': cache[t]})
                url = ''
                try:
                    s1 = 'https://openlibrary.org/search.json?limit=1&fields=cover_i,title&title=' + quote(t)
                    req = urllib.request.Request(s1, headers={'User-Agent': 'nur/1.0'})
                    with urllib.request.urlopen(req, timeout=20) as r:
                        d = json.loads(r.read().decode('utf-8'))
                    docs = d.get('docs') or []
                    if docs and docs[0].get('cover_i'):
                        url = 'https://covers.openlibrary.org/b/id/' + str(docs[0]['cover_i']) + '-M.jpg'
                except Exception:
                    url = ''
                cache[t] = url
                try:
                    if len(cache) % 20 == 0:
                        cf.write_text(json.dumps(cache, ensure_ascii=False), encoding='utf-8')
                except Exception:
                    pass
                return self._json({'url': url})
            except Exception as e:
                return self._json({'url': '', 'error': str(e)})
        if p == '/api/coverimg':
            # 直接把封面图回给 <img>（没有则 404，前端回退到渐变封面）
            try:
                from urllib.parse import parse_qs, quote
                qs = parse_qs(urlparse(self.path).query)
                t = (qs.get('t') or [''])[0].strip()
                cf = DIR / 'data' / 'covers.json'
                try:
                    cache = json.loads(cf.read_text(encoding='utf-8'))
                except Exception:
                    cache = {}
                url = cache.get(t, '')
                if t not in cache:
                    url = ''
                    try:
                        s1 = 'https://openlibrary.org/search.json?limit=1&fields=cover_i&title=' + quote(t)
                        req = urllib.request.Request(s1, headers={'User-Agent': 'nur/1.0'})
                        with urllib.request.urlopen(req, timeout=20) as r:
                            d = json.loads(r.read().decode('utf-8'))
                        docs = d.get('docs') or []
                        if docs and docs[0].get('cover_i'):
                            url = 'https://covers.openlibrary.org/b/id/' + str(docs[0]['cover_i']) + '-L.jpg'
                    except Exception:
                        url = ''
                    # 兜底：Archive.org 搜同名书 → 用它的扫描封面
                    if not url:
                        try:
                            s2 = 'https://archive.org/advancedsearch.php?q=' + quote('mediatype:texts AND title:("' + t + '")') + \
                                 '&fl%5B%5D=identifier&rows=1&output=json'
                            rq = urllib.request.Request(s2, headers={'User-Agent': 'nur/1.0'})
                            with urllib.request.urlopen(rq, timeout=25) as r:
                                dd = json.loads(r.read().decode('utf-8'))['response']['docs']
                            if dd:
                                url = 'https://archive.org/services/img/' + dd[0]['identifier']
                        except Exception:
                            url = ''
                    cache[t] = url
                    try:
                        cf.write_text(json.dumps(cache, ensure_ascii=False), encoding='utf-8')
                    except Exception:
                        pass
                if not url:
                    self.send_response(404); self.send_header('Content-Length', '0'); self.end_headers(); return
                req2 = urllib.request.Request(url, headers={'User-Agent': 'nur/1.0'})
                with urllib.request.urlopen(req2, timeout=40) as r2:
                    data = r2.read()
                self.send_response(200)
                self.send_header('Content-Type', 'image/jpeg')
                self.send_header('Content-Length', str(len(data)))
                self.send_header('Cache-Control', 'public, max-age=604800')
                self.end_headers()
                self.wfile.write(data)
            except Exception:
                try:
                    self.send_response(404); self.send_header('Content-Length', '0'); self.end_headers()
                except Exception:
                    pass
                return
        if p == '/api/islamic/search':
            try:
                from urllib.parse import parse_qs
                qs = parse_qs(urlparse(self.path).query)
                source = (qs.get('source') or ['all'])[0]
                query = (qs.get('q') or [''])[0]
                page = int((qs.get('page') or ['1'])[0] or 1)
                size = int((qs.get('size') or ['24'])[0] or 24)
                if source == 'all':
                    return self._json({'items': [], 'page': 1, 'total': 0, 'sources': [
                        {'id': 'maktabah', 'title': 'Maktabah Salafiyyah', 'url': 'https://maktabahsalafiyyah.org/category/books/'},
                        {'id': 'shamela', 'title': 'Shamela', 'url': 'https://shamela.ws/'},
                        {'id': 'sunnah', 'title': 'Sunnah.com 六大部', 'url': 'https://sunnah.com/'},
                        {'id': 'quran', 'title': 'Quran.com / AlQuran.Cloud', 'url': 'https://quran.com/'},
                        {'id': 'archive', 'title': 'Internet Archive / Open Library', 'url': 'https://archive.org/advancedsearch.php'}
                    ]})
                return self._json(_isl_search(source, query, page, size))
            except HTTPError as e:
                return self._json({'items': [], 'error': '来源暂时限流或不可访问，请稍后重试。', 'status': getattr(e, 'code', 502)}, 502)
            except Exception as e:
                print('[Islamic source search]', e)
                return self._json({'items': [], 'error': '来源目录暂时无法读取。'}, 502)
        if p == '/api/quran/tafsir':
            # 经注按章按需加载；原文、译文、经注和诵读音频始终分层返回。
            try:
                from urllib.parse import parse_qs
                qs = parse_qs(urlparse(self.path).query)
                sid = (qs.get('surah') or qs.get('s') or ['1'])[0]
                edition = (qs.get('edition') or ['ar.muyassar'])[0]
                return self._json({'ok': True, **_quran_tafsir(sid, edition),
                                   'notice': '经注为独立学习资料，不是古兰经原文；请以页面来源和版本标注为准。'})
            except ValueError as e:
                return self._json({'ok': False, 'error': str(e)}, 400)
            except Exception as e:
                print('[Tafsir Error]', e)
                return self._json({'ok': False, 'error': '经注暂时无法加载，请稍后重试。'}, 502)
        if p == '/api/books':
            # 兼容旧版“精选书籍”弹层；世界图书馆使用 /api/catalog，二者数据保持分层。
            try:
                bf = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'books.json')
                with open(bf, 'r', encoding='utf-8') as f:
                    books = json.load(f)
                return self._json({'total': len(books), 'books': books})
            except Exception as e:
                print('[Books Error]', e)
                return self._json({'total': 0, 'books': [], 'error': '精选书籍暂时无法加载。'}, 500)
        if p == '/api/catalog/meta':
            try:
                bf = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'books.json')
                with open(bf, 'r', encoding='utf-8') as f:
                    books = json.load(f)
                self._json({'total': len(books), 'books': books})
            except Exception as e:
                self._json({'error': str(e)}, 500)
            return
        if p == '/api/articles':
            try:
                af = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'articles.json')
                with open(af, 'r', encoding='utf-8') as f:
                    arts = json.load(f)
                arr = [{'key': k, 'title': v.get('title', ''), 'body': v.get('body', ''), 'cn': v.get('cn', '')} for k, v in arts.items()]
                self._json({'total': len(arr), 'articles': arr})
            except Exception as e:
                self._json({'error': str(e)}, 500)
            return
        if p == '/api/vocab':
            try:
                df = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'data.json')
                with open(df, 'r', encoding='utf-8') as f:
                    items = json.load(f)
                words = {}
                for it in items:
                    for w in re.findall(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]+', it.get('ar', '')):
                        w = w.strip('\u064b\u064c\u064d\u064e\u064f\u0650\u0651\u0652\u0640')
                        if len(w) >= 2:
                            words[w] = words.get(w, 0) + 1
                vocab = sorted([{'w': w, 'f': n} for w, n in words.items()], key=lambda x: -x['f'])
                self._json({'total': len(vocab), 'words': vocab})
            except Exception as e:
                self._json({'error': str(e)}, 500)
            return
        if p == '/api/sentences/daily':
            try:
                return self._json(_sentence_daily_payload())
            except Exception as e:
                print('[Daily Sentence Error]', e)
                return self._json({'ok': False, 'error': '今日句子暂时无法加载。'}, 500)
        if p == '/api/sentences':
            try:
                cf = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'categorized.json')
                with open(cf, 'r', encoding='utf-8') as f:
                    arr = json.load(f)
                cats = {}
                for it in arr:
                    k = it.get('cat', 'other')
                    if k not in cats:
                        cats[k] = []
                    cats[k].append({'a': it.get('ar', ''), 'e': it.get('en', ''), 'c': it.get('cn', '')})
                meta = {
                    'greeting': {'icon': '👋', 'cn': '问候', 'ar': 'مرحبا'}, 'daily': {'icon': '🌅', 'cn': '日常', 'ar': 'يومي'},
                    'food': {'icon': '🍽', 'cn': '饮食', 'ar': 'طعام'}, 'travel': {'icon': '✈️', 'cn': '旅行', 'ar': 'سفر'},
                    'family': {'icon': '👨‍👩‍👧', 'cn': '家庭', 'ar': 'عائلة'}, 'work': {'icon': '💼', 'cn': '工作', 'ar': 'عمل'},
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
                payload = {
                    'cats': cats,
                    'meta': meta,
                    'stats': {'sentences': len(arr), 'words': sum(len(i.get('ar', '').split()) for i in arr), 'cats': len(cats)},
                }
                self._json(payload)
            except Exception as e:
                self._json({'error': str(e)}, 500)
            return
        if p == "/":
            p = "/arabic_learning.html"
        # SPA 兜底：任何未命中的普通路径（如 /a、/x）都返回 App 本体（便于拿到最新版，绕过缓存）
        try:
            import pathlib as _pl
            _fp = (_pl.Path(DIR) / p.lstrip('/'))
            if (not _fp.exists()) and (not p.startswith('/api/')) and ('.' not in p.split('/')[-1]):
                return self._serve('/arabic_learning.html')
        except Exception:
            pass
        self._serve(p)
    
    def do_POST(self):
        # 微信公众号消息是 POST → 复用 do_GET 里的 /wechat 处理
        if urlparse(self.path).path in ('/wechat', '/wechat/'):
            return self.do_GET()
        p = urlparse(self.path).path
        _ip = self.client_address[0] if self.client_address else ''
        _wait = _rate_limited(_ip, p)
        if _wait:
            return self._json({'ok': False, 'error': '请求过于频繁，请 %d 秒后再试。' % _wait}, 429)
        if p == '/api/page/analyze':
            # 只接收当前阅读器页文本；不把整本书上传给模型，也不把密钥交给浏览器。
            try:
                _page_claimed = False
                length = int(self.headers.get('Content-Length', 0) or 0)
                if length <= 0 or length > 18000:
                    return self._json({'ok': False, 'error': '页面内容太长或为空，请缩小到当前页后重试。'}, 400)
                data = json.loads(self.rfile.read(length))
                data['book_title'] = str(data.get('book_title') or '经典阅读')[:240]
                data['book_kind'] = str(data.get('book_kind') or 'book')[:30]
                raw_meta = data.get('book_meta') if isinstance(data.get('book_meta'), dict) else {}
                allowed_meta = ('id','t','a','y','c','c_ar','discipline','u','source','access','rights','level','intro','ai_profile','ai_guide_version','guide_summary','guide_background','guide_objectives','guide_terms','guide_focus','guide_boundary','source_evidence','fiqh_school_labels','fiqh_school_evidence','fiqh_school_inference')
                data['book_meta'] = {}
                for _mk in allowed_meta:
                    _mv = raw_meta.get(_mk)
                    if not _mv:
                        continue
                    if isinstance(_mv, list):
                        data['book_meta'][_mk] = _mv[:8]
                    elif isinstance(_mv, dict):
                        data['book_meta'][_mk] = {str(_k)[:80]: (list(_v)[:8] if isinstance(_v, list) else str(_v)[:500]) for _k, _v in list(_mv.items())[:8]}
                    else:
                        data['book_meta'][_mk] = str(_mv)[:900]
                data['fiqh_school'] = _fiqh_school(data)
                data['response_language'] = _analysis_language(data)
                data['page_number'] = max(1, min(int(data.get('page_number') or 1), 999999))
                data['page_total'] = max(1, min(int(data.get('page_total') or 1), 999999))
                data['text'] = str(data.get('text') or '').strip()[:9000]
                if len(data['text']) < 6:
                    return self._json({'ok': False, 'error': '当前页没有足够正文可供分析。'}, 400)
                key = _page_analysis_key(data)
                cached = _page_analysis_cache_get(key)
                if cached:
                    return self._json({'ok': True, 'cached': True, 'analysis': cached})
                if not _page_analysis_claim(key):
                    return self._json({'ok': False, 'pending': True,
                                       'retryable': True,
                                       'error': '同一页正在生成讲解，请稍候片刻。'}, 409)
                _page_claimed = True

                # 与普通聊天一致：先按设备记免费次数，再检查登录用户余额/会员状态。
                _dev = (data.get('device_id') or '').strip()
                _fwd2 = (self.headers.get('X-Forwarded-For') or '').split(',')[0].strip()
                _dev = _dev or _fwd2 or self.client_address[0]
                _is_vip = False
                au = None
                try:
                    _tk = (data.get('token') or self.headers.get('X-Token') or '').strip()
                    _u2 = _check_token(_tk) if _tk else None
                    if _u2:
                        _rec = (_load_users().get(_u2) or {})
                        _unt = str(_rec.get('sub_until') or _rec.get('vip_until') or '')
                        if _unt and _unt >= time.strftime('%Y-%m-%d'):
                            _is_vip = True
                except Exception:
                    pass
                try:
                    _ul = (_ai_cfg().get('unlimited_devices') or [])
                    if _dev and _dev in _ul:
                        _is_vip = True
                    if _fwd2 and _fwd2 in _ul:
                        _is_vip = True
                except Exception:
                    pass
                _leftq = None
                if not _is_vip:
                    _okq, _leftq = _free_daily_use(_dev, 10)
                    if not _okq:
                        _page_analysis_release(key); _page_claimed = False
                        return self._json({'ok': False, 'error': '今天的 AI 讲解次数已用完，请明天再试。', 'limited': True, 'left': 0}, 429)

                _fwd = (self.headers.get('X-Forwarded-For') or '').split(',')[0].strip()
                _cip = _fwd or self.client_address[0]
                if _cip not in ('127.0.0.1', '::1'):
                    token = data.get('token') or self.headers.get('X-Token') or ''
                    device = (data.get('device_id') or '').strip()
                    au = _check_token(token) if token else None
                    if not au and device:
                        users = _load_users()
                        if 'dev:' + device in users:
                            au = 'dev:' + device
                    if not au:
                        users = _load_users()
                        users.setdefault('dev:' + (device or 'anon'), {'pwd': '', 'vip': False, 'vip_until': '',
                                                                         'created': time.strftime('%Y-%m-%d'), 'token': '', 'ai_quota': {}})
                        _save_users(users)
                        au = 'dev:' + (device or 'anon')
                    _vip, _until = _vip_info(au)
                    _ensure_entry_quota(au)
                    _bal = _user_bal(au)
                    if _bal['paid_left'] <= 0 and _bal['free_left'] <= 0:
                        _ok2, _u2, _ = _sub_status(au)
                        if not _ok2:
                            _page_analysis_release(key); _page_claimed = False
                            return self._json({'ok': False, 'error': '当前设备需要先开通 AI 额度，或明天使用免费次数。', 'need_activate': True}, 402)
                    try:
                        _cap = float(_load_pricing().get('pay', {}).get('global_month_cap', 80) or 80)
                    except Exception:
                        _cap = 80.0
                    if _cap > 0 and _global_spend() >= _cap:
                        _page_analysis_release(key); _page_claimed = False
                        return self._json({'ok': False, 'error': '本月 AI 预算已用完，请稍后再试。'}, 503)

                _page_budget = _page_analysis_token_budget(data)
                raw = _page_analysis_ai(_page_analysis_prompt(data), max_tokens=_page_budget, data=data)
                parsed = _page_analysis_json(raw)
                if parsed and not _page_analysis_has_content(parsed):
                    parsed = None
                if not parsed:
                    compact_prompt = (
                        '把下面 AI 草稿整理成一个严格有效、紧凑的 JSON 对象。只输出 JSON，不要 markdown，不要解释。'
                        '所有字段都必须存在；数组最多 4 项，school_comparison 最多 4 项；terms 使用字符串数组；如果没有可靠依据就用空数组或“待核验”。'
                        '输出语言必须是“' + PAGE_ANALYSIS_LANGUAGES[_analysis_language(data)]['label'] + '”。\n'
                        '{"overview":"","key_points":[],"text_structure":[],"questions":[],"practical_guidance":[],"quran_references":[],"hadith_references":[],"fiqh_context":[],"school_comparison":[],"language_notes":[],"terms":[],"source_note":"","caution":""}\n'
                        '当前页原文：\n' + str(data.get('text') or '')[:6500]
                    )
                    repaired = _page_analysis_ai(compact_prompt, max_tokens=700, data=data)
                    parsed = _page_analysis_json(repaired)
                    if parsed and not _page_analysis_has_content(parsed):
                        parsed = None
                if not parsed:
                    # 不把空结果伪装成成功，也不写入缓存或扣除额度；用户可直接重试。
                    _page_analysis_release(key); _page_claimed = False
                    return self._json({'ok': False, 'retryable': True,
                                       'error': 'AI 没有返回完整的结构化讲解；原文阅读不受影响，请点击“再试一次”。'}, 503)
                analysis = _normalize_page_analysis(parsed, data)
                _page_analysis_cache_put(key, analysis)
                if au:
                    try:
                        _charge_ai(au, dict(LAST_USAGE))
                    except Exception as _charge_err:
                        print('[Page analysis charge]', _charge_err)
                _page_analysis_release(key); _page_claimed = False
                _ai_meta = dict(LAST_AI_METRICS) if LAST_AI_METRICS else {}
                return self._json({'ok': True, 'cached': False, 'analysis': analysis, 'ai_meta': _ai_meta, 'left': _leftq})
            except Exception as e:
                if locals().get('_page_claimed'):
                    _page_analysis_release(locals().get('key', ''))
                print('[Page analysis error]', e)
                return self._json({'ok': False, 'error': '本页讲解暂时无法生成，请稍后重试。'}, 500)
        if p == '/api/realtime/session':
            # 浏览器 WebRTC 只上传 SDP；服务端用标准 OpenAI key 完成统一接口握手。
            # 标准 key 永远不返回浏览器，也不接受浏览器传入的 model/instructions。
            try:
                length = int(self.headers.get('Content-Length', 0))
                if length <= 0 or length > 250000:
                    return self._json({'error': 'invalid SDP body'}, 400)
                sdp = self.rfile.read(length).decode('utf-8', errors='replace')
                if 'v=0' not in sdp or 'a=' not in sdp:
                    return self._json({'error': 'invalid SDP'}, 400)
                key = _get_realtime_key()
                if not key:
                    return self._json({'error': 'Realtime API key is not configured',
                                       'code': 'realtime_key_missing'}, 503)
                device = (self.headers.get('X-Device-ID') or self.client_address[0] or 'anon').strip()
                safety_id = hashlib.sha256(device.encode('utf-8')).hexdigest()[:64]
                session = json.dumps({
                    'type': 'realtime',
                    'model': os.environ.get('OPENAI_REALTIME_MODEL', 'gpt-realtime-2.1'),
                    'instructions': ('你是燃灯同学的努尔老师。用自然、简洁、温和的中文或阿拉伯语交流。'
                                     '优先帮助用户学习阿拉伯语；用户使用哪种语言就自然回应哪种语言。'
                                     '不要长篇大论，允许用户随时打断。'),
                    'audio': {
                        'input': {'turn_detection': {
                            'type': 'server_vad', 'threshold': 0.5,
                            'prefix_padding_ms': 300, 'silence_duration_ms': 420,
                            'create_response': True, 'interrupt_response': True}},
                        'output': {'voice': os.environ.get('OPENAI_REALTIME_VOICE', 'marin')}
                    }
                }, ensure_ascii=False)
                boundary = '----NourRealtimeBoundary' + hashlib.sha256(str(time.time()).encode()).hexdigest()[:16]
                parts = []
                for name, value in (('sdp', sdp), ('session', session)):
                    parts.extend([
                        ('--' + boundary + '\r\n').encode(),
                        ('Content-Disposition: form-data; name="' + name + '"\r\n\r\n').encode(),
                        value.encode('utf-8'), b'\r\n'
                    ])
                parts.append(('--' + boundary + '--\r\n').encode())
                body = b''.join(parts)
                req = urllib.request.Request(
                    'https://api.openai.com/v1/realtime/calls', data=body, method='POST',
                    headers={'Authorization': 'Bearer ' + key,
                             'Content-Type': 'multipart/form-data; boundary=' + boundary,
                             'OpenAI-Safety-Identifier': safety_id})
                try:
                    with urllib.request.urlopen(req, timeout=45) as upstream:
                        answer = upstream.read()
                        status = upstream.status
                except HTTPError as e:
                    detail = e.read().decode('utf-8', errors='replace')[:800]
                    return self._json({'error': 'Realtime upstream rejected session',
                                       'status': e.code, 'detail': detail}, 502)
                if status >= 400:
                    return self._json({'error': 'Realtime upstream rejected session', 'status': status}, 502)
                self.send_response(200)
                self.send_header('Content-Type', 'application/sdp')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Cache-Control', 'no-store')
                self.send_header('Content-Length', str(len(answer)))
                self.end_headers()
                self.wfile.write(answer)
            except Exception as e:
                return self._json({'error': 'Realtime session failed', 'detail': str(e)[:300]}, 500)
            return
        if p == '/api/chat/stream_voice':
            # 语音专用低延迟 DeepSeek 流：不触发联网搜索，直接转发 SSE 增量文字。
            # 前端拿到第一句即可开始 TTS，不必等待整段回答完成。
            try:
                length = int(self.headers.get('Content-Length', 0))
                if length <= 0 or length > 12000:
                    return self._json({'error': 'invalid voice prompt'}, 400)
                data = json.loads(self.rfile.read(length))
                text = str(data.get('message') or '').strip()[:1200]
                if not text:
                    return self._json({'error': 'empty voice prompt'}, 400)
                key = _get_deepseek_key()
                if not key:
                    return self._json({'error': 'DeepSeek key is not configured'}, 503)
                prompt = (
                    '你是燃灯同学的努尔老师，正在进行阿拉伯语口语练习。'
                    '请回答得非常简短、自然、温和。第一行只写一到两句带音符的阿拉伯语，'
                    '第二行以“中文：”开头给出简短翻译。不要解释语法，不要网址，不要资料列表。'
                )
                body = json.dumps({
                    'model': AI_CFG.get('model', 'deepseek-chat'),
                    'messages': [
                        {'role': 'system', 'content': prompt},
                        {'role': 'user', 'content': text},
                    ],
                    'max_tokens': 220,
                    'stream': True,
                }, ensure_ascii=False).encode('utf-8')
                req = urllib.request.Request(
                    API_URL, data=body, method='POST',
                    headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + key,
                             'Accept': 'text/event-stream', 'Cache-Control': 'no-cache'})
                upstream = urllib.request.urlopen(req, timeout=45)
                self.send_response(200)
                self.send_header('Content-Type', 'text/event-stream; charset=utf-8')
                self.send_header('Cache-Control', 'no-cache, no-transform')
                self.send_header('Connection', 'close')
                self.close_connection = True
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                try:
                    for line in upstream:
                        if not line:
                            continue
                        self.wfile.write(line)
                        self.wfile.flush()
                        if b'data: [DONE]' in line:
                            break
                finally:
                    upstream.close()
            except urllib.error.HTTPError as e:
                detail = e.read().decode('utf-8', errors='replace')[:500]
                return self._json({'error': 'DeepSeek stream rejected', 'status': e.code, 'detail': detail}, 502)
            except (BrokenPipeError, ConnectionResetError):
                return
            except Exception as e:
                return self._json({'error': 'voice stream failed', 'detail': str(e)[:300]}, 500)
            return
        if (p.startswith('/api/admin/') or p == '/api/deploy_node') and p != '/api/admin/login' and not _is_admin(self):
            return self._json({'ok': False, 'msg': '需要管理员密码', 'need_admin': True}, 401)
        if p == '/api/admin/ai_provider':
            if self.command == 'GET':
                cfg = _ai_cfg()
                _dsk = ''
                try:
                    _dsk = (DIR / 'data' / 'ai_key.txt').read_text(encoding='utf-8').strip()
                except Exception:
                    pass
                return self._json({'ok': True, 'provider': cfg.get('provider') or 'auto',
                                   'has_deepseek': bool(_dsk),
                                   'ds_key': _dsk,
                                   'unlimited_devices': (cfg.get('unlimited_devices') or []),
                                   'keys': _ai_keys()})
            try:
                _ln = int(self.headers.get('Content-Length', 0))
                _d = json.loads(self.rfile.read(_ln)) if _ln else {}
            except Exception:
                _d = {}
            cfg = _ai_cfg()
            if _d.get('provider'):
                cfg['provider'] = str(_d['provider']).strip()
            if _d.get('ai_key'):
                try:
                    (DIR / 'data' / 'ai_key.txt').write_text(str(_d['ai_key']).strip(), encoding='utf-8')
                except Exception:
                    pass
            _ks = _ai_keys()
            for _k in ('gemini', 'groq', 'openrouter', 'google_books'):
                if _d.get(_k) is not None:
                    _ks[_k] = str(_d[_k]).strip()
            try:
                json.dump(_ks, open(DIR / 'data' / 'ai_keys.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
            except Exception:
                pass
            _ai_cfg_save(cfg)
            _dsk2 = ''
            try:
                _dsk2 = (DIR / 'data' / 'ai_key.txt').read_text(encoding='utf-8').strip()
            except Exception:
                pass
            return self._json({'ok': True, 'provider': cfg.get('provider') or 'auto',
                               'has_deepseek': bool(_dsk2), 'ds_key': _dsk2,
                               'unlimited_devices': (cfg.get('unlimited_devices') or []),
                               'keys': _ai_keys()})

        if p == '/api/asr':
            try:
                length = int(self.headers.get('Content-Length', 0))
                if length <= 0:
                    return self._json({'error': 'empty audio', 'text': ''}, 400)
                raw = self.rfile.read(length)
                lang = self.headers.get('X-ASR-Lang') or None
                ct = self.headers.get('Content-Type', '')
                if 'multipart/form-data' in ct:
                    # App 端 FormData 上传：解析 file 字段
                    import io
                    import cgi
                    env = {'REQUEST_METHOD': 'POST', 'CONTENT_TYPE': ct, 'CONTENT_LENGTH': str(length)}
                    form = cgi.FieldStorage(fp=io.BytesIO(raw), environ=env)
                    fi = form['file']
                    audio = fi.file.read()
                else:
                    audio = raw
                text, lang2 = transcribe_audio(audio, lang)
                self._json({'text': text, 'language': lang2})
            except Exception as e:
                print(f'[ASR Error] {e}')
                self._json({'error': str(e), 'text': ''}, 500)
            return
        if p == '/api/auth/register':
            try:
                length = int(self.headers.get('Content-Length', 0))
                data = json.loads(self.rfile.read(length))
                u = (data.get('username') or '').strip()
                pw = (data.get('password') or '').strip()
                if len(u) < 2 or len(pw) < 4:
                    return self._json({'ok': False, 'msg': '用户名至少 2 个字符，密码至少 4 位'})
                users = _load_users()
                if u in users:
                    return self._json({'ok': False, 'msg': '用户名已存在，请直接登录'})
                users[u] = {'pwd': _hash(pw), 'vip': False, 'vip_until': '', 'created': time.strftime('%Y-%m-%d'), 'token': _mk_token(u), 'ai_quota': {}}
                _save_users(users)
                return self._json({'ok': True, 'token': users[u]['token'], 'username': u, 'vip': False, 'msg': '注册成功'})
            except Exception as e:
                return self._json({'ok': False, 'msg': str(e)}, 500)
        if p == '/api/auth/login':
            try:
                length = int(self.headers.get('Content-Length', 0))
                data = json.loads(self.rfile.read(length))
                u = (data.get('username') or '').strip()
                pw = (data.get('password') or '').strip()
                users = _load_users()
                if u not in users or users[u].get('pwd') != _hash(pw):
                    return self._json({'ok': False, 'msg': '用户名或密码错误'})
                users[u]['token'] = _mk_token(u)
                _save_users(users)
                vip, until = _vip_info(u)
                return self._json({'ok': True, 'token': users[u]['token'], 'username': u, 'vip': vip, 'vip_until': until, 'msg': '登录成功'})
            except Exception as e:
                return self._json({'ok': False, 'msg': str(e)}, 500)
        if p == '/api/admin/ai':
            try:
                length = int(self.headers.get('Content-Length', 0))
                data = json.loads(self.rfile.read(length))
                ok = admin_panel.set_ai_config(new_system=data.get('system'), max_tokens=data.get('max_tokens'))
                return self._json({'ok': ok})
            except Exception as e:
                return self._json({'error': str(e)}, 500)
        if p == '/api/search':
            try:
                length = int(self.headers.get('Content-Length', 0))
                data = json.loads(self.rfile.read(length)) if length else {}
                q = (data.get('q') or '').strip()
                token = (data.get('token') or self.headers.get('X-Token') or '').strip()
                u = _check_token(token) if token else None
                vip, until = _vip_info(u) if u else (False, '')
                _has_ai = bool(u) and _user_quota(u)[0] > 0
                items = _search(q, 120)
                # 中文词：补一条"词典释义"结果（带缓存）
                try:
                    if re.match(r'^[\u4e00-\u9fff]{1,8}$', q) and len(items) < 5:
                        _cf = DIR / 'data' / 'dict_cn_cache.json'
                        try:
                            _cc = json.load(open(_cf, encoding='utf-8'))
                        except Exception:
                            _cc = {}
                        _ex = _cc.get(q)
                        if not _ex:
                            _prompt = ('请解释中文词语「' + q + '」。严格按 JSON 输出：'
                                       '{"meaning":"简明释义(50字内)","detail":"详细解释(80-150字)","syn":["近义1","近义2"],"ant":["反义1"]}')
                            _txt = _ai_json(_prompt, 500) or ''
                            _a, _b2 = _txt.find('{'), _txt.rfind('}')
                            if _a >= 0 and _b2 > _a:
                                _ex = json.loads(_txt[_a:_b2 + 1])
                                _cc[q] = _ex
                                try:
                                    json.dump(_cc, open(_cf, 'w', encoding='utf-8'), ensure_ascii=False)
                                except Exception:
                                    pass
                        if _ex:
                            items.insert(0, {'k': 'cnword', 'key': q, 'ar': '', 'zh': q,
                                             'cat': (_ex.get('meaning') or '')[:60],
                                             'detail': _ex.get('detail') or '',
                                             'syn': _ex.get('syn') or [], 'ant': _ex.get('ant') or []})
                except Exception as _ce:
                    print('[中文词搜索失败]', _ce)
                return self._json({'ok': True, 'locked': False, 'items': items, 'q': q, 'msg': ''})
            except Exception as e:
                return self._json({'ok': False, 'error': str(e)}, 500)
        if p == '/api/unlock/use':
            try:
                length = int(self.headers.get('Content-Length', 0))
                data = json.loads(self.rfile.read(length)) if length else {}
                code = (data.get('code') or '').strip().upper().replace('-', '')
                dev = (data.get('device_id') or '').strip()
                if not code or not dev:
                    return self._json({'ok': False, 'msg': '请输入解锁码'})
                un = _load_unlocks()
                rec = un['codes'].get(code)
                if not rec:
                    return self._json({'ok': False, 'msg': '解锁码不存在，请核对'})
                if rec.get('used'):
                    return self._json({'ok': False, 'msg': '该解锁码已被使用（只能用一次、只绑一台设备）'})
                if rec.get('device') and rec.get('device') != dev:
                    return self._json({'ok': False, 'msg': '该解锁码已绑定其他设备'})
                rec['used'] = True
                rec['device'] = dev
                rec['used_at'] = time.strftime('%Y-%m-%d %H:%M')
                _save_unlocks(un)
                u = 'dev:' + dev
                users = _load_users()
                users.setdefault(u, {})['sub_until'] = rec.get('until') or _sub_until()
                users[u]['vip'] = True
                users[u]['vip_until'] = users[u]['sub_until']
                users[u]['unlock_code'] = code
                if float(users[u].get('paid_total', 0) or 0) <= 0:
                    users[u]['paid_total'] = float(rec.get('quota') or 5)
                tok = _mk_token(u)
                users[u]['token'] = tok
                _save_users(users)
                print(f'[解锁码兑换] {dev} ← {code}（绑定本设备）')
                return self._json({'ok': True, 'token': tok, 'until': users[u]['sub_until'],
                                   'msg': '解锁成功！已绑定本设备（仅此一次）'})
            except Exception as e:
                return self._json({'ok': False, 'msg': str(e)}, 500)
        if p == '/api/access/leave':
            try:
                length = int(self.headers.get('Content-Length', 0))
                data = json.loads(self.rfile.read(length)) if length else {}
                dev = (data.get('device_id') or '').strip()
                u = 'dev:' + dev
                users = _load_users()
                if u in users:
                    users[u]['sub_until'] = ''
                    users[u]['vip'] = False
                    users[u]['vip_until'] = ''
                    users[u]['token'] = ''
                    _save_users(users)
                print(f'[退出=弃权] {u}')
                return self._json({'ok': True, 'msg': '已退出，本设备解锁资格已作废'})
            except Exception as e:
                return self._json({'ok': False, 'msg': str(e)}, 500)
        if p == '/api/entry/use':
            try:
                length = int(self.headers.get('Content-Length', 0))
                data = json.loads(self.rfile.read(length)) if length else {}
                code = (data.get('code') or '').strip().upper().replace('-', '')
                dev = (data.get('device_id') or '').strip()
                if not code or not dev:
                    return self._json({'ok': False, 'msg': '请输入开通凭证'})
                users = _load_users()
                src = None
                for k, v in users.items():
                    if (v.get('entry_code') or '').upper() == code:
                        src = v
                        break
                if not src:
                    return self._json({'ok': False, 'msg': '凭证不对，请核对'})
                u = 'dev:' + dev
                users.setdefault(u, {})['sub_until'] = src.get('sub_until') or _sub_until()
                users[u]['vip'] = True
                users[u]['vip_until'] = users[u]['sub_until']
                users[u]['entry_code'] = code
                if float(users[u].get('paid_total', 0) or 0) <= 0:
                    try:
                        users[u]['paid_total'] = float(_load_pricing().get('pay', {}).get('entry_quota', 5) or 5)
                    except Exception:
                        users[u]['paid_total'] = 5.0
                tok = _mk_token(u)
                users[u]['token'] = tok
                _save_users(users)
                print(f'[凭证进入] {u} 用 {code}')
                return self._json({'ok': True, 'token': tok, 'until': users[u]['sub_until'], 'msg': '凭证有效，已开通本设备'})
            except Exception as e:
                return self._json({'ok': False, 'msg': str(e)}, 500)
        if p == '/api/access/login':
            try:
                length = int(self.headers.get('Content-Length', 0))
                data = json.loads(self.rfile.read(length)) if length else {}
                dev = (data.get('device_id') or '').strip()
                u = 'dev:' + dev
                ok, until, left = _sub_status(u) if dev else (False, '', 0)
                if not ok:
                    return self._json({'ok': False, 'msg': '本月还没有开通，请付费后进入'})
                tok = _mk_token(u)
                users = _load_users()
                users.setdefault(u, {})['token'] = tok
                _save_users(users)
                print(f'[月费进入] {u} 到期 {until}')
                return self._json({'ok': True, 'token': tok, 'until': until, 'days_left': left, 'msg': '欢迎回来'})
            except Exception as e:
                return self._json({'ok': False, 'msg': str(e)}, 500)
        if p == '/api/device/login':
            try:
                length = int(self.headers.get('Content-Length', 0))
                data = json.loads(self.rfile.read(length)) if length else {}
                dev = (data.get('device_id') or '').strip()
                u = 'dev:' + dev
                users = _load_users()
                if dev and u in users and users[u].get('vip'):
                    vip, until = _vip_info(u)
                    if not vip:
                        return self._json({'ok': False, 'msg': '本设备的开通已到期'})
                    tok = _mk_token(u)
                    users[u]['token'] = tok
                    _save_users(users)
                    print(f'[设备恢复登录] {u}')
                    return self._json({'ok': True, 'token': tok, 'username': u, 'until': until, 'msg': '已恢复登录'})
                return self._json({'ok': False, 'msg': '本设备没有开通记录，请输入激活码'})
            except Exception as e:
                return self._json({'ok': False, 'msg': str(e)}, 500)
        if p == '/api/pay/claim':
            try:
                length = int(self.headers.get('Content-Length', 0))
                data = json.loads(self.rfile.read(length)) if length else {}
                token = (data.get('token') or '').strip()
                u = _check_token(token) if token else None
                device = (data.get('device_id') or '').strip()
                key = u or ('dev:' + device if device else '')
                if not key:
                    return self._json({'ok': False, 'msg': '无法识别设备，请刷新后重试'})
                kind = (data.get('kind') or 'sub').strip()
                _p = _load_pricing().get('pay', {}) or {}
                _def_amt = float(_p.get('sub_min', 10) or 10)
                amt = float(data.get('amount') or _def_amt)
                # 如实记录用户填写的金额，是否放行由管理员核对后决定
                if kind == 'sub' and amt < float(_p.get('sub_min', 10) or 10):
                    print(f'[付款低于最低] {device} 填了 ¥{amt:g}（最低 ¥{_p.get("sub_min", 10)}）')
                note = (data.get('note') or '').strip()[:200]
                d = _load_pays()
                # 同一设备若有待处理记录，更新而不是重复添加
                for it in d['items']:
                    if it.get('user') == key and it.get('status') == 'pending':
                        it.update({'amount': amt, 'quota': round(amt * _pay_ratio(), 2), 'note': note, 'ts': time.strftime('%Y-%m-%d %H:%M')})
                        _save_pays(d)
                        print(f'[付款待确认] {key} 更新 {amt} 元')
                        return self._json({'ok': True, 'msg': '已提交，管理员确认后自动到账'})
                _q = round(amt * _pay_ratio(), 2)
                _auto = bool(_load_pricing().get('pay', {}).get('auto_approve', True))
                if _auto:
                    rid = str(int(time.time() * 1000))
                    if kind == 'activate':
                        _made = gen_code(3650, 1, '自助开通 ' + (device or key), 'activate')
                        d['items'].append({'kind': kind, 'id': rid, 'user': key, 'device': device or (key[4:] if key.startswith('dev:') else key),
                                           'amount': amt, 'quota': 0, 'note': note, 'code': _made[0],
                                           'ts': time.strftime('%Y-%m-%d %H:%M'), 'status': 'auto'})
                        _save_pays(d)
                        print(f'[自助开通·自动发码] {key} → {_made[0]}')
                        return self._json({'ok': True, 'code': _made[0], 'auto': True,
                                           'msg': '开通成功！激活码已自动生成'})
                    if kind == 'sub':
                        _until = _sub_until()
                        try:
                            _eq = float(_load_pricing().get('pay', {}).get('entry_quota', 5) or 5)
                        except Exception:
                            _eq = 5.0
                        _ec = ''.join(random.choices('ABCDEFGHJKLMNPQRSTUVWXYZ23456789', k=6))
                        un = _load_unlocks()
                        un['codes'][_ec] = {'used': False, 'device': '', 'ts': time.strftime('%Y-%m-%d %H:%M'),
                                            'until': _until, 'amount': amt, 'quota': _eq}
                        _save_unlocks(un)
                        _save_pays(d)
                        print(f'[付款·发解锁码] {key} ¥{amt:g} → {_ec}')
                        return self._json({'ok': True, 'auto': True, 'unlock_code': _ec, 'until': _until, 'quota': _eq,
                                           'msg': f'付款成功！解锁码：{_ec}（只能用一次，绑定一台设备）'})
                    if kind == 'sub_legacy':
                        _until = _sub_until()
                        try:
                            _eq = float(_load_pricing().get('pay', {}).get('entry_quota', 5) or 5)
                        except Exception:
                            _eq = 5.0
                        _ec = ''.join(random.choices('ABCDEFGHJKLMNPQRSTUVWXYZ23456789', k=4))
                        users = _load_users()
                        users.setdefault(key, {})['sub_until'] = _until
                        users[key]['entry_code'] = _ec
                        users[key]['vip'] = True
                        users[key]['vip_until'] = _until
                        users[key]['paid_total'] = round(float(users[key].get('paid_total', 0) or 0) + _eq, 2)
                        _save_users(users)
                        d['items'].append({'kind': kind, 'id': rid, 'user': key, 'device': device or (key[4:] if key.startswith('dev:') else key),
                                           'amount': amt, 'quota': 0, 'note': note,
                                           'ts': time.strftime('%Y-%m-%d %H:%M'), 'status': 'auto'})
                        _save_pays(d)
                        print(f'[月费自助·自动进入] {key} → 到期 {_until}')
                        return self._json({'ok': True, 'auto': True, 'active': True, 'until': _until, 'quota': _eq, 'entry_code': _ec,
                                           'msg': f'欢迎！已开通（到期 {_until}），赠送 AI 额度 ¥{_eq:.0f}。开通凭证：{_ec}'})
                    users = _load_users()
                    users.setdefault(key, {})['paid_total'] = round(float(users.get(key, {}).get('paid_total', 0) or 0) + _q, 2)
                    _save_users(users)
                    d['items'].append({'kind': kind, 'id': rid, 'user': key, 'device': device or (key[4:] if key.startswith('dev:') else key),
                                       'amount': amt, 'quota': _q, 'note': note,
                                       'ts': time.strftime('%Y-%m-%d %H:%M'), 'status': 'auto'})
                    _save_pays(d)
                    print(f'[自助充值·自动到账] {key} +{_q:.2f}元')
                    return self._json({'ok': True, 'auto': True, 'quota': _q,
                                       'msg': f'充值成功！已到账 {_q:.2f} 元额度'})
                d['items'].append({'kind': kind, 'id': str(int(time.time() * 1000)),
                                   'user': key, 'device': device or (key[4:] if key.startswith('dev:') else key),
                                   'amount': amt, 'quota': _q, 'note': note,
                                   'ts': time.strftime('%Y-%m-%d %H:%M'), 'status': 'pending'})
                _save_pays(d)
                print(f'[付款待确认] {key} 提交 {amt} 元')
                if kind == 'donate':
                    return self._json({'ok': True, 'msg': '心意已收到，谢谢！'})
                return self._json({'ok': True, 'msg': '已提交，等待管理员确认'})
            except Exception as e:
                return self._json({'ok': False, 'msg': str(e)}, 500)
        if p == '/api/vip/activate':
            try:
                length = int(self.headers.get('Content-Length', 0))
                data = json.loads(self.rfile.read(length))
                token = data.get('token') or self.headers.get('X-Token') or ''
                au = _check_token(token) if token else None
                # 无 token 时用设备 ID（设备绑定开通）
                device = (data.get('device_id') or '').strip()
                if not au and device:
                    users = _load_users()
                    u = users.setdefault('dev:' + device, {'pwd': '', 'vip': False, 'vip_until': '', 'created': time.strftime('%Y-%m-%d'), 'token': '', 'ai_quota': {}})
                    _save_users(users)
                    au = 'dev:' + device
                if not au:
                    return self._json({'ok': False, 'msg': '无法识别设备，请重试'})
                ok, msg = activate_code(au, data.get('code', ''))
                tok = ''
                if ok:
                    users = _load_users()
                    tok = _mk_token(au)
                    users.setdefault(au, {})['token'] = tok
                    _save_users(users)
                return self._json({'ok': ok, 'msg': msg, 'token': tok, 'username': au})
            except Exception as e:
                return self._json({'ok': False, 'msg': str(e)}, 500)
        if p == '/api/license/check':
            try:
                length = int(self.headers.get('Content-Length', 0))
                data = json.loads(self.rfile.read(length)) if length else {}
                token = (data.get('token') or self.headers.get('X-Token') or '').strip()
                u = _check_token(token) if token else None
                if not u:
                    return self._json({'ok': False, 'msg': '未激活或登录已过期'})
                vip, until = _vip_info(u)
                if not vip:
                    return self._json({'ok': False, 'msg': '已到期', 'until': until})
                return self._json({'ok': True, 'until': until, 'username': u, 'vip': True})
            except Exception as e:
                return self._json({'ok': False, 'msg': str(e)}, 500)
        if p == '/api/admin/pay_action':
            try:
                length = int(self.headers.get('Content-Length', 0))
                data = json.loads(self.rfile.read(length))
                pid = str(data.get('id') or '')
                act = (data.get('action') or '').strip()
                d = _load_pays()
                rec = None
                for x in d['items']:
                    if x.get('id') == pid:
                        rec = x
                        break
                if not rec:
                    return self._json({'ok': False, 'msg': '记录不存在'})
                if act == 'reject':
                    rec['status'] = 'rejected'
                    _save_pays(d)
                    return self._json({'ok': True, 'msg': '已忽略'})
                if act == 'approve':
                    try:
                        _min = float(_load_pricing().get('pay', {}).get('sub_min', 10) or 10)
                    except Exception:
                        _min = 10.0
                    _amt = float(rec.get('amount') or 0)
                    if rec.get('kind') == 'sub' and _amt < _min and not data.get('force'):
                        return self._json({'ok': False,
                                           'msg': '⚠️ 这笔只有 ¥%.0f，低于最低 ¥%.0f，请先核对到账金额（如确认无误可再次点击强制发码）' % (_amt, _min)})
                    users = _load_users()
                    u = rec.get('user') or ('dev:' + (rec.get('device') or ''))
                    rec['status'] = 'approved'
                    rec['approved_at'] = time.strftime('%Y-%m-%d %H:%M')
                    if rec.get('kind') == 'sub':
                        until = _sub_until()
                        try:
                            _eq = float(_load_pricing().get('pay', {}).get('entry_quota', 5) or 5)
                        except Exception:
                            _eq = 5.0
                        if rec.get('unlock_code'):
                            _uc = rec['unlock_code']
                        else:
                            _uc = ''.join(random.choices('ABCDEFGHJKLMNPQRSTUVWXYZ23456789', k=6))
                            un = _load_unlocks()
                            un['codes'][_uc] = {'used': False, 'device': '', 'ts': time.strftime('%Y-%m-%d %H:%M'),
                                                'until': until, 'amount': rec.get('amount', 0), 'quota': _eq,
                                                'for': rec.get('device', '')}
                            _save_unlocks(un)
                            rec['unlock_code'] = _uc
                        _save_pays(d)
                        print(f'[确认到账·发解锁码] {rec.get("device")} ¥{rec.get("amount")} → {_uc}')
                        return self._json({'ok': True, 'code': _uc, 'until': until,
                                           'msg': f'已确认到账！解锁码：{_uc}\n把它发给用户，他在锁屏输入即可进入（只能用一次）'})
                    if rec.get('kind') == 'sub_auto':
                        until = _sub_until()
                        users.setdefault(u, {})['sub_until'] = until
                        users[u]['vip'] = True
                        users[u]['vip_until'] = until
                        _save_users(users)
                        _save_pays(d)
                        print(f'[月费确认] {u} → 到期 {until}')
                        return self._json({'ok': True, 'msg': f'已确认，该用户可进入（到期 {until}）', 'until': until})
                    if rec.get('kind') == 'activate':
                        made = gen_code(3650, 1, '付款开通 ' + (rec.get('device') or ''), 'activate')
                        rec['code'] = made[0]
                        _save_pays(d)
                        print(f'[付款开通] {u} → 生成激活码 {made[0]}')
                        return self._json({'ok': True, 'msg': f'已确认，激活码 {made[0]} 已发给该用户（他页面会自动出现）', 'code': made[0]})
                    _def = rec.get('quota') or round(float(rec.get('amount') or 40) * _pay_ratio(), 2)
                    amt = float(data.get('quota') or _def)
                    users.setdefault(u, {})['paid_total'] = round(float(users.get(u, {}).get('paid_total', 0) or 0) + amt, 2)
                    _save_users(users)
                    rec['quota'] = amt
                    _save_pays(d)
                    print(f'[付款充值] {u} +{amt:.2f}元')
                    return self._json({'ok': True, 'msg': f'已确认到账，已给该用户加 {amt:.2f} 元额度'})
                return self._json({'ok': False, 'msg': '未知操作'})
            except Exception as e:
                return self._json({'ok': False, 'msg': str(e)}, 500)
        if p == '/api/admin/user_action':
            try:
                length = int(self.headers.get('Content-Length', 0))
                data = json.loads(self.rfile.read(length))
                u = (data.get('username') or '').strip()
                act = (data.get('action') or '').strip()
                users = _load_users()
                if u not in users:
                    return self._json({'ok': False, 'msg': '用户不存在'})
                if act == 'delete':
                    users.pop(u, None)
                    _save_users(users)
                    return self._json({'ok': True, 'msg': '已删除 ' + u})
                if act == 'vip':
                    days = max(0, min(int(data.get('days', 30)), 3650))
                    users[u]['vip'] = days > 0
                    users[u]['vip_until'] = time.strftime('%Y-%m-%d', time.localtime(time.time() + days * 86400)) if days > 0 else ''
                    _save_users(users)
                    return self._json({'ok': True, 'msg': f'会员已设 {days} 天' if days > 0 else f'已取消会员'})
                if act == 'quota':
                    amt = float(data.get('amount', 10) or 0)
                    users[u]['ai_quota_cny'] = round(float(users[u].get('ai_quota_cny', 0) or 0) + amt, 2)
                    _save_users(users)
                    return self._json({'ok': True, 'msg': '已充额度 %.2f 元' % amt})
                if act == 'reset_used':
                    users[u]['ai_used_cny'] = 0
                    _save_users(users)
                    return self._json({'ok': True, 'msg': '已清零用量'})
                if act == 'kick':
                    users[u]['token'] = ''
                    _save_users(users)
                    return self._json({'ok': True, 'msg': '已强制下线，该设备需重新激活'})
                return self._json({'ok': False, 'msg': '未知操作'})
            except Exception as e:
                return self._json({'ok': False, 'msg': str(e)}, 500)
        if p == '/api/admin/code_action':
            try:
                length = int(self.headers.get('Content-Length', 0))
                data = json.loads(self.rfile.read(length))
                code = (data.get('code') or '').strip().upper()
                act = (data.get('action') or '').strip()
                c = _load_codes()
                if code not in c.get('codes', {}):
                    return self._json({'ok': False, 'msg': '激活码不存在'})
                if act == 'delete':
                    del c['codes'][code]; msg = '已删除 ' + code
                elif act == 'disable':
                    c['codes'][code]['enabled'] = False; msg = '已停用 ' + code
                elif act == 'enable':
                    c['codes'][code]['enabled'] = True; msg = '已启用 ' + code
                elif act == 'reset':
                    c['codes'][code].update({'used': False, 'used_by': '', 'used_at': ''}); msg = '已重置 ' + code
                else:
                    return self._json({'ok': False, 'msg': '未知操作'})
                _save_codes(c)
                return self._json({'ok': True, 'msg': msg})
            except Exception as e:
                return self._json({'ok': False, 'msg': str(e)}, 500)
        if p == '/api/admin/login':
            try:
                length = int(self.headers.get('Content-Length', 0))
                data = json.loads(self.rfile.read(length)) if length else {}
                pw = (data.get('password') or '').strip()
                return self._json({'ok': pw == _admin_pw(), 'msg': '' if pw == _admin_pw() else '密码错误'})
            except Exception as e:
                return self._json({'ok': False, 'msg': str(e)}, 500)
        if p == '/api/admin/pricing':
            try:
                length = int(self.headers.get('Content-Length', 0))
                data = json.loads(self.rfile.read(length))
                pr = data.get('pricing') or data
                if not pr.get('plans'):
                    return self._json({'ok': False, 'msg': '套餐不能为空'})
                _save_pricing(pr)
                return self._json({'ok': True, 'msg': '计费设置已保存', 'pricing': _load_pricing()})
            except Exception as e:
                return self._json({'ok': False, 'msg': str(e)}, 500)
        if p == '/api/admin/gen_code':
            try:
                length = int(self.headers.get('Content-Length', 0))
                data = json.loads(self.rfile.read(length))
                days = max(1, min(int(data.get('days', 30)), 3650))
                batch = max(1, min(int(data.get('batch', 1)), 100))
                made = gen_code(days, batch, (data.get('note') or '').strip(), data.get('plan'), data.get('charge'))
                return self._json({'ok': True, 'codes': made, 'msg': f'已生成 {len(made)} 个激活码（{days} 天）'})
            except Exception as e:
                return self._json({'ok': False, 'msg': str(e)}, 500)
        if p == '/api/admin/codes':
            return self._json(_admin_codes_payload())
        if p == '/api/admin/set_vip':
            try:
                length = int(self.headers.get('Content-Length', 0))
                data = json.loads(self.rfile.read(length))
                u = (data.get('username') or '').strip()
                days = max(0, int(data.get('days', 30)))
                users = _load_users()
                if u not in users:
                    return self._json({'ok': False, 'msg': '用户不存在'})
                users[u]['vip'] = days > 0
                users[u]['vip_until'] = time.strftime('%Y-%m-%d', time.localtime(time.time() + days * 86400)) if days > 0 else ''
                _save_users(users)
                return self._json({'ok': True, 'msg': f'{u} 会员已设置：' + (f'至 {users[u]["vip_until"]}' if days > 0 else '已取消')})
            except Exception as e:
                return self._json({'ok': False, 'msg': str(e)}, 500)
        if p == '/api/admin/rebuild':
            return self._json(admin_panel.rebuild())
        if p == '/api/admin/scraper':
            return self._json(admin_panel.run_scraper())
        if p == '/api/deploy_node':
            # 一键部署专属高速节点：SSH 到服务器执行 deploy_node.sh
            try:
                import io as _io
                length = int(self.headers.get('Content-Length', 0))
                data = json.loads(self.rfile.read(length))
                ip = (data.get('ip') or '').strip()
                port = int(data.get('port') or 22)
                password = (data.get('password') or '').strip()
                username = (data.get('username') or 'root').strip()
                if not ip or not password:
                    return self._json({'error': '请填写服务器 IP 和 root 密码'}, 400)
                import paramiko
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(ip, port=port, username=username, password=password, timeout=20, look_for_keys=False, allow_agent=False)
                script_path = Path(__file__).parent / 'deploy_node.sh'
                if not script_path.exists():
                    script_path = Path(DIR) / 'deploy_node.sh'
                script = script_path.read_bytes()
                sftp = client.open_sftp()
                sftp.putfo(_io.BytesIO(script), '/root/deploy_node.sh')
                sftp.close()
                stdin, stdout, stderr = client.exec_command('bash /root/deploy_node.sh', timeout=180)
                out = stdout.read().decode('utf-8', errors='ignore')
                err = stderr.read().decode('utf-8', errors='ignore')
                client.close()
                import re as _re
                m = _re.search(r'vless://\S+', out)
                return self._json({'ok': True, 'output': (out + err)[-3000:], 'vless': m.group(0) if m else ''})
            except Exception as e:
                print(f'[DeployNode Error] {e}')
                return self._json({'error': str(e)}, 500)
        if p == '/api/tts':
            try:
                length = int(self.headers.get('Content-Length', 0))
                data = json.loads(self.rfile.read(length))
                text = (data.get('text') or '').strip()[:500]
                lang = (data.get('language') or data.get('lang') or '').strip().lower()
                if not lang:
                    # 兜底：按正文自动选语言（中文 → zh，阿拉伯语 → ar）
                    lang = 'zh' if any('\u4e00' <= ch <= '\u9fff' for ch in text[:200]) else 'ar'
                if not text:
                    return self._json({'error': 'empty text'}, 400)
                kind = str(data.get('content_kind') or 'learning').strip().lower()
                if kind in ('quran_original', 'hadith_original', 'quran_recitation', 'hadith_recitation'):
                    return self._json({'error': '宗教原文与诵读不使用合成音；请使用页面提供的来源标注真人诵读。'}, 400)
                voices = {
                    'ar-SA-HamedNeural', 'ar-SA-ZariyahNeural', 'ar-EG-SalmaNeural',
                    'ar-EG-ShakirNeural', 'ar-JO-TaimNeural', 'ar-JO-SanaNeural',
                    'zh-CN-XiaoxiaoNeural', 'zh-CN-YunxiNeural', 'en-US-JennyNeural'
                }
                defaults = {'zh': 'zh-CN-XiaoxiaoNeural', 'en': 'en-US-JennyNeural', 'ar': 'ar-SA-HamedNeural'}
                voice = str(data.get('voice_id') or '').strip()
                if voice not in voices or (lang == 'ar' and not voice.startswith('ar-')) or (lang == 'zh' and not voice.startswith('zh-')):
                    voice = defaults.get(lang, defaults['zh'])
                try:
                    speed = max(0.82, min(float(data.get('speed', 1.0)), 1.18))
                except Exception:
                    speed = 1.0
                rate = ('+' if speed >= 1 else '') + str(int(round((speed - 1) * 100))) + '%'
                provider_version = 'edge-tts-natural-v1'
                key = hashlib.sha256((text + '|' + lang + '|' + voice + '|' + str(speed) + '|' + provider_version).encode('utf-8')).hexdigest()[:32]
                out_dir = getattr(music_gen, 'OUT_DIR', None) if music_gen else None
                out_dir = out_dir or (DIR / 'music')
                os.makedirs(out_dir, exist_ok=True)
                name = 'tts_' + key + '.mp3'
                out = os.path.join(str(out_dir), name)
                if os.path.exists(out) and os.path.getsize(out) > 1000:
                    return self._json({'url': '/music/' + name, 'provider': provider_version, 'voice_id': voice, 'synthetic': True, 'cached': True})
                import asyncio, edge_tts
                async def _t():
                    c = edge_tts.Communicate(text, voice, rate=rate)
                    await c.save(out)
                asyncio.run(_t())
                return self._json({'url': '/music/' + name, 'provider': provider_version, 'voice_id': voice, 'synthetic': True, 'cached': False})
            except Exception as e:
                print(f'[TTS Error] {e}')
                return self._json({'error': str(e)}, 500)
        if p == '/api/image':
            # AI 生成图片（Pollinations 免费服务，服务器代理解决国内访问）
            try:
                length = int(self.headers.get('Content-Length', 0))
                data = json.loads(self.rfile.read(length))
                prompt = (data.get('prompt') or '').strip()
                w = max(256, min(int(data.get('width', 512)), 1024))
                h = max(256, min(int(data.get('height', 512)), 1024))
                if not prompt:
                    return self._json({'error': '请提供图片描述'}, 400)
                from urllib.parse import quote
                url = f'https://image.pollinations.ai/prompt/{quote(prompt)}?width={w}&height={h}&nologo=true&seed={random.randint(1,99999)}'
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                resp = urllib.request.urlopen(req, timeout=90)
                img = resp.read()
                os.makedirs(os.path.join(DIR, 'images'), exist_ok=True)
                name = f'img_{int(time.time())}.jpg'
                open(os.path.join(DIR, 'images', name), 'wb').write(img)
                return self._json({'url': '/images/' + name, 'size': len(img), 'prompt': prompt})
            except Exception as e:
                print(f'[Image Error] {e}')
                return self._json({'error': str(e)}, 500)
        if p == '/api/music':
            try:
                length = int(self.headers.get('Content-Length', 0))
                data = json.loads(self.rfile.read(length))
                # 电脑本机直接放行；手机等远程设备校验激活码
                if self.client_address[0] not in ('127.0.0.1', '::1'):
                    token = data.get('token') or self.headers.get('X-Token') or ''
                    device = (data.get('device_id') or '').strip()
                    au = _check_token(token) if token else None
                    if not au and device:
                        users = _load_users()
                        if 'dev:' + device in users:
                            au = 'dev:' + device
                    if not au:
                        return self._json({'error': 'AI 音乐需激活码开通，在「我的 → 开通会员」输入激活码解锁', 'need_activate': True}, 403)
                    vip, until = _vip_info(au)
                    if not vip:
                        return self._json({'error': 'AI 音乐需激活码开通，在「我的 → 开通会员」输入激活码解锁', 'need_activate': True}, 403)
                prompt = (data.get('prompt') or '').strip()
                seconds = max(5, min(int(data.get('seconds', 30)), 300))
                lang = (data.get('lang') or '').strip()  # 'zh'/'en'/'ar'/''（歌词语言，空=纯音乐）
                if not prompt:
                    return self._json({'error': '请提供提示词'}, 400)
                seconds = 120 if seconds >= 90 else seconds  # 完整歌曲固定 2 分钟
                # 1. 写歌词（用户选语言时）
                lyrics = ''
                lyrics_cn = ''
                if lang in ('zh', 'en', 'ar'):
                    lyrics, lyrics_cn = _gen_lyrics(prompt, lang)
                # 2. 提示词转英文（MusicGen 英文效果最好）
                en_prompt = _to_en(prompt)
                if lang in ('zh', 'en', 'ar'):
                    en_prompt += ', with clear vocal singing a heartfelt song melody'
                # 3. 生成音乐
                if seconds > 45:
                    name, dur = music_gen.gen_long(en_prompt, seconds)
                else:
                    name, dur = music_gen.gen(en_prompt, seconds)
                return self._json({'url': '/music/' + name, 'duration': dur, 'lyrics': lyrics, 'lyrics_cn': lyrics_cn})
            except Exception as e:
                print(f'[Music Error] {e}')
                return self._json({'error': str(e)}, 500)
        if p != '/api/chat/message':
            return self._json({"error": "Not found"}, 404)
        
        try:
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length))
            msg = data.get("message", "").strip()
            sid = data.get("session_id", "default")
            _fast_chat = bool(data.get('fast'))
            # === 需要时自动联网搜索（免费源）===
            try:
                # 只要输入有点内容就联网（用户要求：输入即查）
                if not _fast_chat and len((msg or '').strip()) >= 4:
                    _ws = _web_search(msg, 4)
                    if _ws:
                        _ctx = '\n'.join([('【' + x['src'] + '】' + x['t'] + '：' + x['s'] + ' ' + x['u']) for x in _ws])
                        data['message'] = (msg + '\n\n[以下是刚从网上查到的资料，请在回答末尾用「📎 参考资料」列出有用的链接]\n' + _ctx
                                           + '\n（要求：1) 先直接回答；2) 末尾列 1-3 条最相关链接，格式「- 标题：链接」；3) 资料不足就说明，不要编造）')
                        msg = data['message']
            except Exception as _we:
                print('[联网搜索异常]', _we)
            try:
                _dev = (data.get('device_id') or '').strip()
                _fwd2 = (self.headers.get('X-Forwarded-For') or '').split(',')[0].strip()
                _dev = _dev or _fwd2 or self.client_address[0]
                _is_vip = False
                try:
                    _tk = (data.get('token') or self.headers.get('X-Token') or '').strip()
                    _u2 = _check_token(_tk) if _tk else None
                    if _u2:
                        _rec = (_load_users().get(_u2) or {})
                        _unt = str(_rec.get('sub_until') or _rec.get('vip_until') or '')
                        if _unt and _unt >= time.strftime('%Y-%m-%d'):
                            _is_vip = True
                except Exception:
                    pass
                # 管理员的设备不受每日次数限制
                try:
                    _ul = (_ai_cfg().get('unlimited_devices') or [])
                    if _dev and (_dev in _ul):
                        _is_vip = True
                    # IP 也在名单里（老版本页面不传设备号时兜底）
                    _fwd3 = (self.headers.get('X-Forwarded-For') or '').split(',')[0].strip()
                    if _fwd3 and (_fwd3 in _ul):
                        _is_vip = True
                except Exception:
                    pass
                if not _is_vip:
                    _okq, _leftq = _free_daily_use(_dev, 10)
                    if not _okq:
                        return self._json({'reply': '今天的 10 次免费对话用完啦 🌙 明天再来，或点「💖 支持网站」解锁无限 ✓', 'arabic': '', 'limited': True, 'left': 0})
            except Exception as _qe:
                print('[额度检查异常]', _qe)
            au = None
            # 电脑本机（localhost）直接放行；手机等远程设备校验激活码
            # 注意：经 Apache/Nginx 反代时 client_address 恒为 127.0.0.1，必须看 X-Forwarded-For
            _fwd = (self.headers.get('X-Forwarded-For') or '').split(',')[0].strip()
            _cip = _fwd or self.client_address[0]
            if _cip in ('127.0.0.1', '::1'):
                pass
            else:
                token = data.get("token") or self.headers.get('X-Token') or ''
                device = (data.get('device_id') or '').strip()
                au = _check_token(token) if token else None
                if not au and device:
                    users = _load_users()
                    if 'dev:' + device in users:
                        au = 'dev:' + device
                if not au:
                    # 免费开放：按设备号各记各的额度（每人独立 ¥5 欢迎额度）
                    _d = (data.get('device_id') or '').strip()
                    if _d:
                        users = _load_users()
                        users.setdefault('dev:' + _d, {'pwd': '', 'vip': False, 'vip_until': '',
                                                       'created': time.strftime('%Y-%m-%d'), 'token': '', 'ai_quota': {}})
                        _save_users(users)
                        au = 'dev:' + _d
                    else:
                        au = 'dev:anon'
                vip, until = _vip_info(au)
                _ensure_entry_quota(au)
                _b = _user_bal(au)
                if _b['paid_left'] <= 0 and _b['free_left'] <= 0:
                    _ok2, _u2, _ = _sub_status(au)
                    if not _ok2:
                        return self._json({"arabic": "⚠️ 需要先开通才能使用 AI\n\n点首页「💳 付费进入网站」（¥10/月，含 ¥5 AI 额度），付款后立即自动进入。"})
                    return self._json({"arabic": "⚠️ 你的 AI 额度已用完（¥%.2f）\n\n点首页「💖 支持网站」捐一点，额度立即到账，谢谢支持！" % _b['paid_total']})

                try:
                    _cap = float(_load_pricing().get('pay', {}).get('global_month_cap', 80) or 80)
                except Exception:
                    _cap = 80.0
                _spend = _global_spend()
                if _cap > 0 and _spend >= _cap:
                    return self._json({"arabic": "⚠️ 本月 AI 预算已用完\n\n网站靠大家的心意维持，请下月再来。"})
            
            if not msg:
                return self._json({"arabic": "هَلْ تُرِيدُ التَّحَدُّثَ بِالعَرَبِيَّةِ؟\n想练习阿拉伯语吗？"})
            # === "我要去某网站" → 直接给跳转 ===
            try:
                _op = _detect_open(msg)
                if _op:
                    return self._json({'arabic': '好啊，帮你打开 **' + _op['label'] + '** ✓\n\n（手机没自动跳的话，点下面的按钮 ✓）',
                                       'action': {'url': _op['url'], 'label': '打开 ' + _op['label']}})
            except Exception as _oe:
                print('[意图识别异常]', _oe)
            
            # Article check
            if any(w in msg.lower() for w in ["اكتب", "write", "مقال", "article", "文章", "写篇"]):
                art = find_article(msg)
                if art:
                    return self._json({"arabic": art})
            
            # Real AI
            if sid not in convs:
                convs[sid] = [{"role": "system", "content": _AI_GUARD + SYSTEM}]
            
            convs[sid].append({"role": "user", "content": msg})
            
            resp = call_deepseek(convs[sid], fast=_fast_chat)
            if resp == 'QUOTA_ERROR':
                return self._json({"arabic": "⚠️ AI 服务配额已用尽\nAI 暂时不可用：请稍后重试，或在 AionClaw 设置中恢复 AI 服务配额。"})
            if resp:
                convs[sid].append({"role": "assistant", "content": resp})
                if len(convs[sid]) > 8:
                    convs[sid] = [convs[sid][0]] + convs[sid][-6:]
                if au:
                    _charge_ai(au, dict(LAST_USAGE))
                if resp == 'PAUSED':
                    return self._json({"arabic": "🌙 今天的 AI 老师先休息了\n（站长的 AI 额度用完了，明天或补充后自动恢复）\n其他功能都能正常用：查词典 · 句子库 · 听力 · 口语 · 书库 ✓"})
                return self._json({"arabic": _ai_sanitize(resp)})
            
            # Fallback
            convs[sid].pop()
            return self._json({"arabic": "⚠️ 免费 AI 眼下正忙（上游 500），请稍等 10 秒再问一次 🌙\n（你不是没额度，是免费服务在排队 ✓ 无限次 ✓）", "retry": 1})
            
        except Exception as e:
            print(f"[Error] {e}")
            return self._json({"arabic": "⚠️ عذراً! حَدَثَ خَطَأٌ. أَعِدِ المُحَاوَلَةَ.\n⚠️ 出错了，请重试。"}, 200)
    
    def log_message(self, fmt, *args):
        msg = fmt % args
        if "/api/" in msg:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


# ===== 免费节点订阅（Clash Verge /sub）=====
_SUB_CACHE = {'t': 0, 'data': ''}
_SUB_CACHE_LOCK = threading.Lock()
_SUB_REFRESHING = False
_SUB_LAST_ERROR = ''
_SUB_REFRESH_INTERVAL = 1800
_SUB_EMPTY_YAML = '# 燃灯者 · 节点缓存正在后台刷新，请稍后再次请求。\nproxies: []\n'

def _sub_cache_refresh():
    import time as _t
    import base64 as _b64, urllib.parse as _up, json as _json
    # 从多个源抓取（主源 + 备源）
    sources = [
        'https://cdn.jsdelivr.net/gh/mfuu/v2ray@master/v2ray',
        'https://ghproxy.net/https://raw.githubusercontent.com/mfuu/v2ray/master/v2ray',
        'https://ghproxy.net/https://raw.githubusercontent.com/aiboboxx/v2rayfree/main/v2ray',
        'https://ghproxy.net/https://raw.githubusercontent.com/freefq/free/master/v2ray',
        'https://ghproxy.net/https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub',
    ]
    all_txt = ''
    for s in sources:
        try:
            req = urllib.request.Request(s, headers={'User-Agent': 'Mozilla/5.0'})
            raw = urllib.request.urlopen(req, timeout=2.0).read(2 * 1024 * 1024)
            try:
                t = _b64.b64decode(raw).decode('utf-8')
            except Exception:
                t = raw.decode('utf-8', errors='ignore')
            if '://' in t:
                all_txt += '\n' + t
        except Exception as e:
            print(f'  [Sub] 源失败 {s[:50]}: {e}')
    txt = all_txt
    proxies = []
    seen = set()
    for line in txt.split('\n'):
        line = line.strip()
        if not line or '://' not in line:
            continue
        pp = line.split('://')[0]
        try:
            if pp == 'trojan':
                u = _up.urlparse(line)
                q = dict(_up.parse_qsl(u.query))
                name = 'TJ-' + (u.hostname or '?') + '-' + str(u.port)
                if name in seen: continue
                seen.add(name)
                pr = {'name': name, 'type': 'trojan', 'server': u.hostname, 'port': int(u.port or 443), 'password': _up.unquote(u.username or '')}
                if q.get('sni'): pr['sni'] = q['sni']
                if q.get('allowInsecure') == '1': pr['skip-cert-verify'] = True
                if q.get('ws') == '1' or q.get('type') == 'ws':
                    pr['network'] = 'ws'
                    if q.get('wspath'): pr['ws-opts'] = {'path': _up.unquote(q['wspath'])}
                proxies.append(pr)
            elif pp == 'vmess':
                b64 = line.split('://')[1]
                try:
                    v = _json.loads(_b64.b64decode(b64 + '===').decode('utf-8'))
                except Exception:
                    continue
                name = 'VM-' + str(v.get('add', '?')) + '-' + str(v.get('port', '?'))
                if name in seen: continue
                seen.add(name)
                pr = {'name': name, 'type': 'vmess', 'server': v.get('add', ''), 'port': int(v.get('port', 443)), 'uuid': v.get('id', ''), 'alterId': int(v.get('aid', 0) or 0), 'cipher': 'auto'}
                if v.get('tls') == 'tls': pr['tls'] = True
                if v.get('net') == 'ws':
                    pr['network'] = 'ws'
                    wopts = {}
                    if v.get('path'): wopts['path'] = v['path']
                    if v.get('host'): wopts['headers'] = {'Host': v['host']}
                    if wopts: pr['ws-opts'] = wopts
                proxies.append(pr)
        except Exception:
            continue
    if not proxies:
        raise Exception('未获取到可用节点')
    # 只对有限候选做TCP测速；其余节点保留但不让刷新时间随源规模失控。
    try:
        import socket as _sock
        from concurrent.futures import ThreadPoolExecutor as _TPE
        probe = proxies[:64]
        untested = proxies[64:]
        def _ping(p):
            try:
                st = _t.time()
                s = _sock.create_connection((p['server'], int(p['port'])), timeout=1.2)
                s.close()
                return round((_t.time() - st) * 1000)
            except Exception:
                return 99999
        with _TPE(max_workers=min(12, max(1, len(probe)))) as ex:
            lat = list(ex.map(_ping, probe))
        fast = sorted(zip(probe, lat), key=lambda x: x[1])
        fast = [p for p, l in fast if l < 99999]
        slow = [p for p, l in zip(probe, lat) if l >= 99999]
        proxies = fast + slow + untested
        print(f'  [Sub] 测速完成：{len(fast)} 可达 / {len(slow)} 未达 / {len(untested)} 未测速', flush=True)
    except Exception as e:
        print(f'  [Sub] 测速失败（继续）: {e}')
    # 生成 yaml
    names = [p['name'] for p in proxies]
    import json as _json
    def _j(v):
        return _json.dumps(str(v), ensure_ascii=False)
    y = '# 燃灯者 · 免费节点（时效有限，失效后点更新）\nmixed-port: 7890\nallow-lan: true\nmode: rule\nlog-level: info\n\nproxies:\n'
    for pr in proxies:
        y += f"  - name: {pr['name']}\n    type: {pr['type']}\n    server: {pr['server']}\n    port: {pr['port']}\n"
        for k in ['password', 'uuid', 'cipher', 'alterId', 'sni', 'network', 'tls', 'skip-cert-verify']:
            if k in pr:
                v = pr[k]
                y += f"    {k}: {'true' if v is True else ('false' if v is False else _j(v))}\n"
        if 'ws-opts' in pr:
            y += f"    ws-opts: {_json.dumps(pr['ws-opts'], ensure_ascii=False)}\n"
    y += '\nproxy-groups:\n'
    y += f"  - name: '🚀 节点选择'\n    type: select\n    proxies: {_json.dumps(names, ensure_ascii=False)}\n"
    y += f"  - name: '♻️ 自动选择'\n    type: url-test\n    proxies: {_json.dumps(names, ensure_ascii=False)}\n    url: 'http://www.gstatic.com/generate_204'\n    interval: 300\n\nrules:\n  - GEOIP,CN,DIRECT\n  - MATCH,🚀 节点选择\n"
    return y

def _sub_snapshot():
    now = time.time()
    with _SUB_CACHE_LOCK:
        stamp = float(_SUB_CACHE.get('t') or 0)
        data = str(_SUB_CACHE.get('data') or '')
        refreshing = bool(_SUB_REFRESHING)
        last_error = str(_SUB_LAST_ERROR or '')
    return {'data': data, 'refreshing': refreshing, 'stale': (not data or now - stamp >= _SUB_REFRESH_INTERVAL),
            'age_seconds': round(max(0.0, now - stamp), 1) if stamp else None,
            'last_success': datetime.fromtimestamp(stamp).isoformat(timespec='seconds') if stamp else None,
            'last_error': last_error}

def _sub_refresh_worker():
    global _SUB_REFRESHING, _SUB_LAST_ERROR
    try:
        data = _sub_cache_refresh()
        with _SUB_CACHE_LOCK:
            _SUB_CACHE['t'] = time.time()
            _SUB_CACHE['data'] = data
            _SUB_LAST_ERROR = ''
        print(f'  [Sub] 后台刷新成功：{len(data)} bytes', flush=True)
    except Exception as e:
        with _SUB_CACHE_LOCK:
            _SUB_LAST_ERROR = str(e)[:300]
        print(f'  [Sub] 后台刷新失败（保留旧缓存）: {e}', flush=True)
    finally:
        with _SUB_CACHE_LOCK:
            _SUB_REFRESHING = False

def _sub_start_refresh():
    global _SUB_REFRESHING
    start = False
    now = time.time()
    with _SUB_CACHE_LOCK:
        fresh = bool(_SUB_CACHE.get('data')) and now - float(_SUB_CACHE.get('t') or 0) < _SUB_REFRESH_INTERVAL
        if not fresh and not _SUB_REFRESHING:
            _SUB_REFRESHING = True
            start = True
    if start:
        threading.Thread(target=_sub_refresh_worker, name='nour-sub-refresh', daemon=True).start()
    return _sub_snapshot()

def main():
    print("="*45)
    print("  📖 阿拉伯语学习 + 🤖 DeepSeek AI")
    print("="*45)
    print(f"  http://localhost:{PORT}")
    print(f"  手机: http://192.168.1.9:{PORT}")
    print("  Ctrl+C 停止")
    print("="*45)
    try:
        ThreadingHTTPServer(("", PORT), Handler).serve_forever()
    except KeyboardInterrupt:
        print("\n👋 已停止")

if __name__ == "__main__":
    main()
