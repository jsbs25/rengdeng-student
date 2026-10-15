#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
阿拉伯语学习 - 每小时爬虫 + 全自动流水线
1. 从 Tatoeba 抓取新句子 -> data/data.json
2. 重新分类 -> data/categorized.json
3. 重新生成主页 -> arabic_learning.html
"""
import json, os, random, re, sys, urllib.request
from datetime import datetime
from pathlib import Path

DIR = Path(__file__).parent
DATA_FILE = DIR / 'data' / 'data.json'
CAT_FILE = DIR / 'data' / 'categorized.json'
MAX_SENTENCES = 3000
FETCH_PER_RUN = 50

def log(msg):
    t = datetime.now().strftime('%H:%M:%S')
    print(f'[{t}] {msg}')

def load_existing():
    if DATA_FILE.exists():
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_data(data):
    os.makedirs(DATA_FILE.parent, exist_ok=True)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    log(f'保存 {len(data)} 句')

def fetch_from_tatoeba(limit=50):
    sentences = []
    url = f'https://api.tatoeba.org/unstable/sentences?lang=ara&sort=random&limit={limit}'
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'ArabicLearning/3.0 (macOS; educational)',
            'Accept': 'application/json'
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            for item in data.get('data', []):
                text = item.get('text', '').strip()
                if text and len(text) >= 6:
                    sentences.append({'ar': text, 'en': '', 'cn': ''})
    except Exception as e:
        log(f'Tatoeba 请求失败: {e}')
    return sentences

# ===== 分类 =====
def classify(ar, en, cn):
    text = (ar + ' ' + en + ' ' + cn).lower()
    rules = [
        ('greeting', ['السلام','مرحبا','أهلا','صباح','مساء','hello','hi','你好','问候','تحية','اهلا']),
        ('daily', ['يوم','صباح','أنام','أستيقظ','العمل','بيت','daily','day','日常','生活','早晨','睡觉']),
        ('food', ['اكل','طعام','قهوة','شاي','خبز','حليب','فاكهة','food','eat','coffee','吃','喝','美食','咖啡','茶']),
        ('travel', ['سفر','رحلة','مطار','طائرة','قطار','بلاد','travel','trip','旅行','旅游','飞机','机场','国家']),
        ('family', ['أسرة','عائلة','أب','أم','أخ','أخت','زوج','ولد','بنت','family','parents','家庭','家人','父母','兄弟','姐妹']),
        ('work', ['عمل','وظيفة','مهندس','طبيب','شركة','مكتب','work','job','公司','工作','职业','医生','工程师']),
        ('study', ['تعلم','لغة','درس','مدرسة','جامعة','كتاب','learn','study','language','学习','语言','学校','大学','书']),
        ('religion', ['الله','صلاة','رمضان','مسجد','قرآن','حج','دين','mosque','prayer','ramadan','真主','礼拜','清真寺','斋月','古兰经']),
        ('health', ['صحة','طبيب','مريض','تعب','رياضة','سباحة','health','doctor','健康','医生','病人','运动','游泳']),
        ('weather', ['طقس','جوي','مطر','شمس','ثلج','حر','برد','weather','rain','sunny','天气','雨','雪','热','冷']),
        ('shopping', ['سوق','شراء','سعر','متجر','تسوق','buy','shop','price','市场','购买','价格','商店','购物']),
        ('hobby', ['هواية','موسيقى','فيلم','كتاب','كرة','قراءة','hobby','music','movie','爱好','音乐','电影','阅读','球']),
    ]
    for cat, kws in rules:
        if any(kw in text for kw in kws):
            return cat
    return 'other'

KNOWN_CATS = {'greeting','daily','food','travel','family','work','study','religion','health','weather','shopping','hobby','other'}

def recategorize(data):
    """重新分类（合并模式）：以 categorized.json 为基底，保留自定义分类（如旅途 jordan_*），
    其余句子按规则分类。data.json 缺失的已有句子（如旅途句）不会被冲掉。"""
    base = {}
    if CAT_FILE.exists():
        try:
            for d in json.load(open(CAT_FILE, encoding='utf-8')):
                base[d.get('ar', '')] = d
        except Exception:
            base = {}
    for item in data:
        ar = item.get('ar', '')
        old = item.get('cat', '')
        if old and old not in KNOWN_CATS:
            base[ar] = item  # 自定义分类优先
        else:
            it = dict(item)
            it['cat'] = classify(item.get('ar', ''), item.get('en', ''), item.get('cn', ''))
            base[ar] = it
    merged = list(base.values())
    with open(CAT_FILE, 'w', encoding='utf-8') as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    log(f'分类完成: {len(merged)} 句')

# ===== 重建主页 =====
def rebuild_html(data):
    """重建主页：统一调用 build_home.py（内置数据+离线可用+API_BASE 修复）"""
    import subprocess, sys
    try:
        _out = str(DIR / 'dist' / 'index.html') if (DIR / 'dist' / 'index.html').exists() else str(DIR / 'arabic_learning.html')
        subprocess.run([sys.executable, str(DIR / 'build_home.py'), _out], cwd=str(DIR), check=True, timeout=120)
        log(f'主页已重建: {os.path.getsize(DIR / "arabic_learning.html") / 1024:.0f}KB')
    except Exception as e:
        log(f'主页重建失败: {e}')
    return
    # ===== 以下旧模板构建逻辑已废弃，不再执行 =====
    from collections import OrderedDict
    cats = OrderedDict()
    for item in data:
        c = item['cat']
        if c not in cats:
            cats[c] = []
        cats[c].append(item)

    cat_names = {
        'greeting': '👋 问候', 'daily': '🌅 日常', 'food': '🍽 饮食',
        'travel': '✈️ 旅行', 'family': '👨👩👧 家庭', 'work': '💼 工作',
        'study': '📚 学习', 'religion': '🕌 宗教', 'health': '🏥 健康',
        'weather': '🌤 天气', 'shopping': '🛍 购物', 'hobby': '🎨 爱好',
        'other': '📖 其他'
    }
    total_words = sum(len(item['ar'].split()) for item in data)

    cards_html = []
    for cat, items in cats.items():
        for item in items[:30]:
            ar = item['ar']
            en_safe = item['en'].replace("'", "\\'")
            cards_html.append(f'''<div class="c" data-cat="{cat}">
<div class="ar">{ar}</div>
<div class="tr"><div class="en">🇬🇧 {item['en']}</div><div class="cn">🇨🇳 {item['cn']}</div></div>
<div class="btns"><button onclick="ap(this,0,'{ar.replace(chr(39),chr(92)+chr(39))}')">🔊</button><button onclick="ap(this,1,'{en_safe}')">🇬🇧</button></div>
</div>''')
    all_cards = '\n'.join(cards_html)

    tabs = ['<button class="tab on" data-cat="all">🏠 全部</button>']
    for cat in cats:
        tabs.append(f'<button class="tab" data-cat="{cat}">{cat_names.get(cat, cat)}</button>')

    html = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>العربية | 阿拉伯语学习</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#f0ece6;color:#333;font-family:-apple-system,sans-serif;padding-bottom:70px}}
.hdr{{background:linear-gradient(160deg,#0b1926,#1a2744,#0d1b2a);padding:14px 10px;text-align:center}}
.hdr h1{{font-family:serif;font-size:20px;color:#e8d48b;font-weight:700}}
.hdr p{{font-size:9px;color:rgba(232,212,139,.5);margin-top:2px}}
.stats{{display:flex;background:#fff;border-bottom:1px solid #eee;padding:10px 0}}
.stats .s{{flex:1;text-align:center;border-right:1px solid #f0f0f0}}
.stats .s:last-child{{border-right:0}}
.stats .s .n{{font-size:17px;font-weight:700;color:#1a2744}}
.stats .s .l{{font-size:8px;color:#999;margin-top:1px}}
.cats{{display:flex;gap:3px;padding:6px;overflow-x:auto;background:#fff;border-bottom:1px solid #eee;white-space:nowrap;position:sticky;top:0;z-index:50}}
.cats::-webkit-scrollbar{{display:none}}
.tab{{padding:5px 11px;border:1px solid #ddd;border-radius:15px;background:#fff;color:#666;font-size:9px;cursor:pointer;white-space:nowrap;flex-shrink:0}}
.tab.on{{background:linear-gradient(135deg,#c9a84c,#b8860b);color:#fff;border-color:#b8860b;font-weight:600}}
.tt{{font-size:9px;color:#888;padding:6px 8px 2px}}
.wr{{padding:0 8px 10px}}
.c{{background:#fff;border-radius:7px;padding:7px 9px;margin-bottom:3px;border:1px solid #eee}}
.c .ar{{font-family:serif;font-size:14px;line-height:1.5;font-weight:700;text-align:right;direction:rtl;color:#1a2744}}
.c .tr{{font-size:9px;margin-top:2px;padding-top:2px;border-top:1px solid #eee}}
.c .tr .en{{color:#666;direction:ltr;text-align:left}}
.c .tr .cn{{color:#0f3460;direction:ltr;text-align:left;margin-top:1px}}
.c .btns{{display:flex;gap:2px;margin-top:3px;justify-content:flex-end}}
.c .btns button{{width:20px;height:20px;border-radius:50%;border:1px solid #eee;cursor:pointer;background:#fff;color:#999;font-size:7px;display:flex;align-items:center;justify-content:center}}
.c .btns .on{{background:#c9a84c;color:#fff}}
.elf{{position:fixed;bottom:12px;right:12px;z-index:9999}}
.elf-btn{{width:46px;height:46px;border-radius:50%;border:3px solid #e8d48b;background:linear-gradient(135deg,#1a2744,#0d1b2a);color:#e8d48b;font-size:20px;cursor:pointer;box-shadow:0 3px 14px rgba(0,0,0,.16);display:flex;align-items:center;justify-content:center;animation:bb 2s infinite}}
@keyframes bb{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-3px)}}}}
.elf-btn.h{{display:none}}
.elf-p{{position:fixed;bottom:64px;right:10px;width:320px;height:420px;background:#fff;border-radius:12px;box-shadow:0 6px 28px rgba(0,0,0,.1);display:none;flex-direction:column;overflow:hidden;z-index:9998}}
.elf-p.o{{display:flex}}
.elf-hd{{background:linear-gradient(135deg,#1a2744,#0d1b2a);color:#fff;padding:8px 10px;display:flex;align-items:center;gap:4px;font-size:11px;font-weight:600}}
.elf-hd .bd{{font-size:6px;background:rgba(201,168,76,.15);color:#e8d48b;padding:1px 4px;border-radius:2px}}
.elf-hd .cl{{margin-left:auto;background:0;border:0;color:rgba(255,255,255,.3);font-size:14px;cursor:pointer}}
.elf-m{{flex:1;overflow-y:auto;padding:8px;background:#f8f6f2;font-size:11px;line-height:1.5}}
.ef-msg{{margin-bottom:3px;max-width:90%;animation:f .2s}}
@keyframes f{{from{{opacity:0;transform:translateY(3px)}}to{{opacity:1;transform:translateY(0)}}}}
.ef-msg.bot{{text-align:right}}
.ef-msg.user{{text-align:left;margin-left:6%}}
.ef-msg .bb{{display:inline-block;padding:5px 8px;border-radius:7px;text-align:left;direction:ltr}}
.ef-msg.bot .bb{{background:#fff;border:1px solid #eee;border-bottom-right-radius:2px}}
.ef-msg.user .bb{{background:linear-gradient(135deg,#c9a84c,#b8860b);color:#fff;border-bottom-left-radius:2px}}
.ef-msg .ar{{font-family:serif;font-weight:700;font-size:11px;direction:rtl;text-align:right;display:block;line-height:1.5}}
.ef-msg .tr{{font-size:8px;color:#999;display:block;margin-top:1px}}
.ef-inp{{display:flex;gap:3px;padding:5px;border-top:1px solid #eee;background:#fff}}
.ef-inp input{{flex:1;padding:6px 8px;border:1px solid #ddd;border-radius:12px;font-size:10px;outline:0;text-align:right}}
.ef-inp button{{width:28px;height:28px;border-radius:50%;border:0;background:linear-gradient(135deg,#c9a84c,#b8860b);color:#fff;cursor:pointer;font-size:11px;display:flex;align-items:center;justify-content:center}}
</style>
</head>
<body>
<div class="hdr">
  <h1>📖 العربية</h1>
  <p>阿拉伯语学习 · 分类 · 翻译 · 朗读 · 每小时更新</p>
</div>
<div class="stats">
  <div class="s"><div class="n">{len(data)}</div><div class="l">句子</div></div>
  <div class="s"><div class="n">{total_words}</div><div class="l">单词</div></div>
  <div class="s"><div class="n">{len(cats)}</div><div class="l">分类</div></div>
</div>
<div class="cats">{''.join(tabs)}</div>
<div class="tt" id="tt">🏠 全部 · 每类显示30句</div>
<div class="wr" id="cx">
{all_cards}
</div>
<div class="elf">
  <div class="elf-p" id="ep">
    <div class="elf-hd"><span>🧞</span> AI小精灵 <span class="bd">DeepSeek</span><button class="cl" onclick="ec()">✕</button></div>
    <div class="elf-m" id="em"><div class="ef-msg bot"><div class="bb"><span class="ar">أَهْلًا بِكَ!</span><span class="tr">欢迎学习！问我任何问题 🧞</span></div></div></div>
    <div class="ef-inp"><input id="ei" placeholder="输入..." onkeydown="if(event.key==='Enter')es()"><button onclick="es()">➤</button></div>
  </div>
  <button class="elf-btn" id="eb" onclick="ec()">🧞</button>
</div>
<script>
var catName = ''' + json.dumps(cat_names, ensure_ascii=False) + ''';
document.querySelectorAll('.tab').forEach(function(tab){{
  tab.onclick = function(){{
    document.querySelectorAll('.tab').forEach(function(t){{t.className='tab';}});
    tab.className='tab on';
    var cat = tab.getAttribute('data-cat');
    var count = 0;
    document.querySelectorAll('.c').forEach(function(card){{
      var show = (cat==='all') || card.getAttribute('data-cat')===cat;
      card.style.display = show ? '' : 'none';
      if(show) count++;
    }});
    var name = cat==='all' ? '🏠 全部' : (catName[cat]||cat);
    document.getElementById('tt').textContent = name + ' · ' + count + '句';
  }};
}});
function ap(b,m,t){{if(!window.speechSynthesis)return;window.speechSynthesis.cancel();var u=new SpeechSynthesisUtterance(t);u.lang=m?'en-US':'ar-SA';u.rate=m?.85:.7;u.onstart=function(){{b.className='on';}};u.onend=function(){{b.className='';}};window.speechSynthesis.speak(u);}}
var SID='e_'+Date.now();
function ec(){{var p=document.getElementById('ep'),b=document.getElementById('eb');p.classList.toggle('o');b.classList.toggle('h');}}
function em(t,r){{var d=document.getElementById('em'),m=document.createElement('div');m.className='ef-msg '+(t?'user':'bot');
if(t){{m.innerHTML='<div class="bb">'+r.replace(/</g,'&lt;')+'</div>'}}else{{var pts=r.split('\\n');m.innerHTML='<div class="bb"><span class="ar">'+pts[0].replace(/</g,'&lt;')+'</span>'+(pts[1]?'<span class="tr">'+pts.slice(1).join('\\n').replace(/</g,'&lt;')+'</span>':'')+'</div>';}}
d.appendChild(m);d.scrollTop=d.scrollHeight;return m;}}
async function es(){{var i=document.getElementById('ei'),t=i.value.trim();if(!t)return;i.value='';em(1,t);
try{{var r=await fetch('/api/chat/message',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{message:t,session_id:SID}})}});var d=await r.json(),a=d.arabic||d,pts=(a||'').split('\\n');
var mb=em(0,a);var sp=mb.querySelector('.ar'),txt=pts[0]||'';sp.textContent='';
for(var i2=0;i2<txt.length;i2++){{sp.textContent+=txt[i2];await new Promise(r2=>setTimeout(r2,10));}}
if(pts[1]){{var tr=document.createElement('span');tr.className='tr';tr.textContent=pts.slice(1).join('\\n');mb.querySelector('.bb').appendChild(tr);}}
if(window.speechSynthesis){{var u=new SpeechSynthesisUtterance(txt);u.lang='ar-SA';u.rate=.7;window.speechSynthesis.speak(u);}}
}}catch(e){{em(0,'⚠️ AI暂不可用');}}}}
</script>
</body>
</html>'''

    with open(DIR / 'arabic_learning.html', 'w', encoding='utf-8') as f:
        f.write(html)
    log(f'主页已重建: {os.path.getsize(DIR / "arabic_learning.html") / 1024:.0f}KB')

def main():
    log('=' * 40)
    log('🕷 阿拉伯语爬虫 + 流水线启动')
    data = load_existing()
    log(f'当前词库: {len(data)} 句')

    new_sentences = fetch_from_tatoeba(FETCH_PER_RUN)
    log(f'Tatoeba 返回: {len(new_sentences)} 句')

    existing_ar = {d['ar'] for d in data}
    added = 0
    for s in new_sentences:
        if s['ar'] not in existing_ar:
            data.append(s)
            existing_ar.add(s['ar'])
            added += 1
    if added > 0:
        log(f'新增 {added} 句')

    if len(data) > MAX_SENTENCES:
        data = data[-MAX_SENTENCES:]
        log(f'裁剪至 {MAX_SENTENCES} 句')

    save_data(data)
    recategorize(data)
    # 自动补齐新句子翻译（限每轮 60 句；缺翻译少时跳过）
    try:
        import importlib.util
        if importlib.util.find_spec('translate_fix') is not None:
            import translate_fix as _tf
            missing = sum(1 for it in data if not it.get('en', '').strip() or not it.get('cn', '').strip())
            if missing >= 5:
                log(f'缺翻译 {missing} 句，自动补齐（限 60 句）...')
                _tf.fix_missing(limit=60, quiet=True)
            else:
                log('翻译完整，跳过补全')
        else:
            log('translate_fix 不可用，跳过补全')
    except Exception as e:
        log(f'翻译补全失败: {e}')
    rebuild_html(data)
    log('✅ 完成')

if __name__ == '__main__':
    main()
