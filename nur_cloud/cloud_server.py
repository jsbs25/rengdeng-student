#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""阿拉伯语学习 - 网页 + DeepSeek AI + 文章 + 本地语音识别 (端口8080)"""
import json, os, random, re, urllib.request, threading, tempfile
# 语音识别离线加载优先（模型已下载则不走网络）
os.environ.setdefault('HF_HUB_OFFLINE', '1')
os.environ.setdefault('HF_ENDPOINT', 'https://hf-mirror.com')
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from datetime import datetime
from pathlib import Path
import time
import music_gen
import admin_panel
import hashlib, hmac as _hmac, base64

# ===== 用户 / 会员系统 =====
USERS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'users.json')
SECRET = 'nur-al-arabiyya-2026'
FREE_AI_DAILY = 20  # 普通用户每日 AI 次数

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

def gen_code(days=30, batch=1):
    """生成激活码（days 天会员）"""
    c = _load_codes()
    made = []
    for _ in range(batch):
        code = ''.join(random.choices('ABCDEFGHJKLMNPQRSTUVWXYZ23456789', k=12))
        code = code[:4] + '-' + code[4:8] + '-' + code[8:]
        c['codes'][code] = {'days': days, 'used': False, 'used_by': '', 'used_at': '', 'created': time.strftime('%Y-%m-%d')}
        made.append(code)
    _save_codes(c)
    return made

def activate_code(username, code):
    """兑换激活码：开通会员"""
    code = (code or '').strip().upper()
    c = _load_codes()
    if code not in c['codes']:
        return False, '激活码不存在'
    cd = c['codes'][code]
    if cd.get('used'):
        return False, '激活码已被使用'
    cd['used'] = True
    cd['used_by'] = username
    cd['used_at'] = time.strftime('%Y-%m-%d %H:%M')
    _save_codes(c)
    users = _load_users()
    u = users.setdefault(username, {})
    u['vip'] = True
    u['vip_until'] = time.strftime('%Y-%m-%d', time.localtime(time.time() + cd['days'] * 86400))
    _save_users(users)
    return True, f'开通成功！会员至 {u["vip_until"]}（{cd["days"]} 天）'

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
            return url
        except Exception:
            continue
    return candidates[0]

AI_CFG = _detect_ai_endpoint()
API_URL = AI_CFG['url']
print(f"🤖 AI 端点: {API_URL}")

SYSTEM = "أنت كاتب إسلامي محترف اسمه «حامل المصباح» (笔耕者). تخصصك كتابة المقالات الإسلامية باللغة الصينية.\n\n【لغة الرد】ردّ بالصينية دائماً (إلا إذا طلب المستخدم العربية صراحة أو أراد التدرب على الحوار العربي).\n\n【كتابة المقالات الإسلامية】عندما يطلب المستخدم مقالاً أو تأملات أو نصيحة أو تعليقاً إسلامياً:\n1. الأسلوب: كناية ورمزية وأدبية رفيعة - استخدم الاستعارات والصور البلاغية والتورية، وتجنّب الوعظ المباشر والشعارات الجوفاء\n2. الاستشهاد: استشهد بآيات القرآن الكريم (مع النص العربي والترجمة الصينية) وبالأحاديث النبوية (مع ذكر المصدر مثل صحيح البخاري)، واجعل النصوص المقدسة عموداً للمقال وروحه\n3. التسامح واحترام الاختلاف: احترم المذاهب الفقهية المختلفة (حنفي، مالكي، شافعي، حنبلي) ووجهات النظر المتعددة، وكن معتدلاً في الألفاظ، ولا تنتقص من أي مذهب أو جماعة\n4. البنية: افتتاحية تشويقية - تمهيد - استشهاد - خاتمة رفيعة، تجمع بين الأدب والدقة الشرعية\n5. الطول: حسب الموضوع، ويمكن استخدام عناوين فرعية، وليكن المقال متكاملاً\n\n【وضع التدريب على الحوار】إذا طلب المستخدم صراحة التدرب على الحوار العربي (مثل «练习对话» أو «دعنا نتدرب»)، فتحوّل إلى معلم لغة عربية: السطر الأول بالعربية الفصحى مع التشكيل، ثم سطر فارغ، ثم السطر الثاني بالترجمة الصينية، والسطر الثالث بالترجمة الإنجليزية. وفي وضع الحوار ردّ بجملة واحدة قصيرة وانتظر ردّ المستخدم.\n\n【عام】كن ودوداً وصادقاً، دقيقاً في النقل، حسن الخلق."

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

def call_deepseek(messages):
    """Call DeepSeek API"""
    body = json.dumps({"model": AI_CFG.get('model', 'deepseek-chat'), "messages": messages, "max_tokens": 2000}, ensure_ascii=False).encode("utf-8")
    hdrs = {"Content-Type": "application/json"}
    if AI_CFG.get('key'):
        hdrs["Authorization"] = "Bearer " + AI_CFG['key']
    req = urllib.request.Request(API_URL, data=body, headers=hdrs, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read())
            return data["choices"][0]["message"]["content"].strip()
    except urllib.error.HTTPError as e:
        if e.code == 402 or 'quota' in str(e.read()):
            return 'QUOTA_ERROR'
        return None
    except Exception:
        return None

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

class Handler(BaseHTTPRequestHandler):
    def _json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))
    
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

    def _serve(self, path):
        fp = DIR / path.lstrip("/")
        if not fp.exists():
            fp = DIR / "arabic_learning.html"
        if path.startswith('/music/'):
            fp = Path(music_gen.OUT_DIR) / path[len('/music/'):]
        elif path == '/pay_qr.png':
            fp = Path(DIR) / 'data' / 'pay_qr.png'
        ct = {".html": "text/html; charset=utf-8", ".json": "application/json", ".wav": "audio/wav", ".mp3": "audio/mpeg"}.get(fp.suffix, "application/octet-stream")
        try:
            data = fp.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", ct)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Access-Control-Allow-Origin", "*")
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
            return self._json({'users': [{'username': k, 'vip': v.get('vip', False), 'vip_until': v.get('vip_until', ''), 'created': v.get('created', '')} for k, v in _load_users().items()]})
        if p == '/api/admin/status':
            return self._json(admin_panel.status())
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
            c = _load_codes()
            return self._json({'codes': [{'code': k, 'days': v.get('days'), 'used': v.get('used'), 'used_by': v.get('used_by', ''), 'used_at': v.get('used_at', '')} for k, v in c.get('codes', {}).items()][-50:]})

        p = urlparse(self.path).path
        if p == '/api/asr/status':
            try:
                import importlib.util
                fw = importlib.util.find_spec('faster_whisper') is not None
                md = os.path.expanduser('~/.cache/huggingface/hub/models--Systran--faster-whisper-small')
                self._json({'asr': fw and os.path.isdir(md), 'model_ready': os.path.isdir(md), 'lib_ready': fw})
            except Exception as e:
                self._json({'asr': False, 'error': str(e)})
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
        if p == '/api/books':
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
        self._serve(p)
    
    def do_POST(self):
        p = urlparse(self.path).path
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
                return self._json({'ok': ok, 'msg': msg})
            except Exception as e:
                return self._json({'ok': False, 'msg': str(e)}, 500)
        if p == '/api/admin/gen_code':
            try:
                length = int(self.headers.get('Content-Length', 0))
                data = json.loads(self.rfile.read(length))
                days = max(1, min(int(data.get('days', 30)), 3650))
                batch = max(1, min(int(data.get('batch', 1)), 100))
                made = gen_code(days, batch)
                return self._json({'ok': True, 'codes': made, 'msg': f'已生成 {len(made)} 个激活码（{days} 天）'})
            except Exception as e:
                return self._json({'ok': False, 'msg': str(e)}, 500)
        if p == '/api/admin/codes':
            c = _load_codes()
            return self._json({'codes': [{'code': k, 'days': v.get('days'), 'used': v.get('used'), 'used_by': v.get('used_by', ''), 'used_at': v.get('used_at', '')} for k, v in c.get('codes', {}).items()][-50:]})
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
        if p == '/api/tts':
            try:
                length = int(self.headers.get('Content-Length', 0))
                data = json.loads(self.rfile.read(length))
                text = (data.get('text') or '').strip()[:500]
                lang = (data.get('lang') or 'zh').strip()
                if not text:
                    return self._json({'error': 'empty text'}, 400)
                import asyncio, tempfile, edge_tts
                voice = {'zh': 'zh-CN-XiaoxiaoNeural', 'en': 'en-US-JennyNeural', 'ar': 'ar-SA-ZariyahNeural'}.get(lang, 'zh-CN-XiaoxiaoNeural')
                name = f'tts_{int(time.time()*1000)}.mp3'
                out = os.path.join(music_gen.OUT_DIR, name)
                async def _t():
                    c = edge_tts.Communicate(text, voice, rate='-4%')
                    await c.save(out)
                asyncio.run(_t())
                return self._json({'url': '/music/' + name})
            except Exception as e:
                print(f'[TTS Error] {e}')
                return self._json({'error': str(e)}, 500)
        if p == '/api/music':
            try:
                length = int(self.headers.get('Content-Length', 0))
                data = json.loads(self.rfile.read(length))
                token = data.get('token') or self.headers.get('X-Token') or ''
                au = _check_token(token) if token else None
                if not au:
                    return self._json({'error': '请先登录', 'need_login': True}, 401)
                vip, until = _vip_info(au)
                if not vip:
                    return self._json({'error': '请先激活', 'need_activate': True}, 403)
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
            token = data.get("token") or self.headers.get('X-Token') or ''
            au = _check_token(token) if token else None
            if not au:
                return self._json({"error": "请先登录", "need_login": True}, 401)
            vip, until = _vip_info(au)
            if not vip:
                return self._json({"error": "请先激活", "need_activate": True}, 403)
            if au and not vip:
                ok_q, left_q, qmsg = _check_ai_quota(au)
                if not ok_q:
                    return self._json({"arabic": "⚠️ " + qmsg})
            
            if not msg:
                return self._json({"arabic": "هَلْ تُرِيدُ التَّحَدُّثَ بِالعَرَبِيَّةِ؟\n想练习阿拉伯语吗？"})
            
            # Article check
            if any(w in msg.lower() for w in ["اكتب", "write", "مقال", "article", "文章", "写篇"]):
                art = find_article(msg)
                if art:
                    return self._json({"arabic": art})
            
            # Real AI
            if sid not in convs:
                convs[sid] = [{"role": "system", "content": SYSTEM}]
            
            convs[sid].append({"role": "user", "content": msg})
            
            resp = call_deepseek(convs[sid])
            if resp == 'QUOTA_ERROR':
                return self._json({"arabic": "⚠️ AI 服务配额已用尽\nAI 暂时不可用：请稍后重试，或在 AionClaw 设置中恢复 AI 服务配额。"})
            if resp:
                convs[sid].append({"role": "assistant", "content": resp})
                if len(convs[sid]) > 8:
                    convs[sid] = [convs[sid][0]] + convs[sid][-6:]
                return self._json({"arabic": resp})
            
            # Fallback
            convs[sid].pop()
            fallback = "السَّلَامُ عَلَيْكُمْ! كَيْفَ حَالُكَ اليَوْمَ؟\nالسلام عليكم！你今天好吗？"
            return self._json({"arabic": fallback})
            
        except Exception as e:
            print(f"[Error] {e}")
            return self._json({"arabic": "⚠️ عذراً! حَدَثَ خَطَأٌ. أَعِدِ المُحَاوَلَةَ.\n⚠️ 出错了，请重试。"}, 200)
    
    def log_message(self, fmt, *args):
        msg = fmt % args
        if "/api/" in msg:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

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
