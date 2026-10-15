#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""阿拉伯语学习 - 网页 + DeepSeek AI + 文章 (端口8080)"""
import json, os, random, re, urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from datetime import datetime
from pathlib import Path

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

SYSTEM = "أنت معلم لغة عربية محترف اسمك رفيق العربية. رد بالعربية الفصحى مع التشكيل الكامل. التزم بهذا التنسيق دائماً: السطر الأول بالعربية، ثم سطر فارغ، ثم السطر الثاني الترجمة الصينية، ثم السطر الثالث الترجمة الإنجليزية. كن مشجعاً ومفيداً."

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
    body = json.dumps({"model": AI_CFG.get('model', 'deepseek-chat'), "messages": messages, "max_tokens": 600}, ensure_ascii=False).encode("utf-8")
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

class Handler(BaseHTTPRequestHandler):
    def _json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))
    
    def _serve(self, path):
        fp = DIR / path.lstrip("/")
        if not fp.exists():
            fp = DIR / "arabic_learning.html"
        ct = {".html": "text/html; charset=utf-8", ".json": "application/json"}.get(fp.suffix, "application/octet-stream")
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
        if urlparse(self.path).path != "/api/chat/message":
            return self._json({"error": "Not found"}, 404)
        
        try:
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length))
            msg = data.get("message", "").strip()
            sid = data.get("session_id", "default")
            
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
        HTTPServer(("", PORT), Handler).serve_forever()
    except KeyboardInterrupt:
        print("\n👋 已停止")

if __name__ == "__main__":
    main()
