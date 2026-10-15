#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成高级阿拉伯语学习主页"""
import json, sys
from collections import OrderedDict
from pathlib import Path

DIR = Path(__file__).parent
APP_VERSION = '4.1.0'   # 版本单一来源：网页页脚 / package.json / app.json 保持一致
with open(DIR / 'data' / 'categorized.json', encoding='utf-8') as f:
    data = json.load(f)

CAT_NAMES = {
    'greeting': ('👋', '问候', 'مرحبا'),
    'daily': ('🌅', '日常', 'يومي'),
    'food': ('🍽', '饮食', 'طعام'),
    'travel': ('✈️', '旅行', 'سفر'),
    'family': ('👨‍👩‍👧', '家庭', 'عائلة'),
    'work': ('💼', '工作', 'عمل'),
    'study': ('📚', '学习', 'دراسة'),
    'religion': ('🕌', '宗教', 'دين'),
    'health': ('🏥', '健康', 'صحة'),
    'weather': ('🌤', '天气', 'طقس'),
    'shopping': ('🛍', '购物', 'تسوق'),
    'hobby': ('🎨', '爱好', 'هواية'),
    'other': ('📖', '其他', 'أخرى'),
    'jordan_greet': ('✈️', '旅途问候', 'تحيات'),
    'jordan_airport': ('🛫', '机场交通', 'المطار'),
    'jordan_hotel': ('🏨', '住宿租房', 'السكن'),
    'jordan_food': ('🍽', '餐厅饮食', 'المطاعم'),
    'jordan_shop': ('🛍', '购物讲价', 'التسوق'),
    'jordan_dir': ('🧭', '问路方位', 'الاتجاهات'),
    'jordan_campus': ('🎓', '校园学习', 'الجامعة'),
    'jordan_emerg': ('🚨', '紧急情况', 'طوارئ'),
    'jordan_social': ('👥', '社交文化', 'تواصل'),
    'jordan_daily': ('☕', '日常表达', 'عبارات'),
}

cats = OrderedDict()
for item in data:
    c = item['cat']
    if c not in cats:
        cats[c] = []
    cats[c].append(item)

TOTAL_SENT = len(data)
TOTAL_WORDS = sum(len(i['ar'].split()) for i in data)
TOTAL_CATS = len(cats)

# ---------- 分类句子卡片（每类25句） ----------
cat_cards = {}
for cat, items in cats.items():
    cards = []
    for item in items[:25]:
        ar = item['ar']
        en_safe = item['en'].replace("'", "\\'")
        ar_safe = ar.replace("'", "\\'")
        cards.append(
            ('<div class="s-card" data-cat="%s">'
            '<div class="s-ar">%s</div>'
            '<div class="s-tr"><div class="s-en">🇬🇧 %s</div><div class="s-cn">🇨🇳 %s</div>' + (('%s' and '<div class="s-py">🗣 %s</div>' or '')) + '</div>'
            '<div class="s-btns">'
            '<button class="s-btn" onclick="ap(this,0,\'%s\')">🔊</button>'
            '<button class="s-btn" onclick="ap(this,1,\'%s\')">🇬🇧</button>'
            '<button class="s-btn" onclick="toggleFavWeb(\'%s\')" title="收藏">☆</button>'
            '<button class="s-btn" onclick="reviewSent(\'%s\')" title="加入间隔复习">📌</button>'
            '<button class="s-btn" onclick="explainSentence(\'%s\')" title="逐词拆解">✂️</button>'
            '<button class="s-btn" onclick="trCard(this)" title="AI 中译">中</button>'
            '</div></div>')
            % (cat, ar, item['en'], item['cn'], item.get('py',''), ar_safe, en_safe, ar_safe, ar_safe, ar_safe)
        )
    cat_cards[cat] = '\n'.join(cards)

ALL_CARDS = '\n'.join(cat_cards.values())

# ---------- 分类Tab ----------
tabs = ['<button class="cat-tab on" data-cat="all"><span class="ct-ic">🏛</span><span class="ct-nm">全部</span><span class="ct-ar">الكل</span></button>']
for cat, (icon, cn, ar) in CAT_NAMES.items():
    tabs.append(
        '<button class="cat-tab" data-cat="%s"><span class="ct-ic">%s</span><span class="ct-nm">%s</span><span class="ct-ar">%s</span></button>'
        % (cat, icon, cn, ar)
    )
TABS_HTML = '\n'.join(tabs)

# ---------- 每日文本/名言（按日期从混合池挑选） ----------
import datetime as _dt
ASSET_VERSION = APP_VERSION + '-' + _dt.datetime.now().strftime('%Y%m%d%H%M%S')
try:
    _quotes_pool = json.loads(open(DIR / 'data' / 'quotes.json', encoding='utf-8').read())
except Exception:
    _quotes_pool = []
DAILY_AR = ''
DAILY_CN = ''
DAILY_EN = ''
DAILY_SRC = ''
if _quotes_pool:
    _seed = int(_dt.date.today().strftime('%Y%m%d'))
    _dq = _quotes_pool[_seed % len(_quotes_pool)]
    DAILY_AR = _dq.get('a', '')
    DAILY_CN = _dq.get('z', '')
    DAILY_EN = _dq.get('e', '')
    DAILY_SRC = _dq.get('src', '')

CSS = '''
*{margin:0;padding:0;box-sizing:border-box;-webkit-tap-highlight-color:transparent}
:root{
  --green:#1a5c4a;--green-d:#0f3d31;--green-l:#2a7a63;
  --gold:#c9a84c;--gold-l:#e8d48b;--gold-d:#a8892e;
  --cream:#f7f3ec;--white:#ffffff;--ink:#1c2b26;
  --muted:#8a8f8c;--card:#fffdf8;--radius:18px;
  --shadow:0 8px 32px rgba(15,61,49,.08);
  --glass:rgba(255,255,255,.55);
}
html{scroll-behavior:smooth}
body{font-family:-apple-system,'PingFang SC','Helvetica Neue',sans-serif;background:var(--cream);color:var(--ink);padding-bottom:86px;overflow-x:hidden}

/* ===== 背景阿拉伯几何纹理 ===== */
.bg-pattern{position:fixed;inset:0;z-index:-1;pointer-events:none;opacity:.35;
  background:
    radial-gradient(ellipse 60% 40% at 15% 10%,rgba(201,168,76,.10),transparent 60%),
    radial-gradient(ellipse 50% 35% at 85% 20%,rgba(26,92,74,.08),transparent 60%),
    radial-gradient(ellipse 55% 40% at 50% 100%,rgba(201,168,76,.07),transparent 60%);
}
.bg-pattern::before{content:'';position:absolute;inset:0;opacity:.05;
  background-image:url("data:image/svg+xml,%3Csvg width='80' height='80' viewBox='0 0 80 80' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' stroke='%231a5c4a' stroke-width='1'%3E%3Cpath d='M40 5l35 35-35 35L5 40z'/%3E%3Cpath d='M40 20l20 20-20 20-20-20z'/%3E%3Ccircle cx='40' cy='40' r='8'/%3E%3C/g%3E%3C/svg%3E");
  background-size:80px 80px;
}

/* ===== 顶部 Header ===== */
.hdr{position:relative;padding:calc(26px + env(safe-area-inset-top, 0px)) 20px 34px;text-align:center;overflow:hidden;
  background:linear-gradient(165deg,#0e3529 0%,#14503e 45%,#0e3529 100%);
}
.hdr::before{content:'';position:absolute;inset:0;opacity:.14;
  background-image:url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' stroke='%23c9a84c' stroke-width='0.8'%3E%3Cpath d='M30 2l28 28-28 28L2 30z'/%3E%3Cpath d='M30 12l18 18-18 18-18-18z'/%3E%3C/g%3E%3C/svg%3E");
  background-size:60px 60px;
}
.hdr .glow{position:absolute;top:-60px;left:50%;transform:translateX(-50%);width:340px;height:180px;border-radius:50%;
  background:radial-gradient(ellipse,rgba(201,168,76,.35),transparent 70%);filter:blur(10px);animation:glowPulse 4s ease-in-out infinite}
@keyframes glowPulse{0%,100%{opacity:.5}50%{opacity:1}}
.hdr .arch-wrap{position:relative;display:inline-block;margin-bottom:6px}
.hdr .arch{width:58px;height:38px;border:2.5px solid rgba(232,212,139,.55);border-bottom:none;border-radius:29px 29px 0 0;margin:0 auto;position:relative}
.hdr .arch::before{content:'';position:absolute;top:-9px;left:50%;transform:translateX(-50%);width:12px;height:12px;border-radius:50%;background:rgba(232,212,139,.35)}
.hdr .arch::after{content:'☾';position:absolute;top:-20px;left:50%;transform:translateX(-50%);color:var(--gold-l);font-size:16px;text-shadow:0 0 12px rgba(232,212,139,.6)}
.hdr .logo{font-family:AmiriNur,SF Arabic,Geeza Pro,serif;font-size:30px;font-weight:700;color:var(--gold-l);letter-spacing:1px;text-shadow:0 2px 18px rgba(0,0,0,.35),0 0 30px rgba(201,168,76,.25)}
.hdr .logo-sub{font-size:12px;color:rgba(247,243,236,.75);margin-top:2px;letter-spacing:3px}
.hdr .zh{display:block;font-size:11px;color:rgba(232,212,139,.85);margin-top:8px;letter-spacing:2px}

/* ===== 今日学习模块 ===== */
.daily-mod{max-width:640px;margin:16px auto 0;padding:0 16px}
.daily-card{position:relative;background:var(--glass);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);
  border:1px solid rgba(201,168,76,.28);border-radius:22px;padding:18px;box-shadow:var(--shadow);overflow:hidden}
.daily-card::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,var(--gold),var(--gold-l),var(--gold))}
.daily-head{display:flex;align-items:center;gap:16px}
.ring{position:relative;width:84px;height:84px;flex-shrink:0}
.ring svg{transform:rotate(-90deg)}
.ring .ring-bg{stroke:rgba(201,168,76,.15);fill:none;stroke-width:7}
.ring .ring-fg{stroke:url(#goldGrad);fill:none;stroke-width:7;stroke-linecap:round;stroke-dasharray:220;stroke-dashoffset:176;animation:ringFill 1.6s ease forwards}
@keyframes ringFill{from{stroke-dashoffset:220}to{stroke-dashoffset:176}}
.ring .ring-txt{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center}
.ring .ring-txt b{font-size:15px;color:var(--green-d)}
.ring .ring-txt span{font-size:10.5px;color:var(--muted)}
.daily-info{flex:1}
.daily-info .d-row{display:flex;align-items:center;gap:6px;margin-bottom:7px;font-size:12.5px}
.daily-info .d-row .lb{color:var(--muted);flex-shrink:0}
.daily-info .d-row b{color:var(--green-d)}
.daily-goal{margin-top:10px;padding-top:10px;border-top:1px dashed rgba(201,168,76,.35)}
.daily-goal .g-head{display:flex;justify-content:space-between;font-size:11px;color:var(--muted);margin-bottom:6px}
.daily-goal .g-bar{height:7px;border-radius:4px;background:rgba(201,168,76,.15);overflow:hidden}
.daily-goal .g-bar i{display:block;height:100%;width:35%;border-radius:4px;background:linear-gradient(90deg,var(--gold),var(--gold-l));animation:grow 1.4s ease forwards}
@keyframes grow{from{width:0}}

/* ===== 数据卡片 ===== */
.stat-row{display:flex;gap:10px;max-width:640px;margin:14px auto 0;padding:0 16px}
.stat-card{flex:1;position:relative;background:var(--glass);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);
  border:1px solid rgba(201,168,76,.22);border-radius:16px;padding:14px 10px;text-align:center;cursor:pointer;
  box-shadow:0 4px 18px rgba(15,61,49,.06);transition:transform .2s ease;animation:fadeUp .5s ease both}
.stat-card:hover{transform:translateY(-2px)}
.stat-card:active{transform:scale(.96)}
@keyframes fadeUp{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
.stat-card .ic{width:38px;height:38px;line-height:38px;border-radius:12px;margin:0 auto 6px;font-size:19px;
  background:linear-gradient(135deg,rgba(201,168,76,.16),rgba(201,168,76,.05));border:1px solid rgba(201,168,76,.22)}
.stat-card .num{font-size:24px;font-weight:800;color:var(--green-d);letter-spacing:-.5px}
.stat-card .lb{font-size:10px;color:var(--muted);margin-top:2px}

/* ===== 功能入口 ===== */
.entr-row{max-width:640px;margin:14px auto 0;padding:0 16px;display:grid;grid-template-columns:1fr 1fr;gap:10px}
.entr{position:relative;display:flex;flex-direction:column;align-items:center;gap:6px;background:var(--white);border-radius:18px;padding:16px 10px 14px;
  border:1px solid rgba(201,168,76,.18);box-shadow:0 6px 22px rgba(15,61,49,.06);cursor:pointer;transition:transform .18s ease,box-shadow .18s ease;overflow:hidden;text-align:center}
.entr:hover{transform:translateY(-3px);box-shadow:0 12px 30px rgba(15,61,49,.12)}
.entr:active{transform:scale(.96)}
.entr::before{content:'';position:absolute;top:-24px;right:-24px;width:64px;height:64px;border-radius:50%;background:radial-gradient(circle,rgba(201,168,76,.12),transparent 70%)}
.entr .e-ic{width:52px;height:52px;border-radius:16px;display:flex;align-items:center;justify-content:center;font-size:24px;flex-shrink:0;
  background:linear-gradient(135deg,rgba(201,168,76,.18),rgba(26,92,74,.06));border:1px solid rgba(201,168,76,.25);box-shadow:0 4px 12px rgba(201,168,76,.15);margin-bottom:2px}
.entr .e-tx b{display:block;font-size:13px;color:var(--ink)}
.entr .e-tx span{display:block;font-size:9.5px;color:var(--muted);margin-top:2px;line-height:1.4}
.entr .e-go{display:none}

/* ===== 功能按钮 ===== */
.action-row{max-width:640px;margin:12px auto 0;padding:0 16px;display:grid;grid-template-columns:repeat(auto-fill,minmax(92px,1fr));gap:8px}
.act-btn{padding:11px 6px;border-radius:14px;border:1px solid rgba(201,168,76,.35);background:linear-gradient(135deg,#1a5c4a,#0f3d31);color:var(--gold-l);font-size:12px;font-weight:700;cursor:pointer;text-align:center;line-height:1.35;min-height:44px;transition:transform .15s,box-shadow .2s}
.act-btn:active{transform:scale(.95)}
.flash-card{min-height:260px;border-radius:22px;cursor:pointer;display:flex;align-items:center;justify-content:center;padding:26px;box-shadow:0 8px 24px rgba(15,61,49,.12)}
.flash-front{background:linear-gradient(150deg,#14503e,#0e3529);border-radius:22px;width:100%;min-height:260px;display:flex;align-items:center;justify-content:center;flex-direction:column;position:relative}
.flash-back{background:#fff;border:2px solid #c9a84c;border-radius:22px;width:100%;min-height:260px;display:flex;align-items:center;justify-content:center;flex-direction:column;position:relative}
.flash-ar{font-family:AmiriNur,SF Arabic,Geeza Pro,serif;font-size:23px;font-weight:800;color:#e8d48b;direction:rtl;text-align:center;line-height:1.9;padding:0 12px}
.flash-cn{font-size:16px;color:#333;text-align:center;line-height:1.9;padding:0 12px}
.flash-en{font-size:12px;color:#5a7f9e;text-align:center;margin-top:10px;padding:0 12px}
.flash-hint{position:absolute;bottom:14px;font-size:10px;color:rgba(255,255,255,.5)}
.quiz-opt{display:block;width:100%;padding:13px 16px;margin-bottom:10px;border:1.5px solid rgba(201,168,76,.4);border-radius:12px;background:#fff;font-size:13.5px;color:#333;cursor:pointer;text-align:center;transition:all .2s}
.quiz-opt:hover{border-color:#0f3d31;background:rgba(15,61,49,.04)}
.decomp-box{display:none;background:rgba(247,243,236,.7);border:1px dashed rgba(201,168,76,.4);border-radius:12px;padding:12px;margin-top:10px}
/* ===== 模态框 ===== */
.modal{position:fixed;inset:0;background:rgba(13,27,42,.7);z-index:2000;display:none;flex-direction:column}
.modal.show{display:flex}
.modal .m-head{background:linear-gradient(135deg,#0f3d31,#1a5c4a);color:var(--gold-l);padding:12px 16px;display:flex;align-items:center;gap:8px}
.modal .m-head b{font-size:13px}
.modal .m-close{margin-left:auto;background:none;border:0;color:rgba(255,255,255,.6);font-size:20px;cursor:pointer}
.modal .m-search{padding:8px 12px;background:#fff}
.modal .m-search input{width:100%;padding:8px 12px;border:1px solid #ddd;border-radius:8px;font-size:12px;text-align:right}
.modal .m-body{flex:1;overflow-y:auto;background:var(--cream);padding:10px 12px}
.v-item{background:#fff;border:1px solid rgba(201,168,76,.15);border-radius:10px;padding:10px 12px;margin-bottom:6px;display:flex;align-items:center;gap:10px}
.v-item .v-ar{font-family:AmiriNur,SF Arabic,Geeza Pro,serif;font-size:15px;font-weight:700;color:var(--green-d);flex:1;text-align:right;direction:rtl}
.v-item .v-f{font-size:10px;color:var(--muted);background:rgba(201,168,76,.1);padding:2px 8px;border-radius:8px}
.s-read{border-color:rgba(26,138,92,.5);background:rgba(26,138,92,.05)}
.s-item{background:#fff;border:1px solid rgba(201,168,76,.12);border-radius:10px;padding:10px 12px;margin-bottom:6px}
.s-item .s-ar{font-family:AmiriNur,SF Arabic,Geeza Pro,serif;font-size:15px;font-weight:700;color:var(--green-d);text-align:right;direction:rtl}
.s-item .s-tr{font-size:10px;color:var(--muted);margin-top:4px}
.m-count{padding:8px 12px;background:#fff;font-size:11px;color:var(--muted);border-top:1px solid #eee;text-align:center}
/* ===== 分类导航 ===== */
.sec-title{max-width:640px;margin:22px auto 0;padding:0 16px;display:flex;align-items:center;gap:8px}
.sec-title h2{font-size:15px;color:var(--green-d)}
.sec-title::after{content:'';flex:1;height:1px;background:linear-gradient(90deg,rgba(201,168,76,.4),transparent)}
.cat-scroll{max-width:640px;margin:10px auto 0;padding:0 12px;display:flex;gap:8px;overflow-x:auto;scrollbar-width:none}
.cat-scroll::-webkit-scrollbar{display:none}
.cat-tab{flex-shrink:0;display:flex;flex-direction:column;align-items:center;gap:2px;padding:10px 12px;border-radius:16px;border:1px solid rgba(201,168,76,.2);
  background:var(--white);cursor:pointer;transition:all .2s ease;min-width:74px}
.cat-tab .ct-ic{font-size:19px}
.cat-tab .ct-nm{font-size:10px;color:var(--ink);font-weight:600;margin-top:1px}
.cat-tab .ct-ar{font-size:10.5px;color:var(--muted)}
.cat-tab.on{background:linear-gradient(135deg,var(--green-d),var(--green));border-color:rgba(201,168,76,.5);box-shadow:0 6px 20px rgba(15,61,49,.25);animation:ripple .5s ease}
.cat-tab.on .ct-nm{color:#fff}
.cat-tab.on .ct-ar{color:rgba(255,255,255,.65)}
@keyframes ripple{0%{transform:scale(1)}40%{transform:scale(.94)}100%{transform:scale(1)}}

/* ===== 句子列表 ===== */
.list-wrap{max-width:640px;margin:12px auto 0;padding:0 16px}
.list-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px}
.list-head .tt{font-size:12px;color:var(--muted)}
.s-card{background:var(--white);border:1px solid rgba(201,168,76,.12);border-radius:14px;padding:12px 14px;margin-bottom:8px;
  content-visibility:auto;contain-intrinsic-size:auto 112px;
  box-shadow:0 2px 10px rgba(15,61,49,.04);animation:fadeUp .4s ease both}
@keyframes fadeUp{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
.s-card .s-ar{font-family:AmiriNur,SF Arabic,Geeza Pro,serif;font-size:16px;font-weight:700;text-align:right;direction:rtl;color:var(--green-d);line-height:1.7}
.s-card .s-tr{margin-top:6px;padding-top:6px;border-top:1px dashed rgba(201,168,76,.25)}
.s-card .s-en{font-size:10.5px;color:#6b7270;direction:ltr;text-align:left}
.s-card .s-cn{font-size:10.5px;color:var(--green);direction:ltr;text-align:left;margin-top:2px}
.s-card .s-py{font-size:9.5px;color:#8a8578;font-style:italic;margin-top:2px}
.s-card .s-btns{display:flex;gap:6px;margin-top:8px;justify-content:flex-end}
.s-btn{width:30px;height:30px;border-radius:50%;border:1px solid rgba(201,168,76,.3);background:#fff;color:var(--muted);font-size:11px;
  cursor:pointer;display:flex;align-items:center;justify-content:center;transition:all .15s}
.s-btn:hover{background:var(--gold-l);border-color:var(--gold);color:var(--green-d)}
.s-btn.on{background:var(--gold);color:#fff;border-color:var(--gold-d)}

/* ===== 每日一句 ===== */
.daily-quote{max-width:640px;margin:16px auto 0;padding:0 16px}
.quote-card{background:linear-gradient(150deg,#14503e,#0e3529);border-radius:16px;padding:12px 16px;text-align:center;position:relative;overflow:hidden;color:#fff}
.quote-card::before{content:'❝';position:absolute;top:0;left:10px;font-size:40px;color:rgba(232,212,139,.16);font-family:AmiriNur,SF Arabic,Geeza Pro,serif}
.quote-card::after{content:'❞';position:absolute;bottom:-6px;right:10px;font-size:40px;color:rgba(232,212,139,.16);font-family:AmiriNur,SF Arabic,Geeza Pro,serif}
.quote-card .q-ar{font-family:AmiriNur,SF Arabic,Geeza Pro,serif;font-size:15px;font-weight:700;direction:rtl;color:var(--gold-l);line-height:1.7;position:relative;z-index:1}
.quote-card .q-cn{font-size:10.5px;color:rgba(255,255,255,.8);margin-top:4px;position:relative;z-index:1}
.quote-card .q-src{font-size:10.5px;color:rgba(232,212,139,.72);margin-top:3px;position:relative;z-index:1;letter-spacing:.5px}
.quote-card{cursor:pointer;transition:transform .15s}
.quote-card:active{transform:scale(.985)}
.quote-card .q-switch{position:absolute;bottom:8px;right:14px;font-size:10.5px;color:rgba(232,212,139,.62);z-index:1;letter-spacing:.5px}
.quote-card .q-en{font-size:10px;color:rgba(232,212,139,.7);margin-top:4px;position:relative;z-index:1}

/* ===== AI 小精灵 ===== */
.elf{position:fixed;bottom:92px;right:14px;z-index:999;animation:elfFloat 3.2s ease-in-out infinite}
@keyframes elfFloat{0%,100%{transform:translateY(0)}50%{transform:translateY(-7px)}}
.elf-btn{width:58px;height:58px;border-radius:50%;border:2.5px solid var(--gold-l);
  background:radial-gradient(circle at 32% 28%,#2a7a63,#0f3d31);color:#fff;font-size:26px;cursor:pointer;
  box-shadow:0 8px 28px rgba(15,61,49,.35),0 0 0 6px rgba(201,168,76,.12);display:flex;align-items:center;justify-content:center;position:relative}
.elf-btn::after{content:'';position:absolute;inset:-7px;border-radius:50%;border:1.5px solid rgba(201,168,76,.35);animation:ringPulse 2.4s ease infinite}
@keyframes ringPulse{0%{transform:scale(.92);opacity:.9}70%{transform:scale(1.12);opacity:0}100%{opacity:0}}
.elf-btn.h{display:none}
.elf-panel{position:fixed;bottom:158px;right:12px;width:330px;height:440px;background:var(--white);border-radius:20px;
  box-shadow:0 12px 48px rgba(15,61,49,.18);display:none;flex-direction:column;overflow:hidden;z-index:998;border:1px solid rgba(201,168,76,.2)}
.elf-panel.o{display:flex;animation:panelIn .28s ease}
@keyframes panelIn{from{opacity:0;transform:translateY(14px) scale(.97)}to{opacity:1;transform:translateY(0) scale(1)}}
.elf-hd{background:linear-gradient(135deg,var(--green-d),var(--green));color:#fff;padding:13px 15px;display:flex;align-items:center;gap:8px}
.elf-hd b{font-size:13px}
.elf-hd .bd{font-size:8px;background:rgba(232,212,139,.22);color:var(--gold-l);padding:2px 7px;border-radius:10px}
.elf-hd .cl{margin-left:auto;background:none;border:0;color:rgba(255,255,255,.5);font-size:17px;cursor:pointer}
.elf-body{flex:1;overflow-y:auto;padding:11px;background:#f9f7f2;font-size:12px;line-height:1.55}
.ef-msg{margin-bottom:6px;max-width:90%;animation:fadeUp .25s ease both}
.ef-msg.bot{text-align:right}
.ef-msg.user{text-align:left;margin-left:7%}
.ef-msg .bb{display:inline-block;padding:8px 11px;border-radius:13px;text-align:left;direction:ltr}
.ef-msg.bot .bb{background:#fff;border:1px solid #eee;border-bottom-right-radius:4px;box-shadow:0 2px 6px rgba(0,0,0,.03)}
.ef-msg.user .bb{background:linear-gradient(135deg,var(--gold),var(--gold-d));color:#fff;border-bottom-left-radius:4px}
.ef-msg .ar{font-family:AmiriNur,SF Arabic,Geeza Pro,serif;font-weight:700;font-size:12.5px;direction:rtl;text-align:right;display:block;line-height:1.6}
.ef-msg .tr{font-size:9.5px;color:var(--muted);display:block;margin-top:2px}
.cp-btn{display:block;margin-top:5px;font-size:10px;color:#0f3d31;background:rgba(201,168,76,.15);border:1px solid rgba(201,168,76,.35);border-radius:8px;padding:3px 10px;cursor:pointer}
.cp-btn:hover{background:rgba(201,168,76,.3)}
.ef-inp{display:flex;gap:5px;padding:8px;border-top:1px solid #eee;background:#fff}
.ef-inp input{flex:1;padding:8px 12px;border:1px solid #ddd;border-radius:18px;font-size:11px;outline:0;text-align:right}
.ef-inp input:focus{border-color:var(--gold)}
.ef-inp button{width:34px;height:34px;border-radius:50%;border:0;background:linear-gradient(135deg,var(--gold),var(--gold-d));color:#fff;cursor:pointer;font-size:13px;display:flex;align-items:center;justify-content:center}

/* ===== 底部导航 ===== */
.tabbar{position:fixed;bottom:0;left:0;right:0;z-index:1000;background:rgba(255,255,255,.88);backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px);
  border-top:1px solid rgba(201,168,76,.15);display:flex;padding:8px 6px calc(8px + env(safe-area-inset-bottom))}
.tabbar .tb{flex:1;display:flex;flex-direction:column;align-items:center;gap:2px;padding:5px 0;border:0;background:none;cursor:pointer;color:var(--muted);transition:color .2s}
.tabbar .tb .t-ic{font-size:20px;transition:transform .2s}
.tabbar .tb .t-nm{font-size:11px;line-height:1.2}
.tabbar .tb.on{color:var(--green-d)}
.tabbar .tb.on .t-ic{transform:translateY(-2px);filter:drop-shadow(0 2px 6px rgba(201,168,76,.5))}
.tabbar .tb.on .t-nm{color:var(--gold-d);font-weight:600}

/* ===== 隐藏区 ===== */
.hidden-sec{display:none}

@media(max-width:380px){.stat-card .num{font-size:20px}.entr .e-ic{width:42px;height:42px}}

/* ===== 移动端适配 ===== */
@media (max-width: 480px){
  body{font-size:13px}
  .s-ar{font-size:15px;line-height:1.65}
  .s-card{padding:11px 12px}
  .daily-card{padding:14px}
  .stat-card .num{font-size:19px}
  .cat-tab{padding:7px 9px;min-width:62px}
  .modal{width:100%;height:100%;border-radius:0}
  .tabbar{height:52px}
  .tabbar .tb{font-size:11px}
  .elf-btn{width:50px;height:50px;bottom:66px;right:12px}
  .action-row{gap:7px;grid-template-columns:repeat(auto-fill,minmax(84px,1fr))}
  .act-btn{padding:10px 6px;font-size:12px;line-height:1.3}
  .flash-ar{font-size:20px}
  .flash-front,.flash-back{min-height:220px}
  .v-item .v-ar{font-size:15px}
}
/* ===== 首页视觉升级 ===== */
body{background:
  radial-gradient(ellipse 80% 50% at 50% -5%, rgba(201,168,76,.14), transparent 70%),
  radial-gradient(ellipse 60% 40% at 90% 20%, rgba(15,61,49,.05), transparent 70%),
  linear-gradient(180deg,#faf7f0 0%,#f4efe6 100%)}
.header{position:relative;overflow:hidden}
.header::before{content:'';position:absolute;top:-60px;left:50%;transform:translateX(-50%);width:480px;height:200px;background:radial-gradient(ellipse,rgba(232,212,139,.28),transparent 70%);pointer-events:none}
.hdr .logo{background:linear-gradient(120deg,#f5e3a8,#d4af4e 55%,#f0dd9a);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;text-shadow:none;font-size:34px}
.hdr .logo-sub{letter-spacing:3px}
.daily-card{background:linear-gradient(150deg,#15513f 0%,#0f3d31 55%,#0a2b22 100%);border:1px solid rgba(201,168,76,.3)}
.daily-card .d-row b{color:rgba(255,255,255,.92)}
.daily-card .d-row span{opacity:.85}
.entr-row{display:grid;grid-template-columns:1fr 1fr;gap:8px;max-width:640px}
.entr{flex-direction:column;text-align:center;gap:5px;padding:10px 8px;border-radius:14px;border:1px solid rgba(201,168,76,.22);background:linear-gradient(160deg,#ffffff,#fbf7ee);box-shadow:0 4px 12px rgba(15,61,49,.05);transition:transform .18s,box-shadow .18s}
.entr:hover{transform:translateY(-2px);box-shadow:0 8px 20px rgba(15,61,49,.1)}
.entr .e-ic{width:38px;height:38px;border-radius:12px;font-size:18px;background:linear-gradient(135deg,rgba(201,168,76,.16),rgba(201,168,76,.06));border:1px solid rgba(201,168,76,.25);margin:0 auto}
.entr .e-tx b{font-size:11.5px}
.entr .e-tx span{font-size:10.5px}
.entr::after{display:none}
.entr .e-go{display:none}
.stat-card{background:linear-gradient(160deg,#ffffff,#f9f5ec);border:1px solid rgba(201,168,76,.25);box-shadow:0 6px 18px rgba(15,61,49,.07)}
.stat-card .ic{width:38px;height:38px;line-height:38px;border-radius:12px;background:rgba(201,168,76,.12);font-size:18px;margin:0 auto 6px}
.quote-card{position:relative}
.quote-card::after{content:'';position:absolute;bottom:-1px;left:0;right:0;height:2px;background:linear-gradient(90deg,transparent,var(--gold),transparent)}
.section h3{position:relative;padding-left:0;text-align:center}
.section h3::after{content:'';position:absolute;bottom:-5px;left:50%;transform:translateX(-50%);width:44px;height:2px;border-radius:2px;background:linear-gradient(90deg,var(--gold),var(--gold-l))}
.cat-row{max-width:640px;margin:0 auto}
/* ===== 阿拉伯语排版优化 ===== */
.ar-font, .quran-ayah, .book-para, .s-ar, .flash-ar, .v-item .v-ar, .quote-card .q-ar, .ef-msg .ar{
  font-family:'AmiriNur','Noto Naskh Arabic','Amiri','Scheherazade New','Geeza Pro',serif;
  font-feature-settings:'liga';
}
.book-para{font-size:19px;line-height:2.2;margin:0 0 14px;text-align:right;direction:rtl;color:#e8d48b;font-weight:400}
.book-para-cn{font-size:14px;line-height:2;margin:0 0 12px;color:#333;text-align:justify}
.quran-ayah{font-size:17px;line-height:2.15;letter-spacing:.3px}
/* ===== 视觉打磨 ===== */
body{-webkit-font-smoothing:antialiased}
::-webkit-scrollbar{width:5px;height:5px}
::-webkit-scrollbar-thumb{background:rgba(201,168,76,.35);border-radius:3px}
::-webkit-scrollbar-track{background:transparent}
.ps-banner{max-width:640px;margin:14px auto 0;padding:0 16px}
.ps-banner-in{display:flex;align-items:center;justify-content:center;gap:8px;border-radius:14px;padding:9px 12px;font-size:12px;font-weight:800;color:#fff;letter-spacing:.5px;background:linear-gradient(90deg,#000 0 33%,#009736 33% 66%,#ce1126 66% 100%);box-shadow:0 4px 14px rgba(0,0,0,.18);position:relative;overflow:hidden}
.ps-banner-in::after{content:'';position:absolute;top:0;bottom:0;left:33%;width:1px;background:rgba(255,255,255,.4)}
.ps-banner-in::before{content:'';position:absolute;top:0;bottom:0;left:66%;width:1px;background:rgba(255,255,255,.4)}
.ps-banner .ps-flag{font-size:15px;text-shadow:0 1px 4px rgba(0,0,0,.4)}
.ps-ai{max-width:640px;margin:12px auto 0;padding:0 16px}
.ps-ai-card{background:linear-gradient(160deg,#0d5a33,#062e1d);border:2px solid rgba(255,255,255,.14);border-radius:20px;overflow:hidden;box-shadow:0 12px 34px rgba(0,0,0,.28);position:relative}
.ps-ai-card::before{content:'';position:absolute;inset:0;background:repeating-linear-gradient(45deg,rgba(255,255,255,.025) 0 9px,transparent 9px 18px);pointer-events:none;z-index:0}
.ps-ai-head{display:flex;align-items:center;justify-content:space-between;padding:12px 16px;background:linear-gradient(90deg,#009736,#0a7a2c);color:#fff;font-weight:800;font-size:14px;position:relative;z-index:1}
.ps-ai-head .ps-en{font-size:10.5px;opacity:.85;font-weight:600}
.ps-ai-msgs{height:190px;overflow-y:auto;padding:12px;background:rgba(255,255,255,.05);position:relative;z-index:1}
.ps-ai-msg{font-size:12.5px;line-height:1.7;padding:8px 12px;border-radius:12px;margin-bottom:8px;max-width:92%;white-space:pre-wrap;word-break:break-word}
.ps-ai-msg.bot{background:rgba(255,255,255,.12);color:#f2f7f0;border-bottom-left-radius:4px}
.ps-ai-msg.user{background:linear-gradient(135deg,#ce1126,#a30d1d);color:#fff;margin-left:auto;border-bottom-right-radius:4px;font-weight:600}
.ps-ai-chips{display:flex;flex-wrap:wrap;gap:6px;padding:10px 12px;position:relative;z-index:1;background:rgba(0,0,0,.18)}
.ps-ai-chips button{font-size:10.5px;font-weight:700;color:#eafff1;background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.28);border-radius:20px;padding:5px 12px;cursor:pointer}
.ps-ai-chips button:hover{background:rgba(255,255,255,.24)}
.ps-ai-input{display:flex;gap:8px;padding:12px;background:rgba(0,0,0,.3);position:relative;z-index:1}
.ps-ai-input input{flex:1;background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.25);border-radius:10px;padding:9px 12px;color:#fff;font-size:13px;outline:none}
.ps-ai-input input::placeholder{color:rgba(255,255,255,.5)}
.ps-ai-input button{background:linear-gradient(135deg,#ce1126,#9d0d1c);color:#fff;border:none;border-radius:10px;padding:0 20px;font-size:13px;font-weight:800;cursor:pointer}
.ps-ai-input button:hover{filter:brightness(1.1)}
.ps-ai-avatar{width:34px;height:34px;border-radius:50%;background-image:url(data:image/jpeg;base64,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);background-size:cover;background-position:center;border:2px solid #fff;display:flex;align-items:center;justify-content:center;font-size:20px;box-shadow:0 2px 8px rgba(0,0,0,.3);flex-shrink:0}
.ps-ai-head .ps-ai-head-l span{font-family:'PingFang SC',system-ui;letter-spacing:.2px}
.ps-ai-msg.bot{position:relative}
.ps-ai-msg.bot::before{content:'';position:absolute;left:-38px;top:0;width:28px;height:28px;border-radius:50%;
  background-image:url(data:image/jpeg;base64,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);background-size:cover;border:2px solid rgba(255,255,255,.6)}
@media(max-width:480px){.ps-ai-msg.bot::before{display:none}}
.ps-ai-head-l{display:flex;align-items:center;gap:9px}
.ps-mic{width:40px;height:40px;border-radius:50%;background:linear-gradient(135deg,#009736,#0a7a2c);color:#fff;border:2px solid rgba(255,255,255,.35);font-size:17px;cursor:pointer;flex-shrink:0;transition:transform .15s}
.ps-mic:hover{transform:scale(1.08)}
.ps-mic:active{transform:scale(.92)}
.ps-copy{display:block;margin-top:6px;font-size:10px;color:#d9f2e0;background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.3);border-radius:8px;padding:3px 10px;cursor:pointer}
.ps-copy:hover{background:rgba(255,255,255,.26)}
.s-card{transition:transform .15s}
.s-card{transition:transform .15s}
.s-card:active{transform:scale(.985)}
.act-btn{box-shadow:0 2px 6px rgba(15,61,49,.15)}
.s-item{transition:transform .12s}
.s-item:active{transform:scale(.99)}
.modal{box-shadow:0 10px 40px rgba(15,61,49,.25)}

/* ===== v2.7.1 体验打磨：安全区 / 触控热区 / 无障碍 / 滚动 ===== */
body{font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',system-ui,sans-serif;
  -webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale;overscroll-behavior-y:none;
  padding-bottom:calc(86px + env(safe-area-inset-bottom,0px))}
.tabbar{padding-bottom:env(safe-area-inset-bottom,0);box-shadow:0 -6px 24px rgba(15,61,49,.08)}
.tabbar .tb{min-height:44px}
.s-btn{width:34px;height:34px;font-size:12.5px}
.act-btn{min-height:38px}
button:focus-visible,a:focus-visible,input:focus-visible,textarea:focus-visible{outline:2px solid rgba(201,168,76,.9);outline-offset:2px;border-radius:10px}
::selection{background:rgba(201,168,76,.35);color:#0f3d31}
::-webkit-scrollbar{width:9px;height:9px}
::-webkit-scrollbar-track{background:transparent}
::-webkit-scrollbar-thumb{background:rgba(201,168,76,.4);border-radius:6px;border:2px solid transparent;background-clip:content-box}
::-webkit-scrollbar-thumb:hover{background:rgba(201,168,76,.65);background-clip:content-box}
@media(hover:hover){.s-card:hover{transform:translateY(-2px);box-shadow:0 8px 22px rgba(15,61,49,.10)}}
@media(prefers-reduced-motion:reduce){*{animation-duration:.001ms!important;animation-iteration-count:1!important;transition-duration:.001ms!important;scroll-behavior:auto!important}}

/* ===== v2.8 设计升级：字体层级 / 质感 / 动效 ===== */
:root{
  --ar-font:'AmiriNur','SF Arabic','Geeza Pro',serif;
  --sh-1:0 2px 10px rgba(15,61,49,.06);
  --sh-2:0 10px 30px rgba(15,61,49,.12);
  --line:rgba(201,168,76,.22);
}
.s-ar,.q-ar,.logo,.ct-ar{font-family:var(--ar-font)}
.s-card .s-ar{font-size:18px;line-height:2}
.quote-card .q-ar{font-size:22px;line-height:2.15}
@media(max-width:480px){.s-card .s-ar{font-size:16px;line-height:1.95}.quote-card .q-ar{font-size:19px}}
.logo{font-size:32px}
.daily-card,.quote-card,.s-card,.s-item,.v-item,.stat-card{box-shadow:var(--sh-1)}
.modal.show{animation:modalIn .26s cubic-bezier(.2,.8,.2,1)}
@keyframes modalIn{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:none}}
.act-btn{transition:transform .14s,box-shadow .22s,filter .2s}
.act-btn:active{transform:scale(.97)}
.entr{transition:transform .18s,box-shadow .22s}
input:focus,textarea:focus{border-color:rgba(201,168,76,.8)!important;box-shadow:0 0 0 3px rgba(201,168,76,.15)}
@media(hover:hover){
  .act-btn:hover{filter:brightness(1.05);box-shadow:var(--sh-2)}
  .entr:hover{transform:translateY(-2px)}
}
@media(min-width:820px){
  .modal.show{align-items:center}
  .modal.show .m-head,.modal.show .m-body{width:min(820px,94vw);margin:0 auto}
  .modal.show .m-head{border-radius:18px 18px 0 0}
  .modal.show .m-body{max-height:74vh;border-radius:0 0 18px 18px}
}
'''


# ===== 内嵌阿拉伯字体（Amiri / OFL 授权，离线可用）=====
def _font_face_css():
    import base64 as _b64
    out = []
    for fn, wt in (('amiri-400.woff2', '400'), ('amiri-700.woff2', '700')):
        fp = DIR / 'assets' / 'fonts' / fn
        if fp.exists():
            b64 = _b64.b64encode(fp.read_bytes()).decode('ascii')
            out.append("@font-face{font-family:'AmiriNur';font-style:normal;font-weight:%s;font-display:swap;src:url(data:font/woff2;base64,%s) format('woff2')}" % (wt, b64))
    # 从本机 App 里取的精华字体（Dubai / Scheherazade / Amiri Quran）以静态文件方式加载
    for fam, fn, wt in (('DubaiNur', 'dubai-400.ttf', '400'), ('DubaiNur', 'dubai-500.ttf', '500'),
                        ('DubaiNur', 'dubai-700.ttf', '700'),
                        ('ScheherazadeNur', 'scheherazade-400.ttf', '400'),
                        ('AmiriQuranNur', 'amiri-quran.ttf', '400')):
        if (DIR / 'assets' / 'fonts' / fn).exists():
            out.append("@font-face{font-family:'%s';font-style:normal;font-weight:%s;font-display:swap;src:url(assets/fonts/%s) format('truetype')}" % (fam, wt, fn))
    return ('\n'.join(out) + '\n') if out else ''


CSS = _font_face_css() + CSS + '\n/* 首页只留：左栏分类 + 书架（隐藏旧横幅/全部内容） */\n.feed,#learnSec,#homeShelves~.sec-title{display:none!important;}\n.gtabs{display:flex;gap:8px;margin-bottom:14px}\n.gtab{flex:1;text-align:center;padding:10px 12px;border-radius:10px;border:1px solid #eee7d8;background:#fff;color:#0f5132;font-weight:800;font-size:13.5px;cursor:pointer}\n.gtab.on{background:#0f5132;color:#fff;border-color:#0f5132}\n.ghint{font-size:12.5px;color:#6b736d;line-height:1.9;margin-bottom:10px}\n.gcard{display:flex;align-items:center;gap:12px;padding:13px 14px;border:1px solid #eee7d8;border-radius:14px;margin-bottom:9px;background:#fff;cursor:pointer}\n.gcard:hover{border-color:#cfe0cf}\n.gcard-n{flex:0 0 30px;height:30px;border-radius:9px;background:#eef5ee;color:#0f5132;font-weight:800;display:flex;align-items:center;justify-content:center;font-size:14px}\n.gcard-b{flex:1;min-width:0}\n.gcard-b b{font-size:14.5px;color:#12211b}\n.gcard-ar{font-family:var(--ar-font);color:#8a8f88;font-size:13px;margin-left:6px}\n.gcard-in{font-size:12.5px;color:#5a6159;line-height:1.8;margin-top:3px}\n.gcard-m{font-size:11px;color:#9aa39d;margin-top:5px}\n.gcard-arrow{color:#c9cfc9;font-size:20px}\n.gdetail{background:#fff;border:1px solid #eee7d8;border-radius:14px;padding:14px}\n.gtitle{display:flex;align-items:baseline;gap:8px;flex-wrap:wrap;margin-bottom:9px}\n.gtitle b{font-size:17px;color:#0f5132}\n.gintro{font-size:13px;color:#4a544d;line-height:1.95;background:#f7f9f4;border:1px solid #e8eee0;border-radius:12px;padding:12px}\n.gsec{margin:14px 0 8px;font-size:12px;font-weight:800;color:#0f5132;letter-spacing:.5px}\n.gtable{width:100%;border-collapse:collapse;font-size:13px}\n.gtable tr{border-bottom:1px solid #f2f0e8}\n.gtable tr:last-child{border-bottom:none}\n.gar{padding:10px 8px 10px 0;font-family:var(--ar-font);font-size:18px;color:#0f5132;white-space:nowrap;vertical-align:top}\n.gcn{padding:10px 8px;vertical-align:top;line-height:1.7;color:#2b3a33}\n.gnote{font-size:11.5px;color:#8a8f88;margin-top:3px;line-height:1.6}\n.gsp{padding:8px 0;vertical-align:top;text-align:right;width:52px}\n.gspk{width:auto;padding:5px 10px;background:#0f5132;color:#fff;border:none;border-radius:9px;cursor:pointer;font-size:13px}\n.gtip{margin-top:4px;background:#0f5132;color:#f6e7b4;border-radius:12px;padding:12px 13px;font-size:13px;line-height:1.95}\n.gnav{margin-top:14px}\nbody[data-lang=\'ar\'] .gcard-in,body[data-lang=\'ar\'] .gintro,body[data-lang=\'ar\'] .ghint{font-family:var(--ar-font)}\n'

_bk_css = (
    '\n.bkcard{display:block;cursor:pointer}\n'
    '.bkcov{height:168px;border-radius:4px 9px 9px 4px;position:relative;overflow:hidden;box-shadow:0 10px 22px rgba(18,30,24,.26)}\n'
    '.bkspine{position:absolute;left:0;top:0;bottom:0;width:7px;background:linear-gradient(90deg,rgba(255,255,255,.34),rgba(255,255,255,.05))}\n'
    '.bkframe{position:absolute;inset:9px 9px 9px 16px;border:1px solid rgba(246,231,180,.34);border-radius:2px}\n'
    '.bkorn{position:absolute;top:12px;left:50%;transform:translateX(-50%);color:rgba(246,231,180,.55);font-size:9px}\n'
    '.bktitle{position:absolute;top:25px;left:18px;right:11px;bottom:20px;display:flex;align-items:center;justify-content:center;text-align:center;color:#f6efdc;font-size:13px;line-height:1.85;overflow:hidden;font-family:var(--ar-font)}\n'
    '.bktitle[data-cn="1"]{font-family:inherit;letter-spacing:.5px}\n'
    '.bkrule{position:absolute;bottom:11px;left:50%;transform:translateX(-50%);width:26px;height:1px;background:rgba(246,231,180,.5)}\n'
    '.bkname{display:block;font-size:11.5px;margin-top:8px;line-height:1.5;color:#1d2321;max-height:34px;overflow:hidden;font-weight:600}\n'
    '.bkname:hover{color:#0f5132}\n'
    '.bkcat{display:block;font-size:10px;color:#9aa39d;margin-top:2px}\n'
)
CSS = CSS + _bk_css
_belt_css = (
    '\n.belt-head{margin-bottom:12px}\n'
    '.belt-ttl{font-size:16px;font-weight:800;color:#0f5132}\n'
    '.belt-sub{font-size:11.5px;color:#8a8f88;margin-top:3px}\n'
    '.belt-card{display:flex;gap:10px;padding:12px;border:1px solid #eee7d8;border-radius:13px;background:#fff;margin-bottom:9px}\n'
    '.belt-n{flex:0 0 24px;height:24px;border-radius:7px;background:#eef5ee;color:#0f5132;font-weight:800;font-size:12px;display:flex;align-items:center;justify-content:center}\n'
    '.belt-b{flex:1;min-width:0}\n'
    '.belt-cn{font-size:13.5px;font-weight:700;color:#16241e;line-height:1.7}\n'
    '.belt-ar{font-family:var(--ar-font);font-size:14px;color:#0f5132;line-height:2;margin-top:5px;text-align:right;direction:rtl}\n'
    '.belt-meta{font-size:11px;color:#9aa39d;margin-top:6px}\n'
    '.belt-link{color:#0a84ff;text-decoration:none;margin-left:4px}\n'
)
CSS = CSS + _belt_css
_hs_css = (
    '\n.hs-hero{padding:16px 18px 4px}\n'
    '.hs-h1{font-size:27px;font-weight:800;letter-spacing:-.6px;color:#0f1f19;line-height:1.2}\n'
    '.hs-h2{font-size:11.5px;color:#8a8f88;margin-top:4px;letter-spacing:.2px}\n'
    '.hs-rail{display:flex;gap:7px;overflow-x:auto;padding:12px 16px 4px;-webkit-overflow-scrolling:touch}\n'
    '.hs-rail::-webkit-scrollbar{display:none}\n'
    '.chip{flex:0 0 auto;padding:8px 14px;border-radius:999px;background:#fff;border:1px solid #e6e8ea;font-size:13px;font-weight:600;color:#3a423e;cursor:pointer;white-space:nowrap;-webkit-tap-highlight-color:transparent}\n'
    '.chip.on{background:#0f5132;border-color:#0f5132;color:#fff;box-shadow:0 4px 12px rgba(15,81,50,.22)}\n'
    '.hs-sec{display:flex;align-items:baseline;justify-content:space-between;padding:16px 18px 2px}\n'
    '.hs-sec h3{margin:0;font-size:16.5px;font-weight:800;color:#12211b;letter-spacing:-.2px}\n'
    '.hs-cnt{font-size:11.5px;color:#9aa39d}\n'
    '.hs-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:22px 16px;padding:12px 18px 90px}\n'
    '.hs-load{grid-column:1/-1;color:#8a8f88;font-size:12.5px;padding:10px 0}\n'
    '.bkcov{height:198px}\n'
    '.bktitle{font-size:14px}\n'
    '.bkname{font-size:12.5px}\n'
    '@media(min-width:700px){.hs-grid{grid-template-columns:repeat(4,1fr);gap:26px 22px;padding:14px 26px 100px}.hs-hero{padding:22px 26px 4px}.hs-h1{font-size:32px}.hs-rail{padding:14px 26px 4px}.hs-sec{padding:18px 26px 2px}.bkcov{height:230px}}\n'
    '@media(min-width:1100px){.hs-grid{grid-template-columns:repeat(6,1fr)}}\n'
)
CSS = CSS + _hs_css
_cov_css = (
    '\n.bkimg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;display:block;border-radius:4px 9px 9px 4px}\n'
    '.bkcov{background-color:#0f2a20}\n'
)
CSS = CSS + _cov_css
_apple_css = (
    # 封面：苹果图书规格（圆角小 + 柔和阴影，无内框）
    '\n.bkcov{height:200px;border-radius:5px;box-shadow:0 1px 2px rgba(0,0,0,.10),0 8px 20px rgba(0,0,0,.10);overflow:hidden;position:relative}\n'
    '.bkframe,.bkorn,.bkrule,.bkspine{display:none}\n'
    '.bktitle{position:absolute;inset:14px;display:flex;align-items:center;justify-content:center;text-align:center;color:#f6efdc;font-family:var(--ar-font);font-size:13.5px;line-height:1.85;overflow:hidden}\n'
    '.bkname{display:block;font-size:13px;font-weight:600;color:#111214;margin-top:9px;line-height:1.35;max-height:36px;overflow:hidden;letter-spacing:-.1px}\n'
    '.bkcat{display:block;font-size:11.5px;color:#8a8a8e;margin-top:2px;font-weight:400}\n'
    # 分类胶囊：苹果分段控件风格
    '.chip{background:#fff;border:1px solid #e3e3e6;color:#1c1c1e;font-weight:500;padding:8px 15px;font-size:13.5px}\n'
    '.chip.on{background:#0f5132;border-color:#0f5132;color:#fff;font-weight:600;box-shadow:none}\n'
    # 背景干净
    '.hs-hero{border-bottom:1px solid #ececee;padding-bottom:14px}\n'
    '.hs-h1{color:#0b0b0c;letter-spacing:-.8px}\n'
    '.hs-h2{color:#8a8a8e;margin-top:5px}\n'
    '.hs-sec h3{color:#0b0b0c;font-size:15px;letter-spacing:-.2px}\n'
)
CSS = CSS + _apple_css
_sidebar_css = (
    '\n.hs-body{display:block}\n'
    '.chip{display:inline-flex;align-items:center;gap:7px}\n'
    '.chip-i{font-style:normal;font-size:15px;line-height:1}\n'
    '.chip-t{font-style:normal}\n'
    '@media(min-width:820px){\n'
    '  .hs-body{display:flex;align-items:flex-start;gap:0}\n'
    '  .hs-rail{flex-direction:column;flex:0 0 214px;width:214px;background:#f5f5f7;border-right:1px solid #ececee;border-bottom:none;padding:10px;gap:2px;overflow:visible;position:sticky;top:0}\n'
    '  .chip{width:100%;justify-content:flex-start;border:none;background:transparent;padding:9px 10px;border-radius:8px;font-size:13.5px;color:#1c1c1e}\n'
    '  .chip.on{background:#e3e3e8;color:#0b0b0c;font-weight:600}\n'
    '  .chip-i{font-size:16px;width:20px;text-align:center}\n'
    '  .hs-main{flex:1;min-width:0}\n'
    '}\n'
)
CSS = CSS + _sidebar_css
_row_css = (
    '\n.hs-row,.hs-detail{grid-column:1/-1}\n'
    '.hs-row{display:flex;align-items:center;gap:11px;padding:12px 14px;border:1px solid #ececee;border-radius:12px;background:#fff;margin-bottom:8px;cursor:pointer}\n'
    '.hs-row:hover{border-color:#cfe0cf}\n'
    '.hs-row-i{flex:0 0 auto;font-size:17px;min-width:26px;text-align:center}\n'
    '.hs-row-b{flex:1;min-width:0}\n'
    '.hs-row-b b{display:block;font-size:13.5px;font-weight:600;color:#111214}\n'
    '.hs-row-b em{display:block;font-style:normal;font-size:12px;color:#8a8a8e;margin-top:2px;line-height:1.6}\n'
    '.hs-row-a{color:#c9cfc9;font-size:16px;display:flex;align-items:center;gap:4px}\n'
    '.hs-detail{border:1px solid #ececee;border-radius:12px;padding:14px;background:#fff}\n'
    '.hs-dt b{font-size:16px;color:#0f5132}\n'
    '.hs-dt span{font-family:var(--ar-font);color:#8a8a8e;font-size:13px;margin-left:6px}\n'
    '.hs-di{margin:10px 0 6px;font-size:13px;color:#4a544d;line-height:1.9;background:#f7f9f4;border:1px solid #e8eee0;border-radius:10px;padding:11px}\n'
    '.hs-line{border-bottom:1px solid #f2f2f4;padding:10px 0}\n'
    '.hs-line:last-child{border-bottom:none}\n'
    '.hs-line-ar{font-family:var(--ar-font);font-size:17px;line-height:2;color:#16241e}\n'
    '.hs-line-cn{font-size:12.5px;color:#8a8a8e;margin-top:3px}\n'
    '.q-belt{display:inline-flex;align-items:center;gap:6px;margin-top:9px;padding:7px 13px;border-radius:999px;background:#0f5132;color:#f6e7b4;font-size:12.5px;font-weight:700;cursor:pointer}\n'
)
CSS = CSS + _row_css
_rd_css = (
    '\n.rd-paper{max-width:820px;margin:0 auto;padding:26px 22px 70px;background:#fff;border-radius:0}\n'
    '.rd-page.rd-cn{font-family:"Songti SC","STSong","Noto Serif SC",Georgia,"Times New Roman",serif;direction:ltr;text-align:justify;line-height:2.05;color:#1a1a1a;letter-spacing:.2px;word-break:break-word}\n'
    '.rd-page.rd-cn p{margin:0 0 1.1em}\n'
    '.rd-foot{text-align:center;color:#b0b0b4;font-size:12px;margin-top:26px;letter-spacing:2px}\n'
    '@media(min-width:940px){.rd-page.rd-cn{column-count:2;column-gap:40px;column-rule:1px solid #f0f0f2}.rd-paper{max-width:1040px;padding:34px 40px 80px}}\n'
    'html[data-theme="dark"] .rd-paper{background:#141b16}\n'
)
CSS = CSS + _rd_css
_rd2_css = (
    '\n.rd-head{text-align:center;color:#9a9aa0;font-size:12.5px;letter-spacing:.4px;padding:2px 0 16px;margin-bottom:20px;border-bottom:1px solid #f2f2f4;font-weight:500}\n'
    '.rd-paper{max-width:1080px;margin:0 auto;padding:30px 34px 90px;background:#fff}\n'
    '.rd-page.rd-cn{font-size:19.5px;line-height:2.12;column-gap:48px;text-indent:0}\n'
    '@media(max-width:720px){.rd-paper{padding:18px 18px 70px}.rd-page.rd-cn{font-size:18.5px;line-height:2.05}}\n'
)
CSS = CSS + _rd2_css
_rd3_css = (
    # 阅读时：整个阅读页像苹果图书（干净、无边框、无工具栏头）
    '\nbody.reading #mReader .m-head{display:none!important}\n'
    'body.reading #mReader{background:#fff}\n'
    'body.reading #mReader .m-body{padding:0!important;background:#fff;max-height:100vh}\n'
    'body.reading .rd-paper{border:none!important;box-shadow:none!important;border-radius:0!important;margin:0 auto}\n'
    'body.reading .rd-bar{position:sticky;top:0;z-index:5;background:rgba(255,255,255,.92);backdrop-filter:saturate(180%) blur(14px);border-bottom:1px solid #f0f0f2}\n'
    'html[data-theme="dark"] body.reading #mReader,html[data-theme="dark"] body.reading #mReader .m-body{background:#141b16}\n'
    'html[data-theme="dark"] body.reading .rd-bar{background:rgba(20,27,22,.92)}\n'
)
CSS = CSS + _rd3_css
_ap_ds = '''/* ================= 苹果设计规范（全局统一，最后覆盖） ================= */
:root{
  --ap-bg:#ffffff;
  --ap-grouped:#f2f2f7;
  --ap-text:#1c1c1e;
  --ap-text2:#8a8a8e;
  --ap-sep:#ececee;
  --ap-brand:#0f5132;
  --ap-blue:#0a84ff;
  --ap-r-sm:10px; --ap-r-md:14px; --ap-r-lg:18px;
  --ap-sh:0 1px 2px rgba(0,0,0,.05),0 8px 24px rgba(0,0,0,.07);
  --ap-font:-apple-system,BlinkMacSystemFont,"SF Pro Text","PingFang SC","Helvetica Neue","Microsoft YaHei",sans-serif;
}
html,body{background:var(--ap-grouped)}
body{font-family:var(--ap-font);color:var(--ap-text);-webkit-font-smoothing:antialiased}
/* 顶栏 / 工具栏 */
.topbar,.appbar,.heade,header.hd{background:rgba(255,255,255,.86);backdrop-filter:saturate(180%) blur(18px);border-bottom:1px solid var(--ap-sep)}
/* 弹层：统一苹果卡片 */
.modal .m-head{background:rgba(255,255,255,.92);backdrop-filter:blur(18px);border-bottom:1px solid var(--ap-sep);padding:14px 16px;position:sticky;top:0;z-index:3}
.modal .m-head b{font-size:15.5px;font-weight:600;letter-spacing:-.2px}
.modal .m-head>span{font-size:17px;margin-right:6px}
.modal .m-close{width:30px;height:30px;border-radius:50%;background:#f2f2f7;border:none;color:#8a8a8e;font-size:14px;line-height:1;cursor:pointer}
.modal .m-body{padding:16px}
/* 按钮 */
.act-btn,.s-btn{border-radius:12px;font-family:var(--ap-font);font-weight:600;font-size:13.5px;transition:transform .12s ease,opacity .12s ease}
.act-btn:active,.s-btn:active,.chip:active,.bkcard:active{transform:scale(.97)}
.act-btn{background:#fff;border:1px solid var(--ap-sep);color:var(--ap-brand);padding:10px 15px}
.s-btn{background:var(--ap-brand);color:#fff;border:none}
/* 输入框 */
input[type=text],input[type=search],input:not([type]),textarea{font-family:var(--ap-font);border-radius:12px;border:1px solid var(--ap-sep);background:#fff;padding:11px 13px;font-size:15px;color:var(--ap-text)}
input:focus,textarea:focus{outline:none;border-color:#cfe0cf;box-shadow:0 0 0 3px rgba(15,81,50,.08)}
/* 底部导航（苹果 Tab Bar） */
.tabbar{background:rgba(255,255,255,.94);backdrop-filter:saturate(180%) blur(20px);border-top:1px solid var(--ap-sep);padding:6px 4px 8px}
.tabbar .tb{background:none;border:none;color:var(--ap-text2);gap:3px}
.tabbar .tb .t-ic{font-size:21px;line-height:1}
.tabbar .tb .t-nm{font-size:10.5px;font-weight:500;letter-spacing:.1px}
.tabbar .tb.on{color:var(--ap-brand)}
/* 列表行 / 卡片 */
.bk-card,.hs-row,.gcard,.belt-card,.v-item,.cont-row{border-radius:var(--ap-r-md);border:1px solid var(--ap-sep);background:#fff}
.bk-card:hover,.hs-row:hover,.gcard:hover{border-color:#dfe6df}
/* 分类胶囊 */
.chip{border-radius:999px;border:1px solid var(--ap-sep);background:#fff;font-family:var(--ap-font)}
/* 统一分隔线颜色 */
hr,.sep{border-color:var(--ap-sep)}
/* 夜间 */
html[data-theme="dark"]{--ap-bg:#111311;--ap-grouped:#0e100f;--ap-text:#f2f2f7;--ap-text2:#9a9a9e;--ap-sep:#2a2d2b}
html[data-theme="dark"] body{background:var(--ap-grouped);color:var(--ap-text)}
html[data-theme="dark"] .modal .m-head,html[data-theme="dark"] .tabbar{background:rgba(24,26,24,.92)}
html[data-theme="dark"] .act-btn,html[data-theme="dark"] .hs-row,html[data-theme="dark"] .bk-card,html[data-theme="dark"] .gcard,html[data-theme="dark"] .belt-card,html[data-theme="dark"] input,html[data-theme="dark"] textarea{background:#1a1d1b;border-color:#2a2d2b;color:var(--ap-text)}
/* 二级组件统一 */
.bk-grid{gap:18px 14px}
.bk-card{border:none;background:transparent}
.bk-cover{border-radius:5px;box-shadow:var(--ap-sh)}
.bk-meta b{font-size:12.5px;font-weight:600;color:var(--ap-text)}
.bk-meta span{font-size:11px;color:var(--ap-text2)}
.card{border-radius:var(--ap-r-md);border:1px solid var(--ap-sep);background:#fff;overflow:hidden}
.cbody b{font-size:14px;font-weight:600;color:var(--ap-text)}
.cbody span{font-size:12px;color:var(--ap-text2)}
.cat-tab{border-radius:999px;border:1px solid var(--ap-sep);background:#fff;font-family:var(--ap-font);font-size:13px}
.cat-tab.on{background:var(--ap-brand);border-color:var(--ap-brand);color:#fff}
.daily-quote .quote-card{border-radius:var(--ap-r-lg);border:1px solid var(--ap-sep);background:#fff;box-shadow:var(--ap-sh);padding:20px}
.q-ar{font-size:22px;line-height:2;color:var(--ap-brand)}
.q-cn{font-size:14.5px;color:var(--ap-text);margin-top:8px}
.q-src{font-size:11.5px;color:var(--ap-text2);margin-top:5px}
.q-switch{font-size:11px;color:#b0b0b4}
.hs-hero{border-bottom:1px solid var(--ap-sep);background:transparent}
.hs-h1,.pg-h{font-family:var(--ap-font);letter-spacing:-.7px;color:var(--ap-text)}
.sec-title h2{font-family:var(--ap-font);font-size:16px;font-weight:700;letter-spacing:-.2px}
.m-body::-webkit-scrollbar{width:8px}
.m-body::-webkit-scrollbar-thumb{background:rgba(0,0,0,.16);border-radius:4px}
.m-body::-webkit-scrollbar-track{background:transparent}
/* 词典弹层 */
.tk-dict{border-radius:var(--ap-r-lg);box-shadow:var(--ap-sh)}
/* 底部悬浮按钮（阅读时） */
#nurHomeBtn{border-radius:999px!important;box-shadow:var(--ap-sh)!important;background:var(--ap-brand)!important;color:#fff!important;font-weight:600!important;font-size:13.5px!important}
#rdFloatBack{border-radius:999px!important;box-shadow:var(--ap-sh)!important;font-weight:600!important;font-size:13.5px!important}
/* 弹层遮罩 */
.modal{background:rgba(0,0,0,.34);backdrop-filter:saturate(120%) blur(2px)}
.modal .m-inner,.modal .m-box{border-radius:var(--ap-r-lg) var(--ap-r-lg) 0 0;background:var(--ap-bg);box-shadow:0 -8px 40px rgba(0,0,0,.18)}
@media(min-width:760px){
  .modal .m-inner,.modal .m-box{border-radius:var(--ap-r-lg);margin:auto;max-width:820px;max-height:86vh;box-shadow:0 20px 60px rgba(0,0,0,.24)}
}
/* 阿语文本统一字体 */
.ar,[dir=rtl]{font-family:"AmiriNur","SF Arabic","Geeza Pro",serif}
'''
CSS = CSS + _ap_ds
CSS = CSS + '\n.hs-search{display:flex;align-items:center;gap:8px;margin-top:14px;padding:11px 14px;background:#f2f2f7;border-radius:12px;cursor:pointer}\n.hs-search-i{font-size:15px;opacity:.6}\n.hs-search-p{font-size:14px;color:#8a8a8e}\n'
CSS = CSS + '\n.hs-today{padding:8px 18px 0}\n.td-card{background:linear-gradient(160deg,#0f5132,#0a3d26);border-radius:18px;padding:16px;color:#fff;box-shadow:0 10px 26px rgba(15,81,50,.22)}\n.td-h{display:flex;align-items:baseline;gap:8px}\n.td-badge{font-size:15px;font-weight:800;color:#f6e7b4}\n.td-sub{font-size:11.5px;color:rgba(255,255,255,.72)}\n.td-bar{height:4px;border-radius:2px;background:rgba(255,255,255,.18);margin:12px 0 12px;overflow:hidden}\n.td-bar i{display:block;height:100%;background:#f6e7b4;border-radius:2px;transition:width .35s ease}\n.td-step{display:flex;align-items:center;gap:10px;padding:10px 11px;border-radius:12px;background:rgba(255,255,255,.08);margin-bottom:7px;cursor:pointer}\n.td-step.on{background:rgba(255,255,255,.16)}\n.td-n{flex:0 0 22px;height:22px;border-radius:50%;background:rgba(255,255,255,.16);display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:800}\n.td-step.on .td-n{background:#f6e7b4;color:#0f5132}\n.td-i{font-size:16px}\n.td-b{flex:1;min-width:0}\n.td-b b{display:block;font-size:13.5px;font-weight:600}\n.td-b em{display:block;font-style:normal;font-size:11px;color:rgba(255,255,255,.66);margin-top:1px}\n.td-a{color:rgba(255,255,255,.5)}\n.td-go{margin-top:6px;text-align:center;background:#f6e7b4;color:#0f5132;font-weight:800;font-size:14px;padding:12px;border-radius:12px;cursor:pointer}\n'
CSS = CSS + '\n.srch-box{display:flex;align-items:center;gap:8px;background:#f2f2f7;border-radius:12px;padding:10px 12px}\n.srch-bi{font-size:15px;opacity:.6}\n.srch-box input{flex:1;border:none;background:transparent;font-size:15px;padding:4px 0}\n.srch-bt{background:#0f5132;color:#fff;border:none;border-radius:9px;padding:8px 16px;font-size:13.5px;font-weight:600;cursor:pointer}\n.srch-tips{font-size:11.5px;color:#9a9aa0;margin:9px 2px 4px}\n.srch-res{margin-top:6px}\n'
CSS = CSS + '\n\n'
CSS = CSS + '\n.sup-card{grid-column:1/-1;display:flex;align-items:center;gap:12px;margin-top:6px;padding:16px;border-radius:16px;background:linear-gradient(135deg,#f6e7b4,#e9c96b);box-shadow:0 8px 22px rgba(200,162,74,.28);cursor:pointer}\n.sup-i{font-size:22px}\n.sup-b{flex:1;min-width:0}\n.sup-b b{display:block;font-size:15px;font-weight:800;color:#5a4210}\n.sup-b em{display:block;font-style:normal;font-size:11.5px;color:#7a5f22;margin-top:2px}\n.sup-a{color:#7a5f22;font-size:20px}\n'
CSS = CSS + '\n.ps-ai-msg{max-width:86%;padding:11px 14px;border-radius:18px;font-size:14px;line-height:1.75;margin:8px 0;word-break:break-word}\n.ps-ai-msg.bot{background:#f2f2f7;color:#1c1c1e;border-bottom-left-radius:6px;align-self:flex-start}\n.ps-ai-msg.user{background:#0f5132;color:#fff;border-bottom-right-radius:6px;margin-left:auto;align-self:flex-end}\n.ps-ai-msgs{display:flex;flex-direction:column}\n'
CSS = CSS + '\n.home-stats{display:none!important}\n'
CSS = CSS + '\n.hs-today{display:none!important}\n'
CSS = CSS + '\n#homeAI{max-height:118px;overflow-y:auto;transition:max-height .35s ease}\n.ps-ai-card.ai-grow #homeAI{max-height:62vh}\n.ps-ai-card{border-radius:16px}\n'
CSS = CSS + '\n#page-home{display:flex!important;flex-direction:column}\n'
CSS = CSS + '\nheader.hdr{order:1} #page-home .hs-dictblock{order:2} #quote{order:3} #aiSec{order:4} #homeShelves{order:5}'
CSS = CSS + '\n#page-home>*{order:6}\n'
CSS = CSS + '\n.donbar{order:0!important} #hsSupTop{order:1!important} .tk-hero{order:2!important} .hero{order:3!important}\n'
CSS = CSS + '\nheader.hdr{order:4!important} #hsBigBox{order:5!important} #page-home .hs-dictblock{order:6!important} #quote{order:7!important} #aiSec{order:8!important} #homeShelves{order:9!important}\n'
CSS = CSS + '\n#hsBigBox{padding:14px 18px 2px}\n'
CSS = CSS + '\n.hbb{display:flex;align-items:center;gap:10px;background:#fff;border:1.5px solid #dfe3df;border-radius:16px;padding:14px 16px;box-shadow:0 4px 16px rgba(0,0,0,.06)}\n'
CSS = CSS + '\n.hbb-i{font-size:18px;opacity:.65}\n.hbb input{flex:1;border:none;background:transparent;font-size:16px;padding:2px 0}\n'
CSS = CSS + '\n.hbb-b{background:#0f5132;color:#fff;border:none;border-radius:12px;padding:11px 20px;font-size:14.5px;font-weight:700;cursor:pointer}\n'
CSS = CSS + '\n:root{--ar-font:\'DubaiNur\',\'AmiriNur\',\'SF Arabic\',serif}\n'
CSS = CSS + '\n.rd-page{font-family:\'ScheherazadeNur\',\'AmiriNur\',serif}\n'
CSS = CSS + '\n.q-ar,.bktitle,.hs-line-ar,.gcard-ar,.gar,.belt-ar,.chip-t,[dir=rtl]{font-family:\'DubaiNur\',\'AmiriNur\',serif}\n'
CSS = CSS + '\n.tabbar{display:none!important}\n'
CSS = CSS + '\n#mDict.inline{position:static!important;inset:auto!important;z-index:auto!important;background:transparent!important;display:grid!important;width:100%!important;grid-template-columns:minmax(0,26%) minmax(0,1fr);border:1px solid #ececee;border-radius:16px;overflow:hidden}\n#mDict.inline .m-head{grid-column:1 / -1}\n#mDict.inline .m-search{grid-column:1;flex-direction:column;align-items:stretch;gap:10px;border-right:1px solid #ececee;padding:16px;background:#fafafa}\n#mDict.inline #dictBody{grid-column:2;background:#fff;padding:20px 26px;min-height:460px;width:100%}\n#mDict.inline #dictBody>*{max-width:100%!important;width:auto}\n#mDict.inline .m-search{padding:14px}\n@media(max-width:899px){#mDict.inline{grid-template-columns:minmax(0,1fr)}\n#mDict.inline .m-search{grid-column:1;border-right:none;border-bottom:1px solid #ececee}\n#mDict.inline #dictBody{grid-column:1}}\n'
CSS = CSS + '\n.tk-acts,.lib-search,.lib-acts{display:none!important}\n'
CSS = CSS + '\nheader.hdr{display:none!important}\n'
CSS = CSS + '\n.dict-sug{display:none;position:absolute;left:0;right:0;top:100%;z-index:9;background:#fff;border:1px solid #e6e8ea;border-radius:12px;box-shadow:0 12px 30px rgba(0,0,0,.14);margin-top:6px;overflow:hidden;max-height:280px;overflow-y:auto}\n.dict-sug.on{display:block}\n.dict-sug-i{display:flex;align-items:baseline;gap:10px;padding:11px 13px;cursor:pointer;border-bottom:1px solid #f4f4f6}\n.dict-sug-i:last-child{border-bottom:none}\n.dict-sug-i:hover{background:#f6f9f6}\n.dict-sug-i b{font-family:var(--ar-font);font-size:17px;color:#0f5132;white-space:nowrap}\n.dict-sug-i em{font-style:normal;font-size:12.5px;color:#8a8a8e;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}\n.dict-recents{padding:14px 16px 4px}\n.dr-t{font-size:11.5px;color:#9a9aa0;margin-bottom:7px}\n.dr-c{display:flex;flex-wrap:wrap;gap:6px}\n.dr-c span{padding:7px 12px;border:1px solid #e6e8ea;border-radius:999px;background:#fff;font-family:var(--ar-font);font-size:15px;color:#0f5132;cursor:pointer}\n.dr-c span:hover{background:#f2f7f2}\n'
CSS = CSS + '\n.q-belt{display:none!important}\n'
CSS = CSS + '\n#hsBigBox.split{display:grid;grid-template-columns:minmax(0,28%) minmax(0,1fr);gap:18px;align-items:start}\n'
CSS = CSS + '\n.hs-bigres{background:#fff;border:1px solid #ececee;border-radius:16px;padding:14px 16px;min-height:320px;max-height:70vh;overflow-y:auto}\n'
CSS = CSS + '\n.hs-dictblock #mDict.inline{border:none}\n'
CSS = CSS + '\n.hs-suptop{padding:12px 18px 0}\n.hs-suptop .sup-card{margin-top:0}\n'
CSS = CSS + 'html,body{background:#f5f5f7}\nbody{font-family:-apple-system,BlinkMacSystemFont,"SF Pro Text","PingFang SC","Helvetica Neue",sans-serif;color:#1d1d1f;letter-spacing:-.1px;-webkit-font-smoothing:antialiased}\n.donbar{background:#fbfbfd!important;border-bottom:1px solid #ececef!important;color:#6e6e73!important;font-size:12.5px!important;font-weight:500!important;padding:9px 0!important;letter-spacing:.1px}\n.tk-hero{padding:26px 20px 6px!important;text-align:center}\n.tk-hero>div:first-child{font-size:32px!important;font-weight:800!important;letter-spacing:-1.1px!important;line-height:1.22!important;color:#0b0b0c!important}\n.tk-hero>div:nth-child(2){font-size:14px!important;color:#86868b!important;margin-top:10px!important}\n.hero{max-width:1100px!important;margin:18px auto 6px!important;background:#fff!important;border:1px solid #ececef!important;border-radius:20px!important;box-shadow:0 1px 3px rgba(0,0,0,.04),0 12px 30px rgba(0,0,0,.05)!important;padding:20px 22px!important}\n.hero-tx b{font-size:19px!important;font-weight:700!important;letter-spacing:-.3px!important;color:#0b0b0c!important}\n.hero-tx span{font-size:12.5px!important;color:#86868b!important;line-height:1.85!important;margin-top:7px!important}\n.hero-tx em{background:#0f5132!important;color:#fff!important;border-radius:999px!important;padding:10px 18px!important;font-size:13.5px!important;font-weight:600!important;margin-top:14px!important;box-shadow:0 4px 14px rgba(15,81,50,.22)!important}\n#hsBigBox{padding:18px 20px 4px!important}\n.hbb{background:#fff!important;border:1px solid #e5e5e8!important;border-radius:14px!important;padding:13px 16px!important;box-shadow:0 1px 2px rgba(0,0,0,.04),0 8px 22px rgba(0,0,0,.06)!important}\n.hbb input{font-size:16px!important;color:#1d1d1f!important}\n.hbb-b{background:#0f5132!important;border-radius:10px!important;padding:10px 18px!important;font-size:14px!important;font-weight:600!important}\n.hs-bigres{background:#fff!important;border:1px solid #ececef!important;border-radius:18px!important;box-shadow:0 1px 3px rgba(0,0,0,.04),0 12px 30px rgba(0,0,0,.05)!important}\n.sup-card{background:linear-gradient(135deg,#fdf6e3,#f7e9c3)!important;border:1px solid #f0e0b8!important;border-radius:18px!important;box-shadow:0 1px 3px rgba(0,0,0,.04),0 10px 26px rgba(200,162,74,.16)!important;padding:16px!important}\n.sup-b b{font-size:15.5px!important;font-weight:700!important;color:#5a4210!important}\n.sup-b em{font-size:12px!important;color:#8a6f2e!important}\n.quote-card{background:#fff!important;border:1px solid #ececef!important;border-radius:20px!important;box-shadow:0 1px 3px rgba(0,0,0,.04),0 12px 30px rgba(0,0,0,.05)!important;padding:22px!important}\n.q-ar{font-family:\'ScheherazadeNur\',\'AmiriNur\',serif!important;font-size:24px!important;line-height:2!important;color:#0f5132!important}\n.q-cn{font-size:15px!important;color:#1d1d1f!important;margin-top:9px!important}\n.q-src{font-size:12px!important;color:#86868b!important}\n.ps-ai-card{background:#fff!important;border:1px solid #ececef!important;border-radius:20px!important;box-shadow:0 1px 3px rgba(0,0,0,.04),0 12px 30px rgba(0,0,0,.05)!important}\n.ps-ai-msg.bot{background:#f2f2f7!important;color:#1d1d1f!important;border-radius:18px!important;font-size:14.5px!important;line-height:1.75!important}\n.ps-ai-msg.user{background:#0f5132!important;color:#fff!important;border-radius:18px!important}\n.chip{border:1px solid #e8e8ea!important;background:#fff!important;border-radius:999px!important;font-weight:500!important;color:#1d1d1f!important;padding:9px 15px!important;transition:all .15s ease}\n.chip.on{background:#0f5132!important;border-color:#0f5132!important;color:#fff!important;font-weight:600!important;box-shadow:0 4px 12px rgba(15,81,50,.20)!important}\n.hs-row{border:1px solid #ececef!important;border-radius:14px!important;background:#fff!important;box-shadow:0 1px 2px rgba(0,0,0,.03)!important;transition:transform .12s ease,border-color .15s ease}\n.hs-row:hover{border-color:#cfe0cf!important;transform:translateY(-1px)}\n.hs-sec h3{font-size:17px!important;font-weight:700!important;letter-spacing:-.35px!important;color:#0b0b0c!important}\n.hs-cnt{color:#a1a1a6!important}\n.bkcov{border-radius:6px!important;box-shadow:0 2px 6px rgba(0,0,0,.10),0 12px 26px rgba(0,0,0,.10)!important;transition:transform .18s ease,box-shadow .18s ease}\n.bkcard:hover .bkcov{transform:translateY(-3px);box-shadow:0 4px 10px rgba(0,0,0,.12),0 18px 36px rgba(0,0,0,.14)!important}\n.bkname{font-size:13px!important;font-weight:600!important;color:#1d1d1f!important}\n.bkcat{font-size:11.5px!important;color:#86868b!important}\n.modal{background:rgba(0,0,0,.28)!important;backdrop-filter:saturate(140%) blur(4px)}\n.m-head{background:rgba(255,255,255,.94)!important;backdrop-filter:blur(20px);border-bottom:1px solid #ececef!important}\n.m-body{background:#fff}\n'
CSS = CSS + ".sup-card{display:flex!important;align-items:center;gap:14px!important;background:#fff!important;border:1px solid #efe6d2!important;border-radius:20px!important;padding:16px 18px!important;box-shadow:0 1px 3px rgba(0,0,0,.04),0 10px 26px rgba(196,160,74,.10)!important;position:relative;overflow:hidden}\n.sup-card::before{content:'';position:absolute;left:0;top:0;bottom:0;width:4px;background:linear-gradient(180deg,#e9c96b,#d9b23f)}\n.sup-heart{flex:0 0 auto;width:42px;height:42px;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:20px;background:linear-gradient(135deg,#fdf3dc,#f6e6bf);box-shadow:inset 0 0 0 1px rgba(217,178,63,.28)}\n.sup-b{flex:1;min-width:0}\n.sup-b b{display:block;font-size:15.5px;font-weight:700;color:#1d1d1f;letter-spacing:-.25px}\n.sup-b em{display:block;font-style:normal;font-size:12px;color:#8a8a8e;margin-top:3px}\n.sup-btn{flex:0 0 auto;background:#0f5132;color:#fff;font-size:13.5px;font-weight:600;padding:10px 16px;border-radius:999px;box-shadow:0 4px 14px rgba(15,81,50,.20)}\n.sup-a{display:none}\n"
CSS = CSS + '/* ===== 苹果图书规格（第二批） ===== */\n/* 搜索栏：整条圆角灰底，放大镜在里，无按钮（苹果就是这样） */\n.hbb{background:#f2f2f7!important;border:1px solid #eaeaea!important;border-radius:12px!important;padding:11px 14px!important;box-shadow:none!important}\n.hbb .hbb-i{font-size:17px;opacity:.45}\n.hbb input{font-size:15.5px!important;background:transparent!important;color:#1d1d1f!important}\n.hbb input::placeholder{color:#8e8e93!important}\n.hbb-b{background:#e8e8ed!important;color:#1d1d1f!important;border-radius:9px!important;padding:8px 16px!important;font-size:13.5px!important;font-weight:600!important;box-shadow:none!important;border:none!important}\n.hbb-b:hover{background:#dededf!important}\n/* 区块标题：苹果式（17px 粗 + 右侧蓝色「查看全部 ›」） */\n.hs-sec{padding:20px 20px 6px!important}\n.hs-sec h3{font-size:19px!important;font-weight:700!important;letter-spacing:-.5px!important}\n.hs-row.hs-head{cursor:pointer;background:transparent!important;border:none!important;box-shadow:none!important;padding:6px 0!important}\n.hs-row.hs-head .hs-row-i{font-size:17px}\n.hs-row.hs-head .hs-row-b b{font-size:19px!important;font-weight:700!important;letter-spacing:-.5px}\n.hs-row.hs-head .hs-row-b em{font-size:12.5px!important;color:#86868b!important}\n.hs-row.hs-head .hs-row-a{color:#0a84ff!important;font-size:15px;font-weight:600}\n/* 封面网格：苹果的间距与阴影 */\n.hs-grid{gap:26px 20px!important;padding:14px 20px 90px!important}\n.bkcov{box-shadow:0 1px 2px rgba(0,0,0,.10),0 8px 20px rgba(0,0,0,.10)!important}\n.bkname{font-size:12.5px!important;font-weight:600!important;line-height:1.35!important;margin-top:8px!important;color:#1d1d1f!important}\n.bkcat{font-size:11px!important;color:#8e8e93!important;margin-top:3px!important}\n/* 侧栏项：更细、更苹果 */\n.chip{font-size:13.5px!important;padding:8px 14px!important;border-color:#e6e6e9!important}\n.chip.on{box-shadow:none!important}\n/* 名言卡：苹果阅读卡 */\n.quote-card{padding:24px 22px!important;border-radius:18px!important}\n.q-ar{font-size:26px!important;letter-spacing:.2px}\n/* 努尔老师卡：贴近苹果信息 */\n.ps-ai-msg.bot{background:#f2f2f7!important;border-radius:20px!important}\n.ps-ai-msg.user{background:#0f5132!important;border-radius:20px!important}\n'
CSS = CSS + '/* ===== 苹果图书官方色板对齐（功能不动） ===== */\n:root{--sys-blue:#007AFF;--sys-gray6:#f2f2f7;--sys-gray5:#e5e5ea;--sys-label:#1d1d1f;--sys-label2:#86868b}\nbody{background:#f5f5f7!important;color:#1d1d1f!important}\n/* 链接与「查看全部」→ 系统蓝 */\na,.belt-link,.hs-row.hs-head .hs-row-a,.hs-link{color:#007AFF!important;font-weight:600}\n.belt-link{text-decoration:none!important}\n/* 分隔线统一 #e5e5ea */\n.hs-row,.bk-card,.gcard,.belt-card,.hbb,.srch-box,.quote-card,.ps-ai-card,.hs-bigres,.sup-card{border-color:#e5e5ea!important}\n.hs-sec{border-bottom:1px solid #ececef}\n/* 侧栏选中：苹果浅灰 */\n.chip.on{background:#0f5132!important;color:#fff!important}\n/* 搜索栏：系统灰底圆角 */\n.hbb,.srch-box{background:#f2f2f7!important}\n.srch-box input,.hbb input{background:transparent!important}\n/* 封面：4px 圆角 + 苹果阴影 */\n.bkcov{border-radius:4px!important}\n.bkcard:hover .bkcov{transform:translateY(-2px)}\n/* 网格：24px 间距 */\n.hs-grid{gap:28px 20px!important}\n/* 按钮：系统蓝/绿，无边框 */\n.hbb-b{background:#e8e8ed!important;color:#1d1d1f!important}\n/* 弹层标题：苹果工具栏 */\n.m-head b{font-size:15px!important;font-weight:600!important;letter-spacing:-.2px}\n'
CSS = CSS + '\n.ai-quota-badge{display:flex;align-items:center;gap:6px;font-size:12.5px;color:#86868b;padding:9px 14px;background:#f2f2f7;border-radius:999px;margin:0 0 10px;align-self:flex-start}\n.ai-quota-badge b{color:#0f5132;font-size:14px;font-weight:700}\n.aq-v{background:#0f5132;color:#fff;font-size:10.5px;font-weight:700;padding:2px 7px;border-radius:999px}\n.aq-go{color:#007AFF;font-weight:600;cursor:pointer}\n'
CSS = CSS + '\n.bktitle{font-size:14px!important;letter-spacing:.3px;text-shadow:0 1px 3px rgba(0,0,0,.35)}\n'
CSS = CSS + '\n.bkcov::after{content:\'\';position:absolute;inset:0;background:linear-gradient(180deg,rgba(255,255,255,.06),rgba(0,0,0,.18));pointer-events:none}\n'
CSS = CSS + '\n.bkcov::before{content:\'\';position:absolute;left:0;top:0;bottom:0;width:6px;background:linear-gradient(90deg,rgba(255,255,255,.28),rgba(255,255,255,.03));z-index:2}\n'
CSS = CSS + '\n.hs-dictblock{display:none!important}\n'
CSS = CSS + '\n.ps-ai-card{display:grid!important;grid-template-columns:minmax(0,28%) minmax(0,1fr);grid-template-rows:auto auto 1fr;gap:0!important;padding:0!important;overflow:hidden}\n.ps-ai-card .ps-ai-head{grid-column:1 / -1;grid-row:1}\n.ps-ai-card #aiQuotaBadge{grid-column:1;grid-row:2;margin:10px 12px 0!important;align-self:start}\n.ps-ai-card .ps-ai-input{grid-column:1;grid-row:4;flex-direction:column!important;align-items:stretch!important;gap:8px!important;padding:12px!important;border-right:1px solid #ececef;background:#fafafa}\n.ps-ai-card .ps-ai-chips{grid-column:1;grid-row:3;padding:10px 12px!important;border-right:1px solid #ececef;background:#fafafa;max-height:none!important;overflow:visible!important}\n.ps-ai-card #homeAI{grid-column:2;grid-row:2 / span 3;padding:18px 20px!important;background:#fff;max-height:66vh!important;min-height:360px;overflow-y:auto!important;border-left:1px solid #ececef}\n.ps-ai-msg{white-space:pre-wrap!important;word-break:break-word}\n@media(max-width:899px){.ps-ai-card{grid-template-columns:minmax(0,1fr)!important;grid-template-rows:auto auto 1fr auto}\n.ps-ai-card #homeAI{grid-column:1!important;grid-row:2!important;border-left:none;min-height:240px}\n.ps-ai-card .ps-ai-chips{grid-column:1!important;grid-row:3!important;border-right:none}\n.ps-ai-card .ps-ai-input{grid-column:1!important;grid-row:4!important;border-right:none;border-top:1px solid #ececef}\n.ps-ai-card #aiQuotaBadge{grid-column:1!important;grid-row:1!important}}\n'
CSS = CSS + '\n.bkimg{object-fit:cover!important;object-position:center!important;filter:saturate(1.04) contrast(1.03) brightness(1.01)}\n.bkcov{background:#0f2a20!important}\n.bkcov::after{content:\'\';position:absolute;inset:0;border-radius:5px;box-shadow:inset 0 0 0 1px rgba(255,255,255,.10),inset 0 -34px 40px -20px rgba(0,0,0,.28);pointer-events:none;z-index:3}\n.bkcard:hover .bkimg{filter:saturate(1.08) contrast(1.05) brightness(1.03)}\n'
CSS = CSS + '\n.ps-ai-act{padding:10px 14px;margin:8px 0;background:#f2f7ff;border:1px solid #d6e6ff;border-radius:12px;font-size:13.5px}\n'
CSS = CSS + '\n.dcn{padding:4px 2px}\n.dcn-h{display:flex;align-items:baseline;gap:10px;flex-wrap:wrap;margin-bottom:10px}\n.dcn-h b{font-size:26px;font-weight:800;color:#0b0b0c;letter-spacing:-.5px}\n.dcn-py{color:#0f5132;font-size:15px;font-weight:600}\n.dcn-pos{background:#eef5ee;color:#0f5132;font-size:11.5px;font-weight:700;padding:3px 9px;border-radius:999px}\n.dcn-m{font-size:16px;line-height:1.9;color:#1d1d1f;font-weight:600;margin-bottom:8px}\n.dcn-d{font-size:13.5px;line-height:2;color:#4a544d;background:#f7f9f4;border:1px solid #e8eee0;border-radius:12px;padding:12px;margin-bottom:12px}\n.dcn-l{font-size:12px;font-weight:800;color:#0f5132;letter-spacing:.4px;margin:14px 0 7px}\n.dc-chip{display:inline-block;padding:7px 13px;margin:0 7px 7px 0;border:1px solid #e5e5ea;border-radius:999px;font-size:14.5px;cursor:pointer;background:#fff}\n.dc-chip:hover{background:#f2f7f2;border-color:#cfe0cf}\n.dcn-s{font-size:13.5px;line-height:1.9;color:#2b3a33;padding:8px 12px;border-left:3px solid #cfe0cf;margin-bottom:7px;background:#fafcfa}\n.dcn-note{margin-top:12px;background:#0f5132;color:#f6e7b4;border-radius:12px;padding:11px 13px;font-size:13px;line-height:1.9}\n'
CSS = CSS + '\n.bkcov{height:198px!important;border-radius:4px 8px 8px 4px!important;position:relative;overflow:hidden;box-shadow:0 1px 2px rgba(0,0,0,.12),0 10px 24px rgba(0,0,0,.13)!important;background:#0e3b2a}\n.bk-face{position:absolute;inset:10px 9px 10px 15px;border:1px solid rgba(214,182,106,.42);border-radius:2px;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:8px 10px;z-index:1}\n.bk-line{width:22px;height:1px;background:rgba(214,182,106,.62);margin-bottom:9px}\n.bk-orn{color:rgba(214,182,106,.66);font-size:9px;margin-bottom:7px}\n.bk-ttl{font-family:"Songti SC","STSong",serif;font-size:15px;line-height:1.7;color:#f3ead4;text-align:center;font-weight:600;letter-spacing:1.6px;max-height:88px;overflow:hidden;text-shadow:0 1px 4px rgba(0,0,0,.45)}\n.bk-ttl[dir=rtl]{font-family:"ScheherazadeNur","AmiriNur",serif;font-size:16px;letter-spacing:0;line-height:1.9}\n.bk-rule{width:26px;height:1px;background:rgba(214,182,106,.55);margin:9px 0 7px}\n.bk-sub{font-size:9.5px;color:rgba(214,182,106,.78);letter-spacing:2px}\n.bk-gloss{position:absolute;left:0;top:0;bottom:0;width:7px;z-index:3;background:linear-gradient(90deg,rgba(255,255,255,.30),rgba(255,255,255,.02))}\n.bkimg{z-index:2}\n.bkcov::after{content:\'\';position:absolute;inset:0;z-index:4;pointer-events:none;border-radius:4px 8px 8px 4px;box-shadow:inset 0 0 0 1px rgba(255,255,255,.10),inset 0 -30px 36px -22px rgba(0,0,0,.30)}\n.bkname{font-size:12.5px;font-weight:600;color:#1d1d1f;margin-top:9px;line-height:1.4;max-height:35px;overflow:hidden}\n.bkcat{font-size:10.5px;color:#8e8e93;margin-top:3px}\n'
CSS = CSS + '\n#hsBigBox{display:none!important}\n'
CSS = CSS + '\n.srch-empty{padding:26px 18px;text-align:center;background:#fff;border:1px solid #ececef;border-radius:16px}\n.se-t{font-size:16px;font-weight:700;color:#1d1d1f;margin-bottom:8px}\n.se-d{font-size:12.5px;color:#8a8a8e;line-height:1.9}\n.se-d b{color:#0f5132}\n.se-g{font-size:12px;color:#9a9aa0;margin:16px 0 8px}\n.se-n{margin-top:14px;font-size:12px;color:#8a8a8e;background:#f7f9f4;border-radius:10px;padding:10px}\n'
CSS = CSS + '\n/* 宽屏：苹果图书式左栏（用户选定）*/\n@media(min-width:820px){\n.hs-body{display:flex!important;align-items:flex-start;gap:0}\n.hs-rail{flex:0 0 236px!important;width:236px!important;flex-direction:column!important;background:#fbfbfd!important;border-right:1px solid #ececef!important;border-bottom:none!important;padding:12px 10px!important;gap:3px!important;overflow:visible!important;position:sticky!important;top:0!important}\n.chip{width:100%!important;justify-content:flex-start!important;border:none!important;background:transparent!important;padding:10px 12px!important;border-radius:9px!important;font-size:14px!important;color:#1d1d1f!important;text-align:left}\n.chip.on{background:#0f5132!important;color:#fff!important;font-weight:600!important}\n.chip-i{width:22px!important;text-align:center!important;font-size:16px!important}\n.hs-main{flex:1!important;min-width:0!important}\n.hs-grid{grid-template-columns:repeat(4,1fr)!important;gap:26px 20px!important}\n}\n@media(min-width:1300px){.hs-grid{grid-template-columns:repeat(5,1fr)!important}}\n'
CSS = CSS + '\n/* 手机也用左栏竖排（窄版 118px）*/\n@media(max-width:819px){\n.hs-body{display:flex!important;align-items:flex-start;gap:0}\n.hs-rail{flex:0 0 118px!important;width:118px!important;flex-direction:column!important;background:#fbfbfd!important;border-right:1px solid #ececef!important;border-bottom:none!important;padding:8px 6px!important;gap:2px!important;overflow:visible!important;position:sticky!important;top:0!important;max-height:80vh!important;overflow-y:auto!important}\n.chip{width:100%!important;justify-content:flex-start!important;border:none!important;background:transparent!important;padding:8px 6px!important;border-radius:8px!important;font-size:11.5px!important;color:#1d1d1f!important;text-align:left;white-space:nowrap!important;overflow:hidden!important;text-overflow:ellipsis!important}\n.chip.on{background:#0f5132!important;color:#fff!important;font-weight:600!important}\n.chip-i{width:16px!important;font-size:13px!important;text-align:center!important}\n.hs-main{flex:1!important;min-width:0!important}\n.hs-grid{grid-template-columns:repeat(2,1fr)!important;gap:16px 10px!important;padding:10px 10px 70px!important}\n.hs-hero{padding:14px 12px 4px!important}\n.hs-h1{font-size:21px!important}\n}\n'
CSS = CSS + '/* ================= 精准响应式（逐设备适配） ================= */\n/* 基础（手机优先）：左栏 108px + 2 列 */\n.hs-body{display:flex;align-items:flex-start;gap:0}\n.hs-rail{flex:0 0 108px;width:108px;flex-direction:column;background:#fbfbfd;\n  border-right:1px solid #ececef;padding:10px 6px;gap:2px;position:sticky;top:0;max-height:78vh;overflow-y:auto}\n.chip{width:100%;justify-content:flex-start;border:none;background:transparent;padding:9px 7px;\n  border-radius:9px;font-size:11.5px;color:#1d1d1f;text-align:left;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}\n.chip-i{width:16px;text-align:center;font-size:13px}\n.chip.on{background:#0f5132;color:#fff;font-weight:600}\n.hs-main{flex:1;min-width:0}\n.hs-grid{grid-template-columns:repeat(2,1fr);gap:16px 10px;padding:10px 10px 70px}\n.hs-hero{padding:14px 12px 4px}\n.hs-h1{font-size:21px;letter-spacing:-.5px}\n.hs-h2{font-size:10.5px}\n.bktitle{font-size:12px}\n.bkname{font-size:11.5px}\n/* 大屏手机 / 小平板（≥520）：左栏 130 + 3 列 */\n@media(min-width:520px){\n  .hs-rail{flex-basis:132px;width:132px;padding:12px 8px}\n  .chip{font-size:12.5px;padding:10px 9px}\n  .chip-i{width:19px;font-size:14.5px}\n  .hs-grid{grid-template-columns:repeat(3,1fr);gap:18px 12px;padding:12px 14px 80px}\n  .bktitle{font-size:13px}.bkname{font-size:12.5px}\n}\n/* iPad 竖屏 / 平板（≥768）：左栏 172 + 3 列 */\n@media(min-width:768px){\n  .hs-rail{flex-basis:172px;width:172px;padding:14px 10px;gap:3px;max-height:82vh}\n  .chip{font-size:13.5px;padding:11px 11px;border-radius:10px}\n  .chip-i{width:21px;font-size:15.5px}\n  .hs-grid{grid-template-columns:repeat(3,1fr);gap:22px 16px;padding:14px 18px 90px}\n  .hs-h1{font-size:24px}.bktitle{font-size:13.5px}.bkname{font-size:13px}\n}\n/* iPad 横屏 / 小笔电（≥1024）：左栏 212 + 4 列 */\n@media(min-width:1024px){\n  .hs-rail{flex-basis:212px;width:212px;padding:16px 12px}\n  .chip{font-size:14px;padding:11px 12px}\n  .hs-grid{grid-template-columns:repeat(4,1fr);gap:26px 20px;padding:16px 24px 100px;max-width:1280px;margin:0 auto}\n  .hs-h1{font-size:28px}\n  .hs-hero{padding:20px 24px 6px}\n}\n/* 电脑（≥1366）：左栏 236 + 5 列 */\n@media(min-width:1366px){\n  .hs-rail{flex-basis:236px;width:236px;padding:18px 14px}\n  .chip{font-size:14.5px;padding:12px 13px}\n  .hs-grid{grid-template-columns:repeat(5,1fr);gap:28px 22px;padding:18px 30px 110px;max-width:1500px}\n  .hs-h1{font-size:32px}\n}\n/* 超大屏（≥1700）：6 列 */\n@media(min-width:1700px){ .hs-grid{grid-template-columns:repeat(6,1fr)} }\n/* 平板/电脑：词典左输入右答案；手机：上下 */\n@media(min-width:900px){\n  #mDict.inline{grid-template-columns:minmax(0,26%) minmax(0,1fr)!important}\n}\n'
CSS = CSS + '\n/* 努尔老师：输入区按钮加大 */\n.ps-ai-input button{min-width:88px!important;padding:13px 20px!important;font-size:15px!important;font-weight:700!important;border-radius:12px!important;min-height:46px!important}\n.ps-ai-input input,.ps-ai-input textarea{font-size:15.5px!important;padding:12px 14px!important;border-radius:12px!important;min-height:46px!important}\n.ps-ai-input{display:flex!important;gap:10px!important;align-items:stretch!important}\n@media(min-width:900px){.ps-ai-input{flex-direction:column!important}}\n'
CSS = CSS + '\n.hs-dict-btn{margin-top:12px;display:inline-block;background:#0f5132;color:#fff;font-size:15px;font-weight:800;padding:13px 26px;border-radius:999px;cursor:pointer;box-shadow:0 6px 18px rgba(15,81,50,.22)}\n'
CSS = CSS + '\n.srch-h{margin:12px 0 6px;font-size:12px;font-weight:700;color:#0f5132;letter-spacing:.3px}\n'
CSS = CSS + '''
/* ===== 前三名 skill 精修（frontend-design-pro + ui-ux-pro-max + taste-skill）===== */
:root{
  /* ① 专业缓动（skill 规范：快入慢出，不用 bounce）*/
  --ease-out-quart:cubic-bezier(.16,1,.3,1);
  --ease-out-soft:cubic-bezier(.2,.8,.2,1);
  --dur-micro:150ms; --dur-ui:200ms; --dur-page:320ms;
  /* ② 中性色带色调（暖灰，不用纯灰）*/
  --n-900:#1d1d1f; --n-700:#48484a; --n-600:#6b6b70; --n-500:#8e8e93;
  --n-400:#aeaeb2; --n-300:#c7c7cc; --n-200:#dcdce0; --n-100:#f2f2f7;
  --n-bg:#fbfbfa;   /* 微暖背景，不是死白 */
  /* ③ 间距系统（4px 基数）*/
  --sp-1:4px; --sp-2:8px; --sp-3:12px; --sp-4:16px; --sp-5:20px; --sp-6:24px; --sp-8:32px;
  --container:1280px; --measure:65ch;
}
/* 缓动统一（覆盖旧的 .32,.72 / .2,.8）*/
button,.btn,[onclick],.card,.book,.s-item,.stat,.mi,a,input,select,textarea{
  transition-timing-function:var(--ease-out-quart) !important; }
button,.btn,[onclick]{ transition-duration:var(--dur-micro) !important; }
.card,.book,.s-item,.stat{ transition-duration:var(--dur-ui) !important; }
.modal,.modal .m-body,.drawer{ transition-duration:var(--dur-page) !important; }
/* 纯黑 → 苹果黑 */
[style*="#000"],body{ color:inherit }
/* 阅读宽度 + 容器（长文 65ch，页面 1280px）*/
.read-content p,.rd-page p,.intro p{ max-width:var(--measure); line-height:1.85; }
.hs-wrap,.tk-hero-inner,.content-inner, #page-home > .sec, #page-home > .card{ max-width:var(--container); margin-left:auto; margin-right:auto; }
/* 卡片不嵌套（skill 反模式：卡片套卡片）基于容器是卡片时压平内层 */
.card .card{ background:transparent; border:none; box-shadow:none; padding:0; }
/* 空状态统一样式 */
.empty-state{ text-align:center; padding:40px 20px; color:var(--n-500); line-height:1.9; }
.empty-state b{ color:var(--n-700); display:block; margin-bottom:6px; font-size:15px; }
/* 骨架屏（替代转圈，skill 推荐）*/
.skel{ background:linear-gradient(90deg,#f0f0f2 25%,#f7f7f9 37%,#f0f0f2 63%);
  background-size:400% 100%; animation:skel 1.4s ease infinite; border-radius:8px; min-height:16px; }
@keyframes skel{ 0%{background-position:100% 50%} 100%{background-position:0 50%} }
@media (prefers-reduced-motion:reduce){
  *{ animation-duration:.01ms !important; transition-duration:.01ms !important; } }
/* 加载中的按钮文案（skill：说明在做什么，不要"请稍候"）*/
button[disabled]{ opacity:.55; cursor:default; }
'''
CSS = CSS + '</style><link rel="stylesheet" href="data/upgrade2.css?v=' + ASSET_VERSION + '"><style>'
CSS = CSS + '</style><link rel="stylesheet" href="data/library2.css?v=' + ASSET_VERSION + '"><style>'
CSS = CSS + '</style><link rel="stylesheet" href="data/paper-v3.css?v=' + ASSET_VERSION + '"><style>'

# ===== 首页视觉收口：清晰的首屏层级、统一的暖色品牌与响应式留白 =====
CSS = CSS + r'''
/* 顶部公告静态呈现，避免长文字被跑马灯截断 */
.donbar{margin:0!important;padding:9px 16px!important;background:#f5f4ef!important;color:#68675f!important;border-bottom:1px solid #e9e7df!important;font-size:12px!important;font-weight:500!important;white-space:normal!important;overflow:visible!important;line-height:1.6}
.donbar-in{display:block!important;padding:0!important;animation:none!important;text-align:center;max-width:1240px;margin:auto}
/* 首页首屏统一为一块品牌主视觉 */
.tk-hero{width:min(1100px,calc(100% - 36px))!important;max-width:1100px!important;margin:24px auto 10px!important;padding:30px 34px 26px!important;text-align:left!important;border:1px solid rgba(246,231,180,.18);border-radius:24px;background:radial-gradient(ellipse at 86% 0%,rgba(233,201,107,.2),transparent 35%),linear-gradient(135deg,#0b3b2d 0%,#14553d 58%,#0d3f30 100%);box-shadow:0 16px 40px rgba(13,63,48,.16);position:relative;overflow:hidden}
.tk-hero:after{content:'☾';position:absolute;right:42px;top:18px;color:rgba(246,231,180,.16);font-size:112px;line-height:1;pointer-events:none}
.tk-hero>div:first-child{position:relative;z-index:1;font-size:clamp(27px,3.6vw,42px)!important;font-weight:800!important;line-height:1.28!important;letter-spacing:-.8px!important;color:#fff!important}
.tk-hero>div:nth-child(2){position:relative;z-index:1;color:rgba(255,255,255,.78)!important;font-size:14px!important;line-height:1.9!important;margin-top:9px!important}
.tk-acts{display:flex!important;position:relative;z-index:1;justify-content:flex-start!important;margin-top:18px!important}
.tk-acts span{padding:11px 18px!important;font-size:13.5px!important;font-weight:650!important;transition:transform .18s ease,background .18s ease}
.tk-acts span:active{transform:scale(.97)}
.tk-acts span:first-child,.tk-acts button:first-child{background:#f2d98d!important;color:#173c2e!important;box-shadow:0 5px 16px rgba(0,0,0,.14)}
.tk-acts span:nth-child(2){background:rgba(255,255,255,.08)!important;color:#fff!important;border:1px solid rgba(255,255,255,.38)!important}
/* 内容卡片使用统一宽度与节奏 */
.daily-quote{max-width:760px!important;margin:18px auto 22px!important;padding:0 18px}
.quote-card{padding:22px 24px!important}
.q-ar{font-size:clamp(23px,3vw,30px)!important;line-height:1.9!important}
.hero{width:calc(100% - 36px)!important;margin:14px auto 12px!important}
#homeShelves{max-width:1440px!important;margin:10px auto 0!important}
#homeShelves .hs-hero{padding-top:20px!important}
@media(max-width:600px){
 .tk-hero{width:calc(100% - 24px)!important;margin:14px auto 8px!important;padding:24px 20px 20px!important;border-radius:20px}
 .tk-hero:after{right:16px;top:18px;font-size:82px}
 .tk-hero>div:first-child{font-size:29px!important;max-width:80%}
 .tk-hero>div:nth-child(2){font-size:13px!important;max-width:85%}
 .tk-acts{gap:8px!important;margin-top:15px!important}
 .tk-acts span{padding:10px 14px!important;font-size:12.5px!important}
 .daily-quote{margin:13px auto 16px!important;padding:0 12px}
 .quote-card{padding:18px!important}
 .hero{width:calc(100% - 24px)!important}
}
@media(prefers-reduced-motion:reduce){.tk-acts span{transition:none}}
'''

try:
    CSS = CSS + open('data/paper-v3.css', encoding='utf-8').read()
    pass  # mobile.css 已回滚（2026-09-21 手机排版乱了，先撤掉）
except Exception as _eTHEME:
    print('[主题CSS读取失败]', _eTHEME)
# PAPER_THEME inlined
CSS = CSS + r'''
/* ===== Apple HIG 精修层（ui-designer skill · apple-hig）===== */
:root{
  --hig-blue:#007AFF; --hig-blue-press:#0051D5; --hig-green:#34C759;
  --hig-red:#FF3B30; --hig-orange:#FF9500; --hig-gray1:#8E8E93;
  --hig-gray5:#E5E5EA; --hig-gray6:#F2F2F7;
  --hig-r-s:8px; --hig-r-m:10px; --hig-r-l:12px; --hig-r-xl:16px;
  --hig-sh-1:0 1px 3px rgba(0,0,0,.08),0 1px 2px rgba(0,0,0,.06);
  --hig-sh-2:0 3px 6px rgba(0,0,0,.10),0 2px 4px rgba(0,0,0,.07);
  --hig-sh-3:0 10px 20px rgba(0,0,0,.10),0 3px 6px rgba(0,0,0,.06);
}
/* ① 触控目标 ≥44pt + 按压反馈 */
button,.btn,.h6-cat,.s-btns button,[onclick]{ min-height:44px; }
button:active,.btn:active,[onclick]:active{ transform:scale(.97); }
@media (hover:hover){ button:hover,.btn:hover{ filter:brightness(.97); } }
/* 焦点环（键盘可达性）*/
button:focus-visible,a:focus-visible,input:focus-visible,select:focus-visible,textarea:focus-visible{
  outline:none; box-shadow:0 0 0 3.5px rgba(0,122,255,.35); border-radius:var(--hig-r-m); }
/* ② 字号梯度（HIG Dynamic Type）*/
.card h3{ font-size:22px; font-weight:600; letter-spacing:-.3px; }   /* Title 2 */
.tk-hero .tk-t1,.tk-hero h1{ font-size:34px; font-weight:700; letter-spacing:-.8px; }  /* Large Title */
.hs-sec-t,.hs-row-t{ font-size:17px; font-weight:600; }              /* Headline */
body{ -webkit-font-smoothing:antialiased; }
/* ③ 毛玻璃导航（vibrancy）*/
.side,.hdr,.topbar,.tk-hero,.tabbar{
  backdrop-filter:saturate(180%) blur(20px); -webkit-backdrop-filter:saturate(180%) blur(20px); }
@media (prefers-reduced-motion:no-preference){
  .card,.stat,.book,.s-item{ transition:transform .22s cubic-bezier(.32,.72,0,1), box-shadow .22s ease; }
  .card:active,.book:active{ transform:scale(.985); }
}
/* ④ 分层阴影（depth）*/
.card{ box-shadow:var(--hig-sh-1); border-radius:var(--hig-r-xl); }
.card:hover{ box-shadow:var(--hig-sh-2); }
.modal .m-body,.modal.show{ box-shadow:var(--hig-sh-3); }
/* ⑤ 圆角统一 */
.stat,.book,.s-item,.it{ border-radius:var(--hig-r-l); }
input,select,textarea{ border-radius:var(--hig-r-m); }
/* ⑥ 列表行（HIG List Item）*/
.it{ min-height:44px; align-items:center; border-bottom:1px solid rgba(199,199,204,.30); }
/* ⑦ 分隔线更柔和 */
hr,td,th{ border-color:rgba(199,199,204,.32); }
'''













# ===== v2.9 界面与体验升级层（纯 CSS 覆盖，末尾追加，不改结构）=====
CSS += '''
:root{
  --fs-cap:11px; --fs-sm:12px; --fs-body:13.5px; --fs-tt:16px;
  --muted:#6d7471; --muted-2:#7d847f;
  --card-border:rgba(201,168,76,.16);
  --card-shadow:0 4px 16px rgba(15,61,49,.06),0 1px 2px rgba(15,61,49,.05);
  --card-shadow-h:0 14px 34px rgba(15,61,49,.13),0 2px 6px rgba(15,61,49,.06);
}
/* 1) 文本层级与对比度 */
.list-head .tt,.daily-info .d-row .lb,.daily-goal .g-head{color:var(--muted);font-size:var(--fs-sm)}
.list-head .tt{font-weight:600}
.sec-title h2{font-size:var(--fs-tt);letter-spacing:.2px}
.s-card .s-en{font-size:var(--fs-sm);color:#5f6862;line-height:1.5}
.s-card .s-cn{font-size:var(--fs-sm);color:#155744;line-height:1.55}
.s-card .s-py{font-size:var(--fs-sm);color:#6f6a58}
.quote-card .q-cn{font-size:var(--fs-sm)}
.quote-card .q-en{font-size:var(--fs-cap)}
.quote-card .q-src{font-size:10.5px}
.cat-tab .ct-nm{font-size:var(--fs-cap);font-weight:700}
.cat-tab .ct-ar{font-size:10.5px;color:var(--muted)}
.entr .e-tx b{font-size:var(--fs-body)}
.entr .e-tx span{font-size:var(--fs-cap);color:var(--muted)}
.stat-card .lb{font-size:var(--fs-cap);font-weight:600;color:var(--muted);letter-spacing:.2px}
.ef-msg .tr,.m-count,.v-item .v-f{font-size:var(--fs-sm)}
/* 2) 卡片与按钮质感 */
.s-card{border:1px solid var(--card-border);box-shadow:var(--card-shadow);border-radius:16px}
.s-card .s-tr{border-top-style:solid;border-top-color:rgba(201,168,76,.18)}
.s-card .s-btn:active{transform:scale(.9)}
.stat-card,.entr,.daily-card,.quote-card{box-shadow:var(--card-shadow)}
.act-btn{box-shadow:0 3px 10px rgba(15,61,49,.18),inset 0 1px 0 rgba(232,212,139,.18);letter-spacing:.3px}
.tabbar{box-shadow:0 -8px 28px rgba(15,61,49,.10);border-top:1px solid rgba(201,168,76,.20)}
/* ==== nur-ux 1 END ==== */
'''

# ===== v2.9 界面与体验升级层（第二段：弹窗动效 / 空状态 / 宽屏版式）=====
CSS += '''
/* 3) 弹窗动效 */
.modal.show{animation:backdropIn .22s ease}
@keyframes backdropIn{from{opacity:0}to{opacity:1}}
.modal.show .m-head{animation:modalIn .28s cubic-bezier(.2,.8,.2,1)}
.modal.show .m-body{animation:bodyIn .3s cubic-bezier(.2,.8,.2,1)}
@keyframes bodyIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
.modal .m-close{width:34px;height:34px;border-radius:50%;transition:transform .15s,color .15s}
.modal .m-close:hover{color:#fff;transform:rotate(90deg)}
@media(min-width:820px){
  .modal{backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px)}
  .modal.show{justify-content:center;padding:20px 0}
  .modal.show .m-head,.modal.show .m-body{width:min(760px,92vw);margin-left:auto;margin-right:auto}
  .modal.show .m-body{border-radius:0 0 20px 20px;box-shadow:0 24px 60px rgba(0,0,0,.35)}
}
/* 4) 空状态：筛选后无可见句子时给出提示（:has 不支持则自动忽略） */
#sList:not(:has(.s-card:not([style*="display: none"]))):not(:empty)::after{
  content:'这里还没有内容，试试切换筛选，或先收藏 / 学习一些句子';
  display:block;text-align:center;color:var(--muted);
  font-size:var(--fs-sm);line-height:1.9;padding:28px 16px;
}
/* 5) 宽屏（≥1024px）版式：从 640px 加宽，充分利用桌面空间 */
@media(min-width:1024px){
  body{font-size:14px}
  .daily-mod,.stat-row,.sec-title,.cat-scroll,.list-wrap,.daily-quote,.ps-banner,.ps-ai,.cat-row{max-width:880px}
  #dueBar,#miniChart,#meSec{max-width:880px!important}
  .entr-row{grid-template-columns:repeat(4,1fr);max-width:880px}
  .action-row{grid-template-columns:repeat(auto-fill,minmax(118px,1fr));max-width:880px}
  .s-card{padding:16px 18px}
  .s-card .s-ar{font-size:19px}
  .stat-card{padding:16px 12px}
}
@media(hover:hover){.s-card:hover{box-shadow:var(--card-shadow-h)}}
@media(prefers-reduced-motion:reduce){.modal.show,.modal.show .m-head,.modal.show .m-body{animation:none!important}}
/* ==== nur-ux 2 END ==== */
'''

# ===== v3.0 视觉重做层：更轻、更精致的材质与节奏 =====
CSS += '''
/* 1) 页面背景：极淡几何光晕，增加纵深（不抢内容） */
body{background-image:
  radial-gradient(1100px 420px at 50% -140px, rgba(201,168,76,.10), transparent 70%),
  radial-gradient(760px 360px at 100% 28%, rgba(26,92,74,.05), transparent 70%);
  background-attachment:fixed}
/* 2) 功能瓦片：从「重色块」改为轻卡片 + 金线描边 */
.action-row .act-btn{background:linear-gradient(160deg,#ffffff,#fdfaf3);color:var(--green-d);
  border:1px solid rgba(201,168,76,.28);box-shadow:0 3px 12px rgba(15,61,49,.055);font-weight:650;letter-spacing:.2px}
@media(hover:hover){.action-row .act-btn:hover{transform:translateY(-2px);box-shadow:0 10px 24px rgba(15,61,49,.12);border-color:rgba(201,168,76,.5)}}
.action-row .act-btn:active{transform:scale(.97)}
/* 3) 区块标题层级 */
.sec-title{margin:26px auto 12px}
.sec-title h2{font-size:15px;font-weight:800;letter-spacing:.8px;color:var(--green-d)}
.sec-title h2::before{content:'';display:inline-block;width:7px;height:7px;border-radius:2px;
  background:linear-gradient(135deg,var(--gold),var(--gold-l));margin-right:9px;vertical-align:middle;transform:rotate(45deg)}
/* 4) 入口卡质感 */
.entr{border-radius:16px;border:1px solid rgba(201,168,76,.20);background:linear-gradient(165deg,#ffffff,#fbf8f1)}
.entr .e-ic{font-size:22px}
/* 5) 阴影统一 */
.daily-card,.quote-card,.stat-card{box-shadow:0 6px 20px rgba(15,61,49,.07)}
/* 6) 底部导航：选中指示条 */
.tabbar .tb{position:relative}
.tabbar .tb .t-nm{letter-spacing:.3px}
.tabbar .tb.on::after{content:'';position:absolute;top:0;left:50%;transform:translateX(-50%);
  width:22px;height:3px;border-radius:0 0 3px 3px;background:linear-gradient(90deg,var(--gold),var(--gold-l))}
'''

# ===== v3.1 深色模式 + 外观切换 =====
CSS += '''
/* 外观切换按钮 */
.theme-opts{display:flex;gap:8px}
.theme-opt{flex:1;padding:10px 6px;border-radius:12px;border:1px solid rgba(201,168,76,.28);
  background:linear-gradient(160deg,#ffffff,#fdfaf3);color:#4a4a42;font-size:12px;font-weight:700;
  cursor:pointer;transition:transform .16s,border-color .18s,box-shadow .2s}
.theme-opt:hover{border-color:rgba(201,168,76,.55)}
.theme-opt:active{transform:scale(.97)}
.theme-opt.on{background:linear-gradient(135deg,var(--green-d),var(--green));color:var(--gold-l);
  border-color:rgba(201,168,76,.5);box-shadow:0 4px 14px rgba(15,61,49,.22)}
/* —— 深色主题变量 —— */
html[data-theme="dark"]{color-scheme:dark;
  --cream:#0d1210;--card:#161d18;--white:#161d18;
  --ink:#e9e5da;--muted:#9aa39b;--muted-2:#8b948c;
  --glass:rgba(22,29,24,.62);
  --card-border:rgba(201,168,76,.20);--line:rgba(201,168,76,.24);
  --sh-1:0 2px 10px rgba(0,0,0,.45);--sh-2:0 12px 34px rgba(0,0,0,.6);
  --card-shadow:0 4px 16px rgba(0,0,0,.45),0 1px 2px rgba(0,0,0,.4);
  --card-shadow-h:0 14px 34px rgba(0,0,0,.6),0 2px 6px rgba(0,0,0,.4);}
html[data-theme="dark"] body{
  background:
    radial-gradient(1100px 420px at 50% -140px, rgba(201,168,76,.10), transparent 70%),
    radial-gradient(760px 360px at 100% 28%, rgba(26,92,74,.12), transparent 70%),
    linear-gradient(180deg,#111713 0%,#0a0f0c 100%);
  background-attachment:fixed;color:var(--ink)}
html[data-theme="dark"] .bg-pattern{opacity:.14}
html[data-theme="dark"] .hdr .logo-sub{color:rgba(233,229,218,.72)}
/* 卡片/按钮材质归一到深色 */
html[data-theme="dark"] .entr{background:linear-gradient(165deg,#1a221c,#141b16);border-color:rgba(201,168,76,.16)}
html[data-theme="dark"] .stat-card{background:linear-gradient(160deg,#1a221c,#151c17);border-color:rgba(201,168,76,.18)}
html[data-theme="dark"] .action-row .act-btn,html[data-theme="dark"] .theme-opt{background:linear-gradient(160deg,#1b241d,#161d18);color:var(--gold-l);border-color:rgba(201,168,76,.30)}
html[data-theme="dark"] .flash-back{background:#161d18}
html[data-theme="dark"] .quiz-opt{background:#1b241d;color:var(--ink)}
html[data-theme="dark"] .quiz-opt:hover{border-color:var(--gold);background:rgba(201,168,76,.1)}
html[data-theme="dark"] .modal .m-search,html[data-theme="dark"] .m-count,html[data-theme="dark"] .v-item,html[data-theme="dark"] .s-item,html[data-theme="dark"] .s-btn,html[data-theme="dark"] .ef-inp,html[data-theme="dark"] .ef-msg.bot .bb{background:#161d18}
html[data-theme="dark"] .modal .m-search input,html[data-theme="dark"] .ef-inp input{background:#0f1512;border-color:#2b352d;color:var(--ink)}
html[data-theme="dark"] .m-count,html[data-theme="dark"] .ef-msg.bot .bb,html[data-theme="dark"] .ef-inp{border-color:#2b352d}
html[data-theme="dark"] .elf-body{background:#101612}
html[data-theme="dark"] .tabbar{background:rgba(16,22,18,.9);border-top-color:rgba(201,168,76,.18)}
html[data-theme="dark"] .decomp-box{background:rgba(201,168,76,.06)}
html[data-theme="dark"] input,html[data-theme="dark"] textarea,html[data-theme="dark"] select{background:#0f1512;color:var(--ink)}
html[data-theme="dark"] input::placeholder,html[data-theme="dark"] textarea::placeholder{color:#7d877f}
/* 深色下的文字对比度 */
html[data-theme="dark"] .s-card .s-ar,html[data-theme="dark"] .s-item .s-ar,html[data-theme="dark"] .v-item .v-ar,html[data-theme="dark"] .book-para{color:#efe9da}
html[data-theme="dark"] .s-card .s-en,html[data-theme="dark"] .s-card .s-py{color:#9aa39b}
html[data-theme="dark"] .s-card .s-cn{color:#7fcfa9}
html[data-theme="dark"] .sec-title h2{color:var(--gold-l)}
html[data-theme="dark"] .flash-cn,html[data-theme="dark"] .book-para-cn{color:var(--ink)}
html[data-theme="dark"] .flash-en{color:#8fb6d6}
html[data-theme="dark"] .cp-btn{color:var(--gold-l)}
/* 内联浅底 / 深字兜底（!important 可覆盖行内样式） */
html[data-theme="dark"] [style*="background:#fff"],html[data-theme="dark"] [style*="background: #fff"],
html[data-theme="dark"] [style*="background:#ffffff"],html[data-theme="dark"] [style*="background:#fdf6e3"],
html[data-theme="dark"] [style*="background:#f9f7f2"],html[data-theme="dark"] [style*="background:#fff8e6"],
html[data-theme="dark"] [style*="background:#fffdf8"],html[data-theme="dark"] [style*="background:#fbf7ee"],
html[data-theme="dark"] [style*="background:#fbf8f1"],html[data-theme="dark"] [style*="background:#fdfaf3"],
html[data-theme="dark"] [style*="background:#f9f5ec"]{background:#161d18!important}
html[data-theme="dark"] [style*="color:#333"],html[data-theme="dark"] [style*="color:#555"],
html[data-theme="dark"] [style*="color:#666"],html[data-theme="dark"] [style*="color:#999"],
html[data-theme="dark"] [style*="color:#8a9c8f"],html[data-theme="dark"] [style*="color:#0f3d31"],
html[data-theme="dark"] [style*="color:#1c2b26"],html[data-theme="dark"] [style*="color:#155744"],
html[data-theme="dark"] [style*="color:#5f6862"],html[data-theme="dark"] [style*="color:#6f6a58"]{color:var(--ink)!important}
html[data-theme="dark"] [style*="border:1px solid #e0dccf"],html[data-theme="dark"] [style*="border:1px solid #ddd"],
html[data-theme="dark"] [style*="border:1px solid #eee"]{border-color:#2b352d!important}
'''

# ===== v3.2 弹窗交互与无障碍增强（纯 CSS） =====
CSS += '''
.modal .m-body{overscroll-behavior:contain;-webkit-overflow-scrolling:touch;scrollbar-gutter:stable}
body.modal-open{overflow:hidden}
.modal .m-close{outline:none;display:flex;align-items:center;justify-content:center}
.modal .m-close:focus-visible{outline:2px solid var(--gold-l);outline-offset:2px;color:#fff}
/* 触控热区：主操作按钮不小于 44px */
.action-row .act-btn{min-height:44px}
.ai-chips{display:flex;gap:6px;padding:0 12px 8px;flex-wrap:wrap}
.ai-chips .s-btn{width:auto;padding:7px 11px;font-size:11px}
@media (prefers-reduced-motion:reduce){
  .modal.show,.modal.show .m-head,.modal.show .m-body{animation:none!important}
}
'''

# ===== v4.0 「المكتبة」库式界面（对齐 المكتبة الشاملة 的观感）=====
CSS += '''
:root{--lib-bg:#f8f6f0;--lib-line:rgba(15,61,49,.10);--lib-ink:#12352b}
body{background:var(--lib-bg);background-image:none}
/* 顶栏：扁平色带 + 金色底线（去掉拱门/光晕/渐变字） */
.hdr{padding:15px 16px 13px;background:#0f3d31;border-bottom:3px solid var(--gold)}
.hdr .glow,.hdr .arch-wrap{display:none}
.hdr .logo{background:none!important;-webkit-text-fill-color:#f0e3b4!important;color:#f0e3b4;font-size:25px;letter-spacing:.5px;text-shadow:none;font-weight:700}
.hdr .logo-sub{color:rgba(255,255,255,.72);letter-spacing:1.4px;font-size:11.5px;margin-top:3px}
.hdr .zh{color:rgba(240,227,180,.72);font-size:10.5px;margin-top:5px;letter-spacing:1px}
/* 库式索引行：工具/入口不再用卡片网格 */
.action-row,.entr-row{grid-template-columns:1fr 1fr;gap:0 18px;max-width:880px;margin-top:4px}
.action-row .act-btn,.entr{
  display:flex!important;align-items:center;gap:9px;text-align:left!important;justify-content:flex-start!important;
  background:transparent!important;border:0;border-bottom:1px solid var(--lib-line);border-radius:0!important;
  box-shadow:none!important;padding:12px 4px;min-height:48px;font-size:13px;font-weight:600;color:var(--lib-ink)}
.entr{flex-direction:row!important;padding:12px 4px}
.entr .e-tx{flex:1;min-width:0}
.entr .e-tx b{font-weight:600;font-size:13px}
.entr .e-tx span{display:block;font-size:10.5px;color:var(--muted);margin-top:1px}
.entr .e-go{color:var(--muted);font-size:14px;opacity:.55}
.action-row .act-btn[style*="c9a84c"]{grid-column:1/-1!important;background:linear-gradient(135deg,#c9a84c,#a8892e)!important;
  color:#0f3d31!important;border-bottom:0;border-radius:10px!important;justify-content:center!important;font-weight:700;margin:4px 0 8px}
@media(hover:hover){.action-row .act-btn:hover,.entr:hover{transform:none!important;background:rgba(15,61,49,.04)!important;box-shadow:none!important}}
/* 卡片扁平化 */
.daily-card,.quote-card,.stat-card{box-shadow:none!important;border:1px solid var(--lib-line);border-radius:10px!important}
.stat-card{background:#fff}
/* 小节标题：细下划线，像书库目录 */
.sec-title{margin:22px auto 4px;padding-bottom:6px;border-bottom:1px solid var(--lib-line)}
.sec-title h2{font-size:13px;letter-spacing:1.1px;font-weight:700}
.sec-title h2::before{width:5px;height:5px;border-radius:1px;margin-right:7px}
/* 底部导航：扁平细线 */
.tabbar{background:rgba(255,255,255,.97);border-top:1px solid var(--lib-line);box-shadow:none!important}
.tabbar .tb .t-nm{font-size:11px;font-weight:600}
/* 深色适配 */
html[data-theme="dark"] body{background:#0e1411}
html[data-theme="dark"] .action-row .act-btn,html[data-theme="dark"] .entr{color:#e9e4d6;border-bottom-color:rgba(201,168,76,.18)}
html[data-theme="dark"] .stat-card{background:#151c17}
html[data-theme="dark"] .sec-title{border-bottom-color:rgba(201,168,76,.18)}
'''

# ===== v5.0 「书库」层：导览条 + 搜索 + 书卡（对齐 جامع الكتب）=====
CSS += '''
.lib-nav{display:flex;gap:2px;overflow-x:auto;background:#fff;border-bottom:1px solid var(--lib-line);
  max-width:880px;margin:0 auto;padding:0 10px;-webkit-overflow-scrolling:touch;scrollbar-width:none}
.lib-nav::-webkit-scrollbar{display:none}
.lib-nav button{flex:0 0 auto;border:0;background:none;padding:12px 13px;font-size:13px;font-weight:600;color:#4a5750;cursor:pointer;border-bottom:2px solid transparent;transition:color .15s,border-color .15s}
.lib-nav button:hover{color:var(--green-d);border-bottom-color:var(--gold)}
.lib-search{max-width:880px;margin:10px auto 0;padding:0 16px;box-sizing:border-box}
.lib-search>span{position:absolute;margin:12px 0 0 14px;font-size:13px;opacity:.55;pointer-events:none}
.lib-search input{width:100%;height:42px;border:1px solid var(--lib-line);border-radius:999px;background:#fff;
  padding:0 16px 0 38px;font-size:13px;outline:none;box-sizing:border-box;transition:border-color .2s,box-shadow .2s}
.lib-search input:focus{border-color:rgba(201,168,76,.75);box-shadow:0 0 0 3px rgba(201,168,76,.14)}
/* 入口卡 → 书卡（上封面 下标题） */
.entr-row{grid-template-columns:repeat(3,1fr)!important;gap:12px!important;max-width:880px;margin-top:10px}
.entr{display:block!important;background:#fff!important;border:1px solid var(--lib-line)!important;border-radius:10px!important;
  padding:0!important;overflow:hidden;text-align:center;min-height:0}
.entr .e-ic{display:block!important;height:80px;line-height:80px;font-size:30px;margin:0!important;width:auto!important;
  background:linear-gradient(160deg,#14503e,#0e3529);color:#e8d48b;border-radius:0!important}
.entr .e-tx{padding:9px 7px 11px;flex:none!important}
.entr .e-tx b{display:block;font-size:12.5px;color:var(--green-d);font-weight:700;line-height:1.3}
.entr .e-tx span{display:block;font-size:9.5px;color:var(--muted);margin-top:3px;line-height:1.4}
.entr .e-go{display:none!important}
@media(hover:hover){.entr:hover{transform:translateY(-2px)!important;box-shadow:0 8px 20px rgba(15,61,49,.10)!important;background:#fff!important}}
@media(max-width:420px){.entr-row{grid-template-columns:repeat(2,1fr)!important}}
html[data-theme="dark"] .lib-nav{background:#141b16;border-bottom-color:rgba(201,168,76,.18)}
html[data-theme="dark"] .lib-nav button{color:#a9b3ab}
html[data-theme="dark"] .lib-search input{background:#141b16;color:#e9e4d6;border-color:rgba(201,168,76,.2)}
html[data-theme="dark"] .entr{background:#141b16!important}
'''

# ===== v6.0 桌面书库（左侧分类栏 + 书封网格）=====
CSS += '''
#mCat .m-body{background:#f4f5f4;padding:0}
.bk-wrap{display:flex;min-height:100%;align-items:stretch}
.bk-side{width:192px;flex:0 0 192px;background:#fff;border-right:1px solid rgba(15,61,49,.10);padding:10px 0;overflow-y:auto}
.bk-side-h{font-size:11px;font-weight:700;color:#8a8f8c;padding:6px 14px 8px;letter-spacing:.5px}
.bk-cat{display:flex;justify-content:space-between;align-items:center;gap:6px;width:100%;border:0;background:none;
  padding:9px 14px;font-size:12.5px;color:#3d4a44;cursor:pointer;text-align:left;border-left:3px solid transparent}
.bk-cat i{font-style:normal;font-size:10px;color:#b3b8b5}
.bk-cat:hover{background:rgba(26,92,74,.05)}
.bk-cat.on{background:rgba(26,92,74,.08);border-left-color:#1a5c4a;color:#0f3d31;font-weight:700}
.bk-main{flex:1;min-width:0;padding:12px 16px 24px}
.bk-top{display:flex;align-items:center;gap:12px;margin-bottom:14px}
.bk-title{font-size:15px;font-weight:800;color:#12352b;white-space:nowrap}
.bk-q{flex:1;height:38px;border:1px solid rgba(15,61,49,.14);border-radius:8px;padding:0 12px;font-size:12.5px;background:#fff;outline:none;box-sizing:border-box}
.bk-q:focus{border-color:#1a5c4a;box-shadow:0 0 0 3px rgba(26,92,74,.10)}
.bk-count{font-size:11px;color:#8a8f8c;margin-bottom:10px}
.bk-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(132px,1fr));gap:14px}
.bk-card{cursor:pointer}
.bk-cover{position:relative;aspect-ratio:3/4;border-radius:6px 10px 10px 6px;padding:12px 12px 12px 16px;overflow:hidden;
  display:flex;align-items:flex-start;box-shadow:0 4px 14px rgba(15,61,49,.14);transition:transform .16s,box-shadow .16s}
.bk-cover::before{content:'';position:absolute;left:6px;top:0;bottom:0;width:2px;background:rgba(255,255,255,.25)}
.bk-cover .bk-t{color:#fff;font-family:var(--ar-font);font-size:13px;line-height:1.65;font-weight:700;direction:rtl;text-align:right;width:100%;
  display:-webkit-box;-webkit-line-clamp:4;-webkit-box-orient:vertical;overflow:hidden;text-shadow:0 1px 6px rgba(0,0,0,.3)}
.bk-meta{padding:7px 2px 0}
.bk-meta b{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;font-size:11.5px;font-weight:600;color:#1c2b26;direction:rtl;text-align:right;line-height:1.45}
.bk-meta span{display:block;font-size:10px;color:#8a8f8c;margin-top:3px;direction:rtl;text-align:right}
.bk-meta .bk-source{color:#4f806d;font-size:9px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.bk-card-actions{display:flex;gap:4px;margin-top:6px;direction:ltr}
.bk-in{border:1px solid rgba(26,92,74,.22);border-radius:7px;background:rgba(26,92,74,.06);color:#1a5c4a;padding:4px 6px;font-size:9px;cursor:pointer;white-space:nowrap}
.bk-in:hover{background:rgba(26,92,74,.13);border-color:rgba(26,92,74,.42)}
.bk-cat-discipline{font-size:11.5px}
@media(hover:hover){.bk-card:hover .bk-cover{transform:translateY(-3px);box-shadow:0 12px 26px rgba(15,61,49,.20)}}
@media(max-width:760px){.bk-side{display:none}.bk-grid{grid-template-columns:repeat(auto-fill,minmax(110px,1fr));gap:10px}}
html[data-theme="dark"] #mCat .m-body{background:#0e1411}
html[data-theme="dark"] .bk-side{background:#141b16;border-right-color:rgba(201,168,76,.18)}
html[data-theme="dark"] .bk-cat{color:#c9d1cb}
html[data-theme="dark"] .bk-meta b{color:#e9e4d6}
html[data-theme="dark"] .bk-meta .bk-source{color:#8fc0a5}
html[data-theme="dark"] .bk-in{background:rgba(201,168,76,.10);border-color:rgba(201,168,76,.26);color:#e5cf8b}
html[data-theme="dark"] .bk-q{background:#141b16;color:#e9e4d6;border-color:rgba(201,168,76,.2)}
html[data-theme="dark"] .bk-title{color:#e9e4d6}
/* 世界典籍 */
#mH6 .m-body{background:#f4f5f4}
.h6-total{font-size:12px;color:#8a8f8c;margin-bottom:12px}
html[data-theme="dark"] #mH6 .m-body{background:#0e1411}
/* 阅读器 */
#mReader .m-body{background:#f4f2ec;padding:0}
.bk-badge{display:inline-block;font-size:9.5px;color:#0f3d31;background:rgba(201,168,76,.30);border-radius:4px;padding:1px 5px;margin-top:4px}
.rd-bar{display:flex;align-items:center;justify-content:center;gap:10px;padding:9px 10px;background:#fff;border-bottom:1px solid rgba(15,61,49,.08);position:sticky;top:0;z-index:3;flex-wrap:wrap}
.rd-pos{font-size:12px;color:#8a8f8c;min-width:96px;text-align:center}
.rd-page{font-family:var(--ar-font);font-size:17.5px;line-height:2.15;direction:rtl;text-align:right;color:#1c2b26;
  background:#fff;margin:10px 12px;padding:20px 22px;border:1px solid rgba(15,61,49,.07);border-radius:10px;
  white-space:pre-wrap;word-break:break-word;box-shadow:0 2px 10px rgba(15,61,49,.05)}
html[data-theme="dark"] #mReader .m-body{background:#0e1411}
html[data-theme="dark"] .rd-page{background:#141b16;color:#ece6d8;border-color:rgba(201,168,76,.16)}
html[data-theme="dark"] .rd-bar{background:#141b16;border-bottom-color:rgba(201,168,76,.16)}
'''

# ===== v7.0 YouTube 风：浅色中性主题 + 内容流（去绿）=====
CSS += '''
:root{
  --ink:#0f0f0f; --muted:#606060; --line:#e5e5e5; --lib-bg:#f9f9f9; --lib-line:#e8e8e8; --lib-ink:#0f0f0f;
  --accent:#1a5c96; --acc2:#123f68;
}
body{background:#f9f9f9!important;color:var(--ink);background-image:none!important}
/* 顶栏：白底细线，左对齐 */
.hdr{background:#fff!important;border-bottom:1px solid var(--line)!important;padding:11px 16px!important;
  text-align:left!important;display:flex;align-items:center;gap:10px;border-top:0!important}
.hdr .logo{color:var(--ink)!important;-webkit-text-fill-color:var(--ink)!important;font-size:19px!important;letter-spacing:0;font-weight:800;background:none!important}
.hdr .logo-sub{color:var(--muted)!important;font-size:10.5px;margin-top:0!important;letter-spacing:.3px}
.hdr .zh{color:var(--muted)!important;font-size:9.5px;margin-top:0!important;letter-spacing:.2px;display:block}
.hdr::after{content:'حامل المصباح';margin-left:auto;font-family:var(--ar-font);font-size:13px;color:var(--muted)}
/* 导览条 -> 胶囊 chips */
.lib-nav{background:transparent!important;border:0!important;max-width:1100px;padding:10px 16px 2px!important;gap:8px!important}
.lib-nav button{border:1px solid var(--line)!important;background:#fff!important;border-radius:999px!important;
  padding:7px 15px!important;font-size:12.5px!important;color:var(--ink)!important;font-weight:500!important;border-bottom:1px solid var(--line)!important}
@media(hover:hover){.lib-nav button:hover{background:#f2f2f2!important;color:var(--ink)!important;border-color:#ccc!important}}
/* 搜索框 */
.lib-search{max-width:1100px!important}
.lib-search input{height:40px!important;border-radius:999px!important;background:#fff!important;border:1px solid var(--line)!important;font-size:13px}
.lib-search>span{margin-top:11px!important}
/* 内容流 */
.sec-title{max-width:1100px!important;border-bottom:0!important;margin:22px auto 10px!important;padding:0 16px!important}
.sec-title h2{font-size:15px!important;font-weight:800;color:var(--ink);letter-spacing:0!important}
.sec-title h2::before{display:none!important}
.feed{display:grid;grid-template-columns:repeat(auto-fill,minmax(228px,1fr));gap:16px;max-width:1100px;margin:0 auto;padding:0 16px}
.card{background:#fff;border:1px solid var(--line);border-radius:12px;overflow:hidden;cursor:pointer;
  transition:box-shadow .18s,transform .18s;display:flex;flex-direction:column}
.card .thumb{aspect-ratio:16/9;display:flex;align-items:center;justify-content:center;font-size:38px;color:#fff}
.card .cbody{padding:10px 12px 13px;flex:1}
.card .cbody b{display:block;font-size:13.5px;font-weight:700;color:var(--ink);line-height:1.4}
.card .cbody span{display:block;font-size:11px;color:var(--muted);margin-top:3px;line-height:1.55}
@media(hover:hover){.card:hover{box-shadow:0 8px 22px rgba(0,0,0,.12);transform:translateY(-2px)}}
.card:active{transform:scale(.985)}
/* 缩略图配色（蓝/紫/橙/青/铜…不再用绿） */
.t-1{background:linear-gradient(140deg,#1a5c96,#123f68)}
.t-2{background:linear-gradient(140deg,#6d4aa8,#42266b)}
.t-3{background:linear-gradient(140deg,#c05a2e,#8a3a1a)}
.t-4{background:linear-gradient(140deg,#1f7a8c,#0d4a56)}
.t-5{background:linear-gradient(140deg,#9a7b3f,#634c20)}
.t-6{background:linear-gradient(140deg,#2b6cb0,#1c4674)}
.t-7{background:linear-gradient(140deg,#b03a63,#74233f)}
.t-8{background:linear-gradient(140deg,#4a5568,#2d3748)}
.t-9{background:linear-gradient(140deg,#0e7490,#0b4f61)}
.t-10{background:linear-gradient(140deg,#b7791f,#7b4e12)}
.t-11{background:linear-gradient(140deg,#553c9a,#322659)}
.t-12{background:linear-gradient(140deg,#c05621,#8a3a15)}
.t-13{background:linear-gradient(140deg,#2c5282,#1a365d)}
.t-14{background:linear-gradient(140deg,#97266d,#63184a)}
.t-15{background:linear-gradient(140deg,#744210,#4a2c0a)}
.t-16{background:linear-gradient(140deg,#2a4365,#1a2b44)}
.t-17{background:linear-gradient(140deg,#8b6b3d,#5a4527)}
/* 其余模块：统一成白卡片 */
.ps-ai-card,.daily-card,.quote-card,.stat-card,.entr,.s-item,.v-item{box-shadow:none!important;border:1px solid var(--line)!important;border-radius:12px!important}
.ps-ai-card,.quote-card{background:#fff!important;color:var(--ink)!important}
.quote-card .q-ar{color:var(--ink)!important}
.quote-card .q-cn,.quote-card .q-src{color:var(--muted)!important}
.ps-banner{background:#fff!important;border:1px solid var(--line);color:var(--muted)!important}
/* 底部导航：中性 */
.tabbar{background:rgba(255,255,255,.98)!important;border-top:1px solid var(--line)!important}
.tabbar .tb{color:var(--muted)!important}
.tabbar .tb.on{color:var(--ink)!important}
.tabbar .tb.on::after{background:var(--accent)!important}
.tabbar .tb.on .t-ic{filter:none!important}
/* 书库卡片封面：改为多彩封面（不再千篇一律深绿） */
.bk-cover{box-shadow:0 3px 10px rgba(0,0,0,.14)!important}
.bk-cat.on{border-left-color:var(--accent)!important;color:var(--ink)!important}
.bk-title{color:var(--ink)!important}
#mCat .m-body,#mH6 .m-body{background:#f9f9f9!important}
/* 调色残留兜底：把旧绿换成中性 */
.act-btn{background:#fff!important;color:var(--ink)!important;border:1px solid var(--line)!important}
'''

# ===== v7.1 深色主题重做：中性灰（彻底去绿）+ 默认深色 =====
CSS += '''
html[data-theme="dark"]{
  --ink:#f1f1f1; --muted:#aaaaaa; --line:#303030; --bg:#0f0f0f; --card:#1a1a1a; --accent:#3ea6ff; --acc2:#1a5c96;
}
html[data-theme="dark"] body{background:#0f0f0f!important;color:#f1f1f1!important;background-image:none!important}
/* 顶栏 */
html[data-theme="dark"] .hdr{background:#181818!important;border-bottom:1px solid #303030!important}
html[data-theme="dark"] .hdr .logo,html[data-theme="dark"] .hdr .logo-sub,html[data-theme="dark"] .hdr .zh,html[data-theme="dark"] .hdr::after{color:#f1f1f1!important;-webkit-text-fill-color:#f1f1f1!important}
html[data-theme="dark"] .hdr .logo-sub,html[data-theme="dark"] .hdr .zh,html[data-theme="dark"] .hdr::after{color:#aaa!important;-webkit-text-fill-color:#aaa!important}
/* chips / 搜索 */
html[data-theme="dark"] .lib-nav button{background:#1f1f1f!important;border-color:#333!important;color:#e8e8e8!important}
html[data-theme="dark"] .lib-search input{background:#1f1f1f!important;border-color:#333!important;color:#f1f1f1!important}
html[data-theme="dark"] .lib-search input::placeholder{color:#888}
/* 卡片 */
html[data-theme="dark"] .card,html[data-theme="dark"] .ps-ai-card,html[data-theme="dark"] .daily-card,
html[data-theme="dark"] .stat-card,html[data-theme="dark"] .quote-card,html[data-theme="dark"] .s-card,
html[data-theme="dark"] .s-item,html[data-theme="dark"] .v-item,html[data-theme="dark"] .entr{
  background:#1a1a1a!important;border-color:#2e2e2e!important;color:#f1f1f1!important;box-shadow:none!important}
html[data-theme="dark"] .card .cbody b{color:#f1f1f1!important}
html[data-theme="dark"] .card .cbody span{color:#aaa!important}
html[data-theme="dark"] .s-card .s-ar,html[data-theme="dark"] .s-item .s-ar,html[data-theme="dark"] .quote-card .q-ar{
  color:#f1f1f1!important;-webkit-text-fill-color:#f1f1f1!important}
html[data-theme="dark"] .s-card .s-cn,html[data-theme="dark"] .s-card .s-en,html[data-theme="dark"] .s-card .s-py{color:#aaa!important}
html[data-theme="dark"] .quote-card .q-cn,html[data-theme="dark"] .quote-card .q-src{color:#bbb!important}
html[data-theme="dark"] .sec-title h2,html[data-theme="dark"] .sec-title{color:#f1f1f1!important;border-bottom-color:#2e2e2e!important}
html[data-theme="dark"] .ps-banner{background:#181818!important;border-color:#2e2e2e!important;color:#aaa!important}
/* 底部导航 */
html[data-theme="dark"] .tabbar{background:rgba(24,24,24,.98)!important;border-top-color:#2e2e2e!important;box-shadow:none!important}
html[data-theme="dark"] .tabbar .tb{color:#aaa!important}
html[data-theme="dark"] .tabbar .tb.on{color:#fff!important}
html[data-theme="dark"] .tabbar .tb.on::after{background:#3ea6ff!important}
html[data-theme="dark"] .tabbar .tb.on .t-ic{filter:none!important}
/* 弹层 */
html[data-theme="dark"] .modal .m-head{background:#1f1f1f!important;color:#f1f1f1!important;border-bottom:1px solid #2e2e2e}
html[data-theme="dark"] .modal .m-body{background:#121212!important;color:#f1f1f1!important}
html[data-theme="dark"] #mCat .m-body,html[data-theme="dark"] #mH6 .m-body,html[data-theme="dark"] #mReader .m-body{background:#121212!important}
html[data-theme="dark"] .modal .m-search{background:#1f1f1f!important}
/* 书库 */
html[data-theme="dark"] .bk-side{background:#181818!important;border-right-color:#2e2e2e!important}
html[data-theme="dark"] .bk-side-h{color:#888!important}
html[data-theme="dark"] .bk-cat{color:#ccc!important}
html[data-theme="dark"] .bk-cat i{color:#777!important}
html[data-theme="dark"] .bk-cat:hover{background:rgba(255,255,255,.05)!important}
html[data-theme="dark"] .bk-cat.on{background:rgba(62,166,255,.12)!important;border-left-color:#3ea6ff!important;color:#fff!important}
html[data-theme="dark"] .bk-title{color:#f1f1f1!important}
html[data-theme="dark"] .bk-meta b{color:#f1f1f1!important}
html[data-theme="dark"] .bk-meta span{color:#999!important}
html[data-theme="dark"] .bk-q{background:#1f1f1f!important;border-color:#333!important;color:#f1f1f1!important}
html[data-theme="dark"] .bk-count{color:#888!important}
/* 阅读器 */
html[data-theme="dark"] .rd-bar{background:#1a1a1a!important;border-bottom-color:#2e2e2e!important}
html[data-theme="dark"] .rd-pos{color:#aaa!important}
html[data-theme="dark"] .rd-page{background:#1a1a1a!important;color:#ececec!important;border-color:#2e2e2e!important;box-shadow:none!important}
/* 输入控件 */
html[data-theme="dark"] input,html[data-theme="dark"] textarea,html[data-theme="dark"] select{
  background:#1f1f1f!important;color:#f1f1f1!important;border-color:#333!important}
html[data-theme="dark"] input::placeholder,html[data-theme="dark"] textarea::placeholder{color:#888!important}
/* 残留的深绿内联底 / 深绿字，一律压成中性 */
html[data-theme="dark"] [style*="background:#0f3d31"],html[data-theme="dark"] [style*="background:#14503e"],
html[data-theme="dark"] [style*="background:#123f31"],html[data-theme="dark"] [style*="#0e3529"]{background:#1f1f1f!important}
html[data-theme="dark"] [style*="color:#0f3d31"],html[data-theme="dark"] [style*="color:#14503e"]{color:#f1f1f1!important}
html[data-theme="dark"] [style*="background:#fff"],html[data-theme="dark"] [style*="background: #fff"],
html[data-theme="dark"] [style*="background:#ffffff"],html[data-theme="dark"] [style*="background:#fdfaf3"],
html[data-theme="dark"] [style*="background:#fbf8f1"],html[data-theme="dark"] [style*="background:#fff8e6"]{background:#1a1a1a!important}
/* 主按钮（开始学习）：深色下用蓝色，不用金色 */
html[data-theme="dark"] .act-btn[style*="c9a84c"]{background:#3ea6ff!important;color:#0f0f0f!important}
/* AI 卡片与其余绿块，全改中性 */
html[data-theme="dark"] .ps-ai-head{background:#202020!important;color:#f1f1f1!important}
html[data-theme="dark"] .ps-ai-avatar{background:#2a2a2a!important;color:#f1f1f1!important}
html[data-theme="dark"] .ps-ai-msg.bot{background:#242424!important;color:#eaeaea!important}
html[data-theme="dark"] .ps-ai-msg.me,html[data-theme="dark"] .ps-ai-msg.user{background:#3ea6ff!important;color:#0f0f0f!important}
html[data-theme="dark"] .ps-ai-input input{background:#1f1f1f!important;border-color:#333!important;color:#f1f1f1!important}
html[data-theme="dark"] .ps-ai-input button{background:#3ea6ff!important;color:#0f0f0f!important;border:0!important}
html[data-theme="dark"] .ps-ai-chips button,html[data-theme="dark"] .ai-chips .s-btn{background:#242424!important;color:#ddd!important;border-color:#383838!important}
html[data-theme="dark"] .ps-mic{background:#2f2f2f!important;border-color:#4a4a4a!important}
html[data-theme="dark"] .ps-en,html[data-theme="dark"] .ps-ai-head span{color:#aaa!important}
html[data-theme="dark"] .daily-goal .act-btn{background:#3ea6ff!important;color:#0f0f0f!important;border:0!important}
html[data-theme="dark"] .ring .ring-fg{stroke:#3ea6ff}
html[data-theme="dark"] .elf-btn,html[data-theme="dark"] .ps-copy{background:#2a2a2a!important;color:#eee!important;border-color:#3a3a3a!important}
/* 顶栏回到「大标题居中」的头部（对全你截图里的版式） */
.hdr{display:block!important;text-align:center!important;padding:24px 16px 20px!important;background:#fff!important}
.hdr .logo{display:block;font-size:30px!important;line-height:1.25;margin:0 auto;color:#0f0f0f!important;-webkit-text-fill-color:#0f0f0f!important}
.hdr .logo-sub{font-size:12px!important;margin-top:6px!important;color:#606060!important}
.hdr .zh{font-size:10.5px!important;margin-top:4px!important;color:#909090!important}
.hdr::after{content:none!important}
html[data-theme="dark"] .hdr{background:#181818!important}
html[data-theme="dark"] .hdr .logo{color:#f1f1f1!important;-webkit-text-fill-color:#f1f1f1!important}
html[data-theme="dark"] .hdr .logo-sub{color:#b0b0b0!important}
html[data-theme="dark"] .hdr .zh{color:#888!important}
.lang-btn{position:static;border:1px solid var(--line);background:#fff;color:var(--ink);
  border-radius:999px;padding:5px 12px;font-size:12px;cursor:pointer;font-weight:600}
html[data-theme="dark"] .lang-btn{background:#242424;border-color:#3a3a3a;color:#e8e8e8}
.hdr{position:relative!important}
.tr-cn{margin-top:6px;padding-top:6px;border-top:1px dashed rgba(127,127,127,.35);font-size:12.5px;line-height:1.9;color:var(--muted)}
/* 哲言：篇章 chips + 逐段中译 */
.h6-top{display:flex;align-items:center;gap:10px;margin-bottom:10px;flex-wrap:wrap}
.h6-meta{font-size:11px;color:var(--muted)}
.h6-secs{display:flex;gap:6px;overflow-x:auto;padding:0 0 10px}
.chip{flex:0 0 auto;border:1px solid var(--line);background:#fff;border-radius:999px;padding:6px 12px;font-size:11.5px;cursor:pointer;color:var(--ink);white-space:nowrap}
.chip.on{background:#3ea6ff;border-color:#3ea6ff;color:#0f0f0f;font-weight:700}
.h6-count{font-size:11px;color:var(--muted);margin-bottom:8px}
.h6-item{background:#fff;border:1px solid var(--line);border-radius:10px;padding:12px;margin-bottom:10px}
.h6-line{display:flex;align-items:center;gap:8px;margin-bottom:6px}
.h6-no{font-size:11px;color:#b7791f;font-weight:700}
.h6-sec{font-size:10.5px;color:var(--muted);flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.h6-ar{font-family:var(--ar-font);font-size:15.5px;line-height:2;direction:rtl;text-align:right;color:var(--ink)}
.h6-cn{margin-top:8px;padding-top:8px;border-top:1px dashed var(--line);font-size:13px;line-height:1.9;color:var(--muted)}
.h6-pg{display:flex;gap:8px;justify-content:center;padding:12px 0}
html[data-theme="dark"] .chip{background:#1f1f1f;border-color:#333;color:#e8e8e8}
html[data-theme="dark"] .chip.on{background:#3ea6ff;border-color:#3ea6ff;color:#0f0f0f}
html[data-theme="dark"] .h6-item{background:#1a1a1a;border-color:#2e2e2e}
html[data-theme="dark"] .h6-ar{color:#f1f1f1}
html[data-theme="dark"] .h6-cn{color:#aaa;border-top-color:#2e2e2e}
.h6-an{margin-top:9px;padding-top:9px;border-top:1px dashed var(--line)}
.h6-an .an-cn{font-size:13.5px;line-height:1.95;color:var(--ink)}
.h6-an .an-note{margin-top:8px;font-size:12px;line-height:1.9;color:var(--muted)}
.h6-an .an-tag{display:inline-block;font-size:10px;font-weight:700;color:#0f0f0f;background:#e8b04b;border-radius:4px;padding:1px 6px;margin-right:6px;vertical-align:1px}
html[data-theme="dark"] .h6-an{border-top-color:#2e2e2e}
html[data-theme="dark"] .h6-an .an-cn{color:#f1f1f1}
html[data-theme="dark"] .h6-an .an-note{color:#aaa}
.bk-in{margin-top:6px;border:1px solid var(--line);background:transparent;color:var(--muted);
  border-radius:6px;padding:2px 8px;font-size:10.5px;cursor:pointer}
html[data-theme="dark"] .bk-in{border-color:#3a3a3a;color:#bbb}


'''

# ===== v4.1 可读性与触控细节修正 =====
CSS += '''
/* 底部导航标签：回归 11px（v4.0 层误降到 10px） */
.tabbar .tb .t-nm{font-size:11px}
/* 首页 AI 快捷问句：24px → 40px 触控热区 */
.ps-ai-chips button{min-height:40px;font-size:11.5px;padding:9px 14px;display:inline-flex;align-items:center}
/* 每日一句 出处/换一条：提高在深绿底上的可读性 */
.quote-card .q-src{color:rgba(232,212,139,.86)}
.quote-card .q-switch{color:rgba(232,212,139,.78)}
/* 弹窗列表内小按钮：热区 26→32px，字号 10→11px */
.v-item .s-btn,.s-item .s-btn{min-height:32px;min-width:32px;font-size:11px!important}
/* 首页“今日进度”目标切换按钮：热区抬到 32px */
#goalBtn{padding:6px 8px;min-height:32px}
/* 服务器状态行：字号 + 主题化颜色（修复深色下深绿字不可读） */
#serverStatus{font-size:11px}
#serverStatus.srv-on{color:#1a8a5c}
#serverStatus.srv-off{color:#c0392b}
html[data-theme="dark"] #serverStatus.srv-on{color:#6fd7a2}
html[data-theme="dark"] #serverStatus.srv-off{color:#ff8f7a}
/* 深色下首页统计环百分比/单位（原为深绿字，在深色卡上不可见） */
html[data-theme="dark"] .ring .ring-txt b{color:var(--gold-l)}
html[data-theme="dark"] .ring .ring-txt span{color:rgba(233,229,218,.72)}
/* 回到顶部浮动按钮 */
#toTop{position:fixed;right:14px;bottom:calc(74px + env(safe-area-inset-bottom,0));z-index:900;
  width:44px;height:44px;border-radius:50%;border:1px solid rgba(201,168,76,.45);
  background:rgba(15,61,49,.92);color:#f0e3b4;font-size:18px;line-height:1;cursor:pointer;
  display:flex;align-items:center;justify-content:center;
  box-shadow:0 6px 20px rgba(0,0,0,.28);opacity:0;visibility:hidden;transform:translateY(8px);
  transition:opacity .25s,transform .25s,visibility .25s}
#toTop.show{opacity:1;visibility:visible;transform:none}
#toTop:active{transform:scale(.94)}
html[data-theme="dark"] #toTop{background:rgba(28,40,33,.95);border-color:rgba(201,168,76,.5);color:var(--gold-l)}
@media(prefers-reduced-motion:reduce){#toTop{transition:none}}
'''

# ===== v8.0 蓝灰主题（对齐用户参考海报：钢蓝 + 板岩蓝） =====
CSS += '''
html[data-theme="dark"]{
  --ink:#e9f0f6; --muted:#9aaec0; --line:#3b4856; --bg:#1f2731; --card:#2a3441; --accent:#5b93bd; --acc2:#40718b;
}
html[data-theme="dark"] body{background:#1f2731!important;color:#e9f0f6!important}
html[data-theme="dark"] .hdr{background:#27313d!important;border-bottom:1px solid #3b4856!important}
html[data-theme="dark"] .hdr .logo{color:#e9f0f6!important;-webkit-text-fill-color:#e9f0f6!important}
html[data-theme="dark"] .hdr .logo-sub,html[data-theme="dark"] .hdr .zh,html[data-theme="dark"] .hdr::after{color:#9aaec0!important;-webkit-text-fill-color:#9aaec0!important}
html[data-theme="dark"] .lib-nav button{background:#2a3441!important;border-color:#3b4856!important;color:#cfdbe6!important}
html[data-theme="dark"] .lib-search input{background:#2a3441!important;border-color:#3b4856!important;color:#e9f0f6!important}
html[data-theme="dark"] .card,html[data-theme="dark"] .ps-ai-card,html[data-theme="dark"] .daily-card,
html[data-theme="dark"] .stat-card,html[data-theme="dark"] .quote-card,html[data-theme="dark"] .s-card,
html[data-theme="dark"] .s-item,html[data-theme="dark"] .v-item,html[data-theme="dark"] .entr{
  background:#2a3441!important;border-color:#3b4856!important;color:#e9f0f6!important}
html[data-theme="dark"] .card .cbody b{color:#e9f0f6!important}
html[data-theme="dark"] .card .cbody span{color:#9aaec0!important}
html[data-theme="dark"] .tabbar{background:rgba(39,49,61,.98)!important;border-top-color:#3b4856!important}
html[data-theme="dark"] .tabbar .tb{color:#9aaec0!important}
html[data-theme="dark"] .tabbar .tb.on{color:#fff!important}
html[data-theme="dark"] .tabbar .tb.on::after{background:#5b93bd!important}
html[data-theme="dark"] .modal .m-head{background:#2a3441!important;color:#e9f0f6!important}
html[data-theme="dark"] .modal .m-body{background:#1f2731!important}
html[data-theme="dark"] #mCat .m-body,html[data-theme="dark"] #mH6 .m-body,html[data-theme="dark"] #mReader .m-body{background:#1f2731!important}
html[data-theme="dark"] .bk-side{background:#27313d!important;border-right-color:#3b4856!important}
html[data-theme="dark"] .bk-cat{color:#cfdbe6!important}
html[data-theme="dark"] .bk-cat.on{background:rgba(91,147,189,.16)!important;border-left-color:#5b93bd!important;color:#fff!important}
html[data-theme="dark"] .h6-item{background:#2a3441!important;border-color:#3b4856!important}
html[data-theme="dark"] .chip{background:#2a3441!important;border-color:#3b4856!important;color:#cfdbe6!important}
html[data-theme="dark"] .chip.on{background:#5b93bd!important;border-color:#5b93bd!important;color:#fff!important}
html[data-theme="dark"] .rd-page{background:#2a3441!important;border-color:#3b4856!important;color:#e9f0f6!important}
html[data-theme="dark"] .rd-bar{background:#27313d!important;border-bottom-color:#3b4856!important}
.lib-tabs{display:flex;gap:8px;padding:10px 14px 0}
.lib-tabs .lt{border:1px solid var(--line);background:#fff;color:var(--ink);border-radius:999px;
  padding:7px 16px;font-size:13px;cursor:pointer;font-weight:600}
.lib-tabs .lt.on{background:#5b93bd;border-color:#5b93bd;color:#fff}
html[data-theme="dark"] .lib-tabs .lt{background:#2a3441;border-color:#3b4856;color:#cfdbe6}
html[data-theme="dark"] .lib-tabs .lt.on{background:#5b93bd;border-color:#5b93bd;color:#fff}

#mReader.full .m-head{display:none}
#mReader.full .m-body{background:#fff}
html[data-theme="dark"] #mReader.full .m-body{background:#1f2731}
#mReader.full .rd-page{margin:0;border-radius:0;min-height:calc(100vh - 108px)}
.rd-w{cursor:pointer;border-radius:4px;padding:0 1px}
.rd-w:hover{background:rgba(91,147,189,.22)}
html[data-theme="dark"] .rd-w:hover{background:rgba(91,147,189,.30)}
.rd-wordbox{position:fixed;left:50%;bottom:22px;transform:translateX(-50%);max-width:92vw;z-index:3000;
  background:#27313d;color:#e9f0f6;border:1px solid #3b4856;border-radius:10px;padding:10px 14px;font-size:13px;
  box-shadow:0 10px 30px rgba(0,0,0,.35);cursor:pointer;line-height:1.7}

html[data-theme="dark"] .h6-an .an-tag{background:#c07a63;color:#fff}
html[data-theme="dark"] .act-btn[style*="c9a84c"]{background:#5b93bd!important;color:#12202c!important}
html[data-theme="dark"] .daily-goal .act-btn{background:#5b93bd!important;color:#12202c!important}
html[data-theme="dark"] .ps-ai-input button{background:#5b93bd!important;color:#12202c!important}
html[data-theme="dark"] .ring .ring-fg{stroke:#5b93bd}
html[data-theme="dark"] input,html[data-theme="dark"] textarea{background:#2a3441!important;border-color:#3b4856!important;color:#e9f0f6!important}
html[data-theme="dark"] .lang-btn{background:#2a3441!important;border-color:#3b4856!important;color:#cfdbe6!important}
html[data-theme="dark"] #toTop{background:rgba(42,52,65,.95)!important;border-color:#3b4856!important;color:#cfdbe6!important}
/* 缩略图统一为海报的蓝调 */
.t-1,.t-6,.t-13{background:linear-gradient(140deg,#5b93bd,#2f4a5f)!important}
.t-2,.t-11,.t-14{background:linear-gradient(140deg,#6c7d9a,#3a4358)!important}
.t-3,.t-12,.t-15{background:linear-gradient(140deg,#a4695c,#6d423a)!important}
.t-4,.t-9,.t-16{background:linear-gradient(140deg,#4e7f96,#2c4854)!important}
.t-5,.t-10,.t-17{background:linear-gradient(140deg,#7d93a6,#47535f)!important}
.t-7,.t-8{background:linear-gradient(140deg,#5d6f88,#333c4c)!important}
'''

# ===== v9.0 浅色图书馆风（对齐 مكتبة أهل البيت） =====
CSS += '''
:root{--ink:#1c1c1e;--muted:#6b7280;--line:#e3e4e6;--accent:#2f6f9f}
html[data-theme="light"]{--ink:#1c1c1e;--muted:#6b7280;--line:#e3e4e6;--accent:#2f6f9f}
html[data-theme="light"] body{background:#ececed!important;color:#1c1c1e!important}
/* 顶栏：白底、大标题居中、细线 */
html[data-theme="light"] .hdr{background:#fff!important;border-bottom:1px solid #e3e4e6!important;padding:22px 16px 18px!important}
html[data-theme="light"] .hdr .logo{color:#1c1c1e!important;-webkit-text-fill-color:#1c1c1e!important;font-size:28px!important}
html[data-theme="light"] .hdr .logo-sub{color:#6b7280!important}
html[data-theme="light"] .hdr .zh{color:#9aa0a6!important}
html[data-theme="light"] .lang-btn{background:#f4f4f5;border-color:#e3e4e6;color:#1c1c1e}
/* 搜索：醒目圆角长条 */
html[data-theme="light"] .lib-search input{background:#fff!important;border:1px solid #dcdde0!important;
  border-radius:12px!important;height:46px!important;font-size:14px;box-shadow:0 1px 2px rgba(0,0,0,.04)}
html[data-theme="light"] .lib-search>span{margin-top:14px!important}
/* 胶囊导航：浅灰底药丸 */
html[data-theme="light"] .lib-nav{background:transparent!important}
html[data-theme="light"] .lib-nav button{background:#fff!important;border:1px solid #e3e4e6!important;color:#374151!important;
  border-radius:999px!important;padding:7px 15px!important;font-weight:500!important}
html[data-theme="light"] .lib-nav button:hover{background:#f6f6f7!important;color:#1c1c1e!important}
/* 卡片：白底细边、去阴影 */
html[data-theme="light"] .card,html[data-theme="light"] .ps-ai-card,html[data-theme="light"] .daily-card,
html[data-theme="light"] .stat-card,html[data-theme="light"] .quote-card,html[data-theme="light"] .s-card,
html[data-theme="light"] .s-item,html[data-theme="light"] .v-item,html[data-theme="light"] .entr{
  background:#fff!important;border:1px solid #e3e4e6!important;border-radius:12px!important;box-shadow:none!important}
html[data-theme="light"] .sec-title{border-bottom:0!important;margin:22px auto 10px!important}
html[data-theme="light"] .sec-title h2{color:#374151!important;font-size:13.5px!important;letter-spacing:.5px}
/* 底部导航：白底细线 */
html[data-theme="light"] .tabbar{background:rgba(255,255,255,.98)!important;border-top:1px solid #e3e4e6!important;box-shadow:none!important}
html[data-theme="light"] .tabbar .tb{color:#9aa0a6!important}
html[data-theme="light"] .tabbar .tb.on{color:#2f6f9f!important}
html[data-theme="light"] .tabbar .tb.on::after{background:#2f6f9f!important}
html[data-theme="light"] .tabbar .tb.on .t-ic{filter:none!important}
/* 弹层与书库 */
html[data-theme="light"] .modal .m-head{background:#fff!important;color:#1c1c1e!important;border-bottom:1px solid #e3e4e6}
html[data-theme="light"] .modal .m-body{background:#ececed!important}
html[data-theme="light"] #mCat .m-body,html[data-theme="light"] #mH6 .m-body,html[data-theme="light"] #mReader .m-body{background:#ececed!important}
html[data-theme="light"] .bk-side{background:#fff!important;border-right:1px solid #e3e4e6!important}
html[data-theme="light"] .bk-cat.on{background:#eef4f9!important;border-left-color:#2f6f9f!important}
html[data-theme="light"] .chip,html[data-theme="light"] .lib-tabs .lt{background:#fff!important;border-color:#e3e4e6!important;color:#374151!important}
html[data-theme="light"] .chip.on,html[data-theme="light"] .lib-tabs .lt.on{background:#2f6f9f!important;border-color:#2f6f9f!important;color:#fff!important}
html[data-theme="light"] .rd-page{background:#fff!important;border-color:#e3e4e6!important;box-shadow:none!important}
html[data-theme="light"] .h6-item{background:#fff!important;border-color:#e3e4e6!important}
html[data-theme="light"] .rd-bar{background:#fff!important;border-bottom-color:#e3e4e6!important}
html[data-theme="light"] .act-btn[style*="c9a84c"]{background:#2f6f9f!important;color:#fff!important}
html[data-theme="light"] .daily-goal .act-btn{background:#2f6f9f!important;color:#fff!important}
html[data-theme="light"] .ps-ai-input button{background:#2f6f9f!important;color:#fff!important}
html[data-theme="light"] input:focus,html[data-theme="light"] textarea:focus{border-color:#2f6f9f!important;box-shadow:0 0 0 3px rgba(47,111,159,.12)!important}
/* ===== 牛皮纸阅读页（经典选读 / 哲言 / 书籍通用） ===== */
#mReader .m-body{background:#e6d9bd!important}
#mReader .m-head{background:#efe3c6!important;color:#4a3a22!important;border-bottom:1px solid #ddceac!important}
#mReader .m-head .m-close{color:#8a7350!important}
.rd-bar{background:#f2e9d2!important;border-bottom:1px solid #e0d2b2!important}
.rd-pos{color:#7a6a4c!important}
.rd-page{background:#f8f2e0!important;border:1px solid #e6d8b8!important;border-radius:8px!important;
  color:#3b2f1e!important;box-shadow:0 2px 10px rgba(120,95,50,.12)!important;
  background-image:radial-gradient(rgba(150,120,70,.055) 1px,transparent 1px),radial-gradient(rgba(150,120,70,.04) 1px,transparent 1px);
  background-size:14px 14px,22px 22px;background-position:0 0,7px 11px}
.rd-page .rd-w:hover{background:rgba(160,120,60,.20)!important}
.rd-wordbox{background:#f6efdb!important;color:#3b2f1e!important;border:1px solid #ddceac!important}
html[data-theme="dark"] #mReader .m-body{background:#2a2a26!important}
html[data-theme="dark"] .rd-page{background:#33322c!important;color:#e8dfc8!important;border-color:#413f36!important}
html[data-theme="dark"] .rd-bar{background:#33322c!important;border-bottom-color:#413f36!important}
/* 口语陪练 */
.tk-topics{display:flex;gap:6px;overflow-x:auto;padding:0 0 10px}
.tk-msgs{min-height:280px;max-height:52vh;overflow-y:auto;padding:6px 2px}
.tk-tip{background:#f8f2e0;border:1px solid #e6d8b8;border-radius:10px;padding:14px 16px;font-size:12.5px;line-height:2;color:#6b5a3c}
.tk-row{display:flex;margin-bottom:10px}
.tk-row.me{justify-content:flex-end}
.tk-b{max-width:86%;border-radius:12px;padding:10px 14px}
.tk-row.me .tk-b{background:#2f6f9f;color:#fff}
.tk-row.ai .tk-b{background:#f8f2e0;border:1px solid #e6d8b8;color:#3b2f1e}
.tk-ar{font-family:var(--ar-font);font-size:16.5px;line-height:2.1;direction:rtl;text-align:right}
.tk-cn{font-size:12px;opacity:.8;margin-top:6px;padding-top:6px;border-top:1px dashed rgba(127,127,127,.35)}
.tk-ctrls{display:flex;gap:8px;align-items:center;padding-top:12px;flex-wrap:wrap}
.tk-mic{flex:1;min-width:180px;border:0;border-radius:999px;padding:14px;font-size:14px;font-weight:700;
  background:#2f6f9f;color:#fff;cursor:pointer}
.tk-mic.rec{background:#c0392b;animation:tkPulse 1.1s infinite}
@keyframes tkPulse{0%,100%{opacity:1}50%{opacity:.62}}
html[data-theme="dark"] .tk-tip,html[data-theme="dark"] .tk-row.ai .tk-b{background:#33322c;border-color:#413f36;color:#e8dfc8}
.tk-in{flex:1;min-width:150px;height:44px;border-radius:12px;border:1px solid #ddceac;background:#fff;
  padding:0 14px;font-size:13.5px;outline:none;color:#3b2f1e;box-sizing:border-box}
.tk-in:focus{border-color:#a8892e}
html[data-theme="dark"] .tk-in{background:#33322c;color:#e8dfc8;border-color:#413f36}
.tk-status{font-size:12px;color:#a8613a;padding:6px 2px 2px;min-height:18px}
html[data-theme="dark"] .tk-status{color:#d9a06a}
.bk-cover .bk-img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;border-radius:inherit;display:block}
.bk-cover .bk-img.off{display:none}
/* 注释 */
.tf-title{font-size:18px;font-weight:800;color:#2e2620;padding:2px 0 12px}
.tf-item{background:#fffaf2;border:1px solid #e8dfd0;border-radius:12px;padding:13px 15px;margin-bottom:10px}
.tf-h{display:flex;align-items:baseline;gap:8px;margin-bottom:7px;flex-wrap:wrap}
.tf-h b{font-size:14px;color:#2e2620}
.tf-h span{font-family:var(--ar-font);font-size:14px;color:#a8613a}
.tf-tx{font-size:13.5px;line-height:2;color:#4a4034;text-align:justify}
/* ===== 世界文明图谱（学术博物馆风） ===== */
.civ-lead{font-size:13px;color:#6b5f52;line-height:2;margin-bottom:14px}
.civ-card{background:#fbf7ee;border:1px solid #e4dcc9;border-radius:16px;padding:14px 16px 6px;margin-bottom:18px;
  box-shadow:0 1px 3px rgba(120,95,50,.05),0 8px 22px rgba(120,95,50,.05)}
.civ-card-h{display:flex;align-items:baseline;gap:10px;margin-bottom:6px}
.civ-card-h b{font-size:14px;color:#3a4a34;letter-spacing:.5px}
.civ-card-h span{font-family:var(--ar-font);font-size:13px;color:#a88b4c}
.civ-svg{width:100%;height:auto;display:block}
.civ-sec{font-size:13px;font-weight:700;color:#8a7a3f;letter-spacing:2px;margin:22px 0 12px;
  padding-bottom:8px;border-bottom:1px solid #e4dcc9}
.civ-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:12px}
.civ-sub{background:#fbf7ee;border:1px solid #e4dcc9;border-radius:14px;padding:14px 15px 15px}
.civ-num{font-family:Georgia,'Songti SC',serif;font-size:26px;line-height:1;color:#b08d4f;font-weight:700}
.civ-t{font-size:15px;font-weight:700;color:#3a4a34;margin-top:8px}
.civ-ar{font-family:var(--ar-font);font-size:14px;color:#8a7a3f;margin-top:3px}
.civ-d{font-size:11.5px;color:#8a8071;line-height:1.8;margin-top:8px}
.civ-evt{display:flex;gap:14px;align-items:flex-start;background:#fbf7ee;border:1px solid #e4dcc9;
  border-radius:14px;padding:13px 15px;margin-bottom:10px}
.civ-year{font-family:Georgia,'Songti SC',serif;font-size:22px;font-weight:700;color:#b08d4f;min-width:64px;letter-spacing:.5px}
.civ-sec-ar{font-family:var(--ar-font);font-size:12px;color:#a88b4c;font-weight:400;letter-spacing:0;margin-left:6px}
.civ-sec i{font-style:normal;font-size:11px;color:#a09684;margin-left:6px}
.civ-item{cursor:pointer;transition:transform .16s,box-shadow .16s}
@media(hover:hover){.civ-item:hover{transform:translateY(-2px);box-shadow:0 8px 20px rgba(120,95,50,.10)}}

.civ-evtx b{display:block;font-size:14px;color:#3a4a34}
.civ-evtx span{display:block;font-size:12px;color:#8a8071;margin-top:3px;line-height:1.8}
html[data-theme="dark"] .civ-card,html[data-theme="dark"] .civ-sub,html[data-theme="dark"] .civ-evt{background:#2a2a26;border-color:#413f36}
html[data-theme="dark"] .civ-card-h b,html[data-theme="dark"] .civ-t,html[data-theme="dark"] .civ-evtx b{color:#d9e0cf}
html[data-theme="dark"] .civ-sec{color:#c0a468;border-bottom-color:#413f36}

html[data-theme="dark"] .tf-item{background:#2a2a26;border-color:#413f36}
html[data-theme="dark"] .tf-h b,html[data-theme="dark"] .tf-tx{color:#e8dfc8}
html[data-theme="dark"] .tf-title{color:#f1f1f1}

/* 卡片/书架配图 */
.shelf-cv img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;border-radius:inherit}
.shelf-cv{position:relative;overflow:hidden}
.shelf-cv .shelf-tt{position:relative;z-index:2}
.shelf-cv::after{content:'';position:absolute;inset:0;background:linear-gradient(to top,rgba(0,0,0,.62),rgba(0,0,0,.12));z-index:1}
.card .thumb{position:relative;overflow:hidden}
.card .thumb .card-img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.card .thumb span{position:relative;z-index:2}
.card .thumb::after{content:'';position:absolute;inset:0;background:linear-gradient(to top,rgba(0,0,0,.5),transparent 60%);z-index:1}

.bk-cover{position:relative;overflow:hidden}
/* 顶栏 AI 按钮 + 主视觉卡（对齐 جامع الكتب） */
.ai-btn{position:static;border:1px solid #e2d8c8;background:#fffaf2;color:#a8613a;
  border-radius:999px;padding:6px 13px;font-size:12.5px;font-weight:600;cursor:pointer}
html[data-theme="dark"] .ai-btn{background:#2a2a26;border-color:#413f36;color:#e0a86a}
.hero{display:flex;align-items:center;gap:18px;max-width:1100px;margin:16px auto 4px;padding:18px 20px;
  background:linear-gradient(120deg,#fdf7ec,#f6ecdc);border:1px solid #ece0cd;border-radius:18px}
.hero-tx{flex:1;min-width:0}
.hero-tx b{display:block;font-size:17px;font-weight:800;color:#2e2620}
.hero-tx span{display:block;font-size:12.5px;color:#8a7f72;line-height:1.9;margin-top:6px}
.hero-tx em{display:inline-block;font-style:normal;margin-top:10px;font-size:13px;font-weight:700;color:#fff;
  background:#b06a2c;border-radius:999px;padding:8px 16px;cursor:pointer}
.hero-art{font-size:52px;flex:0 0 auto}
html[data-theme="dark"] .hero{background:linear-gradient(120deg,#332f27,#2a2620);border-color:#413f36}
html[data-theme="dark"] .hero-tx b{color:#f1f1f1}
html[data-theme="dark"] .hero-tx span{color:#9a8f80}
@media(max-width:640px){.hero-art{display:none}.ai-btn{right:84px;top:14px;font-size:11.5px;padding:5px 10px}}

.bk-cover .bk-t{position:relative;z-index:2}
.bk-cover::after{content:'';position:absolute;inset:auto 0 0 0;height:46%;
  background:linear-gradient(to top,rgba(0,0,0,.62),rgba(0,0,0,0));z-index:1;pointer-events:none}
.shelf-cv{position:relative;overflow:hidden}
.shelf-cv img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.shelf-cv span{position:relative;z-index:2}


/* ===== 分页（主页/书库/搜索/我的） ===== */
.page{display:block}
.pg-h{max-width:1100px;margin:0 auto;padding:22px 20px 6px;font-size:30px;font-weight:800;color:#2e2620;letter-spacing:-.4px}
.pg-wrap{max-width:1100px;margin:0 auto;padding:0 16px 24px}
.srch-big{width:100%;height:48px;border-radius:12px;border:1px solid #e2d8c8;background:#fffaf2;padding:0 16px;
  font-size:15px;outline:none;box-sizing:border-box;color:#2e2620;margin-bottom:12px}
.srch-big:focus{border-color:#b06a2c;box-shadow:0 0 0 3px rgba(176,106,44,.14)}
.srch-chips{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:14px}
.srch-tip{font-size:13px;color:#8a7f72;line-height:2;background:#fffaf2;border:1px solid #e8dfd0;border-radius:12px;padding:14px 16px}
.srch-g{font-size:13px;font-weight:700;color:#a8613a;margin:14px 0 8px}
.srch-it{background:#fffaf2;border:1px solid #e8dfd0;border-radius:12px;padding:11px 14px;margin-bottom:8px;cursor:pointer}
.si-ar{font-family:var(--ar-font);font-size:15.5px;line-height:2;direction:rtl;text-align:right;color:#2e2620}
.si-cn{font-size:12.5px;color:#8a7f72;margin-top:4px}
.si-b{font-size:13.5px;font-weight:600;color:#2e2620}
.si-t{font-size:11px;color:#a8613a;margin-bottom:3px}
.theme-opts{display:flex;gap:8px;flex-wrap:wrap}
.theme-opt{border:1px solid #e8dfd0;background:#fffaf2;color:#4a4034;border-radius:10px;padding:9px 14px;font-size:13px;cursor:pointer}
.theme-opt.on{background:#b06a2c;border-color:#b06a2c;color:#fff}
html[data-theme="dark"] .pg-h{color:#f1f1f1}
html[data-theme="dark"] .srch-big,html[data-theme="dark"] .srch-it,html[data-theme="dark"] .srch-tip,
html[data-theme="dark"] #meBox,html[data-theme="dark"] .theme-opt{background:#2a2a26;border-color:#413f36;color:#e8dfc8}
html[data-theme="dark"] .si-ar,html[data-theme="dark"] .si-b{color:#f1f1f1}


/* ===== 阅读页 v2（仿阿拉伯阅读器） ===== */
/* 阅读 = 独立整页（隐藏所有页面与底部导航） */
body.reading .page{display:none!important}
body.reading .tabbar{display:none!important}
body.reading{overflow:hidden}
body.reading #mReader{position:fixed;inset:0;z-index:3000;background:#e6d9bd;display:flex!important;
  flex-direction:column;animation:rdIn .26s cubic-bezier(.2,.8,.2,1)}
@keyframes rdIn{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:none}}
body.reading #mReader .m-head{display:flex;align-items:center;justify-content:space-between;gap:10px}
.m-back{background:transparent;border:0;color:#7a6a4c;font-size:14px;font-weight:600;cursor:pointer;padding:6px 4px}
body.reading #mReader .m-body{flex:1;overflow-y:auto}
/* 装帧封面（阿拉伯/中国古籍） */
.bk-cover.cv{background:linear-gradient(160deg,var(--cv1,#5b6b7a),var(--cv2,#2b3540))!important;
  display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px;padding:16px 12px;text-align:center}
.bk-cover.cv::before{content:'';position:absolute;inset:7px;border:1px solid rgba(255,255,255,.34);border-radius:3px;z-index:3;pointer-events:none}
.bk-cover.cv::after{content:'';position:absolute;inset:11px;border:1px solid rgba(255,255,255,.18);border-radius:2px;z-index:3;pointer-events:none}
.bk-cover .cv-orn{position:relative;z-index:2;color:rgba(255,255,255,.55);font-size:11px;line-height:1}
.bk-cover .bk-t{position:relative;z-index:2;font-family:var(--ar-font);font-size:13.5px;line-height:1.75;font-weight:700;
  color:#fff;display:-webkit-box;-webkit-line-clamp:5;-webkit-box-orient:vertical;overflow:hidden;text-shadow:0 1px 8px rgba(0,0,0,.35)}
.bk-cover .cv-line{position:relative;z-index:2;width:34px;height:1px;background:rgba(255,255,255,.45);margin-top:2px}
.bk-cover .cv-cat{position:relative;z-index:2;font-size:9px;color:rgba(255,255,255,.7);letter-spacing:.5px}
.bk-cover .bk-img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;z-index:4}
.bk-cover .bk-img.off{display:none}

.rd-toc{max-height:64vh;overflow-y:auto;min-width:240px}
.rd-toc .rd-toc-h{font-size:12px;font-weight:700;color:#a8613a;padding:8px 12px 4px}
.rd-toc button{white-space:nowrap}

@media(prefers-reduced-motion:reduce){body.reading #mReader{animation:none}}

#mReader .m-body{background:#e6d9bd!important;padding:0!important}
#mReader .m-head{background:#efe3c6!important;color:#4a3a22!important;border-bottom:1px solid #ddceac!important;padding:11px 14px!important}
.rd-bar{display:flex;align-items:center;justify-content:space-between;gap:6px;padding:8px 12px;background:#f2e9d2;
  border-bottom:1px solid #e0d2b2;position:sticky;top:0;z-index:5}
.rd-ic{width:38px;height:38px;border:0;border-radius:50%;background:transparent;color:#5c4a2c;font-size:22px;line-height:1;
  cursor:pointer;display:flex;align-items:center;justify-content:center}
.rd-ic:active{background:rgba(120,95,50,.14)}
.rd-pos{font-size:13px;color:#7a6a4c;font-weight:600}
.rd-prog{height:2px;background:rgba(150,120,70,.18)}
.rd-prog i{display:block;height:100%;background:#a8892e;transition:width .25s}
.rd-paper{padding:0 0 8px}
.rd-head{text-align:center;font-family:var(--ar-font);font-size:12.5px;color:#9c8a66;padding:12px 16px 2px}
.rd-page{font-family:var(--ar-font);font-size:18px;line-height:2.25;direction:rtl;text-align:justify;color:#3b2f1e;
  background:#f8f2e0;margin:8px 12px;padding:22px 20px;border:1px solid #e8dbbd;border-radius:8px;
  box-shadow:0 2px 10px rgba(120,95,50,.10);white-space:pre-wrap;word-break:break-word;min-height:56vh}
.rd-foot{text-align:center;font-size:12px;color:#9c8a66;padding:10px 0 4px}
/* 沉浸模式：藏起上下栏 */
#mReader.zen .rd-bar,#mReader.zen .rd-prog,#mReader.zen .m-head{display:none}
#mReader.zen .m-body{background:#e6d9bd!important}
.rd-sheet{position:fixed;left:50%;bottom:calc(16px + env(safe-area-inset-bottom,0));transform:translateX(-50%);z-index:3000;
  background:#f6efdb;border:1px solid #ddceac;border-radius:14px;box-shadow:0 12px 40px rgba(0,0,0,.25);
  padding:8px;display:flex;flex-direction:column;gap:2px;min-width:190px}
.rd-sheet button{background:transparent;border:0;text-align:left;padding:11px 14px;font-size:13.5px;color:#3b2f1e;border-radius:9px;cursor:pointer}
.rd-sheet button:active{background:rgba(120,95,50,.12)}
html[data-theme="dark"] .rd-sheet{background:#33322c;border-color:#413f36}
html[data-theme="dark"] .rd-sheet button{color:#e8dfc8}
.rd-reciters{display:flex;gap:6px;flex-wrap:wrap;padding:8px 10px 4px;border-top:1px solid rgba(150,120,70,.2);margin-top:6px}
.rd-reciters button{border:1px solid #ddceac;background:#fff8e6;color:#5c4a2c;border-radius:999px;padding:5px 10px;font-size:12px;cursor:pointer}
.rd-reciters button.on{background:#a8892e;border-color:#a8892e;color:#fff}




'''

# ===== v10.0 苹果图书风（Apple Books） =====
CSS += '''
html[data-theme="light"]{--ink:#1c1c1e;--muted:#8e8e93;--line:rgba(60,60,67,.12);--accent:#0071e3}
html[data-theme="light"] body{background:#f2f2f7!important;color:#1c1c1e!important}
/* 头部：iOS 大标题 */
html[data-theme="light"] .hdr{background:#f2f2f7!important;border-bottom:0!important;padding:20px 20px 8px!important}
html[data-theme="light"] .hdr .logo{color:#1c1c1e!important;-webkit-text-fill-color:#1c1c1e!important;font-size:30px!important;font-weight:800!important;letter-spacing:-.4px}
html[data-theme="light"] .hdr .logo-sub{color:#1c1c1e!important;font-size:15px!important;font-weight:600;margin-top:2px!important}
html[data-theme="light"] .hdr .zh{color:#8e8e93!important;font-size:12px!important}
/* 搜索：iOS 搜索框 */
html[data-theme="light"] .lib-search input{background:#e9e9eb!important;border:0!important;border-radius:10px!important;
  height:38px!important;font-size:16px}
html[data-theme="light"] .lib-search>span{margin-top:11px!important}
/* 胶囊导航：iOS 分段感 */
html[data-theme="light"] .lib-nav{background:#f2f2f7!important}
html[data-theme="light"] .lib-nav button{background:transparent!important;border:0!important;color:#0071e3!important;
  font-size:15px!important;font-weight:600!important;padding:8px 10px!important}
/* 卡片：iOS 白卡 + 极轻阴影（去边框） */
html[data-theme="light"] .card,html[data-theme="light"] .ps-ai-card,html[data-theme="light"] .daily-card,
html[data-theme="light"] .stat-card,html[data-theme="light"] .quote-card,html[data-theme="light"] .s-card,
html[data-theme="light"] .s-item,html[data-theme="light"] .v-item,html[data-theme="light"] .entr{
  background:#fff!important;border:0!important;border-radius:14px!important;
  box-shadow:0 1px 3px rgba(0,0,0,.05),0 6px 18px rgba(0,0,0,.045)!important}
/* 内容流：更圆的封面卡（Apple Books 书架感） */
html[data-theme="light"] .feed{gap:18px!important}
html[data-theme="light"] .card .thumb{aspect-ratio:3/3.2;font-size:40px}
html[data-theme="light"] .card .cbody{padding:10px 4px 14px;background:transparent}
html[data-theme="light"] .card{background:transparent!important;box-shadow:none!important;border:0!important}
html[data-theme="light"] .sec-title h2{font-size:20px!important;font-weight:800!important;letter-spacing:-.3px;color:#1c1c1e!important}
/* 图书馆：书封网格（无边框 + 封面阴影） */
html[data-theme="light"] #mCat .m-body{background:#f2f2f7!important}
html[data-theme="light"] .bk-wrap{background:#f2f2f7}
html[data-theme="light"] .bk-side{background:#f2f2f7!important;border-right:1px solid rgba(60,60,67,.10)!important}
html[data-theme="light"] .bk-cat{color:#1c1c1e!important;font-size:14px;padding:9px 14px}
html[data-theme="light"] .bk-cat.on{background:#e5e5ea!important;border-left-color:#0071e3!important;font-weight:700}
html[data-theme="light"] .bk-grid{grid-template-columns:repeat(auto-fill,minmax(118px,1fr));gap:22px 16px}
html[data-theme="light"] .bk-cover{border-radius:8px!important;
  box-shadow:0 6px 18px rgba(0,0,0,.20),0 1px 2px rgba(0,0,0,.12)!important;aspect-ratio:2/3!important}
html[data-theme="light"] .bk-meta b{color:#1c1c1e!important;font-size:13px!important;font-weight:600;margin-top:10px}
html[data-theme="light"] .bk-meta span{color:#8e8e93!important;font-size:11px!important}
html[data-theme="light"] .bk-badge{background:#e5e5ea!important;color:#0071e3!important;font-weight:600}
html[data-theme="light"] .lib-tabs{background:#f2f2f7;padding:10px 14px 4px}
html[data-theme="light"] .lib-tabs .lt{background:#e9e9eb!important;border:0!important;color:#1c1c1e!important;font-size:13.5px;padding:8px 16px}
html[data-theme="light"] .lib-tabs .lt.on{background:#fff!important;color:#0071e3!important;box-shadow:0 1px 4px rgba(0,0,0,.10)!important}
html[data-theme="light"] .chip{background:#e9e9eb!important;border:0!important;color:#1c1c1e!important}
html[data-theme="light"] .chip.on{background:#0071e3!important;color:#fff!important}
/* 底部标签栏：iOS 风 */
html[data-theme="light"] .tabbar{background:rgba(249,249,249,.94)!important;border-top:1px solid rgba(60,60,67,.12)!important;
  backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px)}
html[data-theme="light"] .tabbar .tb{color:#8e8e93!important;font-size:10.5px}
html[data-theme="light"] .tabbar .tb.on{color:#0071e3!important}
html[data-theme="light"] .tabbar .tb.on::after{display:none}
/* 弹层 */
html[data-theme="light"] .modal .m-head{background:rgba(249,249,249,.96)!important;color:#1c1c1e!important;border-bottom:1px solid rgba(60,60,67,.12)}
html[data-theme="light"] .m-close{color:#8e8e93!important}
html[data-theme="light"] .modal .m-body{background:#f2f2f7!important}
/* 超大居中标题（对齐 مكتبة أهل البيت 桌面版） */
@media(min-width:820px){
  html[data-theme="light"] .hdr{padding:48px 20px 30px!important}
  html[data-theme="light"] .hdr .logo{font-size:64px!important;font-weight:700!important;letter-spacing:0!important;line-height:1.2}
  html[data-theme="light"] .hdr .logo-sub{font-size:17px!important;margin-top:10px!important;color:#6b7280!important;font-weight:400}
  html[data-theme="light"] .hdr .zh{font-size:13px!important;margin-top:8px!important}
  html[data-theme="light"] .lang-btn{top:20px;right:20px}
}
/* 顶部统计行（册数） */
.home-stats{display:flex;gap:26px;justify-content:center;flex-wrap:wrap;max-width:1100px;margin:18px auto 4px;padding:0 16px}
.home-stats div{font-size:13.5px;color:#6b7280}
.home-stats b{color:#1c1c1e;font-weight:700;font-size:15px}
html[data-theme="dark"] .home-stats div{color:#9aa0a6}
html[data-theme="dark"] .home-stats b{color:#f1f1f1}
/* 宽屏双栏（对齐参考 app 的两栏布局） */
@media(min-width:1000px){
  #homeShelves{display:block;max-width:1100px;margin:6px auto 0}
  #homeShelves .shelf{margin:10px 0 6px}
  #homeShelves .shelf-row{padding:0 16px 8px}
  .cont-row{grid-column:1/-1}
}


/* 「全部内容」= 苹果图书书架网格 */
html[data-theme="light"] .feed{grid-template-columns:repeat(auto-fill,minmax(104px,1fr))!important;gap:22px 16px!important;max-width:1100px}
html[data-theme="light"] .feed .card{background:transparent!important;border:0!important;box-shadow:none!important;border-radius:0!important;overflow:visible!important}
html[data-theme="light"] .feed .card .thumb{aspect-ratio:2/3!important;border-radius:8px!important;font-size:34px!important;
  box-shadow:0 6px 18px rgba(0,0,0,.20),0 1px 2px rgba(0,0,0,.12)!important;position:relative;overflow:hidden}
html[data-theme="light"] .feed .card .thumb::after{content:'';position:absolute;left:8px;top:0;bottom:0;width:2px;background:rgba(255,255,255,.22)}
html[data-theme="light"] .feed .card .cbody{padding:9px 2px 0!important;background:transparent!important}
html[data-theme="light"] .feed .card .cbody b{font-size:12.5px!important;font-weight:600!important;color:#1c1c1e!important;letter-spacing:0}
html[data-theme="light"] .feed .card .cbody span{font-size:11px!important;color:#8e8e93!important;margin-top:3px!important;
  display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
@media(hover:hover){html[data-theme="light"] .feed .card:hover{transform:translateY(-3px)}}
html[data-theme="light"] .feed .card{transition:transform .18s ease}
/* 分区标题更像苹果图书 */
html[data-theme="light"] .sec-title{margin:26px auto 12px!important;padding:0 16px!important;max-width:1100px}
html[data-theme="light"] .sec-title h2{font-size:20px!important;font-weight:800!important;color:#1c1c1e!important}
/* 继续阅读（苹果图书「现在阅读」） */
.cont-row{display:flex;gap:16px;align-items:center;max-width:1100px;margin:0 auto;padding:0 16px 6px;cursor:pointer}
.cont-cv{width:96px;height:144px;border-radius:8px;flex:0 0 auto;display:flex;align-items:flex-end;padding:9px;
  background:linear-gradient(150deg,#2f6f9f,#16344c);box-shadow:0 6px 18px rgba(0,0,0,.20)}
.cont-cv span{color:#fff;font-family:var(--ar-font);font-size:12.5px;line-height:1.6;direction:rtl;text-align:right;width:100%;text-shadow:0 1px 6px rgba(0,0,0,.35)}
.cont-tx{flex:1;min-width:0}
.cont-tx b{display:block;font-size:16px;font-weight:700;color:#1c1c1e}
.cont-tx span{display:block;font-size:12.5px;color:#8e8e93;margin-top:3px}
.cont-bar{height:4px;border-radius:2px;background:rgba(120,120,128,.20);margin-top:10px;overflow:hidden}
.cont-bar i{display:block;height:100%;border-radius:2px;background:#0071e3}
.cont-tx em{display:block;font-style:normal;font-size:12.5px;color:#0071e3;font-weight:600;margin-top:8px}
html[data-theme="dark"] .cont-tx b{color:#f1f1f1}
html[data-theme="dark"] .cont-tx span{color:#9aa0a6}
html[data-theme="dark"] .cont-bar{background:rgba(255,255,255,.14)}


/* 横向书架（Apple Books） */
.shelf{margin:20px 0 4px}
.shelf-h{display:flex;align-items:baseline;justify-content:space-between;padding:0 16px 10px;max-width:1100px;margin:0 auto}
.shelf-h b{font-size:20px;font-weight:800;letter-spacing:-.3px;color:#1c1c1e}
.shelf-h span{font-size:13.5px;color:#0071e3;cursor:pointer}
.shelf-row{display:flex;gap:16px;overflow-x:auto;padding:0 16px 10px;max-width:1100px;margin:0 auto;scrollbar-width:none;-webkit-overflow-scrolling:touch}
.shelf-row::-webkit-scrollbar{display:none}
.shelf-it{flex:0 0 auto;width:104px;cursor:pointer}
.shelf-cv{width:104px;height:156px;border-radius:8px;padding:9px;display:flex;align-items:flex-end;
  box-shadow:0 6px 18px rgba(0,0,0,.20),0 1px 2px rgba(0,0,0,.12);overflow:hidden}
.shelf-tt{color:#fff;font-family:var(--ar-font);font-size:13px;line-height:1.6;direction:rtl;text-align:right;width:100%;
  display:-webkit-box;-webkit-line-clamp:4;-webkit-box-orient:vertical;overflow:hidden;text-shadow:0 1px 6px rgba(0,0,0,.35)}
.shelf-it b{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;
  font-size:12.5px;font-weight:600;margin-top:9px;line-height:1.35;color:#1c1c1e}
.shelf-it span{display:block;font-size:11px;color:#8e8e93;margin-top:2px}
@media(hover:hover){.shelf-it:hover{transform:translateY(-2px);transition:transform .18s}}
html[data-theme="dark"] .shelf-h b{color:#f1f1f1}
html[data-theme="dark"] .shelf-it b{color:#e9e9ea}

'''

# ===== v11.0 暖米色主题（对齐桌面阿拉伯 App）+ AI 界面 + 进场动画 =====
CSS += '''
html[data-theme="light"]{--ink:#2e2620;--muted:#8a7f72;--line:#e4dbcd;--accent:#b06a2c}
html[data-theme="light"] body{background:#efe9df!important;color:#2e2620!important}
html[data-theme="light"] .hdr{background:#efe9df!important}
html[data-theme="light"] .hdr .logo{color:#2e2620!important;-webkit-text-fill-color:#2e2620!important}
html[data-theme="light"] .hdr .logo-sub{color:#6b5f52!important}
html[data-theme="light"] .hdr .zh{color:#9a8f80!important}
html[data-theme="light"] .home-stats b{color:#2e2620!important}
html[data-theme="light"] .home-stats div{color:#8a7f72!important}
html[data-theme="light"] .lib-search input{background:#fff!important;border:1px solid #e2d8c8!important}
html[data-theme="light"] .lib-nav button{color:#a8613a!important}
html[data-theme="light"] .card,html[data-theme="light"] .ps-ai-card,html[data-theme="light"] .daily-card,
html[data-theme="light"] .stat-card,html[data-theme="light"] .quote-card,html[data-theme="light"] .s-card,
html[data-theme="light"] .s-item,html[data-theme="light"] .v-item{background:#fffaf2!important;border-color:#e8dfd0!important;
  box-shadow:0 1px 3px rgba(120,95,50,.06),0 6px 18px rgba(120,95,50,.06)!important}
html[data-theme="light"] .sec-title h2,html[data-theme="light"] .shelf-h b{color:#2e2620!important}
html[data-theme="light"] .shelf-h span{color:#a8613a!important}
html[data-theme="light"] .tabbar{background:rgba(247,242,234,.96)!important;border-top:1px solid #e4dbcd!important}
html[data-theme="light"] .tabbar .tb{color:#9a8f80!important}
html[data-theme="light"] .tabbar .tb.on{color:#a8613a!important}
html[data-theme="light"] .modal .m-head{background:#f7f2ea!important;color:#2e2620!important;border-bottom:1px solid #e4dbcd!important}
html[data-theme="light"] .modal .m-body,html[data-theme="light"] #mCat .m-body,html[data-theme="light"] #mH6 .m-body{background:#efe9df!important}
html[data-theme="light"] .bk-side{background:#f7f2ea!important;border-right:1px solid #e4dbcd!important}
html[data-theme="light"] .bk-cat{color:#4a4034!important}
html[data-theme="light"] .bk-cat.on{background:#f0e6d6!important;border-left-color:#b06a2c!important}
html[data-theme="light"] .chip,html[data-theme="light"] .lib-tabs .lt{background:#fffaf2!important;border:1px solid #e8dfd0!important;color:#4a4034!important}
html[data-theme="light"] .chip.on,html[data-theme="light"] .lib-tabs .lt.on{background:#b06a2c!important;border-color:#b06a2c!important;color:#fff!important}
html[data-theme="light"] .cont-bar i,html[data-theme="light"] .rd-prog i{background:#b06a2c!important}
html[data-theme="light"] .cont-tx em{color:#a8613a!important}
html[data-theme="light"] .lang-btn{background:#fffaf2!important;border:1px solid #e2d8c8!important;color:#4a4034!important}
html[data-theme="light"] .act-btn[style*="c9a84c"],html[data-theme="light"] .daily-goal .act-btn,
html[data-theme="light"] .ps-ai-input button{background:#b06a2c!important;color:#fff!important}
html[data-theme="light"] input:focus,html[data-theme="light"] textarea:focus{border-color:#b06a2c!important;box-shadow:0 0 0 3px rgba(176,106,44,.15)!important}
/* ===== AI 界面（努尔老师） ===== */
.ps-ai-card{background:#fffaf2!important;border:1px solid #e8dfd0!important;border-radius:18px!important;overflow:hidden}
.ps-ai-head{background:linear-gradient(135deg,#f7efe2,#f1e6d6)!important;color:#2e2620!important;border-bottom:1px solid #eadfce;padding:14px 16px!important}
.ps-ai-head .ps-ai-head-l span{font-size:15px!important;font-weight:800;color:#2e2620!important}
.ps-ai-head .ps-en{color:#9a8f80!important;font-size:10.5px!important}
.ps-ai-avatar{width:42px!important;height:42px!important;border:2px solid #fff!important;box-shadow:0 3px 10px rgba(120,95,50,.25)!important}
.ps-ai-msgs{padding:14px!important}
.ps-ai-msg{font-size:13.5px!important;line-height:1.85;border-radius:14px!important;padding:11px 14px!important}
.ps-ai-msg.bot{background:#fff!important;color:#3b2f1e!important;border:1px solid #eadfce!important}
.ps-ai-msg.me{background:#b06a2c!important;color:#fff!important}
.ps-ai-chips .s-btn,.ai-chips .s-btn{background:#fff!important;border:1px solid #e8dfd0!important;color:#6b5a3c!important;border-radius:999px!important;padding:7px 12px!important}
.ps-ai-input input{background:#fff!important;border:1px solid #e2d8c8!important;color:#2e2620!important}
/* ===== 进场动画 ===== */
#splash{position:fixed;inset:0;z-index:9999;background:#efe9df;display:flex;flex-direction:column;
  align-items:center;justify-content:center;gap:14px;transition:opacity .5s ease,visibility .5s}
#splash.hide{opacity:0;visibility:hidden}
#splash .sp-lamp{width:96px;height:96px;border-radius:50%;
  background:radial-gradient(circle at 50% 42%,#ffd98a,#e0a24a 55%,#b06a2c);
  box-shadow:0 0 0 0 rgba(224,162,74,.55);animation:spPulse 1.6s ease-out infinite;}
@keyframes spPulse{0%{transform:scale(.9);box-shadow:0 0 0 0 rgba(224,162,74,.55)}70%{transform:scale(1.02);box-shadow:0 0 0 26px rgba(224,162,74,0)}100%{transform:scale(.9);box-shadow:0 0 0 0 rgba(224,162,74,0)}}
#splash .sp-ar{font-family:var(--ar-font);font-size:34px;color:#3b2f1e;opacity:0;animation:spUp .8s ease .15s forwards}
#splash .sp-cn{font-size:14px;color:#8a7f72;letter-spacing:3px;opacity:0;animation:spUp .8s ease .35s forwards}
@keyframes spUp{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:none}}
#splash .sp-bar{width:120px;height:3px;border-radius:2px;background:#e4dbcd;overflow:hidden;margin-top:6px}
#splash .sp-bar i{display:block;height:100%;width:40%;background:#b06a2c;animation:spBar 1.1s ease-in-out infinite}
@keyframes spBar{0%{transform:translateX(-110%)}100%{transform:translateX(280%)}}
/* 内容进场：淡入上浮 */
body.app-in .hdr,body.app-in #homeShelves,body.app-in .feed{animation:appIn .55s cubic-bezier(.2,.8,.2,1) both}
body.app-in #homeShelves{animation-delay:.06s}
body.app-in .feed{animation-delay:.12s}
@keyframes appIn{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
@media(prefers-reduced-motion:reduce){#splash .sp-lamp,#splash .sp-bar i{animation:none}body.app-in .hdr,body.app-in #homeShelves,body.app-in .feed{animation:none}}
'''

JS = """
// ===== 句子筛选（已学/收藏/复习）=====
var CUR_FLT = 'all';
function setFilter(f){
  CUR_FLT = f;
  document.querySelectorAll('.flt').forEach(function(b){
    b.classList.toggle('on', b.getAttribute('data-flt') === f);
  });
  applyFilter();
}
function applyFilter(){
  var learned = getLearned();
  var favs = favLoad();
  var srs = srsLoad();
  var cards = document.querySelectorAll('.s-card');
  var count = 0;
  cards.forEach(function(card){
    var ar = (card.querySelector('.s-ar') || {}).textContent || '';
    var show = true;
    if(CUR_FLT === 'learned') show = learned.indexOf(ar) >= 0;
    else if(CUR_FLT === 'fav') show = favs.indexOf(ar) >= 0;
    else if(CUR_FLT === 'review') show = !!(srs['s:' + ar]);
    card.style.display = show ? '' : 'none';
    if(show) count++;
  });
  var el = document.getElementById('listCount');
  if(el && CUR_FLT !== 'all'){
    var nm = {learned:'已学', fav:'收藏', review:'复习中'}[CUR_FLT] || CUR_FLT;
    el.textContent = nm + ' · ' + count + ' 句';
  }
}

// ===== 分类筛选 =====
var catName = %s;
document.querySelectorAll('.cat-tab').forEach(function(tab){
  tab.addEventListener('click', function(){
    document.querySelectorAll('.cat-tab').forEach(function(t){t.classList.remove('on');});
    tab.classList.add('on');
    var cat = tab.getAttribute('data-cat');
    var cards = document.querySelectorAll('.s-card');
    var count = 0;
    cards.forEach(function(card){
      var show = (cat==='all') || card.getAttribute('data-cat')===cat;
      card.style.display = show ? '' : 'none';
      if(show) count++;
    });
    var name = tab.querySelector('.ct-nm').textContent;
    document.getElementById('listCount').textContent = name + ' · ' + count + '句';
  });
});

// ===== 数字增长动画 =====
function animateNum(el, target){
  var dur = 1200, start = null;
  function step(ts){
    if(!start) start = ts;
    var p = Math.min((ts-start)/dur, 1);
    var eased = 1 - Math.pow(1-p, 3);
    el.textContent = Math.floor(target * eased).toLocaleString();
    if(p < 1) requestAnimationFrame(step);
    else el.textContent = target.toLocaleString();
  }
  requestAnimationFrame(step);
}
document.querySelectorAll('.stat-num').forEach(function(el){
  animateNum(el, parseInt(el.getAttribute('data-num')));
});

// ===== 朗读 =====
// ===== 标准英语语音选择（优先高品质美式发音）=====
var EN_VOICE = null;
function pickEnVoice(){
  if(EN_VOICE) return EN_VOICE;
  var list = window.speechSynthesis ? window.speechSynthesis.getVoices() : [];
  var pref = ['Enhanced', 'Samantha', 'Google US English', 'Alex', 'Natural', 'Premium'];
  for(var i = 0; i < pref.length; i++){
    for(var j = 0; j < list.length; j++){
      var lang = (list[j].lang || '').toLowerCase();
      var name = ((list[j].name || '') + ' ' + (list[j].voiceURI || '')).toLowerCase();
      if(lang.indexOf('en') === 0 && name.indexOf(pref[i].toLowerCase()) >= 0){
        EN_VOICE = list[j]; return list[j];
      }
    }
  }
  for(var k = 0; k < list.length; k++){
    if((list[k].lang || '').toLowerCase().indexOf('en') === 0){ EN_VOICE = list[k]; return list[k]; }
  }
  return null;
}
if(window.speechSynthesis){
  pickEnVoice();
  window.speechSynthesis.onvoiceschanged = function(){ EN_VOICE = null; pickEnVoice(); };
}
function speakEn(text, btn){
  if(!window.speechSynthesis || !text) return;
  window.speechSynthesis.cancel();
  var u = new SpeechSynthesisUtterance(text);
  var v = pickEnVoice();
  if(v){ u.voice = v; u.lang = v.lang; } else { u.lang = 'en-US'; }
  u.rate = 0.9; u.pitch = 1;   // 标准清晰语速
  if(btn){ u.onstart = function(){btn.classList.add('on');}; u.onend = function(){btn.classList.remove('on');}; }
  window.speechSynthesis.speak(u);
}
function ap(btn, m, t){
  if(!window.speechSynthesis) return;
  if(m){ speakEn(t, btn); return; }
  window.speechSynthesis.cancel();
  var u = new SpeechSynthesisUtterance(t);
  u.lang = 'ar-SA';
  u.rate = .7;
  u.onstart = function(){btn.classList.add('on');};
  u.onend = function(){btn.classList.remove('on');};
  window.speechSynthesis.speak(u);
}

// ===== AI 小精灵 =====
var SID = 'e_' + Date.now();
function newSession(){
  SID = 'e_' + Date.now();
  var em2 = document.getElementById('em');
  if(em2){
    em2.innerHTML = '<div class="ef-msg bot"><div class="bb"><span class="ar">أَهْلًا بِكَ يَا صَدِيقِي!</span>' +
      '<span class="tr">新会话开始啦！今天想学什么？翻译 · 纠错 · 情景对话 🧞</span></div></div>';
  }
}
function ec(){
  var p = document.getElementById('ep'), b = document.getElementById('eb');
  p.classList.toggle('o'); b.classList.toggle('h');
  if(p.classList.contains('o') && document.getElementById('em').children.length === 1){
    setTimeout(function(){
      if(window.speechSynthesis){
        var u = new SpeechSynthesisUtterance('أهلاً بك يا صديقي!');
        u.lang = 'ar-SA'; u.rate = .7;
        window.speechSynthesis.speak(u);
      }
    }, 400);
  }
}
function em(t, r){
  var d = document.getElementById('em'), m = document.createElement('div');
  m.className = 'ef-msg ' + (t ? 'user' : 'bot');
  if(t){
    m.innerHTML = '<div class="bb">' + esc(r) + '</div>';
  }else{
    var pts = r.split('\\n').filter(function(x){ return x.trim(); });
    m.innerHTML = '<div class="bb"><span class="ar">' + esc(pts[0] || '') + '</span>' +
      (pts[1] ? '<span class="tr">🇨🇳 ' + esc(pts[1]) + '</span>' : '') +
      (pts[2] ? '<span class="tr" style="color:#5a7f9e">🇬🇧 ' + esc(pts[2]) + '</span>' : '') + '</div>' +
      '<button class="cp-btn" onclick="copyMsg(this)" title="复制全文">📋 复制</button>';
    m.dataset.full = r;
  }
  d.appendChild(m); d.scrollTop = d.scrollHeight; return m;
}
// 复制 AI 消息全文
function copyMsg(btn){
  var m = btn.parentElement, full = m.dataset.full || m.textContent;
  var ta = document.createElement('textarea');
  ta.value = full; document.body.appendChild(ta); ta.select();
  try{ document.execCommand('copy'); }catch(e){}
  document.body.removeChild(ta);
  btn.textContent = '✅ 已复制';
  setTimeout(function(){ btn.textContent = '📋 复制'; }, 1500);
}
// API 地址：只有从 8080 服务打开才同源；file:// 双击或其他端口都显式指向 8080
function API_BASE(){
  // 同源优先：无论 http/https、8080/域名/隧道/桌面壳，接口都在同一个源上
  if(location.protocol === 'http:' || location.protocol === 'https:') return '';
  return 'http://localhost:8080';
}
function esc(s){ if(!s) return ''; return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }

// ===== 🎙 AI 语音唤醒（本地 Whisper 识别 · 离线可用 · 喊「马晓梅」）=====
var WAKE_ON = false;       // 唤醒开关
var WAKE_TALK = false;     // 对话模式中
var WAKE_MIC = null;       // MediaRecorder
var WAKE_CHUNKS = [];
var WAKE_TIMER = null;     // 分段识别定时器
var WAKE_BUSY = false;     // 识别请求进行中
var WAKE_TALKING = false;  // AI 正在朗读（暂停识别防串音）
function wakeSupported(){
  return !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia && window.MediaRecorder);
}
function wakeStatus(txt, color){
  var el = document.getElementById('wakeStatus');
  if(el){ el.textContent = txt || ''; el.style.color = color || '#1a8a5c'; }
}
function openAIFocus(){
  var p = document.getElementById('ep');
  var b = document.getElementById('eb');
  if(p && !p.classList.contains('o')){ p.classList.add('o'); if(b) b.classList.add('h'); }
  var i = document.getElementById('ei');
  if(i) setTimeout(function(){ i.focus(); }, 120);
}
// 快捷键唤醒：Alt+A 或 Ctrl+Shift+A（所有环境可用）
document.addEventListener('keydown', function(e){
  if((e.altKey && (e.key === 'a' || e.key === 'A')) || (e.ctrlKey && e.shiftKey && (e.key === 'A' || e.key === 'a'))){
    e.preventDefault();
    openAIFocus();
  }
});
// 服务器 ASR 自检
function asrStatus(){
  return fetch(API_BASE() + '/api/asr/status', {cache:'no-store'})
    .then(function(r){ return r.json(); })
    .catch(function(){ return {asr:false}; });
}
function toggleWake(){
  if(!wakeSupported()){
    alert('当前环境不支持录音，已为你打开 AI 面板：可直接打字，或按 Alt+A 唤出。\\n（语音唤醒需要 Chrome/Edge/桌面 App）');
    openAIFocus();
    return;
  }
  if(!WAKE_ON){
    wakeStatus('⏳ 检查语音服务…', '#c9a84c');
    asrStatus().then(function(s){
      if(!s.asr){
        wakeStatus('⚠️ 语音服务不可用：请先运行 bash run.sh 启动服务器', '#c0392b');
        alert('语音识别服务不可用：\\n1. 请先启动本地服务器（终端运行 bash run.sh，或打开桌面 App）\\n2. 首次使用需联网下载语音模型（约 460MB），之后完全离线');
        return;
      }
      WAKE_ON = true;
      startWakeMic();
      var btn = document.getElementById('wakeBtn');
      if(btn){ btn.textContent = '🎙 聆听中'; btn.style.background = '#1a8a5c'; }
    });
  } else {
    stopWakeMic();
    wakeStatus('');
    WAKE_ON = false;
    var btn = document.getElementById('wakeBtn');
    if(btn){ btn.textContent = '🎙 唤醒'; btn.style.background = ''; }
  }
}
function startWakeMic(){
  stopWakeMic();
  WAKE_CHUNKS = [];
  wakeStatus('① 请求麦克风…', '#c9a84c');
  try{
    navigator.mediaDevices.getUserMedia({audio:true}).then(function(stream){
      var mr = null;
      try{ mr = new MediaRecorder(stream); }
      catch(e){
        stream.getTracks().forEach(function(t){ t.stop(); });
        wakeFail('录音格式不支持');
        return;
      }
      mr.ondataavailable = function(e){ if(e.data && e.data.size) WAKE_CHUNKS.push(e.data); };
      mr.onstop = function(){ stream.getTracks().forEach(function(t){ t.stop(); }); };
      mr.start(1000);
      WAKE_MIC = mr;
      WAKE_TIMER = setInterval(wakeCut, WAKE_TALK ? 6000 : 4000);
      // 对话模式切换时更新窗口
      var _wakeOld = WAKE_TALK;
      wakeStatus('② 聆听中：喊「马晓梅」', '#1a8a5c');
      speakCn('唤醒已开启，叫我马晓梅');
    }).catch(function(){
      wakeFail('麦克风被拒绝');
    });
  }catch(e){
    wakeFail('麦克风启动失败');
  }
}
function wakeFail(msg){
  WAKE_ON = false;
  stopWakeMic();
  var btn = document.getElementById('wakeBtn');
  if(btn){ btn.textContent = '🎙 ' + msg; btn.style.background = '#c0392b'; }
  wakeStatus('');
  setTimeout(function(){ if(btn && !WAKE_ON){ btn.textContent = '🎙 唤醒'; btn.style.background = ''; } }, 5000);
}
function stopWakeMic(){
  if(WAKE_MIC && WAKE_MIC.state !== 'inactive'){ try{ WAKE_MIC.stop(); }catch(e){} }
  WAKE_MIC = null;
  if(WAKE_TIMER){ clearInterval(WAKE_TIMER); WAKE_TIMER = null; }
}
function wakeCut(){
  if(WAKE_BUSY || !WAKE_MIC || WAKE_MIC.state !== 'recording' || WAKE_TALKING) return;
  var blob = new Blob(WAKE_CHUNKS, {type: (WAKE_MIC.mimeType || 'audio/webm')});
  WAKE_CHUNKS = [];
  if(blob.size < 2000) return; // 太短视为静音
  WAKE_BUSY = true;
  wakeStatus(WAKE_TALK ? '③ 识别你的话…' : '③ 识别中…', '#c9a84c');
  fetch(API_BASE() + '/api/asr', {method:'POST', headers:{'Content-Type':'application/octet-stream'}, body: blob})
    .then(function(r){ return r.json(); })
    .then(function(d){
      WAKE_BUSY = false;
      var t = (d.text || '').trim();
      if(!t){ wakeStatus(WAKE_TALK ? '对话中：请说（说「退出」结束）' : '② 聆听中：喊「马晓梅」', '#1a8a5c'); return; }
      if(WAKE_TALK){
        if(/退出|再见|拜拜|结束|停止|不说了/.test(t)){
          WAKE_TALK = false;
          wakeStatus('② 聆听中：喊「马晓梅」', '#1a8a5c');
          speakCn('好的，随时叫我');
        } else {
          wakeStatus('④ 已发送，AI 回复中…', '#c9a84c');
          esText(t);
        }
      } else {
        if(/马\s*[晓小]\s*梅|小梅|晓梅/.test(t)) wakeUp();
        else wakeStatus('② 聆听中：喊「马晓梅」', '#1a8a5c');
      }
    })
    .catch(function(){
      WAKE_BUSY = false;
      wakeFail('识别需服务器');
    });
}
function wakeUp(){
  WAKE_TALK = true;
  if(WAKE_TIMER){ clearInterval(WAKE_TIMER); WAKE_TIMER = setInterval(wakeCut, 6000); }
  openAIFocus();
  wakeStatus('💬 对话模式：直接说（「退出」结束）', '#1a8a5c');
  speakCn('我在，请说');
}
function speakCn(txt, done){
  if(!window.speechSynthesis) return;
  window.speechSynthesis.cancel();
  var u = new SpeechSynthesisUtterance(txt);
  var vs = window.speechSynthesis.getVoices() || [];
  for(var i = 0; i < vs.length; i++){
    if((vs[i].lang || '').indexOf('zh') === 0){ u.voice = vs[i]; break; }
  }
  u.lang = 'zh-CN'; u.rate = 1;
  if(done){
    u.onend = function(){ done(); };
    u.onerror = function(){ done(); };
  }
  window.speechSynthesis.speak(u);
}
// 发送文本到 AI（不走输入框）
function esText(t){
  var i = document.getElementById('ei');
  if(i) i.value = '';
  em(1, t);
  sendAI(t);
}
// 与 es() 共用发送逻辑
async function sendAI(t){
  if(!t || AI_BUSY) return;
  AI_BUSY = true;
  var sb = document.getElementById('eiSend');
  if(sb) sb.disabled = true;
  try{
    var r = await fetch(API_BASE() + '/api/chat/message', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({message:t, session_id:SID, token:webToken(), device_id:(typeof devId==='function'?devId():'')})});
    var d = await r.json(), a = d.arabic || d;
    refreshQuota();
    var full = (a || '').trim();
    var pts = full.split('\\n').map(function(s){ return s.trim(); }).filter(Boolean);
    var mb = em(0, full), sp = mb.querySelector('.ar');
    // 兼容旧三行格式（阿语/中文/英文）；文章类回答整篇显示
    var is3 = pts.length <= 3 && /[\\u0600-\\u06FF]/.test(pts[0] || '') && pts[1] && /[\\u4e00-\\u9fff]/.test(pts[1]);
    var txt = is3 ? (pts[0] || '') : full;
    sp.textContent = '';
    if (txt.length > 500) {
      sp.textContent = txt; // 长文章直接完整显示
    } else {
      for(var i2 = 0; i2 < txt.length; i2 += 2){
        sp.textContent = txt.slice(0, i2 + 2);
        await new Promise(function(r2){ setTimeout(r2, 12); });
      }
    }
    // 唤醒对话模式下朗读中文翻译（读完恢复识别），否则读正文
    if(WAKE_TALK && pts[1] && is3){
      WAKE_TALKING = true;
      speakCn(pts[1].replace(/[🇨🇳🇬🇧]/g, ''), function(){ WAKE_TALKING = false; wakeStatus('💬 对话模式：直接说（「退出」结束）', '#1a8a5c'); });
    } else if(window.speechSynthesis && txt){
      WAKE_TALKING = true;
      var u = new SpeechSynthesisUtterance(txt);
      u.lang = 'ar-SA'; u.rate = .7;
      u.onend = function(){ WAKE_TALKING = false; };
      u.onerror = function(){ WAKE_TALKING = false; };
      window.speechSynthesis.speak(u);
    }
  }catch(e){
    em(0, '⚠️ AI 服务未启动\\n请先运行服务器：终端执行 bash run.sh，或 python3 server.py');
  }
  AI_BUSY = false;
  if(sb) sb.disabled = false;
}
var AI_BUSY = false;
// ===== 主页 AI 聊天（巴勒斯坦风格）=====
var PS_CHIPS = ['解释「忍耐」的经训依据', '把「你好，（已移除）保佑你」翻译成阿拉伯语', '经典选读中关于公正的文本', '讲讲学习的意义'];
var HOME_AI_FAST = true;
function homeAIResize(inp){
  if(!inp) return;
  inp.style.height = 'auto';
  inp.style.height = Math.min(Math.max(inp.scrollHeight, 46), 132) + 'px';
}
function homeAIInputState(inp){
  homeAIResize(inp);
  var text = inp ? String(inp.value || '') : '';
  var count = document.getElementById('homeAICount'), compose = document.querySelector('.home-ai-compose'), send = document.getElementById('homeAISendBtn');
  var n = text.trim().length;
  if(count) count.textContent = n ? (n + ' 字') : '就绪';
  if(compose) compose.classList.toggle('has-text', !!n);
  if(send) send.classList.toggle('is-ready', !!n && !AI_BUSY);
}
function homeAIKeydown(ev){
  if(ev.isComposing || ev.keyCode === 229) return;
  if(ev.key === 'Enter' && !ev.shiftKey){ ev.preventDefault(); homeAISend(); }
}
function homeAIToggleFast(){
  HOME_AI_FAST = !HOME_AI_FAST;
  var b = document.getElementById('homeAIFast');
  if(b){ b.classList.toggle('on', HOME_AI_FAST); b.textContent = HOME_AI_FAST ? '快答' : '查资料'; b.title = HOME_AI_FAST ? '直接回答，速度更快' : '先查资料再回答，速度会更慢'; }
}
function homeAIRenderChips(){
  var box = document.getElementById('homeAIChips');
  if(!box || box.dataset.done) return;
  box.dataset.done = '1';
  var h = '';
  PS_CHIPS.forEach(function(c, i){
    h += '<button onclick="homeAISet(' + i + ')">' + c + '</button>';
  });
  box.innerHTML = h;
}
function homeAISet(i){
  var inp = document.getElementById('homeAIIn');
  if(inp && PS_CHIPS[i]){ inp.value = PS_CHIPS[i]; homeAIInputState(inp); inp.focus(); }
}
function homeAISend(){
  var inp = document.getElementById('homeAIIn');
  var t = (inp ? inp.value : '').trim();
  if(!t || AI_BUSY) return;
  if(inp){ inp.value = ''; homeAIInputState(inp); }
  var originalPrompt = t;
  var box = document.getElementById('homeAI');
  if(!box) return;
  box.innerHTML += '<div class="ps-ai-msg user">' + esc(t) + '</div>';
  box.scrollTop = box.scrollHeight;
  AI_BUSY = true;
  var wait = document.createElement('div');
  wait.className = 'ps-ai-msg bot';
  wait.textContent = HOME_AI_FAST ? '正在回答…' : '正在查资料…';
  box.appendChild(wait);
  box.scrollTop = box.scrollHeight;
  var sendBtn = document.getElementById('homeAISendBtn');
  var compose = document.querySelector('.home-ai-compose');
  if(compose) compose.classList.add('is-sending');
  if(sendBtn){ sendBtn.disabled = true; sendBtn.classList.add('is-busy'); sendBtn.textContent = '…'; }
  return fetch(API_BASE() + '/api/chat/message', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({message:t, fast:HOME_AI_FAST, session_id:SID, token:webToken(), device_id:(typeof devId==='function'?devId():'')})})
    .then(function(r){ return r.json().then(function(d){ if(!r.ok || (d && d.error)) throw new Error((d && (d.error || d.message)) || ('HTTP ' + r.status)); return d; }); })
    .then(function(d){
      if(apiNeedAuth(d)) return;
      if(d.action && d.action.url){
        try{
          var _ab = document.createElement('div');
          _ab.className = 'ps-ai-act';
          _ab.innerHTML = '🔗 <span style="color:#007AFF;font-weight:700;text-decoration:underline;cursor:pointer" onclick="window.open(&quot;' + d.action.url + '&quot;,&quot;_blank&quot;)">' + (d.action.label || '打开链接') + ' ›</span>';
          box.appendChild(_ab);
          box.scrollTop = box.scrollHeight;
          try{ window.open(d.action.url, '_blank'); }catch(e){}
        }catch(e){}
      }
      if(d.limited){
        wait.className = 'ps-ai-msg bot';
        wait.innerHTML = '今天的 10 次免费对话已用完。明天可以继续使用。';
        try{ AI_BUSY = false; }catch(e){}
        return;
      }
      var a = d.arabic || d;
      var full = (a || '').trim();
      var pts = full.split('\\n').map(function(s){ return s.trim(); }).filter(Boolean);
      var is3 = pts.length <= 3 && /[\u0600-\u06FF]/.test(pts[0] || '') && pts[1] && /[\u4e00-\u9fff]/.test(pts[1]);
      wait.className = 'ps-ai-msg bot';
      var txt = is3 ? pts.slice(0,3).join('\\n') : full;
      wait.dataset.full = txt;
      wait.innerHTML = '<span style="white-space:pre-wrap">' + esc(txt) + '</span><button class="ps-copy" onclick="copyMsg(this)">📋 复制</button><button class="ps-ai-speak" onclick="nourSpeakReply(this)" aria-label="朗读这条回复">🔊 朗读</button>';
      box.scrollTop = box.scrollHeight;
      try{ if(typeof nourMaybeSpeak === 'function') nourMaybeSpeak(txt); }catch(_voiceErr){}
    })
    .catch(function(e){
      var msg = (e && e.message) ? e.message : '暂时没有连接上，请稍后重试';
      wait.className = 'ps-ai-msg bot ps-ai-error';
      wait.textContent = '⚠️ ' + msg;
      if(inp) inp.value = originalPrompt;
    })
    .finally(function(){ AI_BUSY = false; if(compose) compose.classList.remove('is-sending'); if(sendBtn){ sendBtn.disabled = false; sendBtn.classList.remove('is-busy'); sendBtn.textContent = '发送'; } if(inp) homeAIInputState(inp); });
}
// 主页 AI 语音对话（打电话模式）：点一下开始对话 → 说→AI语音答→自动继续听 → 说「退出」结束
var HOME_TALK = false;
var HOME_SILENCE_T = null;
var HOME_AUDIO_CTX = null;
var HOME_MIC = null;
var HOME_CHUNKS = [];
var HOME_REC = false;
function homeAIVoice(){
  var btn = document.getElementById('homeMic');
  if(!btn) return;
  if(!HOME_TALK){
    // 进入对话模式
    HOME_TALK = true;
    btn.textContent = '📞';
    btn.style.background = '#ce1126';
    homeTalkMsg('📞 语音对话已接通！直接说话，AI 会语音回答（说「退出」结束）');
    homeTalkListen();
  } else {
    // 结束对话
    HOME_TALK = false;
    var nourPanel = document.getElementById('aiSec'); if(nourPanel) nourPanel.classList.remove('nour-live');
    btn.textContent = '🎙';
    btn.style.background = '';
    if(HOME_SILENCE_T){ clearInterval(HOME_SILENCE_T); HOME_SILENCE_T = null; }
    if(HOME_AUDIO_CTX){ try{ HOME_AUDIO_CTX.close(); }catch(e){} HOME_AUDIO_CTX = null; }
    homeTalkStopRec();
    homeTalkMsg('📞 对话已挂断。再点 🎙 重新开始');
  }
}
function homeTalkMsg(txt){
  var box = document.getElementById('homeAI');
  if(!box) return;
  box.innerHTML += '<div class="ps-ai-msg bot" style="background:rgba(206,17,38,.25);color:#ffe9e9">' + esc(txt) + '</div>';
  box.scrollTop = box.scrollHeight;
}
function homeTalkStopRec(){
  if(HOME_MIC && HOME_MIC.state !== 'inactive'){ try{ HOME_MIC.stop(); }catch(e){} }
  HOME_MIC = null;
}
function homeTalkListen(){
  if(!HOME_TALK) return;
  var btn = document.getElementById('homeMic');
  if(btn){ btn.textContent = '🎧'; btn.style.background = '#009736'; }
  if(!navigator.mediaDevices || !window.MediaRecorder){ HOME_TALK = false; if(btn){ btn.textContent = '🎙'; btn.style.background = ''; } alert('浏览器不支持录音'); return; }
  try{
    navigator.mediaDevices.getUserMedia({audio:true}).then(function(stream){
      if(!HOME_TALK){ stream.getTracks().forEach(function(t){ t.stop(); }); return; }
      var mr = null;
      try{ mr = new MediaRecorder(stream); }
      catch(e){ stream.getTracks().forEach(function(t){ t.stop(); }); homeTalkMsg('⚠️ 录音格式不支持'); return; }
      HOME_CHUNKS = [];
      mr.ondataavailable = function(e){ if(e.data && e.data.size) HOME_CHUNKS.push(e.data); };
      mr.onstop = function(){
        stream.getTracks().forEach(function(t){ t.stop(); });
        if(HOME_SILENCE_T){ clearInterval(HOME_SILENCE_T); HOME_SILENCE_T = null; }
        if(HOME_AUDIO_CTX){ try{ HOME_AUDIO_CTX.close(); }catch(e){} HOME_AUDIO_CTX = null; }
      };
      mr.start(300);
      HOME_MIC = mr;
      // 🔊 静音检测：你说完（停顿 1.4 秒）自动停止发送；不停顿就继续说
      var silenceStart = null;
      var audioCtx = null, analyser = null;
      try{
        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        analyser = audioCtx.createAnalyser();
        analyser.fftSize = 1024;
        audioCtx.createMediaStreamSource(stream).connect(analyser);
        HOME_AUDIO_CTX = audioCtx;
      }catch(e){}
      if(HOME_SILENCE_T) clearInterval(HOME_SILENCE_T);
      HOME_SILENCE_T = setInterval(function(){
        if(HOME_MIC !== mr || mr.state !== 'recording') return;
        var silent = true;
        if(analyser){
          var data = new Uint8Array(analyser.fftSize);
          analyser.getByteTimeDomainData(data);
          var sum = 0;
          for(var i = 0; i < data.length; i++){ var v = (data[i] - 128) / 128; sum += v * v; }
          var rms = Math.sqrt(sum / data.length);
          silent = rms < 0.015;
        }
        if(silent){
          if(silenceStart === null) silenceStart = Date.now();
          if(Date.now() - silenceStart > 1400){
            // 说完（停顿 1.4 秒）→ 停止发送
            if(HOME_MIC === mr && mr.state === 'recording'){ mr.stop(); }
          }
        } else {
          silenceStart = null;
        }
      }, 200);
    }).catch(function(){ HOME_TALK = false; if(btn){ btn.textContent = '🎙'; btn.style.background = ''; } homeTalkMsg('⚠️ 麦克风被拒绝，请在浏览器设置中允许'); });
  }catch(e){ HOME_TALK = false; if(btn){ btn.textContent = '🎙'; btn.style.background = ''; } homeTalkMsg('⚠️ 麦克风启动失败'); }
}
// 录音停止后识别
function homeTalkOnStop(blob){
  if(!HOME_TALK) return;
  if(blob.size < 1500){ homeTalkMsg('👂 没听清，请再说一遍…'); homeTalkListen(); return; }
  var btn = document.getElementById('homeMic');
  if(btn){ btn.textContent = '⏳'; }
  fetch(API_BASE() + '/api/asr', {method:'POST', headers:{'Content-Type':'application/octet-stream'}, body:blob})
    .then(function(r){ return r.json(); })
    .then(function(d){
      if(!HOME_TALK) return;
      var t = (d.text || '').trim();
      if(!t){ homeTalkMsg('👂 没识别到内容，请再说一遍…'); homeTalkListen(); return; }
      if(/退出|再见|拜拜|结束|挂断|不说了/.test(t)){
        homeAIVoice(); // 挂断
        return;
      }
      // 显示用户说的话
      var box = document.getElementById('homeAI');
      if(box){
        box.innerHTML += '<div class="ps-ai-msg user">' + esc(t) + '</div>';
        box.scrollTop = box.scrollHeight;
      }
      // 发给 AI
      fetch(API_BASE() + '/api/chat/message', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({message:'请作为阿拉伯语老师，用阿拉伯语自然回答一到两句，下一行以“中文：”给出简体中文翻译。不要解释语法。用户说：'+t, session_id:SID, token:webToken(), device_id:(typeof devId==='function'?devId():'')})})
        .then(function(r){ return r.json(); })
        .then(function(dd){
          if(apiNeedAuth(dd)) return;
          if(!HOME_TALK) return;
          var a = dd.arabic || dd;
          var full = (a || '').trim();
          var pts = full.split('\\n').map(function(s){ return s.trim(); }).filter(Boolean);
          var speakReply = pts[0] || full;
          var reply = full;
          // 显示回复
          if(box){
            var w = document.createElement('div');
            w.className = 'ps-ai-msg bot';
            w.dataset.full = reply;
            w.innerHTML = '<span style="white-space:pre-wrap">' + esc(reply) + '</span><button class="ps-copy" onclick="copyMsg(this)">📋 复制</button>';
            box.appendChild(w);
            box.scrollTop = box.scrollHeight;
          }
          // 语音朗读回复（edge-tts 高质量；阿语/中文自动选择）
          var lang = /[\u0600-\u06FF]/.test(speakReply) ? 'ar' : 'zh';
          var speakTxt = speakReply.replace(/[#*>`\\n]+/g, ' ').slice(0, 400);
          fetch(API_BASE() + '/api/tts', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({text:speakTxt, lang:lang})})
            .then(function(r2){ return r2.json(); })
            .then(function(dd2){
              if(!HOME_TALK) return;
              if(dd2.url){
                var u = (API_BASE() === '' ? '' : API_BASE()) + dd2.url;
                var au = new Audio(u);
                au.onended = function(){ if(HOME_TALK) homeTalkListen(); };
                au.play().catch(function(){ if(HOME_TALK) homeTalkListen(); });
              } else {
                // 兜底：浏览器 TTS
                if(window.speechSynthesis){
                  var u2 = new SpeechSynthesisUtterance(speakTxt);
                  u2.lang = lang === 'ar' ? 'ar-SA' : 'zh-CN';
                  u2.rate = .9;
                  u2.onend = function(){ if(HOME_TALK) homeTalkListen(); };
                  window.speechSynthesis.speak(u2);
                } else { if(HOME_TALK) homeTalkListen(); }
              }
            })
            .catch(function(){ if(HOME_TALK) homeTalkListen(); });
        })
        .catch(function(){ homeTalkMsg('⚠️ AI 服务连接失败'); homeTalkListen(); });
    })
    .catch(function(){ homeTalkMsg('⚠️ 语音识别失败，请确认服务器已启动'); if(HOME_TALK) homeTalkListen(); });
}
// 监听录音停止 → 识别
setInterval(function(){
  if(HOME_TALK && HOME_MIC && HOME_MIC.state === 'inactive' && HOME_CHUNKS.length){
    var mr2 = HOME_MIC;
    HOME_MIC = null;
    var blob = new Blob(HOME_CHUNKS, {type:(mr2.mimeType || 'audio/webm')});
    HOME_CHUNKS = [];
    homeTalkOnStop(blob);
  }
}, 400);
setTimeout(homeAIRenderChips, 800);
setTimeout(function(){ renderMe(); }, 1000);
async function es(){
  var i = document.getElementById('ei'), t = i.value.trim();
  if(!t || AI_BUSY) return;
  i.value = '';
  sendAI(t);
}

function startNourVoice(){
  nav('ai');
  if(!HOME_TALK) homeAIVoice();
  setTimeout(function(){var box=document.getElementById('homeAI');if(box)box.scrollTop=box.scrollHeight;},120);
}
function closeNourVoice(){
  nav('home');
}
// ===== 底部导航 =====
function nav(tab){
  // 旧版本把搜索页称作 listen；保留别名，统一新导航使用 search。
  if(tab === 'listen') tab = 'search';
  var ids = {home:'page-home', learn:'mCat', search:'page-search', me:'page-me', ai:'aiSec'};
  if(!Object.prototype.hasOwnProperty.call(ids, tab)) tab = 'home';
  var target = document.getElementById(ids[tab]);
  if(!target) return;
  if(tab !== 'ai' && HOME_TALK) homeAIVoice();
  RD_PREV_MODAL = null;
  document.querySelectorAll('.modal.show').forEach(function(p){ closeModal(p.id); });
  document.body.classList.remove('reading', 'modal-open', 'ai-open');
  document.documentElement.style.overflow = '';
  var oldAI = document.getElementById('aiView');
  if(oldAI) oldAI.style.display = 'none';
  target.classList.remove('modal', 'show', 'nour-live');
  target.classList.add('page');
  if(tab === 'learn') target.classList.add('library-page');
  if(tab === 'ai') target.classList.add('ai-page');
  if(target.parentNode !== document.body) document.body.appendChild(target);
  target.removeAttribute('aria-modal');
  target.setAttribute('role', 'main');
  document.querySelectorAll('.page').forEach(function(p){
    var active = p === target;
    p.setAttribute('aria-hidden', active ? 'false' : 'true');
    p.style.setProperty('display', active ? (tab === 'home' ? 'flex' : 'block') : 'none', 'important');
  });
  window.NUR_ACTIVE_TAB = tab;
  document.querySelectorAll('.tabbar .tb').forEach(function(t){
    var active = t.getAttribute('data-tab') === (tab === 'ai' ? 'home' : tab);
    t.classList.toggle('on', active);
    if(active) t.setAttribute('aria-current', 'page'); else t.removeAttribute('aria-current');
  });
  if(tab === 'learn' && !target.dataset.loaded){
    target.dataset.loaded = '1'; CAT_META = null;
    // 入口可能已经预选了伊斯兰来源目录；不要用历史书库初始化覆盖它。
    var initialLibraryTab = window.NUR_LIBRARY_INITIAL_TAB || '';
    window.NUR_LIBRARY_INITIAL_TAB = '';
    if(initialLibraryTab === 'islamic-sources'){
      LIB_TAB = 'islamic-sources';
    } else {
      LIB_TAB = 'hist'; showHist();
    }
  }
  if(tab === 'me'){ try{ updateStats(); renderMe(); }catch(e){} }
  if(tab === 'search'){
    var q = document.getElementById('sQ');
    if(q && innerWidth > 700) setTimeout(function(){ if(window.NUR_ACTIVE_TAB === 'listen') q.focus({preventScroll:true}); }, 80);
  }
  if(tab === 'ai'){
    var box = document.getElementById('homeAI'); if(box) box.scrollTop = box.scrollHeight;
  }
  window.scrollTo({top:0, left:0, behavior:'instant'});
}
// ===== 搜索页 =====
var S_KIND = 'all';
function searchTool(kind){var q=document.getElementById('sQ');if(kind==='analysis'||kind==='translate'){if(q&&!q.value.trim()){q.focus();var box=document.getElementById('sRes');if(box)box.innerHTML='<div class="srch-tip">先输入要处理的阿拉伯语内容。</div>';return}runSearchAI(kind);return}S_KIND=kind||'all';var c=document.querySelector('.srch-chips .chip[data-s="'+S_KIND+'"]');document.querySelectorAll('.srch-chips .chip').forEach(function(x){x.classList.toggle('on',x===c)});if(q)q.focus();if(q&&q.value.trim())doSearch();}
async function runSearchAI(kind){var q=((document.getElementById('sQ')||{}).value||'').trim(),box=document.getElementById('sRes');if(!q||!box)return;box.innerHTML='<div class="srch-tip">正在处理…</div>';var ask=kind==='translate'?'请将下面的阿拉伯语或中文内容完整翻译成中文，保留原文并逐句对照：\\n':'请分析下面阿拉伯语句子的词法和句法，并简洁说明每个成分：\\n';try{var r=await fetch(API_BASE()+'/api/chat/message',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:ask+q,session_id:SID,token:webToken(),device_id:(typeof devId==='function'?devId():'')})});var d=await r.json(),txt=String(d.arabic||d.message||'暂时没有结果');box.innerHTML='<article class="search-assist-result">'+catEsc(txt).replace(/\\n/g,'<br>')+'</article>';refreshQuota();}catch(e){box.innerHTML='<div class="srch-tip">服务暂时不可用，请稍后再试。</div>';}}
function sPick(btn){
  S_KIND = btn.getAttribute('data-s') || 'all';
  document.querySelectorAll('.srch-chips .chip').forEach(function(c){ c.classList.remove('on'); });
  btn.classList.add('on');
  doSearch();
}
async function doSearch(){
  var box = document.getElementById('sRes');
  var q = ((document.getElementById('sQ') || {}).value || '').trim();
  if(!q){ box.innerHTML = '<div class="srch-tip">输入关键词后回车。</div>'; return; }
  var out = [];
  if(S_KIND === 'all' || S_KIND === 'sent'){
    try{ await window.NOUR_loadDataAsset('sentences'); }catch(e){}
    var hit = [], arr = window.BUILTIN_SENTENCES || [];
    for(var i = 0; i < arr.length && hit.length < 20; i++){
      var x = arr[i];
      if(((x.a || '').indexOf(q) >= 0) || ((x.c || '').indexOf(q) >= 0)) hit.push(x);
    }
    if(hit.length){
      out.push('<div class="srch-g">句子 · ' + hit.length + ' 条</div>' + hit.map(function(x){
        return '<div class="srch-it"><div class="si-ar">' + catEsc(x.a || '') + '</div><div class="si-cn">' + catEsc(x.c || '') + '</div></div>';
      }).join(''));
    }
  }
  if(S_KIND === 'all' || S_KIND === 'vocab'){
    try{ await window.NOUR_loadDataAsset('vocab'); }catch(e){}
    var hv = [], av = window.BUILTIN_VOCAB || [];
    for(var i2 = 0; i2 < av.length && hv.length < 20; i2++){
      var v = av[i2];
      var s0 = (v.ar || v.a || '') + ' ' + (v.cn || v.c || '');
      if(s0.indexOf(q) >= 0) hv.push(v);
    }
    if(hv.length){
      out.push('<div class="srch-g">词汇 · ' + hv.length + ' 个</div>' + hv.map(function(v){
        return '<div class="srch-it"><div class="si-ar">' + catEsc(v.ar || v.a || '') + '</div><div class="si-cn">' + catEsc(v.cn || v.c || '') + '</div></div>';
      }).join(''));
    }
  }
  if(S_KIND === 'all' || S_KIND === 'quran'){
    try{ await window.NOUR_loadDataAsset('quran'); }catch(e){}
    var hq = [], aq = window.BUILTIN_QURAN || [];
    for(var i3 = 0; i3 < aq.length && hq.length < 20; i3++){
      var su = aq[i3], vs = su.vs || [];
      for(var k = 0; k < vs.length && hq.length < 20; k++){
        if(((vs[k].z || '') + '').indexOf(q) >= 0 || ((vs[k].a || '') + '').indexOf(q) >= 0){
          hq.push({s: su.tz + ' ' + su.n + ' · ' + (k + 1), a: vs[k].a || '', c: vs[k].z || ''});
        }
      }
    }
    if(hq.length){
      out.push('<div class="srch-g">经典选读 · ' + hq.length + ' 节</div>' + hq.map(function(x){
        return '<div class="srch-it"><div class="si-t">' + catEsc(x.s) + '</div><div class="si-ar">' + catEsc(x.a) + '</div><div class="si-cn">' + catEsc(x.c) + '</div></div>';
      }).join(''));
    }
  }
  if(S_KIND === 'all' || S_KIND === 'lib'){
    try{
      var r1 = await fetch(API_BASE() + '/api/catalog?q=' + encodeURIComponent(q) + '&size=12');
      var d1 = await r1.json();
      var it = d1.items || [];
      if(it.length){
        out.push('<div class="srch-g">图书馆 · 共 ' + (d1.total || 0) + ' 部</div>' + it.map(function(b){
          return '<div class="srch-it" onclick="openLib()"><div class="si-b">' + catEsc(b.t || '') + '</div><div class="si-cn">' + catEsc([b.a, b.c].filter(Boolean).join(' · ')) + '</div></div>';
        }).join(''));
      }
      var r2 = await fetch(API_BASE() + '/api/history?q=' + encodeURIComponent(q) + '&size=8');
      var d2 = await r2.json();
      var ht = d2.items || [];
      if(ht.length){
        out.push('<div class="srch-g">历史书 · ' + (d2.total || 0) + ' 部</div>' + ht.map(function(b){
          return '<div class="srch-it" onclick="openLib()"><div class="si-b">' + catEsc(b.title || '') + '</div><div class="si-cn">' + catEsc([b.creator, b.year, b.lang].filter(Boolean).join(' · ')) + '</div></div>';
        }).join(''));
      }
    }catch(e){}
  }
  box.innerHTML = out.length ? out.join('') : '<div class="srch-tip">没有找到「' + catEsc(q) + '」。</div>';
}


// ===== 🔑 账号 / 会员（网页版登录）=====
function apiNeedAuth(d){
  // 电脑本机已放行；手机端限制提示由服务器返回，直接显示在对话区
  if(d && (d.need_login || d.need_activate)) return true;
  return false;
}
function webToken(){ try{ return localStorage.getItem('nur_token') || ''; }catch(e){ return ''; } }
function webUser(){ try{ return localStorage.getItem('nur_username') || ''; }catch(e){ return ''; } }
function webVip(){ try{ return localStorage.getItem('nur_vip') === '1'; }catch(e){ return false; } }
function showLogin(){ openModal('mLogin'); }
function webAuth(mode){
  var u = document.getElementById('lUser').value.trim();
  var p = document.getElementById('lPass').value;
  if(!u || p.length < 4){ alert('用户名至少 2 字符，密码至少 4 位'); return; }
  fetch(API_BASE() + '/api/auth/' + mode, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({username:u, password:p})})
    .then(function(r){ return r.json(); })
    .then(function(d){
      if(d.ok){
        try{
          localStorage.setItem('nur_token', d.token);
          localStorage.setItem('nur_username', d.username);
          localStorage.setItem('nur_vip', d.vip ? '1' : '0');
          localStorage.setItem('nur_vip_until', d.vip_until || '');
        }catch(e){}
        closeModal('mLogin');
        renderMe();
        alert(mode === 'login' ? '✅ 登录成功' : '✅ 注册成功');
      } else { alert(d.msg || '操作失败'); }
    })
    .catch(function(){ alert('⚠️ 无法连接服务器'); });
}
async function webActivate(){
  var c = prompt('请输入激活码（从管理员处获取）：');
  if(!c) return;
  var t = webToken();
  if(!t){ alert('请先登录'); openModal('mLogin'); return; }
  var r = await fetch(API_BASE() + '/api/vip/activate', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({code:c.trim().toUpperCase(), token:t})});
  var d = await r.json();
  if(d.ok){ alert('🎉 ' + d.msg); localStorage.setItem('nur_vip','1'); renderMe(); } else { alert('兑换失败：' + (d.msg||'请检查激活码')); }
}
function webLogout(){
  try{
    fetch(API_BASE() + '/api/access/leave', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({device_id: devId()})}).catch(function(){});
    localStorage.removeItem('nur_token');
    localStorage.removeItem('nur_username');
    localStorage.removeItem('nur_vip');
  }catch(e){}
  try{ if(window.__rdAudio){ window.__rdAudio.pause(); window.__rdAudio = null; } }catch(e){}
  location.reload();
}
async function deviceLogin(){
  var m = document.getElementById('lockMsg');
  try{
    if(m){ m.style.color = '#5a6159'; m.textContent = '正在恢复登录…'; }
    var r = await fetch(API_BASE() + '/api/device/login', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({device_id: devId()})});
    var d = await r.json();
    if(d.ok){
      try{ localStorage.setItem('nur_token', d.token); localStorage.setItem('nur_username', d.username||''); localStorage.setItem('nur_vip','1'); }catch(e){}
      if(m){ m.style.color = '#0f5132'; m.textContent = '✅ 已恢复登录，正在进入…'; }
      setTimeout(function(){ location.reload(); }, 600);
    } else if(m){ m.style.color = '#b4553a'; m.textContent = (d.msg || '本设备没有开通记录'); }
  }catch(e){ if(m){ m.style.color='#b4553a'; m.textContent='⚠️ 无法连接服务器'; } }
}
function renderMe(){
  var el = document.getElementById('meBox');
  if(!el) return;
  var u = webUser() || '学习者';
  el.innerHTML = '<div class="profile-identity"><div class="profile-avatar">ن</div><div><div class="profile-greeting">你好，'+catEsc(u)+'</div><div class="profile-level">Level 5 · Arabic learner</div></div></div>';
  var recent=[];try{recent=JSON.parse(localStorage.getItem('nur_read_footprints')||'[]')}catch(e){}
  var activity=document.getElementById('profileActivity');
  if(activity){activity.innerHTML='<h2>浏览足迹</h2>'+(recent.length?'<div class="footprint-list">'+recent.slice(0,5).map(function(x){return '<div class="footprint-row"><span class="footprint-mark">'+(x.kind==='书籍'?'▤':'◉')+'</span><span><b>'+catEsc(x.title||'阅读')+'</b><small>'+catEsc(x.kind||'阅读')+' · '+catEsc(x.time||'')+'</small></span></div>'}).join('')+'</div>':'<p class="empty-footprint">开始阅读后，最近浏览会显示在这里。</p>')}
}
// ===== 🌓 深色模式 =====
var THEME_MODE = (function(){ try{ return localStorage.getItem('nur_theme2') || 'auto'; }catch(e){ return 'light'; } })();
function _sysDark(){ try{ return !!(window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches); }catch(e){ return false; } }
function applyTheme(){
  var dark = THEME_MODE === 'dark' || (THEME_MODE === 'auto' && _sysDark());
  document.documentElement.setAttribute('data-theme', dark ? 'dark' : 'light');
  var m = document.querySelector('meta[name="theme-color"]');
  if(m) m.setAttribute('content', dark ? '#181818' : '#ffffff');
  document.querySelectorAll('.theme-opt').forEach(function(b){ b.classList.toggle('on', b.getAttribute('data-th') === THEME_MODE); });
}
function setTheme(mode){ THEME_MODE = mode; try{ localStorage.setItem('nur_theme2', mode); }catch(e){} applyTheme(); }
function showThemeSettings(){
  detachModal('mTheme');
  openModal('mTheme');
  renderThemeSettings();
}
function themeSet(mode){ setTheme(mode); renderThemeSettings(); }
function renderThemeSettings(){
  var body = document.getElementById('mThemeBody');
  if(!body) return;
  var opts = [['light','☀️','浅色模式','温暖、清晰，适合白天学习'],['dark','🌙','深色模式','降低眩光，适合夜间专注'],['auto','◐','跟随系统','根据设备外观自动切换']];
  body.innerHTML = '<div class="theme-settings-intro"><div class="theme-settings-orb">◐</div><div><strong>选择你的学习氛围</strong><span>外观只影响当前设备，不会改变学习数据。</span></div></div><div class="theme-settings-options">' + opts.map(function(x){ return '<button class="theme-settings-option ' + (THEME_MODE === x[0] ? 'on' : '') + '" onclick="themeSet(\\'' + x[0] + '\\')"><span class="theme-settings-icon">' + x[1] + '</span><span><b>' + x[2] + '</b><small>' + x[3] + '</small></span><i>' + (THEME_MODE === x[0] ? '✓' : '') + '</i></button>'; }).join('') + '</div><div class="theme-settings-tip">当前模式：<b>' + (THEME_MODE === 'light' ? '浅色模式' : THEME_MODE === 'dark' ? '深色模式' : '跟随系统') + '</b></div>';
}
try{ if(window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').addEventListener){ window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function(){ if(THEME_MODE === 'auto') applyTheme(); }); } }catch(e){}

// ===== ⭐ 句子收藏 & 📌 加入复习 =====
function favLoad(){ try{ return JSON.parse(localStorage.getItem('nur_favorites') || '[]'); }catch(e){ return []; } }
function toggleFavWeb(txt){
  var f = favLoad();
  var i = f.indexOf(txt);
  if(i >= 0) f.splice(i, 1); else f.push(txt);
  try{ localStorage.setItem('nur_favorites', JSON.stringify(f)); }catch(e){}
  renderFavState();
}
function reviewSent(txt){
  srsAdd('s', txt);
  alert('✅ 已加入间隔复习：这句会按遗忘曲线提醒你');
}
function renderFavState(){
  var favs = favLoad();
  document.querySelectorAll('.s-card').forEach(function(card){
    var btns = card.querySelectorAll('.s-btns .s-btn');
    var ar = (card.querySelector('.s-ar') || {}).textContent || '';
    if(btns.length >= 3){
      btns[2].textContent = favs.indexOf(ar) >= 0 ? '⭐' : '☆';
      btns[2].style.background = favs.indexOf(ar) >= 0 ? 'rgba(201,168,76,.3)' : '';
    }
  });
}

// ===== 全部句子 & 词汇表 & 图书馆（内置数据优先，服务器后台增强）=====
var ALL_SENTENCES = [];
var ALL_VOCAB = [];
var ALL_ARTICLES = [];
var RD_PREV_MODAL = null;
function openModal(id){
  var el = document.getElementById(id);
  if(!el) return;
  if(id === 'mReader'){
    try{ if(typeof rdOpenitiCancel === 'function') rdOpenitiCancel(); }catch(e){}
    RD_OPENITI = null;
    document.body.classList.add('reading');
    // 收起其它已打开的弹层（关闭阅读器时恢复）
    var opens = document.querySelectorAll('.modal.show');
    RD_PREV_MODAL = null;
    for(var i = 0; i < opens.length; i++){ if(opens[i].id !== 'mReader'){ RD_PREV_MODAL = opens[i].id; opens[i].classList.remove('show'); } }
  }
  el.classList.add('show');
  try{ if(!el.dataset.hist){ el.dataset.hist = '1'; history.pushState({ modal: id }, ''); } }catch(e){}
  try{ var fb=document.getElementById('rdFloatBack'); if(fb) fb.style.display=''; try{ var hb=document.getElementById('nurHomeBtn'); if(hb) hb.style.display=''; }catch(e){} }catch(e){}
}
function closeModal(id){
  var el = document.getElementById(id);
  if(!el) return;
  el.classList.remove('show');
  try{ delete el.dataset.hist; var fb=document.getElementById('rdFloatBack'); if(fb && !document.querySelector('.modal.show')) fb.style.display='none'; try{ var hb=document.getElementById('nurHomeBtn'); if(hb && !document.querySelector('.modal.show')) hb.style.display='none'; }catch(e){} }catch(e){}
  if(id === 'mReader'){
    document.body.classList.remove('reading'); el.classList.remove('full'); el.classList.remove('zen');
    try{ if(typeof rdOpenitiCancel === 'function') rdOpenitiCancel(); }catch(e){}
    RD_OPENITI = null;
    try{ if(typeof rdStopAudio === 'function') rdStopAudio(); }catch(e){}
    try{ window.__rdAudio && window.__rdAudio.pause(); window.__rdAudio = null; }catch(e){}
    try{ window.speechSynthesis && window.speechSynthesis.cancel(); }catch(e){}
    if(RD_PREV_MODAL){ var prev = document.getElementById(RD_PREV_MODAL); if(prev) prev.classList.add('show'); RD_PREV_MODAL = null; }
  }
}
// 书库式顶部搜索：跳到句子库并带入关键字
async function libSearch(q){
  q = String(q || '').trim();
  try{ await showAllSentences(); }catch(e){}
  var el = document.getElementById('mSentSearch');
  if(el){ el.value = q; }
  try{ renderAllS(); }catch(e){}
}
// ===== 图书馆：阿拉伯书籍 / 中国书籍 合并 =====
var LIB_TAB = 'islamic';
function libTabs(){
  return '<div class="lib-tabs">' +
    '<button class="lt' + (LIB_TAB === 'hist' ? ' on' : '') + '" onclick="libTab(&#39;hist&#39;)">历史</button>' +
    '<button class="lt' + (LIB_TAB === 'cn' ? ' on' : '') + '" onclick="libTab(&#39;cn&#39;)">书籍</button>' +
    '<button class="lt' + (LIB_TAB === 'islamic' ? ' on' : '') + '" onclick="libTab(&#39;islamic&#39;)">书库</button>' +
    '<button class="lt' + (LIB_TAB === 'islamic-sources' ? ' on' : '') + '" onclick="libTab(&#39;islamic-sources&#39;)">伊斯兰来源</button>' +
  '</div>';
}
function openLib(){ nav('learn'); }
function saveFootprint(title,kind){try{var a=JSON.parse(localStorage.getItem('nur_read_footprints')||'[]');var d=new Date();var t=String(d.getHours()).padStart(2,'0')+':'+String(d.getMinutes()).padStart(2,'0');a.unshift({title:String(title||'阅读').slice(0,120),kind:kind||'阅读',time:t});localStorage.setItem('nur_read_footprints',JSON.stringify(a.slice(0,30)));}catch(e){}}
function libTab(t){
  LIB_TAB = t;
  if(t === 'islamic'){ showCatalog(); }
  else if(t === 'islamic-sources'){ showIslamicLibrary(); }
  else if(t === 'cn'){ showCnBooks(); }
  else { showHist(); }
}
// ===== 历史（世界史书，Archive.org）=====
var HWR_CAT = 'ar', HWR_Q = '', HWR_PAGE = 0, HWR_ITEMS = [], HWR_TOTAL = 0;
async function showHist(){
  var body = document.getElementById('mCatBody');
  if(!body) return;
  body.innerHTML = libTabs() + '<div style="padding:44px;text-align:center;color:var(--muted);font-size:13px">加载历史书库…</div>';
  HWR_PAGE = 0; HWR_ITEMS = [];
  histLoad();
}
async function histLoad(){
  var body = document.getElementById('mCatBody');
  if(!body) return;
  try{
    var u = API_BASE() + '/api/history?cat=' + encodeURIComponent(HWR_CAT) + '&q=' + encodeURIComponent(HWR_Q) + '&page=' + HWR_PAGE + '&size=60';
    var r = await fetch(u);
    var d = await r.json();
    if(!d || d.error) throw new Error((d && d.error) || 'empty');
    HWR_TOTAL = d.total || 0;
    HWR_ITEMS = HWR_ITEMS.concat(d.items || []);
    renderHist(d.categories || {});
  }catch(e){
    body.innerHTML = libTabs() + '<div style="padding:40px 24px;text-align:center;color:var(--muted);font-size:13px;line-height:2">历史书库正在导入中（Archive.org 世界史书，含各国各民族历史）。<br>完成后可在此按语言浏览、点开即读。</div>';
  }
}
function renderHist(cats){
  var body = document.getElementById('mCatBody');
  if(!body) return;
  var side = '<div class="bk-side"><div class="bk-side-h">历史 · 文学</div>';
  side += '<button class="bk-cat' + (HWR_CAT === '全部' ? ' on' : '') + '" onclick="histPick(&#39;全部&#39;)"><span>全部</span><i>' + HWR_TOTAL + '</i></button>';
  Object.keys(cats).forEach(function(c){
    var cl = c === 'ar' ? '阿拉伯书籍' : (c === 'zh' ? '中文书籍' : c);
    side += '<button class="bk-cat' + (HWR_CAT === c ? ' on' : '') + '" onclick="histPick(&#39;' + catEsc(c) + '&#39;)"><span>' + catEsc(cl) + '</span><i>' + cats[c] + '</i></button>';
  });
  side += '</div>';
  var grid = HWR_ITEMS.map(function(b){
    var t = catEsc(b.title || '');
    var isCn = (b.lang === 'zh');
    var sub = catEsc((b.cat || '') + (isCn ? ' · 中文' : ' · عربي'));
    var hue = isCn ? 25 : 200;
    return '<div class="bk-card" data-hid="' + b.id + '" onclick="openHist(this)">' +
      '<div class="bk-cover cv" style="--cv1:hsl(' + hue + ',32%%,36%%);--cv2:hsl(' + hue + ',38%%,18%%)">' +
      '<span class="cv-orn">❁</span><span class="bk-t">' + t + '</span><span class="cv-line"></span><span class="cv-cat">' + catEsc(b.cat || '') + '</span></div>' +
      '<div class="bk-meta"><b>' + t + '</b><span>' + sub + '</span></div></div>';
  }).join('');
  body.innerHTML = libTabs() + '<div class="bk-wrap">' + side +
    '<div class="bk-main"><div class="bk-top"><div class="bk-title">' + (HWR_CAT === 'ar' ? '阿拉伯书库' : (HWR_CAT === 'zh' ? '中文书库' : '世界历史')) + '</div>' +
    '<input class="bk-q" id="histQ" placeholder="搜索书名 / 作者…" oninput="histFilter(this.value)"></div>' +
    '<div class="bk-count">已显示 ' + HWR_ITEMS.length + ' / ' + HWR_TOTAL + ' 部</div>' +
    '<div class="bk-grid" id="histGrid">' + grid + '</div>' +
    '<div style="text-align:center;padding:12px"><button class="act-btn" onclick="histMore()">加载更多</button></div></div></div>';
}
function histPick(c){ HWR_CAT = c; HWR_PAGE = 0; HWR_ITEMS = []; histLoad(); }
function histFilter(v){ HWR_Q = v; HWR_PAGE = 0; HWR_ITEMS = []; histLoad(); }
function histMore(){ HWR_PAGE++; histLoad(); }
async function openHist(el){
  var id = el.getAttribute('data-hid');
  openModal('mReader');
  var body = document.getElementById('mReaderBody');
  var tEl = document.getElementById('mReaderTitle');
  var nm = (el.querySelector('.bk-meta b') || {}).textContent || '阅读';
  saveFootprint(nm,'书籍');
  if(tEl) tEl.textContent = nm;
  body.innerHTML = '<div style="padding:44px;text-align:center;color:#7a6a4c;font-size:13px">载入全书…（首次从 Archive.org 下载，稍等）</div>';
  RD_PAGES = []; RD_PAGE = 0; RD_BOOK_META = null; RD_ISLAMIC_GUIDE = false;
  try{
    var r = await fetch(API_BASE() + '/api/histbook?id=' + encodeURIComponent(id));
    var d = await r.json();
    if(!d || d.error) throw new Error((d && d.error) || 'fail');
    if(!d.text && d.url){ closeModal('mReader'); try{ window.open(d.url, '_blank'); }catch(e){} return; }
    var txt = String(d.text || '').replace(/\\r/g, '');
    var parts = txt.split(/\\n\\s*\\n/).filter(function(x){ return x.trim().length > 20; });
    var buf = '', out = [];
    parts.forEach(function(x){
      if((buf + x).length > 1400){ if(buf) out.push(buf); buf = x; } else { buf += (buf ? '\\n' : '') + x; }
    });
    if(buf) out.push(buf);
    RD_PAGES = out.length ? out : [(txt.slice(0, 2000) || '（无内容）')];
    rdBuildToc();
    renderRead();
  }catch(e){
    body.innerHTML = '<div style="padding:32px;text-align:center;color:#b3261e;font-size:13px">载入失败，请稍后再试</div>';
  }
}
async function showCnBooks(){
  var body = document.getElementById('mCatBody');
  if(!body) return;
  body.innerHTML = libTabs() + '<div style="padding:44px;text-align:center;color:var(--muted);font-size:13px">加载中国书籍…</div>';
  try{
    var r = await fetch(API_BASE() + '/api/cnbooks?page=0&size=60');
    var d = await r.json();
    if(!d || d.error) throw new Error((d && d.error) || 'empty');
    renderCn(d);
  }catch(e){
    body.innerHTML = libTabs() + '<div style="padding:40px 24px;text-align:center;color:var(--muted);font-size:13px;line-height:2">中国书籍正在导入中（儒藏·史藏·子藏·集藏·诗藏·医藏·易藏·艺藏·佛藏·道藏，约 1 万部）。<br>完成后这里就能按类浏览、点开即读。</div>';
  }
}
function renderCn(d){
  var body = document.getElementById('mCatBody');
  if(!body) return;
  var cats = d.categories || {};
  var side = '<div class="bk-side"><div class="bk-side-h">中国古籍 · 分类</div>';
  side += '<button class="bk-cat on" onclick="cnPick(&#39;全部&#39;)"><span>全部</span><i>' + (d.total || 0) + '</i></button>';
  Object.keys(cats).forEach(function(c){
    side += '<button class="bk-cat" onclick="cnPick(&#39;' + catEsc(c) + '&#39;)"><span>' + catEsc(c) + '</span><i>' + cats[c] + '</i></button>';
  });
  side += '</div>';
  var items = d.items || [];
  var grid = items.map(function(b){
    var t = catEsc(b.title || '');
    return '<div class="bk-card" data-cid="' + b.id + '" onclick="openCn(this)">' +
      '<div class="bk-cover cv" style="--cv1:#8a6a52;--cv2:#4d3628"><img class="bk-img" loading="lazy" src="' + API_BASE() + '/api/coverimg?t=' + encodeURIComponent(b.title || '') + '" onerror="this.classList.add(&#39;off&#39;)">' +'<span class="cv-orn">❁</span><span class="bk-t">' + t + '</span><span class="cv-line"></span><span class="cv-cat">' + catEsc(b.category || '') + '</span></div>' +
      '<div class="bk-meta"><b>' + t + '</b><span>' + catEsc(b.category || '') + '</span></div></div>';
  }).join('');
  body.innerHTML = libTabs() + '<div class="bk-wrap">' + side +
    '<div class="bk-main"><div class="bk-top"><div class="bk-title">中国书籍</div>' +
    '<input class="bk-q" id="cnQ" placeholder="搜索书名…" oninput="cnFilter(this.value)"></div>' +
    '<div class="bk-count" id="cnCount">已显示 ' + items.length + ' / ' + (d.total || 0) + ' 部</div>' +
    '<div class="bk-grid" id="cnGrid">' + grid + '</div></div></div>';
}
function cnPick(c){ CN_CAT = c; cnLoad(); }
var CN_CAT = '全部', CN_Q = '';
async function cnLoad(){
  try{
    var r = await fetch(API_BASE() + '/api/cnbooks?cat=' + encodeURIComponent(CN_CAT) + '&q=' + encodeURIComponent(CN_Q) + '&page=0&size=60');
    var d = await r.json();
    renderCn(d);
  }catch(e){}
}
function cnFilter(v){ CN_Q = v; cnLoad(); }
async function openCn(el){
  var id = el.getAttribute('data-cid');
  openModal('mReader');
  var body = document.getElementById('mReaderBody');
  var tEl = document.getElementById('mReaderTitle');
  var nm = (el.querySelector('.bk-meta b') || {}).textContent || '阅读';
  if(tEl) tEl.textContent = nm;
  body.innerHTML = '<div style="padding:44px;text-align:center;color:var(--muted);font-size:13px">载入中…</div>';
  RD_PAGES = []; RD_PAGE = 0; RD_BOOK_META = null; RD_ISLAMIC_GUIDE = false;
  try{
    var r = await fetch(API_BASE() + '/api/cnbook?id=' + encodeURIComponent(id));
    var d = await r.json();
    if(!d || d.error) throw new Error((d && d.error) || 'fail');
    var txt = String(d.text || '');
    var parts = txt.split(/\\n{2,}/).filter(function(x){ return x.trim().length; });
    if(parts.length < 2){ parts = txt.split(/(?<=[。！？])/).filter(function(x){ return x.trim().length; }); }
    var buf = '', out = [];
    parts.forEach(function(x){
      if((buf + x).length > 900){ if(buf) out.push(buf); buf = x; } else { buf += (buf ? '\\n' : '') + x; }
    });
    if(buf) out.push(buf);
    RD_PAGES = out.length ? out : ['（无内容）'];
    rdBuildToc();
    renderRead();
  }catch(e){
    body.innerHTML = '<div style="padding:32px;text-align:center;color:#b3261e;font-size:13px">载入失败</div>';
  }
}

// ===== 世界书库（服务端分页，手机不爆内存）=====
var CAT_META = null, CAT_CUR = '全部', CAT_Q = '', CAT_TAG = '', CAT_SCHOOL = '', CAT_PAGE = 0, CAT_SIZE = 60, CAT_TOTAL = 0, CAT_ITEMS = [];
function catEsc(s){ return String(s == null ? '' : s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }
function catHue(s){ var h = 0, i; for(i = 0; i < s.length; i++){ h = (h * 31 + s.charCodeAt(i)) %% 360; } return h; }
function bkOpen(el){
  var catid = el.getAttribute('data-catid');
  if(catid){ openIslamicBook(catid); return; }
  var t = el.getAttribute('data-rt');
  if(t){ openRead(el); return; }          // 有全文 → 直接进阅读页
  var u = el.getAttribute('data-u');
  if(u){ try{ window.open(u, '_blank'); }catch(e){} return; }
  alert('这部书暂时没有可打开的来源。');
}
function bkInApp(ev, el){
  ev.stopPropagation();
  var catid = el.getAttribute('data-catid');
  if(catid){ openIslamicBook(catid); return; }
  if(el.getAttribute('data-rt')) openRead(el);
  else alert('这部书没有 App 内全文，只能跳原网页。');
}
function bkGuide(ev, el){
  if(ev) ev.stopPropagation();
  var catid = el && el.getAttribute ? el.getAttribute('data-catid') : '';
  if(catid) openIslamicGuide(catid);
}
function bkOriginal(ev, el){
  if(ev) ev.stopPropagation();
  var catid = el && el.getAttribute ? el.getAttribute('data-catid') : '';
  var b = catid ? islamicBook(catid) : null;
  if(b && b.text_mode === 'arabic_original_link'){ openIslamicBook(catid); return; }
  var u = b && (b.text_url || b.u);
  if(u){ try{ window.open(u, '_blank'); }catch(e){ location.href = u; } }
}
function islamicBook(id){
  try{ return (window.NUR_ISLAMIC_BOOKS || {})[id] || null; }catch(e){ return null; }
}
function rdOpenitiCacheKey(state, page){ return 'nur_openiti_page_v2:' + String(state.id || '') + ':' + String(page); }
function rdOpenitiLoadCache(state, page){
  try{
    var raw = localStorage.getItem(rdOpenitiCacheKey(state, page));
    var d = raw ? JSON.parse(raw) : null;
    if(d && d.id === state.id && typeof d.text === 'string' && d.text.length) return d;
  }catch(e){}
  return null;
}
function rdOpenitiSaveCache(state, page, d){
  try{
    var prefix = 'nur_openiti_page_v2:' + String(state.id || '') + ':';
    localStorage.setItem(rdOpenitiCacheKey(state, page), JSON.stringify({id:state.id,page:page,text:String(d.text || ''),source:d.source || state.source,at:Date.now()}));
    var keys=[];
    for(var i=0;i<localStorage.length;i++){ var k=localStorage.key(i); if(k && k.indexOf(prefix)===0) keys.push(k); }
    keys.sort(function(a,b){
      try{ return Number(JSON.parse(localStorage.getItem(a)||'{}').at||0)-Number(JSON.parse(localStorage.getItem(b)||'{}').at||0); }catch(e){ return 0; }
    });
    while(keys.length > 24) localStorage.removeItem(keys.shift());
  }catch(e){}
}
function rdOpenitiRenderProgress(state, page, message){
  var bar = document.getElementById('rdOpenitiProgress');
  var fill = document.getElementById('rdOpenitiProgressFill');
  var label = document.getElementById('rdOpenitiProgressLabel');
  var meta = document.getElementById('rdOpenitiProgressMeta');
  if(!bar) return;
  bar.hidden = false;
  var pct = Math.max(0, Math.min(100, Math.round((Number(state.progress) || 0) * 100)));
  if(fill) fill.style.width = pct + '%%';
  if(label) label.textContent = message || (state.pending ? '正在按需读取阿拉伯原文…' : '原文已就绪');
  if(meta){
    var bytes = Number(state.bytesRead || 0), total = Number(state.sourceBytes || 0);
    meta.textContent = (bytes && total ? Math.round(bytes / 1024) + ' KB / ' + Math.round(total / 1024) + ' KB · ' : '') + '第 ' + (Number(page) + 1) + ' 页';
  }
}
function rdOpenitiCancel(){
  var state = window.RD_OPENITI;
  if(!state) return;
  state.cancelled = true;
  try{ Object.keys(state.controllers || {}).forEach(function(k){ if(state.controllers[k]) state.controllers[k].abort(); }); }catch(e){}
  try{ Object.keys(state.retryTimers || {}).forEach(function(k){ clearTimeout(state.retryTimers[k]); }); }catch(e){}
  state.controllers = {}; state.retryTimers = {};
}
function rdOpenitiFetch(page, show){
  var state = window.RD_OPENITI;
  if(!state || !state.id) return;
  page = parseInt(page, 10);
  if(isNaN(page) || page < 0 || (state.total && page >= state.total)) return;
  var cached = rdOpenitiLoadCache(state, page);
  if(cached && !state.loaded[page]){
    RD_PAGES[page] = cached.text;
    state.loaded[page] = true;
    state.pagesReady = Math.max(Number(state.pagesReady || 0), page + 1);
    if(show){ RD_PAGE = page; rdBuildToc(); renderRead(); }
  }
  if(state.loaded[page]){ if(show){ RD_PAGE = page; renderRead(); } return; }
  if(state.pending[page]){ if(show){ RD_PAGE = page; renderRead(); rdOpenitiRenderProgress(state, page); } return; }
  var req = ++state.req;
  state.pending[page] = req;
  if(show){
    RD_PAGE = page;
    RD_PAGES[page] = '正在载入阿拉伯原文…';
    renderRead();
    rdOpenitiRenderProgress(state, page, '正在按需读取阿拉伯原文…');
  }
  var controller = (window.AbortController ? new AbortController() : null);
  if(controller) state.controllers[page] = controller;
  var signal = controller ? {signal:controller.signal} : {};
  fetch(API_BASE() + '/api/catalog/read?id=' + encodeURIComponent(state.id) + '&page=' + page + '&stream=1', signal)
    .then(function(r){ return r.json().then(function(d){ return {ok:r.ok,status:r.status,data:d}; }); })
    .then(function(d){
      if(window.RD_OPENITI !== state || state.cancelled || state.pending[page] !== req) return;
      var data = d.data || {};
      if(!d.ok && d.status !== 202){
        var err = new Error((data && (data.error || data.message)) || '原文载入失败');
        err.code = data && data.error_code; err.status = d.status; throw err;
      }
      state.total = data.total == null ? Number(state.total || 0) : Number(data.total || 0);
      state.bytesRead = Number(data.bytes_read || state.bytesRead || 0);
      state.sourceBytes = Number(data.source_bytes || state.sourceBytes || 0);
      state.progress = Number(data.progress || state.progress || 0);
      state.eof = !!data.eof;
      state.pagesReady = Number(data.pages_ready || state.pagesReady || 0);
      state.source = data.source || state.source;
      state.sourceUrl = data.source_url || state.sourceUrl;
      state.textUrl = data.text_url || state.textUrl;
      rdOpenitiRenderProgress(state, page, d.status === 202 ? (data.message || '正在按需读取阿拉伯原文…') : '原文已就绪');
      if(d.status === 202 || !data.ready){
        delete state.pending[page];
        delete state.controllers[page];
        state.retryTimers[page] = setTimeout(function(){ rdOpenitiFetch(page, show); }, Math.max(250, Math.min(2500, Number(data.retry_after_ms || 500))));
        return;
      }
      RD_PAGES[page] = String(data.text || '（本页没有可显示的正文）');
      state.loaded[page] = true;
      delete state.pending[page];
      delete state.controllers[page];
      rdOpenitiSaveCache(state, page, data);
      if(show){ RD_PAGE = page; rdBuildToc(); renderRead(); rdOpenitiRenderProgress(state, page, '原文已就绪'); }
      if(show && (!state.total || page + 1 < state.total) && !state.loaded[page + 1]) setTimeout(function(){ rdOpenitiFetch(page + 1, false); }, 80);
    })
    .catch(function(e){
      if(window.RD_OPENITI !== state || state.cancelled || state.pending[page] !== req) return;
      delete state.pending[page]; delete state.controllers[page];
      state.error = e && e.message ? e.message : '原文暂时无法载入';
      if(show){
        RD_PAGES[page] = '原文载入失败：' + state.error;
        RD_PAGE = page;
        renderRead();
        rdOpenitiRenderProgress(state, page, '读取失败，可点击下一页或重试');
      }
    })
    .finally(function(){
      if(state.controllers) delete state.controllers[page];
    });
}
function openIslamicBook(id){
  var b = islamicBook(id); if(!b) return;
  if(b.special === 'quran'){ showQuran(); return; }
  if(b.special === 'hadith'){ showH6(); return; }
  if(b.text_mode === 'arabic_original_link'){
    openModal('mReader');
    var body = document.getElementById('mReaderBody'), tEl = document.getElementById('mReaderTitle');
    if(tEl) tEl.textContent = b.t || '阿拉伯原文';
    if(body) body.innerHTML = '<div style="padding:22px;text-align:center;color:#8a8c8f;font-size:12px">正在打开软件内阿拉伯原文…</div>';
    rdStopAudio(); RD = null; RD_BOOK_META = b; RD_ISLAMIC_GUIDE = false; RD_OPENITI = {id:b.id,total:0,loaded:{},pending:{},controllers:{},retryTimers:{},req:0,pagesReady:0,bytesRead:0,sourceBytes:0,progress:0,eof:false,cancelled:false,source:b.source || 'OpenITI/KITAB',sourceUrl:b.u || '',textUrl:b.text_url || '',error:''};
    RD_PAGES = ['正在载入阿拉伯原文…']; RD_PAGE = 0; RD_TOC = []; rdBuildToc(); renderRead(); rdOpenitiFetch(0, true); return;
  }
  try{ window.open(b.u, '_blank'); }catch(e){ location.href = b.u; }
}
function openIslamicGuide(id){
  var b = islamicBook(id); if(!b) return;
  openModal('mReader');
  var tEl = document.getElementById('mReaderTitle'), body = document.getElementById('mReaderBody');
  if(tEl) tEl.textContent = 'AI 导读 · ' + (b.t || '经典书目');
  RD_AUDIO = null; RD_BOOK_META = b; RD_ISLAMIC_GUIDE = !!b.ai_guide; RD_PAGES = [];
  var nl = String.fromCharCode(10);
  var source = [b.source || '公开书目来源', b.access || '', b.rights || ''].filter(Boolean).join(' · ');
  var g = b.ai_guide || {};
  var terms = (g.key_terms || []).map(function(x){ return (x.ar || '') + '：' + (x.cn || '') + '。' + (x.explanation || ''); }).join(nl);
  var guideText = ['【详细书目 AI 导读】', '书名：' + (b.t || ''), '作者：' + (b.a || '未标明'), '时代/版本：' + (b.y || '未标明'), '学科：' + (b.c || '') + ' · ' + (b.c_ar || ''), '', '作品概览：' + (g.summary || b.intro || '暂无导览'), '历史与文本背景：' + (g.historical_context || ''), '学习目标：' + (g.study_objectives || []).join('；'), '阅读路径：' + (g.reading_route || []).join('；'), '核心术语：' + terms, '比较角度：' + (g.comparative_focus || []).join('；'), 'AI 讲解规则：' + (g.ai_profile || b.ai_profile || ''), '证据边界：' + (g.evidence_boundary || ''), '来源：' + source, '阅读入口：' + (b.u || '')].join(nl);
  RD_PAGES = [guideText];
  RD_PAGE = 0; RD_TOC = []; rdBuildToc(); renderRead();
}
async function showCatalog(){
  var body = document.getElementById('mCatBody');
  if(!body) return;
  if(CAT_META){ renderCat(); return; }
  body.innerHTML = '<div style="padding:44px;text-align:center;color:#8a8c8f;font-size:13px">加载书库…</div>';
  try{
    var r = await fetch(API_BASE() + '/api/catalog/meta');
    if(!r.ok) throw new Error('HTTP ' + r.status);
    CAT_META = await r.json();
  }catch(e){
    body.innerHTML = '<div style="padding:32px;text-align:center;color:#b3261e;font-size:13px">书库加载失败：' + catEsc(e && e.message ? e.message : e) + '</div>';
    return;
  }
  renderCat();
}
function renderCat(){
  var body = document.getElementById('mCatBody');
  if(!body || !CAT_META) return;
  var cats = CAT_META.categories || {};
  var side = '<div class="bk-side"><div class="bk-side-h">جميع الكتب · 全部书目</div>';
  side += '<button class="bk-cat' + (CAT_CUR === '全部' ? ' on' : '') + '" onclick="catPick(&#39;全部&#39;)"><span>全部书目</span><i>' + (CAT_META.total || 0) + '</i></button>';
  if(CAT_META.disciplines && CAT_META.disciplines.length){
    side += '<div class="bk-side-h" style="margin-top:10px">伊斯兰学科 · العلوم</div>';
    CAT_META.disciplines.forEach(function(d){
      var count = cats[d.name] || 0;
      side += '<button class="bk-cat bk-cat-discipline' + (CAT_CUR === d.name ? ' on' : '') + '" onclick="catPick(&#39;' + catEsc(d.name) + '&#39;)"><span>' + catEsc((d.icon || '•') + ' ' + d.name) + '</span><i>' + count + '</i></button>';
    });
  }
  Object.keys(cats).forEach(function(c){
    if(CAT_META.disciplines && CAT_META.disciplines.some(function(d){ return d.name === c; })) return;
    side += '<button class="bk-cat' + (CAT_CUR === c ? ' on' : '') + '" onclick="catPick(&#39;' + catEsc(c) + '&#39;)"><span>' + catEsc(c) + '</span><i>' + cats[c] + '</i></button>';
  });
  if(CAT_META.tag_facets && CAT_META.tag_facets.length){
    side += '<div class="bk-side-h" style="margin-top:10px">专题标签 · الموضوعات</div>';
    CAT_META.tag_facets.slice(0, 18).forEach(function(f){
      side += '<button class="bk-cat bk-cat-tag' + (CAT_TAG === f.id ? ' on' : '') + '" onclick="catTagPick(&#39;' + catEsc(f.id) + '&#39;)"><span>' + catEsc(f.name) + '</span><i>' + (f.count || 0) + '</i></button>';
    });
  }
  if(CAT_META.fiqh_school_facets && CAT_META.fiqh_school_facets.length){
    side += '<div class="bk-side-h" style="margin-top:10px">法学派作品 · المذاهب</div>';
    CAT_META.fiqh_school_facets.forEach(function(f){
      side += '<button class="bk-cat bk-cat-school' + (CAT_SCHOOL === f.id ? ' on' : '') + '" onclick="catSchoolPick(&#39;' + catEsc(f.id) + '&#39;)"><span>' + catEsc(f.name) + '</span><i>' + (f.count || 0) + '</i></button>';
    });
  }
  side += '<div class="bk-side-h" style="margin-top:10px">其他</div>';
  side += '<button class="bk-cat' + (CAT_CUR === '__HIST__' ? ' on' : '') + '" onclick="catPick(&#39;__HIST__&#39;)"><span>世界历史 · Archive</span><i>20129</i></button>';
  side += '</div>';
  var main = '<div class="bk-main"><div class="bk-top"><div class="bk-title">' + catEsc(CAT_CUR === '__HIST__' ? '世界历史' : CAT_CUR) + '</div>' +
    '<input class="bk-q" id="catQ" placeholder="搜索书名 / 作者…" value="' + catEsc(CAT_Q) + '" oninput="catFilter(this.value)"></div>' +
    '<div class="bk-count" id="catCount"></div><div class="bk-grid" id="catGrid"></div>' +
    '<div class="bk-more"><button class="act-btn" onclick="catPage(1)">加载更多</button></div></div>';
  body.innerHTML = libTabs() + '<div class="bk-wrap">' + side + main + '</div>';
  renderCatGrid();
}
function catPick(c){ CAT_CUR = c; CAT_TAG = ''; CAT_SCHOOL = ''; CAT_PAGE = 0; renderCat(); }
function catTagPick(tag){ CAT_TAG = CAT_TAG === tag ? '' : tag; CAT_SCHOOL = ''; CAT_PAGE = 0; renderCat(); }
function catSchoolPick(school){ CAT_SCHOOL = CAT_SCHOOL === school ? '' : school; CAT_TAG = ''; CAT_PAGE = 0; renderCat(); }
function catList(){ renderCatGrid(); }
async function renderCatGrid(){
  var box = document.getElementById('catGrid');
  if(!box) return;
  if(CAT_CUR === '__HIST__'){ return histIntoGrid(box); }
  if(CAT_PAGE === 0){ CAT_ITEMS = []; box.innerHTML = '<div style="padding:20px;color:#8a8c8f;font-size:12px">加载中…</div>'; }
  try{
    var u = API_BASE() + '/api/catalog?cat=' + encodeURIComponent(CAT_CUR) + '&tag=' + encodeURIComponent(CAT_TAG) + '&school=' + encodeURIComponent(CAT_SCHOOL) + '&q=' + encodeURIComponent(CAT_Q) + '&page=' + CAT_PAGE + '&size=' + CAT_SIZE;
    var r = await fetch(u);
    var d = await r.json();
    if(d.error) throw new Error(d.error);
    CAT_TOTAL = d.total || 0;
    CAT_ITEMS = CAT_ITEMS.concat(d.items || []);
  }catch(e){
    box.innerHTML = '<div style="padding:20px;color:#b3261e;font-size:12px">加载失败</div>';
    return;
  }
  box.innerHTML = CAT_ITEMS.map(function(b){
    window.NUR_ISLAMIC_BOOKS = window.NUR_ISLAMIC_BOOKS || {};
    if(b.id) window.NUR_ISLAMIC_BOOKS[b.id] = b;
    var hue = catHue(b.c_ar || b.c || 'x');
    var t = catEsc(b.t);
    var versionNote = b.openiti && b.openiti.version_count ? ('版本 ' + b.openiti.version_count) : '';
    var sub = catEsc([b.a, b.y, b.level, versionNote].filter(Boolean).join(' · '));
    var _u = b.u || (b.t ? ('https://shamela.ws/index.php/search?q=' + encodeURIComponent(b.t)) : '');
    var _attr = ' data-u="' + catEsc(_u) + '"' + (b.id ? ' data-catid="' + catEsc(b.id) + '"' : '') + ' onclick="bkOpen(this)"';
    if(b.r){ _attr += ' data-rt="' + b.r.t + '" data-rid="' + (b.r.id || '') + '" data-rp="' + catEsc(b.r.p || '') + '"'; }
    return '<div class="bk-card"' + _attr + '>' +
      '<div class="bk-cover cv" style="--cv1:hsl(' + hue + ',34%%,36%%);--cv2:hsl(' + hue + ',40%%,18%%)">' +
      (b.cover ? '<img class="bk-img" loading="lazy" src="' + catEsc(b.cover) + '" onerror="this.classList.add(&#39;off&#39;)">' : '') +
      '<span class="cv-orn">❁</span>' +
      '<span class="bk-t">' + t + '</span>' +
      '<span class="cv-line"></span>' +
      '<span class="cv-cat">' + catEsc(b.c || '') + '</span></div>' +
      '<div class="bk-meta"><b>' + t + '</b><span>' + sub + '</span><span class="bk-source">' + catEsc(b.source || '') + '</span>' +
      '<div class="bk-card-actions"><button class="bk-in" onclick="bkGuide(event, this.parentNode.parentNode.parentNode)">✦ AI 导读</button>' +
      (b.text_url ? '<button class="bk-in bk-original" onclick="bkOriginal(event, this.parentNode.parentNode.parentNode)">软件内读原文</button>' : '') +
      ((b.special || b.r) ? ('<button class="bk-in" onclick="bkInApp(event, this.parentNode.parentNode.parentNode)">' + (b.special ? '进入阅读' : 'App 内读') + '</button>') : '') + '</div></div></div>';
  }).join('');
  var cc = document.getElementById('catCount');
  if(cc) cc.textContent = '已显示 ' + CAT_ITEMS.length + ' / ' + CAT_TOTAL + ' 部';
}
async function histIntoGrid(box){
  box.innerHTML = '<div style="padding:20px;color:#8a8c8f;font-size:12px">加载中…</div>';
  try{
    var r = await fetch(API_BASE() + '/api/history?q=' + encodeURIComponent(CAT_Q) + '&page=' + CAT_PAGE + '&size=60');
    var d = await r.json();
    if(!d || d.error) throw new Error('fail');
    var items = d.items || [];
    box.innerHTML = items.map(function(b){
      var t = catEsc(b.title || '');
      var sub = catEsc([b.creator, b.year, b.lang].filter(Boolean).join(' · '));
      return '<div class="bk-card" data-hid="' + b.id + '" onclick="openHist(this)">' +
        '<div class="bk-cover" style="background:linear-gradient(150deg,#a1887f,#6d4c41)"><img class="bk-img" loading="lazy" src="https://archive.org/services/img/' + b.id + '" onerror="this.classList.add(&#39;off&#39;)"><span class="bk-t">' + t + '</span></div>' +
        '<div class="bk-meta"><b>' + t + '</b><span>' + sub + '</span></div></div>';
    }).join('');
    var cc = document.getElementById('catCount');
    if(cc) cc.textContent = '世界历史 · 共 ' + (d.total || 0) + ' 部（已显示 ' + items.length + '）';
  }catch(e){
    box.innerHTML = '<div style="padding:20px;color:#8a8c8f;font-size:12px">历史书库加载失败</div>';
  }
}
function catPage(d){ CAT_PAGE += d; renderCatGrid(); }
function catFilter(v){ CAT_Q = v; CAT_PAGE = 0; renderCatGrid(); }
// ===== 世界典籍哲人哲言（按部加载）=====
var H6_IDX = null, H6_BOOK = null, H6_PAGE = 0, H6_Q = '', H6_PER = 50, H6_SEC = '全部', H6_KEY = '';
async function showH6(){
  openModal('mH6');
  var body = document.getElementById('mH6Body');
  if(!body) return;
  if(H6_IDX){ renderH6Index(); return; }
  body.innerHTML = '<div style="padding:44px;text-align:center;color:#8a9c8f;font-size:13px">加载世界典籍目录…</div>';
  try{
    var r = await fetch(API_BASE() + '/data/hadith/index.json');
    if(!r.ok) throw new Error('HTTP ' + r.status);
    H6_IDX = await r.json();
  }catch(e){
    body.innerHTML = '<div style="padding:24px;text-align:center;color:#b3261e;font-size:13px">加载失败：' + catEsc(e && e.message ? e.message : e) + '</div>';
    return;
  }
  renderH6Index();
}
function renderH6Index(){
  var body = document.getElementById('mH6Body');
  if(!body || !H6_IDX) return;
  var list = H6_IDX.books || [];
  var h = '<div class="h6-total">世界典籍格言 · 共 ' + H6_IDX.total + ' 段（阿语原典）</div>';
  h += '<div class="bk-grid">';
  list.forEach(function(x){
    h += '<div class="bk-card" onclick="openH6Book(&#39;' + x.key + '&#39;)">' +
      '<div class="bk-cover" style="background:linear-gradient(150deg,#14503e,#0e3529);aspect-ratio:3/3.6">' +
      '<span class="bk-t" style="font-size:14px">' + catEsc(x.ar) + '</span></div>' +
      '<div class="bk-meta"><b>' + catEsc(x.cn) + '</b><span>' + x.n + ' 段 · ' + x.mb + ' MB</span></div></div>';
  });
  h += '</div>';
  body.innerHTML = h;
}
async function openH6Book(k){
  var body = document.getElementById('mH6Body');
  if(!body) return;
  H6_BOOK = null; H6_PAGE = 0; H6_Q = ''; H6_KEY = k;
  body.innerHTML = '<div style="padding:44px;text-align:center;color:#8a9c8f;font-size:13px">加载中…</div>';
  try{
    var r = await fetch(API_BASE() + '/data/hadith/' + k + '.json');
    if(!r.ok) throw new Error('HTTP ' + r.status);
    H6_BOOK = await r.json();
  }catch(e){
    body.innerHTML = '<div style="padding:24px;text-align:center;color:#b3261e;font-size:13px">加载失败</div>';
    return;
  }
  renderH6Book();
}
function h6SecName(k){
  var secs = (H6_BOOK && H6_BOOK.sections) || {};
  var x = secs[k];
  if(!x) return '';
  return x.cn || x.en || '';
}
function renderH6Book(){
  var body = document.getElementById('mH6Body');
  if(!body || !H6_BOOK) return;
  var d = H6_BOOK, secs = d.sections || {};
  var h = '<div class="h6-top"><button class="s-btn" style="width:auto;padding:6px 11px;font-size:11.5px" onclick="renderH6Index()">‹ 目录</button>' +
    '<b>' + catEsc(d.name_cn) + '</b><span class="h6-meta">' + (d.hadiths || []).length + ' 段 · ' + Object.keys(secs).length + ' 篇</span></div>';
  h += '<div class="h6-secs">';
  h += '<button class="chip' + (H6_SEC === '全部' ? ' on' : '') + '" onclick="h6Sec(&#39;全部&#39;)">全部</button>';
  Object.keys(secs).forEach(function(k){
    var nm = (secs[k] && secs[k].cn) ? secs[k].cn : k;
    h += '<button class="chip' + (H6_SEC === k ? ' on' : '') + '" onclick="h6Sec(&#39;' + k + '&#39;)">' + catEsc(nm) + '</button>';
  });
  h += '</div>';
  h += '<input class="bk-q" id="h6Q" placeholder="搜阿语文字或序号…" value="' + catEsc(H6_Q) + '" oninput="H6_Q=this.value;H6_PAGE=0;renderH6List()" style="width:100%%;margin:0 0 10px">';
  h += '<div id="h6List"></div>';
  body.innerHTML = h;
  renderH6List();
}
function h6Sec(k){ H6_SEC = k; H6_PAGE = 0; renderH6Book(); }
function renderH6List(){
  var box = document.getElementById('h6List');
  if(!box || !H6_BOOK) return;
  var all = H6_BOOK.hadiths || [], q = (H6_Q || '').trim(), list = [], i, x;
  for(i = 0; i < all.length; i++){
    x = all[i];
    if(H6_SEC !== '全部' && String(x.s) !== String(H6_SEC)) continue;
    if(q && String(x.n).indexOf(q) < 0 && (x.ar || '').indexOf(q) < 0) continue;
    list.push(x);
  }
  var start = H6_PAGE * H6_PER, page = list.slice(start, start + H6_PER);
  var pages = Math.max(1, Math.ceil(list.length / H6_PER));
  var h = '<div class="h6-count">' + ((H6_SEC === '全部') ? '全部' : catEsc(h6SecName(H6_SEC))) + ' · 共 ' + list.length + ' 段 · 第 ' + (H6_PAGE + 1) + ' / ' + pages + ' 页</div>';
  h += page.map(function(y){
    return '<div class="h6-item" data-n="' + y.n + '"><div class="h6-line"><span class="h6-no">#' + y.n + '</span>' +
      '<span class="h6-sec">' + catEsc(h6SecName(y.s)) + '</span>' +
      '<button class="s-btn h6-tr" style="width:auto;padding:3px 10px;font-size:11px" onclick="h6Trans(this)">译文+注释</button>' +
      '<button class="s-btn h6-tr" style="width:auto;padding:3px 10px;font-size:11px" onclick="h6Read(this)">阅读</button></div>' +
      '<div class="h6-ar" onclick="h6Read(this)">' + catEsc(y.ar) + '</div></div>';
  }).join('');
  h += '<div class="h6-pg"><button class="act-btn" onclick="h6Page(-1)">‹ 上一页</button><button class="act-btn" onclick="h6Page(1)">下一页 ›</button></div>';
  box.innerHTML = h;
}
async function h6Read(el){
  var item = el.closest('.h6-item');
  if(!item) return;
  var n = item.getAttribute('data-n') || '';
  var ar = (item.querySelector('.h6-ar') || {}).textContent || '';
  var nm = (H6_BOOK && H6_BOOK.name_cn) ? H6_BOOK.name_cn : '哲言';
  openModal('mReader');
  var tEl = document.getElementById('mReaderTitle');
  if(tEl) tEl.textContent = nm + ' · 第 ' + n + ' 段';
  RD_PAGES = [ar];
  RD_PAGE = 0;
  RD_TOC_TITLE = nm + ' · 篇';
  RD_TOC = [];
  var _secs = (H6_BOOK && H6_BOOK.sections) || {};
  Object.keys(_secs).forEach(function(k){ RD_TOC.push({name: (_secs[k] && _secs[k].cn) ? _secs[k].cn : k, act: 'h6SecJump(' + JSON.stringify(String(k)) + ')'}); });
  renderRead();
  try{
    var r = await fetch(API_BASE() + '/api/hnote?b=' + encodeURIComponent(H6_KEY) + '&n=' + encodeURIComponent(n));
    var d = await r.json();
    if(d && !d.error){
      var pg = (d.cn ? ('【译文】\\n' + d.cn) : '') + (d.note ? ('\\n\\n【注释】\\n' + d.note) : '');
      if(pg){ RD_PAGES.push(pg); }
    }
  }catch(e){}
}
async function h6Trans(btn){
  var item = btn.closest('.h6-item');
  if(!item) return;
  var old = item.querySelector('.h6-an');
  if(old){ old.parentNode.removeChild(old); btn.textContent = '译文+注释'; return; }
  var n = item.getAttribute('data-n') || '';
  btn.textContent = '生成中…';
  try{
    var r = await fetch(API_BASE() + '/api/hnote?b=' + encodeURIComponent(H6_KEY) + '&n=' + encodeURIComponent(n));
    var d = await r.json();
    if(!d || d.error) throw new Error((d && d.error) || 'fail');
    var el = document.createElement('div');
    el.className = 'h6-an';
    el.innerHTML = '<div class="an-cn">' + catEsc(d.cn || '') + '</div>' +
      (d.note ? ('<div class="an-note"><span class="an-tag">注释</span>' + catEsc(d.note) + '</div>') : '');
    item.appendChild(el);
    btn.textContent = '收起';
  }catch(e){ btn.textContent = '译文+注释'; alert('生成失败：' + (e && e.message ? e.message : e)); }
}
function h6Page(d){
  H6_PAGE = Math.max(0, H6_PAGE + d);
  renderH6List();
  var b = document.getElementById('mH6Body');
  if(b) b.scrollTop = 0;
}

// ===== AI 翻译：句子卡 =====
async function trCard(btn){
  var card = btn.closest('.s-card');
  if(!card) return;
  var old = card.querySelector('.tr-cn');
  if(old){ old.parentNode.removeChild(old); btn.classList.remove('on'); return; }
  var ar = (card.querySelector('.s-ar') || {}).textContent || '';
  if(!ar) return;
  btn.classList.add('on');
  var box = card.querySelector('.s-tr') || card;
  var el = document.createElement('div');
  el.className = 'tr-cn';
  el.textContent = '翻译中…';
  box.appendChild(el);
  try{
    var r = await fetch(API_BASE() + '/api/chat/message', {method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({message: '把下面这段阿拉伯语翻译成简体中文，只输出译文，不要解释：\\n' + ar, session_id: 'tr', token: webToken()})});
    var d = await r.json();
    el.textContent = (d && d.arabic) ? d.arabic : '（翻译失败）';
  }catch(e){ el.textContent = '翻译失败，请稍后再试'; }
}
// ===== 世界文明图谱（极简抽象 / 学术博物馆风） =====
var CIV_SUB = [
  {n:'01', t:'医学', ar:'الطب', d:'伊本·西那《医典》影响欧洲六百年'},
  {n:'02', t:'法学', ar:'الفقه', d:'四大教法学派的形成与体系'},
  {n:'03', t:'天文', ar:'الفلك', d:'星盘、历法与马拉盖天文台'},
  {n:'04', t:'数学', ar:'الرياضيات', d:'代数与印度数字的西传'},
  {n:'05', t:'哲学', ar:'الفلسفة', d:'翻译运动与理性传统'},
  {n:'06', t:'地理', ar:'الجغرافيا', d:'伊本·白图泰的三十年旅程'},
  {n:'07', t:'语言', ar:'اللغة', d:'语法学与辞书的辉煌'},
  {n:'08', t:'建筑', ar:'العمارة', d:'拱券、穹顶与几何装饰'}
];
var CIV_EVT = [
  {y:'610', t:'启示降示', d:'麦加希拉山洞中开始降示《经典选读》'},
  {y:'622', t:'希吉拉', d:'迁徙麦地那，公元 622 年'},
  {y:'762', t:'巴格达建城', d:'阿拔斯王朝奠基，智慧宫兴起'},
  {y:'830', t:'翻译运动', d:'希腊·波斯·印度典籍译为阿拉伯语'},
  {y:'1000', t:'黄金时代', d:'医学、天文、数学的巅峰'},
  {y:'1325', t:'伊本·白图泰启程', d:'三十年行历三大洲'}
];
function civMapSvg(){
  // 抽象线描地图：地理节点 + 连线 + 星月几何
  var nodes = [[70,120],[130,70],[210,95],[300,60],[360,120],[300,170],[215,190],[140,175],[250,130],[180,120]];
  var paths = [[0,1],[1,2],[2,3],[3,4],[4,5],[5,6],[6,7],[7,8],[8,9],[9,2],[9,0],[6,0]];
  var h = '<svg viewBox="0 0 440 240" class="civ-svg" preserveAspectRatio="xMidYMid meet">';
  h += '<rect x="0" y="0" width="440" height="240" fill="none"/>';
  paths.forEach(function(p){
    var a = nodes[p[0]], b = nodes[p[1]];
    var mx = (a[0]+b[0])/2, my = (a[1]+b[1])/2 - 18;
    h += '<path d="M' + a[0] + ' ' + a[1] + ' Q' + mx + ' ' + my + ' ' + b[0] + ' ' + b[1] + '" fill="none" stroke="#6b7a5c" stroke-width="1" opacity=".55"/>';
  });
  nodes.forEach(function(nd, i){
    h += '<circle cx="' + nd[0] + '" cy="' + nd[1] + '" r="' + (i %% 4 === 0 ? 5 : 3) + '" fill="#f7f2e6" stroke="#8a7a3f" stroke-width="1.2"/>';
  });
  // 星月几何装饰
  h += '<g opacity=".75" transform="translate(390,26)"><path d="M0 0a9 9 0 1 0 0 18 7 7 0 1 1 0-18z" fill="#b08d4f"/></g>';
  h += '<g opacity=".6" transform="translate(392,60) scale(.8)"><path d="M9 0l2.2 5.4L17 6.2l-4.2 3.8L14 15.6 9 12.6 4 15.6l1.2-5.6L1 6.2l5.8-.8z" fill="#8a7a3f"/></g>';
  h += '<g opacity=".5" transform="translate(34,34) scale(.9)"><circle cx="9" cy="9" r="9" fill="none" stroke="#6b7a5c"/><circle cx="9" cy="9" r="4" fill="none" stroke="#8a7a3f"/></g>';
  h += '</svg>';
  return h;
}
var CIV = null;
async function loadCiv(){
  if(CIV) return CIV;
  try{ var r = await fetch(API_BASE() + '/data/civ.json'); CIV = await r.json(); }catch(e){ CIV = {}; }
  return CIV;
}
function civCard(x){
  var d = (x.text || '').replace(/\s+/g, ' ').slice(0, 90);
  return '<div class="civ-sub civ-item" onclick="openCivItem(this)" data-name="' + catEsc(x.name || '') + '">' +
    '<div class="civ-t">' + catEsc(x.name || '') + '</div>' +
    (x.ar ? ('<div class="civ-ar">' + catEsc(x.ar) + '</div>') : '') +
    '<div class="civ-d">' + catEsc(d) + '…</div></div>';
}
function civSection(title, ar, list){
  if(!list || !list.length) return '';
  return '<div class="civ-sec">' + title + ' <span class="civ-sec-ar">' + ar + '</span> <i>' + list.length + '</i></div>' +
    '<div class="civ-grid">' + list.map(civCard).join('') + '</div>';
}
async function renderCiv(){
  var box = document.getElementById('civWrap');
  if(!box) return;
  box.innerHTML = '<div class="civ-lead">加载文明图谱…</div>';
  await loadCiv();
  var h = '<div class="civ-lead">以地图、学者、王朝、城市与大事五味线索，铺开阿拉伯世界文明的细节。点击任一卡片可看详细条目。</div>';
  h += '<div class="civ-card"><div class="civ-card-h"><b>疆域与路线</b><span>الخرائط والمسالك</span></div>' + civMapSvg() + '</div>';
  h += '<div class="civ-sec">文明主题 <span class="civ-sec-ar">الموضوعات</span></div><div class="civ-grid">';
  h += CIV_SUB.map(function(x){
    return '<div class="civ-sub"><div class="civ-num">' + x.n + '</div><div class="civ-t">' + x.t + '</div>' +
      '<div class="civ-ar">' + x.ar + '</div><div class="civ-d">' + x.d + '</div></div>';
  }).join('');
  h += '</div>';
  h += '<input class="bk-q" id="civQ" placeholder="搜索学者 / 王朝 / 城市 / 大事…" oninput="civFilter(this.value)" style="width:100%%;margin:16px 0 6px">';
  h += '<div id="civLists"></div>';
  box.innerHTML = h;
  civFilter('');
}
var CIVR = null;
async function loadCivRulers(){
  if(CIVR) return CIVR;
  try{ var r = await fetch(API_BASE() + '/data/civ_rulers.json'); CIVR = await r.json(); }catch(e){ CIVR = {}; }
  return CIVR;
}
async function openCivDynasty(name){
  await loadCivRulers();
  var list = (CIVR || {})[name];
  var it = (CIV.dynasties || []).filter(function(x){ return x.name === name; })[0] || {name: name, text: ''};
  openModal('mReader');
  var tEl = document.getElementById('mReaderTitle');
  if(tEl) tEl.textContent = name + (list ? (' · ' + list.length + ' 位君主') : '');
  rdStopAudio(); RD_AUDIO = null; RD_TOC = []; RD_BOOK_META = null; RD_ISLAMIC_GUIDE = false;
  var pages = [ it.text || '（无简介）' ];
  if(list && list.length){
    pages.push('【君主列表 · ' + list.length + ' 位】' + String.fromCharCode(10, 10) +
      list.map(function(x, i){ return (i + 1) + '. ' + x.name + (x.ar ? (' / ' + x.ar) : ''); }).join(String.fromCharCode(10)));
    list.forEach(function(x){
      pages.push('◆ ' + x.name + (x.ar ? (' · ' + x.ar) : '') + String.fromCharCode(10, 10) + (x.text || ''));
    });
  }
  RD_PAGES = pages;
  RD_PAGE = 0;
  rdBuildToc();
  renderRead();
}
window.CIV_ALL = null;
function civFilter(q){
  var wrap = document.getElementById('civLists');
  if(!wrap || !CIV) return;
  q = (q || '').trim();
  var f = function(list){
    if(!q) return list;
    return (list || []).filter(function(x){ return (x.name || '').indexOf(q) >= 0 || (x.ar || '').indexOf(q) >= 0 || (x.text || '').indexOf(q) >= 0; });
  };
  var h = '';
  h += civSection('学者与思想家', 'العلماء', f(CIV.scholars));
  h += civSection('王朝与帝国', 'الدول', f(CIV.dynasties));
  h += civSection('城市与圣地', 'المدن', f(CIV.cities));
  h += civSection('大事与战役', 'الأحداث', f(CIV.events));
  wrap.innerHTML = h || '<div class="srch-tip">没有找到。</div>';
}
function openCivItem(el){
  var name = el.getAttribute('data-name');
  if((CIV.dynasties || []).some(function(x){ return x.name === name; })){ return openCivDynasty(name); }
  var all = [].concat(CIV.scholars || [], CIV.dynasties || [], CIV.cities || [], CIV.events || []);
  var it = all.filter(function(x){ return x.name === name; })[0];
  if(!it) return;
  openModal('mReader');
  var tEl = document.getElementById('mReaderTitle');
  if(tEl) tEl.textContent = it.name + (it.ar ? (' · ' + it.ar) : '');
  rdStopAudio(); RD_AUDIO = null; RD_TOC = []; RD_BOOK_META = null; RD_ISLAMIC_GUIDE = false;
  RD_PAGES = [it.text || '（无内容）'];
  RD_PAGE = 0;
  renderRead();
}
// ===== Apple Books 式横向书架 =====
function shelfHtml(title, moreAct, items){
  var h = '<div class="shelf"><div class="shelf-h"><b>' + title + '</b>' + (moreAct ? ('<span onclick="' + moreAct + '">全部 ›</span>') : '') + '</div><div class="shelf-row">';
  h += items.map(function(it){
    return '<div class="shelf-it" onclick="' + (it.a || '') + '">' +
      '<div class="shelf-cv" style="background:' + (it.bg || 'linear-gradient(150deg,#5b93bd,#2f4a5f)') + '">' +
      (it.img ? ('<img loading="lazy" src="' + it.img + '" onerror="this.remove()">') : '') +
      '<span class="shelf-tt">' + catEsc(it.t || '') + '</span></div>' +
      '<b>' + catEsc(it.t || '') + '</b><span>' + catEsc(it.s || '') + '</span></div>';
  }).join('');
  h += '</div>'
  return h;
}
function tkScroll(){try{var g=document.getElementById('homeShelves');if(g&&g.scrollIntoView)g.scrollIntoView({behavior:'smooth'});}catch(e){}}
async function renderShelves(){
  var box = document.getElementById('homeShelves');
  if(!box) return;
  var K = [
    {t:'\u4e66\u5e93', i:'📚', k:'books'},
        {t:'\u4e16\u754c\u4e66\u5e93', i:'🌍', k:'library'},
    {t:'\u53e4\u5170\u7ecf\u4e0e\u7ecf\u6ce8', i:'🕌', k:'quran'},
    {t:'\u963f\u62c9\u4f2f\u8bed\u5165\u95e8', i:'🔤', k:'intro'},
    {t:'\u8bed\u6cd5', i:'📐', k:'grammar'},
    {t:'\u8bcd\u6cd5', i:'🧩', k:'morph'},
    {t:'\u65e5\u5e38\u53e3\u8bed', i:'🗣', k:'talk'},
    {t:'\u542c\u529b\u8bad\u7ec3', i:'🎧', k:'listen'},
    {t:'\u53e5\u5b50\u5e93', i:'📝', k:'sent'},
    {t:'\u4e2d\u963f\u8981\u95fb', i:'\U0001F4F0', k:'belt'},
    {t:'\u641c\u7d22', i:'🔍', k:'search'},

  ];
  window.HS_K = K;
  var _d = 0; for(var _i = 0; _i < K.length; _i++){ if(K[_i].k === 'books'){ _d = _i; break; } }
  window.HS_TAB = _d;
  var h = '';
  h += '<div class="hs-hero"><div class="hs-h1">\u71c3\u706f\u540c\u5b66</div>'
     + '<div class="hs-h2">\u0645\u0646\u0635\u0629 \u062a\u0639\u0644\u064f\u0651\u0645 \u0627\u0644\u0639\u0631\u0628\u064a\u0629 \u00b7 \u963f\u62c9\u4f2f\u5b66\u4e60\u5e73\u53f0</div>' + '<div class="hs-dict-btn" onclick="openDict()">\U0001F4D6 \u67e5\u5355\u8bcd\uff08\u963f\u8bed \u2192 \u4e2d\u6587\u91ca\u4e49 \u00b7 \u8bcd\u6839 \u00b7 \u8fd1\u4e49/\u53cd\u4e49\u8bcd \u00b7 \u4f8b\u53e5\uff09</div></div>';
  h += '<div class="hs-body">';
  h += '<div class="hs-rail" id="tkSeg">' + K.map(function(x, xi){
      return '<span class="chip' + (x.k === 'books' ? ' on' : '') + '" onclick="hsGo(' + xi + ', this)">'
        + '<i class="chip-i">' + x.i + '</i><em class="chip-t">' + x.t + '</em></span>';
    }).join('') + '</div>';
  h += '<div class="hs-main">';
  h += '<div class="hs-sec"><h3 id="hsSecTitle">\u4e66\u67b6</h3><span class="hs-cnt" id="hsSecSub"></span></div>';
  h += '<div class="hs-grid" id="tkBooks"><div class="hs-load">\u8f7d\u5165\u4e66\u5e93\u2026</div></div>';
  h += '</div></div>';
  box.innerHTML = h;
  try{
    window.__COVERS = await (await fetch(API_BASE() + '/data/covers.json')).json();
  }catch(e){ window.__COVERS = window.__COVERS || {}; }
  try{ hsToday(); }catch(e){} try{ hsRender(); }catch(e){}
  // 自动更新检查：页面版本落后就自动重载（解决顽固缓存）
  try{
    var _bv = window.__NUR_BUILD || '';
    var _ls = '';
    try{ _ls = localStorage.getItem('nur_build') || ''; }catch(e){}
    if(_bv && _ls && _ls !== _bv){
      try{ localStorage.setItem('nur_build', _bv); }catch(e){}
      location.reload(true);
      return;
    }
    if(_bv){ try{ localStorage.setItem('nur_build', _bv); }catch(e){} }
  }catch(e){}
}
function tkPick(el){
  try{
    var seg = document.getElementById('tkSeg');
    if(seg) Array.prototype.forEach.call(seg.querySelectorAll('.chip'), function(x){ x.classList.remove('on'); });
    el.classList.add('on');
    var fn = el.getAttribute('data-act');
    if(fn){ new Function(fn)(); }
    else { try{ window.scrollTo({top:0,behavior:'smooth'}); }catch(e){} }
  }catch(e){}
}
function tkOpen(el){
  try{
    var id = el.getAttribute('data-bid');
    var rt = el.getAttribute('data-rt') || 'shamela';
    if(!id) return;
    if(rt === 'zy'){ try{ showH6(); }catch(e){} return; }
    openReadById(id, rt);
  }catch(e){}
}

function tkSeg(idx){
  var seg = document.getElementById('tkSeg'), grid = document.getElementById('tkGrid');
  if(!seg || !grid) return;
  seg.innerHTML = '<span onclick="openSearchAll()" style="text-align:left;padding:9px 10px;font-size:13.5px;font-weight:600;color:#5a6159;cursor:pointer">🔍 搜索</span>' +
    TK_KINDS.map(function(x, xi){
      var on = (xi === idx);
      return '<span onclick="tkSeg(' + xi + ')" style="text-align:left;padding:9px 10px;font-size:13.5px;font-weight:700;border-radius:8px;cursor:pointer;' +
        (on ? 'background:#0f5132;color:#fff' : 'color:#3a423e') + '">' + x + '</span>';
    }).join('');
  var kind = TK_KINDS[idx] || '世界书库';
  grid.innerHTML = '<div style="grid-column:1/-1;color:#8a8f88;font-size:12.5px;padding:6px 2px">载入中…</div>';
  var url = kind === '世界书库' ? (API_BASE() + '/api/catalog?page=0&size=36')
          : kind === '历史文库' ? (API_BASE() + '/api/history?page=0')
          : kind === '中文古籍' ? (API_BASE() + '/api/cnbooks?size=36')
          : '';
  if(kind === '课程' || kind === '工具'){
    var K = [
      {t:'阿拉伯语入门', s:'字母 · 发音', e:'📗', bg:'#0f5132', a:'showAlphabet()'},
      {t:'阿语语法', s:'名词 · 动词', e:'📐', bg:'#2f6f9f', a:'showGrammar()'},
      {t:'高频词汇', s:'两千词', e:'🔤', bg:'#4e7f96', a:'showVocab()'},
      {t:'日常口语', s:'问候 · 点餐', e:'💬', bg:'#c07a63', a:'openTalk()'},
      {t:'听力训练', s:'真人朗读', e:'🎧', bg:'#3f6f7a', a:'showListen()'},
      {t:'哲言集', s:'先贤语录', e:'📜', bg:'#7d93a6', a:'showH6()'},
      {t:'查词典', s:'阿语→中文', e:'🔍', bg:'#08301e', a:'openDict()'},
      {t:'句子库', s:'日常用语', e:'💬', bg:'#16344c', a:"openModal('mLearn')"},
      {t:'每日一句', s:'谚语 · 点读', e:'✨', bg:'#8a6d2b', a:'nextQuote()'},
      {t:'全站搜索', s:'搜全部', e:'🔎', bg:'#22414c', a:'openSearchAll()'},
      {t:'字母课', s:'28 个字母', e:'🅰️', bg:'#333c4c', a:'showAlphabet()'},
    ].filter(function(x){ return kind === '课程' ? (['showAlphabet()','showGrammar()','showVocab()','openTalk()','showListen()','showH6()'].indexOf(x.a) >= 0) : true; });
    grid.innerHTML = K.map(function(x){
      return '<div onclick="' + x.a + '" style="cursor:pointer"><div style="height:118px;border-radius:6px 10px 10px 6px;background:' + x.bg +
        ';display:flex;align-items:center;justify-content:center;font-size:32px;box-shadow:0 6px 16px rgba(20,30,25,.2)">' + x.e + '</div>' +
        '<b style="display:block;font-size:12.5px;margin-top:7px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">' + x.t + '</b>' +
        '<span style="display:block;font-size:10.5px;color:#8a8f88">' + x.s + '</span></div>';
    }).join('');
    return;
  }
  fetch(url).then(function(r){ return r.json(); }).then(function(d){
    var list = (d.items || d.books || []).slice(0, 36);
    if(!list.length){ grid.innerHTML = '<div style="grid-column:1/-1;color:#8a8f88;padding:10px">暂无</div>'; return; }
    var PAL = ['#0f5132','#2f6f9f','#4e7f96','#c07a63','#5b93bd','#7d93a6','#3f6f7a','#6c7d9a','#8a6d2b','#333c4c','#1d7a4f','#22414c'];
    grid.innerHTML = list.map(function(b, bi){
      var t = b.t || b.title || '';
      var id = b.id || '';
      var c = PAL[bi %% PAL.length];
      var short = t.length > 26 ? (t.slice(0, 26) + '…') : t;
      return '<div data-bid="' + id + '" onclick="openBookCard(this)" style="cursor:pointer">' +
        '<div style="height:132px;border-radius:5px 9px 9px 5px;background:linear-gradient(160deg,' + c + ',#0b2b1f);position:relative;overflow:hidden;box-shadow:0 7px 18px rgba(20,30,25,.22)">' +
          '<div style="position:absolute;left:0;top:0;bottom:0;width:6px;background:linear-gradient(90deg,rgba(255,255,255,.3),rgba(255,255,255,.04))"></div>' +
          '<div style="position:absolute;inset:6px 8px 8px 12px;display:flex;align-items:center;justify-content:center;text-align:center;color:#f3eddc;font-family:var(--ar-font);font-size:12px;line-height:1.7;overflow:hidden">' + String(short || '') + '</div>' +
        '</div>' +
        '<b style="display:block;font-size:11.5px;margin-top:6px;line-height:1.4;max-height:32px;overflow:hidden">' + String(t || '').slice(0, 40) + '</b></div>';
    }).join('');
  }).catch(function(){ grid.innerHTML = '<div style="grid-column:1/-1;color:#b4553a;padding:10px">载入失败</div>'; });
  try{}catch(e){}
}
function openBookCard(el){ try{ var id = el.getAttribute('data-bid'); if(id) openBookById(id); }catch(e){} }
function openBookById(id){
  try{
    if(!id) return;
    if(String(id).indexOf('cn:') === 0){ if(typeof openCn === 'function') return openCn(null, id); }
    return openReadById(id);
  }catch(e){}
}
function paginateText(txt, size){
  size = size || 1500;
  var NL = String.fromCharCode(10);
  var t = String(txt || '');
  var lines = t.split(NL);
  var pages = [], cur = '';
  var RE = /^第[0-9〇一二三四五六七八九十百千零两]+[回卷章节]/;
  for(var i = 0; i < lines.length; i++){
    var raw = lines[i];
    var hd = RE.test(String(raw).replace(/\s/g, ''));
    if(hd && cur.length > size){ pages.push(cur); cur = raw; continue; }
    cur += (cur ? NL : '') + raw;
    if(cur.length >= size * 1.6){ pages.push(cur); cur = ''; }
  }
  if(String(cur).replace(/\s/g, '')) pages.push(cur);
  var out = pages.filter(function(x){ return String(x).replace(/\s/g, ''); });
  if(!out.length && String(t).replace(/\s/g, '')) out = [String(t)];
  return out;
}
async function openReadById(id, t){
  try{
    openModal('mReader');
    var body = document.getElementById('mReaderBody');
    var tEl = document.getElementById('mReaderTitle');
    if(body) body.innerHTML = '<div style="padding:44px;text-align:center;color:#8a8f88;font-size:13px">正在载入全文…（首次需从云端取，稍等几秒）</div>';
    rdStopAudio(); RD = null; RD_PAGES = []; RD_PAGE = 0; RD_AUDIO = null; RD_TOC = []; RD_BOOK_META = null; RD_ISLAMIC_GUIDE = false;
    window.RD_ISCN = (t === 'cn');
    var u = (t === 'cn')
      ? (API_BASE() + '/api/cnbook?id=' + encodeURIComponent(id))
      : (API_BASE() + '/api/read?t=' + encodeURIComponent(t || 'shamela') + '&id=' + encodeURIComponent(id));
    var r = await fetch(u);
    var d = await r.json();
    if(!d || d.error){
      if(body) body.innerHTML = '<div style="padding:32px;text-align:center;color:#b4553a;font-size:13px">' + ((d && d.error) || '无内容') + '</div>';
      return;
    }
    if(t === 'cn'){
      RD_PAGES = paginateText(d.text || '');
    }else{
      var pages = (d.pages || []).map(function(p){ return String(p.body || p.text || p.content || '').replace(/<[^>]+>/g, ''); }).filter(function(x){ return x.trim(); });
      RD_PAGES = pages.length ? pages : paginateText(d.text || '');
    }
    if(!RD_PAGES.length){
      if(body) body.innerHTML = '<div style="padding:32px;text-align:center;color:#8a8f88">这本书没有可用正文</div>';
      return;
    }
    var _tt = String(d.title || d.t || '阅读').replace(/-/g, ' ').replace(/\s+/g, ' ').trim();
    if(tEl) tEl.textContent = _tt;
    rdBuildToc(); renderRead();
  }catch(e){
    var b2 = document.getElementById('mReaderBody');
    if(b2) b2.innerHTML = '<div style="padding:32px;text-align:center;color:#b4553a">载入失败：' + (e && e.message ? e.message : '') + '</div>';
  }
}

function tkSeg(idx){
  var seg = document.getElementById('tkSeg'), grid = document.getElementById('tkGrid');
  if(!seg || !grid) return;
  var ALL = window.__TK_ALL || [];
  seg.innerHTML = '<span onclick="openSearchAll()" style="text-align:left;padding:9px 10px;font-size:13.5px;font-weight:600;color:#5a6159;cursor:pointer">🔍 搜索</span>' +
    ALL.map(function(x, xi){
      var on = (xi === idx);
      return '<span onclick="tkSeg(' + xi + ')" style="text-align:left;padding:9px 10px;font-size:13.5px;font-weight:700;border-radius:8px;cursor:pointer;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;' +
        (on ? 'background:#0f5132;color:#fff' : 'color:#3a423e') + '">' + x.t + '</span>';
    }).join('');
  var x = ALL[idx];
  if(!x){ grid.innerHTML = ''; return; }
  grid.innerHTML =
    '<div style="text-align:center;padding:6px 0 2px">' +
      '<div style="width:120px;height:164px;margin:0 auto;border-radius:6px 12px 12px 6px;position:relative;overflow:hidden;background:' + x.bg + ';box-shadow:0 10px 24px rgba(20,30,25,.24)">' +
        '<div style="position:absolute;left:0;top:0;bottom:0;width:8px;background:linear-gradient(90deg,rgba(255,255,255,.34),rgba(255,255,255,.05))"></div>' +
        '<div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:44px">' + x.e + '</div>' +
      '</div>' +
      '<div style="font-size:18px;font-weight:800;margin-top:14px;color:#1d2321">' + x.t + '</div>' +
      '<div style="font-size:12.5px;color:#8a8f88;margin-top:6px;line-height:1.7">' + x.s + '</div>' +
      '<div onclick="' + x.a + '" style="margin-top:16px;display:inline-block;background:#0f5132;color:#fff;font-size:14px;font-weight:800;padding:11px 30px;border-radius:999px;cursor:pointer">开始学习</div>' +
    '</div>';
}

function tkSeg(idx){
  var seg = document.getElementById('tkSeg'), grid = document.getElementById('tkGrid');
  if(!seg || !grid) return;
  var KS = ['全部','最近学习','课程','书库','工具','我的'];
  var k = KS[idx] || '全部';
  seg.innerHTML = '<span onclick="openSearchAll()" style="text-align:left;padding:10px 12px;font-size:14.5px;font-weight:700;border-radius:9px;cursor:pointer;color:#5a6159">🔍 搜索</span>' + KS.map(function(x, xi){
    var on = (x === k);
    return '<span onclick="tkSeg(' + xi + ')" style="text-align:left;padding:10px 12px;font-size:14.5px;font-weight:700;border-radius:9px;cursor:pointer;' +
      (on ? 'background:#0f5132;color:#fff' : 'color:#5a6159') + '">' + x + '</span>';
  }).join('');
  var list;
  if(k === '书库'){ openLib(); list = (window.__TK_ALL || []); }
  else if(k === '我的'){ try{ var tb=document.querySelector('.tabbar .tb:nth-child(3)'); if(tb) tb.click(); }catch(e){} list = (window.__TK_ALL || []); }
  else if(k === '最近学习'){ list = (window.__TK_ALL || []).slice(0,6); }
  else { list = (window.__TK_ALL || []).filter(function(x){ return k === '全部' || x.k === k; }); }
  grid.innerHTML = list.map(function(x){
    return '<div onclick="' + x.a + '" style="cursor:pointer">' +
      '<div style="position:relative;height:140px;border-radius:6px 10px 10px 6px;background:' + x.bg + ';overflow:hidden;box-shadow:0 8px 18px rgba(20,30,25,.22)">' +
        '<div style="position:absolute;left:0;top:0;bottom:0;width:7px;background:linear-gradient(90deg,rgba(255,255,255,.34),rgba(255,255,255,.06))"></div>' +
        '<div style="position:absolute;left:7px;top:0;bottom:0;width:1px;background:rgba(0,0,0,.16)"></div>' +
        '<div style="position:absolute;left:0;right:0;top:0;height:38%%;background:linear-gradient(180deg,rgba(255,255,255,.22),rgba(255,255,255,0))"></div>' +
        '<div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:34px">' + x.e + '</div>' +
      '</div>' +
      '<b style="display:block;font-size:12.5px;margin-top:8px;color:#1d2321;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">' + x.t + '</b>' +
      '<span style="display:block;font-size:10.5px;color:#8a8f88;margin-top:1px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">' + x.s + '</span></div>';
  }).join('');
}

var TK_LOG = [];
var TK_TOPICS = ['日常问候','自我介绍','点餐吃饭','问路出行','购物讲价','学校学习','家庭朋友','旅行见闻','工作职业','新闻时事'];
var TK_TOPIC = '';
var TK_BUSY = false;
var TK_REC = null;
var TK_TIMER = null;
var TK_T = 0;
function openTalk(){ openModal('mTalk'); renderTalk(); }
function openCiv(){
  document.querySelectorAll('.page').forEach(function(p){ p.style.display = 'none'; });
  var el = document.getElementById('page-civ');
  if(el) el.style.display = '';
  document.querySelectorAll('.tabbar .tb').forEach(function(t){ t.classList.remove('on'); });
  renderCiv();
  window.scrollTo(0, 0);
}
function renderTalk(){
  var body = document.getElementById('mTalkBody');
  if(!body) return;
  var h = '<div class="tk-topics">';
  TK_TOPICS.forEach(function(t){
    h += '<button class="chip' + (TK_TOPIC === t ? ' on' : '') + '" onclick="tkSetTopic(&#39;' + t + '&#39;)">' + t + '</button>';
  });
  h += '</div>';
  h += '<div class="tk-msgs" id="tkMsgs"></div>';
  h += '<div class="tk-status" id="tkStatus"></div>';
  h += '<div class="tk-ctrls">' +
       '<button class="tk-mic" id="tkMicBtn" onclick="tkMic()">🎙 点一下开始说（说完自动停）</button>' +
       '<input class="tk-in" id="tkText" placeholder="也可以用文字说…（阿语或中文，回车发送）" onkeydown="if(event.key===&#39;Enter&#39;){tkTextSend()}">' +
       '<button class="s-btn" style="width:auto;padding:10px 14px;font-size:12px" onclick="tkTextSend()">发送</button>' +
       '<button class="s-btn" style="width:auto;padding:10px 14px;font-size:12px" onclick="tkHint()">提示一句</button>' +
       '<button class="s-btn" style="width:auto;padding:10px 14px;font-size:12px" onclick="tkClear()">清空</button></div>';
  body.innerHTML = h;
  tkRender();
}
function tkSetTopic(t){ TK_TOPIC = t; renderTalk(); }
function tkClear(){ TK_LOG = []; renderTalk(); }
function tkRender(){
  var box = document.getElementById('tkMsgs');
  if(!box) return;
  if(!TK_LOG.length){
    box.innerHTML = '<div class="tk-tip">场景：<b>' + TK_TOPIC + '</b><br>点下面麦克风，用阿拉伯语说一句（比如 السلام عليكم），说完停顿一下就会自动发送。<br>AI 会用阿语回你并朗读出来，可以练听力和口语。</div>';
    return;
  }
  box.innerHTML = TK_LOG.map(function(m){
    return '<div class="tk-row ' + m.who + '"><div class="tk-b">' +
      '<div class="tk-ar">' + catEsc(m.ar || '') + '</div>' +
      (m.cn ? ('<div class="tk-cn">' + catEsc(m.cn) + '</div>') : '') +
      '</div></div>';
  }).join('');
  box.scrollTop = box.scrollHeight;
}
function tkPush(who, ar, cn){ TK_LOG.push({who: who, ar: ar, cn: cn || ''}); tkRender(); }
var TK_T0 = 0, TK_TIMER = null;
function tkStatus(txt){
  var el = document.getElementById('tkStatus');
  if(el) el.textContent = txt || '';
}
async function tkMic(){
  var btn = document.getElementById('tkMicBtn');
  if(TK_REC){ try{ TK_REC.stop(); }catch(e){} return; }
  if(TK_BUSY) return;
  if(!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia){
    alert('这个环境不支持麦克风（浏览器要求 https 或 localhost）。用下面输入框打字也能练。');
    return;
  }
  try{
    var stream = await navigator.mediaDevices.getUserMedia({audio: {echoCancellation: true, noiseSuppression: true}});
    var mime = '';
    try{
      if(window.MediaRecorder && MediaRecorder.isTypeSupported && MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) mime = 'audio/webm;codecs=opus';
    }catch(e){}
    var mr = mime ? new MediaRecorder(stream, {mimeType: mime}) : new MediaRecorder(stream);
    TK_CHUNKS = [];
    mr.ondataavailable = function(e){ if(e.data && e.data.size) TK_CHUNKS.push(e.data); };
    mr.onstop = function(){
      try{ stream.getTracks().forEach(function(t){ t.stop(); }); }catch(e){}
      if(TK_SIL){ clearInterval(TK_SIL); TK_SIL = null; }
      if(TK_TIMER){ clearInterval(TK_TIMER); TK_TIMER = null; }
      TK_REC = null;
      if(btn){ btn.textContent = '🎙 点一下开始说'; btn.classList.remove('rec'); }
      var blob = new Blob(TK_CHUNKS, {type: mr.mimeType || 'audio/webm'});
      if(blob.size < 1200){ tkStatus('录到的声音太短，再说一次？'); return; }
      tkSend(blob);
    };
    TK_REC = mr; mr.start(250);
    TK_T0 = Date.now();
    if(btn){ btn.textContent = '⏹ 正在听…点一下可手动结束'; btn.classList.add('rec'); }
    tkStatus('🎙 正在听… 0.0s（说完停顿约 1.5 秒自动发送）');
    TK_TIMER = setInterval(function(){ tkStatus('🎙 正在听… ' + ((Date.now() - TK_T0) / 1000).toFixed(1) + 's（停顿即发送）'); }, 200);
    var actx = new (window.AudioContext || window.webkitAudioContext)();
    var src = actx.createMediaStreamSource(stream);
    var an = actx.createAnalyser(); an.fftSize = 1024; src.connect(an);
    var data = new Uint8Array(an.fftSize), silence = 0, ticks = 0;
    TK_SIL = setInterval(function(){
      ticks++;
      an.getByteTimeDomainData(data);
      var sum = 0;
      for(var i = 0; i < data.length; i++){ var v = (data[i] - 128) / 128; sum += v * v; }
      var rms = Math.sqrt(sum / data.length);
      if(rms < 0.008) silence++; else silence = 0;
      var secs = (Date.now() - TK_T0) / 1000;
      if((silence > 14 && secs > 1.6) || secs > 25){ try{ mr.stop(); }catch(e){} try{ actx.close(); }catch(e){} }
    }, 110);
  }catch(e){
    var msg = (e && e.name) ? e.name : '';
    if(msg === 'NotAllowedError'){ alert('麦克风被拒绝。请在系统设置 → 隐私与安全性 → 麦克风 里允许本 App，或用下方输入框打字练习。'); }
    else if(msg === 'NotFoundError'){ alert('没有检测到麦克风设备。可以用下方输入框打字练习。'); }
    else { alert('无法使用麦克风（' + (e && e.message ? e.message : e) + '）。可用下方输入框打字练习。'); }
  }
}
async function tkTextSend(){
  var inp = document.getElementById('tkText');
  var t = (inp && inp.value || '').trim();
  if(!t || TK_BUSY) return;
  if(inp) inp.value = '';
  tkPush('me', t, '');
  TK_BUSY = true;
  try{
    var prompt = '【阿语口语陪练】场景：' + TK_TOPIC + '。学生说：' + t +
      '。请用阿拉伯语自然回应一到两句（带音符，口语化），然后换行用「中文：」开头给中文翻译。不要解释语法。';
    var r2 = await fetch(API_BASE() + '/api/chat/message', {method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({message: prompt, session_id: 'talk_' + TK_TOPIC, token: webToken()})});
    var d2 = await r2.json();
    var full = ((d2 && d2.arabic) || '').trim();
    var lines = full.split(/\\n+/).filter(function(x){ return x.trim(); });
    var ar = [], cn = '';
    lines.forEach(function(l){ if(/^中文[:：]/.test(l.trim())) cn = l.replace(/^中文[:：]\s*/, ''); else if(!cn) ar.push(l); });
    var arTxt = ar.join(' ').trim() || full;
    tkPush('ai', arTxt, cn);
    tkSpeak(arTxt);
  }catch(e){
    tkPush('ai', '（连接失败，请稍后再试）', '');
  }
  TK_BUSY = false;
}
async function tkSend(blob){
  TK_BUSY = true;
  tkStatus('📝 识别中…');
  tkPush('me', '…', '');
  try{
    var r = await fetch(API_BASE() + '/api/asr', {method:'POST', headers:{'Content-Type':'application/octet-stream','X-ASR-Lang':'ar'}, body: blob});
    var d = await r.json();
    var said = (d.text || '').trim();
    TK_LOG.pop();
    if(!said){ tkPush('me', '（没听清，再说一遍？）', ''); TK_BUSY = false; return; }
    tkPush('me', said, '');
    tkStatus('🤔 努尔老师思考中…');
    var prompt = '【阿语口语陪练】场景：' + TK_TOPIC + '。学生说：' + said +
      '。请用阿拉伯语自然回应一到两句（带音符，口语化），然后换行用「中文：」开头给中文翻译。不要解释语法。';
    var r2 = await fetch(API_BASE() + '/api/chat/message', {method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({message: prompt, session_id: 'talk_' + TK_TOPIC, token: webToken()})});
    var d2 = await r2.json();
    var full = ((d2 && d2.arabic) || '').trim();
    var lines = full.split(/\\n+/).filter(function(x){ return x.trim(); });
    var ar = [], cn = '';
    lines.forEach(function(l){
      if(/^中文[:：]/.test(l.trim())){ cn = l.replace(/^中文[:：]\s*/, ''); }
      else if(!cn){ ar.push(l); }
    });
    var arTxt = ar.join(' ').trim() || full;
    tkPush('ai', arTxt, cn);
    tkSpeak(arTxt);
    tkStatus('');
  }catch(e){
    TK_LOG.pop();
    tkPush('ai', '（连接失败，请稍后再试）', '');
    tkStatus('出错：' + (e && e.message ? e.message : e));
  }
  TK_BUSY = false;
}
function tkSpeak(txt){
  try{
    if(!window.speechSynthesis) return;
    window.speechSynthesis.cancel();
    var u = new SpeechSynthesisUtterance(String(txt).slice(0, 500));
    var vs = window.speechSynthesis.getVoices() || [], ar = null;
    for(var i = 0; i < vs.length; i++){ if((vs[i].lang || '').toLowerCase().indexOf('ar') === 0){ ar = vs[i]; break; } }
    if(ar){ u.voice = ar; u.lang = ar.lang; } else { u.lang = 'ar-SA'; }
    u.rate = 0.92;
    window.speechSynthesis.speak(u);
  }catch(e){}
}
async function tkHint(){
  tkPush('ai', 'جارٍ التحضير…', '');
  try{
    var r = await fetch(API_BASE() + '/api/chat/message', {method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({message: '【阿语口语陪练】场景：' + TK_TOPIC + '。请给学生一句可以说的阿拉伯语开场句（带音符），换行用「中文：」给翻译。', session_id: 'talk_hint', token: webToken()})});
    var d = await r.json();
    var full = ((d && d.arabic) || '').trim();
    TK_LOG.pop();
    var lines = full.split(/\\n+/).filter(function(x){ return x.trim(); });
    var ar = [], cn = '';
    lines.forEach(function(l){ if(/^中文[:：]/.test(l.trim())) cn = l.replace(/^中文[:：]\s*/, ''); else if(!cn) ar.push(l); });
    tkPush('ai', ar.join(' ').trim() || full, cn);
    tkSpeak(ar.join(' ').trim() || full);
  }catch(e){ TK_LOG.pop(); }
}

// ===== 中 / 阿 界面语言切换 =====
var UI_LANG = (function(){ try{ return localStorage.getItem('nur_lang') || 'zh'; }catch(e){ return 'zh'; } })();
var I18N = {
  zh: { n1:'句子', n2:'词汇', n3:'经典选读', n4:'历史', n5:'图书馆', n6:'', n7:'哲人哲言',
        home:'首页', learn:'世界图书馆', listen:'搜索', wordbook:'生词本', ai:'练习', me:'我的', all:'全部内容',
        sch:'搜索句子、词汇、文本、哲言…（回车）' },
  ar: { n1:'الجمل', n2:'المفردات', n3:'القرآن', n4:'التاريخ', n5:'المكتبة', n6:'', n7:'الحديث',
        home:'أقرأ الآن', learn:'المكتبة', listen:'بحث', wordbook:'الكلمات', ai:'تدريب', me:'حسابي', all:'كل المحتوى',
        sch:'ابحث في الجمل والمفردات والقرآن والحديث…' }
};
function applyLang(){
  var L = I18N[UI_LANG] || I18N.zh;
  ['n1','n2','n3','n4','n5','n6','n7'].forEach(function(k, i){
    var el = document.getElementById('nav' + (i + 1));
    if(el && L[k]) el.textContent = L[k];
  });
  var names = [L.home, L.learn, L.listen, L.wordbook, L.me];
  document.querySelectorAll('.tabbar .tb .t-nm').forEach(function(el, i){
    if(names[i]) el.textContent = names[i];
  });
  var st = document.querySelector('.sec-title h2');
  if(st) st.textContent = L.all;
  var q = document.getElementById('libQ');
  if(q) q.setAttribute('placeholder', L.sch);
  var b = document.getElementById('langBtn');
  if(b) b.textContent = (UI_LANG === 'zh') ? '中文' : 'عربي';
}
function toggleLang(){
  UI_LANG = (UI_LANG === 'zh') ? 'ar' : 'zh';
  try{ localStorage.setItem('nur_lang', UI_LANG); }catch(e){}
  applyLang();
}

// ===== 阅读器（可读全文：Shamela4 逐页 / waqfeya 整本）=====
var HOME_STATS = {};
function hs(k, d){
  var v = HOME_STATS[k];
  if(v === 0 || v) { try { return Number(v).toLocaleString(); } catch(e) { return v; } }
  return d;
}
function loadHomeStats(){
  fetch(API_BASE() + '/api/home_stats').then(function(r){ return r.json(); }).then(function(d){
    if(!d) return;
    HOME_STATS = d;
    try { renderShelves(); } catch(e){}
    var m = [['hsBooks','islamic_total'],['hsHistory','history_books'],['hsHadith','hadith'],['hsReadable','islamic_readable']];
    m.forEach(function(pr){ var e = document.getElementById(pr[0]); if(e && d[pr[1]] != null) e.textContent = Number(d[pr[1]]).toLocaleString(); });
    var t = document.getElementById('hsTime');
    if(t && d.time) t.textContent = '数据更新于 ' + d.time;
  }).catch(function(){});
}
var RD = null, RD_PAGES = [], RD_PAGE = 0, RD_AUDIO = null, RD_RECITER = 0,
 RD_TOC = [], RD_TOC_TITLE = '目录', RD_BOOK_META = null;
var RD_ISLAMIC_GUIDE = false;
var RD_OPENITI = null;
var RD_TOUCH_ACTIVE = false, RD_TOUCH_X = 0, RD_TOUCH_Y = 0, RD_TOUCH_SUPPRESS_CLICK_UNTIL = 0;
function rdTouchStart(ev){
  var t = ev && ev.touches && ev.touches[0];
  if(!t) return;
  RD_TOUCH_ACTIVE = true; RD_TOUCH_X = t.clientX; RD_TOUCH_Y = t.clientY;
}
function rdTouchMove(ev){
  if(!RD_TOUCH_ACTIVE) return;
  var t = ev && ev.touches && ev.touches[0];
  if(!t) return;
  var dx = t.clientX - RD_TOUCH_X, dy = t.clientY - RD_TOUCH_Y;
  if(Math.abs(dx) > 10 && Math.abs(dx) > Math.abs(dy) * 1.15 && ev.cancelable){
    ev.preventDefault();
  }
}
function rdTouchEnd(ev){
  if(!RD_TOUCH_ACTIVE) return;
  var t = ev && ev.changedTouches && ev.changedTouches[0];
  RD_TOUCH_ACTIVE = false;
  if(!t) return;
  var dx = t.clientX - RD_TOUCH_X, dy = t.clientY - RD_TOUCH_Y;
  if(Math.abs(dx) >= 56 && Math.abs(dx) > Math.abs(dy) * 1.25){
    RD_TOUCH_SUPPRESS_CLICK_UNTIL = Date.now() + 520;
    rdGo(dx < 0 ? 1 : -1);
  }
}
function rdTouchCancel(){ RD_TOUCH_ACTIVE = false; }
function rdShouldSuppressClick(){ return Date.now() < RD_TOUCH_SUPPRESS_CLICK_UNTIL; }
function rdBindTouch(paper){
  if(!paper) return;
  try{
    paper.addEventListener('touchstart', rdTouchStart, {passive:true});
    paper.addEventListener('touchmove', rdTouchMove, {passive:false});
    paper.addEventListener('touchend', rdTouchEnd, {passive:true});
    paper.addEventListener('touchcancel', rdTouchCancel, {passive:true});
  }catch(e){
    paper.addEventListener('touchstart', rdTouchStart, false);
    paper.addEventListener('touchmove', rdTouchMove, false);
    paper.addEventListener('touchend', rdTouchEnd, false);
    paper.addEventListener('touchcancel', rdTouchCancel, false);
  }
}
var RD_QURAN_AYAHS = [], RD_QURAN_PAGE_AYAHS = [], RD_QAUDIO = null, RD_QAUDIO_ROW = -1, RD_QRATE = 1, RD_QAUTO = true;
var RD_RECITERS = [
  {n:'米谢里·阿法西', u:'https://everyayah.com/data/Alafasy_128kbps/', path:'Alafasy_128kbps/'},
  {n:'苏达伊斯', u:'https://everyayah.com/data/Abdurrahmaan_As-Sudais_192kbps/', path:'Abdurrahmaan_As-Sudais_192kbps/'},
  {n:'舒莱姆', u:'https://everyayah.com/data/Saood_ash-Shuraym_128kbps/', path:'Saood_ash-Shuraym_128kbps/'},
  {n:'胡宰菲', u:'https://everyayah.com/data/Husary_128kbps/', path:'Husary_128kbps/'},
  {n:'明沙维', u:'https://everyayah.com/data/Minshawy_Mujawwad_192kbps/', path:'Minshawy_Mujawwad_192kbps/'}
];
async function openRead(el){
  var t = el.getAttribute('data-rt'), id = el.getAttribute('data-rid'), p = el.getAttribute('data-rp');
  if(!t){ return; }
  saveFootprint((el.querySelector('.bk-meta b')||{}).textContent||'阅读','书籍');
  openModal('mReader');
  var body = document.getElementById('mReaderBody');
  var tl = el.querySelector('.bk-meta b');
  var tEl = document.getElementById('mReaderTitle');
  if(tEl) tEl.textContent = tl ? tl.textContent : '阅读';
  if(!body) return;
  body.innerHTML = '<div style="padding:44px;text-align:center;color:#8a8c8f;font-size:13px">正在载入全文…（首次需从云端下载，稍等几秒）</div>';
  rdStopAudio();
  RD = null; RD_PAGES = []; RD_PAGE = 0; RD_AUDIO = null; RD_BOOK_META = null; RD_ISLAMIC_GUIDE = false;
  RD_QURAN_AYAHS = []; RD_QURAN_PAGE_AYAHS = []; RD_QAUDIO_ROW = -1;
  try{
    var u = API_BASE() + '/api/read?t=' + encodeURIComponent(t) + (t === 'shamela' ? ('&id=' + encodeURIComponent(id)) : ('&p=' + encodeURIComponent(p)));
    var r = await fetch(u);
    if(!r.ok) throw new Error('HTTP ' + r.status);
    RD = await r.json();
  }catch(e){
    body.innerHTML = '<div style="padding:32px;text-align:center;color:#b3261e;font-size:13px">载入失败：' + catEsc(e && e.message ? e.message : e) + '</div>';
    return;
  }
  if(!RD || RD.error){
    body.innerHTML = '<div style="padding:32px;text-align:center;color:#b3261e;font-size:13px">' + catEsc((RD && RD.error) || '无内容') + '</div>';
    return;
  }
  if(RD.t === 'shamela'){
    (RD.pages || []).forEach(function(x){ var b = (x.body || '').trim(); if(b) RD_PAGES.push(b); });
  }else{
    RD_PAGES = String(RD.text || '').split('PAGE_SEPARATOR').map(function(x){ return x.trim(); }).filter(Boolean);
  }
  if(!RD_PAGES.length){ body.innerHTML = '<div style="padding:32px;text-align:center;color:#8a8c8f">这本书没有可用正文</div>'; return; }
  // 目录：属于本书自己的（不再沿用上一本的）
  rdBuildToc();
  renderRead();
}
function rdJumpTo(n){
  try{
    n = parseInt(n, 10);
    if(RD_OPENITI){ if(!isNaN(n) && n >= 0 && (!RD_OPENITI.total || n < RD_OPENITI.total)) rdOpenitiFetch(n, true); return; }
    if(isNaN(n) || n < 0 || n >= RD_PAGES.length) return;
    if(RD_AUDIO && RD_AUDIO.kind === 'quran') rdQuranStop();
    RD_PAGE = n;
    try{ var old = document.querySelector('#rdTocBox'); if(old && old.parentNode) old.parentNode.removeChild(old); }catch(e){}
    renderRead();
  }catch(e){}
}
function rdBookmarkKey(){
  var meta = RD_BOOK_META || {};
  var state = RD_OPENITI || {};
  return String(state.id || meta.id || ((document.getElementById('mReaderTitle') || {}).textContent || 'reader')).trim().slice(0, 180);
}
function rdBookmarks(){
  try{ var d = JSON.parse(localStorage.getItem('nur_reader_bookmarks') || '{}'); return d && typeof d === 'object' ? d : {}; }catch(e){ return {}; }
}
function rdIsBookmarked(){ return !!rdBookmarks()[rdBookmarkKey()]; }
function rdSavePosition(){
  try{
    var key = rdBookmarkKey(), d = JSON.parse(localStorage.getItem('nur_reader_positions') || '{}');
    d[key] = {title:String((document.getElementById('mReaderTitle') || {}).textContent || '阅读').trim(), page:RD_PAGE + 1, total:(RD_OPENITI && RD_OPENITI.total) || RD_PAGES.length, updatedAt:Date.now()};
    localStorage.setItem('nur_reader_positions', JSON.stringify(d));
  }catch(e){}
}
function rdToggleBookmark(ev){
  try{ if(ev && ev.stopPropagation) ev.stopPropagation(); var key=rdBookmarkKey(), d=rdBookmarks();
    if(d[key]) delete d[key]; else d[key]={title:String((document.getElementById('mReaderTitle') || {}).textContent || '阅读').trim(),page:RD_PAGE+1,total:(RD_OPENITI&&RD_OPENITI.total)||RD_PAGES.length,updatedAt:Date.now()};
    localStorage.setItem('nur_reader_bookmarks', JSON.stringify(d)); renderRead();
  }catch(e){}
}
function rdBar(){
  var total = RD_PAGES.length;
  var pct = total > 1 ? Math.round((RD_PAGE + 1) * 100 / total) : 100;
  var marked = rdIsBookmarked();
  return '<div class="rd-bar">' +
    '<button class="rd-ic" onclick="rdGo(-1)" title="上一页">‹</button>' +
    '<span class="rd-pos">RDPOS</span>' +
    '<button class="rd-ic" onclick="rdGo(1)" title="下一页">›</button>' +
    '<button class="rd-ic rd-bookmark' + (marked ? ' on' : '') + '" onclick="rdToggleBookmark(event)" title="' + (marked ? '取消书签' : '添加书签') + '" aria-label="' + (marked ? '取消书签' : '添加书签') + '">' + (marked ? '★' : '☆') + '</button>' +
    '<button class="rd-ic rd-speak" onclick="' + ((RD_AUDIO && RD_AUDIO.kind === 'quran') ? 'rdQuranToggle(event)' : 'rdSpeak(this)') + '" title="诵读 / 朗读" style="background:#0f5132;color:#f6e7b4">🔊</button>' +
    (window.currentSurah && (currentSurah.id) ? '<button class="rd-ic" onclick="surahTafsir()" title="本章注释">📖</button>' : '') +
    '<button class="rd-ic" onclick="rdToc()" title="目录">☰</button>' +
    '<button class="rd-ic" onclick="rdMore()" title="更多">⋯</button></div>' +
    '<div class="rd-prog"><i style="width:RD_PCT%%"></i></div>';
}
function rdBarHtml(){
  var total = RD_OPENITI && RD_OPENITI.total ? RD_OPENITI.total : RD_PAGES.length;
  var unknown = !!(RD_OPENITI && !RD_OPENITI.total && !RD_OPENITI.eof);
  var pct = total > 1 ? Math.round((RD_PAGE + 1) * 100 / total) : (unknown ? Math.round((RD_OPENITI.progress || 0) * 100) : 100);
  var pos = (RD_PAGE + 1) + ' / ' + (unknown ? '…' : total);
  return rdBar().replace('RDPOS', pos).replace('RD_PCT', pct);
}
function rdToc(){
  var old = document.querySelector('#rdTocBox');
  if(old){ old.parentNode.removeChild(old); return; }
  if(!RD_TOC || !RD_TOC.length){ alert('这本还没有目录信息。'); return; }
  var d = document.createElement('div');
  d.id = 'rdTocBox'; d.className = 'rd-sheet rd-toc';
  var h = '<div class="rd-toc-h">' + catEsc(RD_TOC_TITLE || '目录') + ' · ' + RD_TOC.length + ' 项</div>';
  h += RD_TOC.map(function(x, i){ return '<button onclick="' + x.act + ';rdTocClose()">' + catEsc(x.name || '') + '</button>'; }).join('');
  d.innerHTML = h;
  document.body.appendChild(d);
}
function rdTocClose(){ var m = document.querySelector('#rdTocBox'); if(m) m.parentNode.removeChild(m); }
function h6SecJump(k){ try{ h6Sec(k); closeModal('mReader'); }catch(e){} }
function rdMore(){
  var m = document.querySelector('#rdSheet');
  if(m){ m.parentNode.removeChild(m); return; }
  var d = document.createElement('div');
  d.id = 'rdSheet'; d.className = 'rd-sheet';
  d.innerHTML =
    '<button onclick="' + ((RD_AUDIO && RD_AUDIO.kind === 'quran') ? 'rdQuranToggle(event);rdMore();' : 'rdSpeak(this);rdMore();') + '">🔊 播放真人诵读 / 朗读</button>' +
    '<button onclick="rdAudioBook(this);">🎧 有声书（真人朗读）</button>' +
    '<div class="rd-reciters">诵经人：' + RD_RECITERS.map(function(r, i){ return '<button class="' + (i === RD_RECITER ? 'on' : '') + '" onclick="rdReciter(' + i + ')">' + r.n + '</button>'; }).join('') + '</div>' +
    '<button onclick="rdTrans(this);rdMore();">🌐 中译本页</button>' +
    '<button onclick="rdToggleBookmark();rdMore();">' + (rdIsBookmarked() ? '★ 取消本页书签' : '☆ 添加本页书签') + '</button>' +
    '<button onclick="rdJump()">↦ 跳转页码</button>' +
    '<button onclick="rdFs(1)">A+ 放大字号</button>' +
    '<button onclick="rdFs(-1)">A− 缩小字号</button>' +
    '<div class="rd-appearance"><b>阅读外观</b><button onclick="rdTheme(&quot;paper&quot;);rdMore()">纸张</button><button onclick="rdTheme(&quot;sepia&quot;);rdMore()">暖白</button><button onclick="rdTheme(&quot;night&quot;);rdMore()">夜间</button></div>' +
    '<button onclick="rdToggleChrome();rdMore()">◌ 沉浸模式</button>' +
    '<button onclick="rdFull(this);rdMore();">⛶ 全屏 / 退出全屏</button>';
  document.body.appendChild(d);
  setTimeout(function(){ document.addEventListener('click', rdSheetClose); }, 50);
}
function rdSheetClose(ev){
  var m = document.querySelector('#rdSheet');
  if(m && !m.contains(ev.target) && ev.target.className !== 'rd-ic'){ m.parentNode.removeChild(m); document.removeEventListener('click', rdSheetClose); }
}
var RD_AB = null, RD_AB_TITLE = '';
async function rdAudioBook(btn){
  try{
    if(RD_AB){ if(RD_AB.paused){ RD_AB.play(); if(btn) btn.textContent = '🎧 暂停有声书'; } else { RD_AB.pause(); if(btn) btn.textContent = '🎧 继续有声书'; } return; }
    var title = ((document.getElementById('mReaderTitle') || {}).textContent || '').split('·')[0].trim();
    if(!title){ alert('没有识别到书名'); return; }
    if(btn) btn.textContent = '🎧 搜索有声书…';
    var r = await fetch(API_BASE() + '/api/audio?q=' + encodeURIComponent(title));
    var d = await r.json();
    if(!d || !d.found){ if(btn) btn.textContent = '🎧 有声书'; alert('这部书暂时没有找到真人朗读有声书（有声书多为公版英文书）。'); return; }
    var f = (d.files || [])[0];
    if(!f){ if(btn) btn.textContent = '🎧 有声书'; return; }
    var a = new Audio(f.u);
    RD_AB = a; RD_AB_TITLE = d.title || '';
    a.onended = function(){ RD_AB = null; if(btn) btn.textContent = '🎧 有声书'; };
    a.play();
    if(btn) btn.textContent = '🎧 暂停有声书';
  }catch(e){ if(btn) btn.textContent = '🎧 有声书'; alert('有声书加载失败'); }
}
function rdReciter(i){ RD_RECITER = i; try{ if(RD_QAUDIO) rdQuranStop(); window.__rdAudio && window.__rdAudio.pause(); window.__rdAudio = null; }catch(e){} var m=document.querySelector('#rdSheet'); if(m) m.parentNode.removeChild(m); rdMore(); }
function rdFs(d){
  var cur = parseInt(localStorage.getItem('nur_rdfont') || '18', 10);
  cur = Math.max(13, Math.min(30, cur + d));
  try{ localStorage.setItem('nur_rdfont', String(cur)); }catch(e){}
  var pg = document.querySelector('.rd-page');
  if(pg) pg.style.fontSize = cur + 'px';
}
function rdTheme(name){
  name = /^(paper|sepia|night|white)$/.test(name) ? name : 'paper';
  var m = document.getElementById('mReader');
  if(!m) return;
  m.classList.remove('rd-theme-paper','rd-theme-sepia','rd-theme-night','rd-theme-white');
  m.classList.add('rd-theme-' + name);
  try{ localStorage.setItem('nur_rdtheme', name); }catch(e){}
}
function rdApplyTheme(){
  var n = 'paper';
  try{ n = localStorage.getItem('nur_rdtheme') || 'paper'; }catch(e){}
  rdTheme(n);
}
function rdToggleChrome(){
  var m = document.getElementById('mReader');
  if(!m) return;
  m.classList.toggle('zen');
}
function rdQuranPageMarkup(){
  var rows = RD_QURAN_PAGE_AYAHS[RD_PAGE] || [];
  if(!rows.length) return rdWords(RD_PAGES[RD_PAGE] || '');
  return rows.map(function(row){
    var v = RD_QURAN_AYAHS[row] || {};
    return '<article class="rd-qayah" data-qrow="' + row + '" dir="rtl">' +
      '<div class="rd-qayah-top"><span class="rd-qayah-no">' + catEsc(String(v.n || row + 1)) + '</span><button class="rd-qayah-play" onclick="rdQuranPlayRow(' + row + ',event)" title="播放这一节">▶</button></div>' +
      '<div class="rd-qayah-ar">' + rdWords(v.a || '') + '</div>' +
      (v.z || v.c ? '<div class="rd-qayah-cn" dir="ltr">' + catEsc(v.z || v.c || '') + '</div>' : '') +
      '</article>';
  }).join('');
}
function rdQuranControlsHtml(){
  return '<section class="rd-qcontrols" aria-label="古兰经真人诵读控制">' +
    '<div class="rd-qcontrols-main"><button id="rdQuranPlayBtn" class="rd-qcontrol-primary" onclick="rdQuranToggle(event)">▶ 开始跟读</button>' +
    '<button class="rd-qcontrol-icon" onclick="rdQuranPrev()" title="上一节">‹</button><button class="rd-qcontrol-icon" onclick="rdQuranNext()" title="下一节">›</button>' +
    '<label class="rd-qcontrol-speed">速度 <select onchange="rdQuranSetRate(this.value)"><option value="0.75">0.75×</option><option value="1" selected>1×</option><option value="1.25">1.25×</option><option value="1.5">1.5×</option></select></label>' +
    '<label class="rd-qcontrol-auto"><input type="checkbox" checked onchange="rdQuranSetAuto(this.checked)"> 自动下一节</label></div>' +
    '<input id="rdQuranRange" class="rd-qrange" type="range" min="0" max="1000" value="0" step="1" oninput="rdQuranScrub(this.value)" aria-label="诵读进度">' +
    '<div class="rd-qcontrols-meta"><span id="rdQuranStatus">选择诵读家后开始跟读</span><span id="rdQuranTime">0:00 / 0:00</span></div></section>';
}
function rdQuranUpdateControls(){
  var a = RD_QAUDIO, playing = !!(a && !a.paused), btn = document.getElementById('rdQuranPlayBtn');
  if(btn) btn.textContent = playing ? 'Ⅱ 暂停跟读' : (RD_QAUDIO_ROW >= 0 ? '▶ 继续跟读' : '▶ 开始跟读');
  var range = document.getElementById('rdQuranRange');
  if(range && a && a.duration && isFinite(a.duration)) range.value = String(Math.round((a.currentTime / a.duration) * 1000));
  var tm = document.getElementById('rdQuranTime');
  if(tm) tm.textContent = fmtDur(a && a.currentTime) + ' / ' + fmtDur(a && a.duration);
  var st = document.getElementById('rdQuranStatus');
  if(st && RD_QAUDIO_ROW >= 0){ st.textContent = (playing ? '正在诵读 · ' : '已暂停 · ') + '第 ' + (RD_QAUDIO_ROW + 1) + ' 节'; }
}
function rdQuranSetActive(row, scroll){
  RD_QAUDIO_ROW = typeof row === 'number' ? row : -1;
  var nodes = document.querySelectorAll('.rd-qayah');
  for(var i = 0; i < nodes.length; i++){
    var on = parseInt(nodes[i].getAttribute('data-qrow'), 10) === RD_QAUDIO_ROW;
    nodes[i].classList.toggle('is-playing', on);
    if(on) nodes[i].setAttribute('aria-current', 'true'); else nodes[i].removeAttribute('aria-current');
    if(on && scroll){ try{ nodes[i].scrollIntoView({behavior:'smooth', block:'center'}); }catch(e){ try{ nodes[i].scrollIntoView(); }catch(e2){} } }
  }
  rdQuranUpdateControls();
}
function rdQuranAudioUrl(row){
  var rec = RD_RECITERS[RD_RECITER] || RD_RECITERS[0], sid = RD_AUDIO && RD_AUDIO.sid;
  return rec.u + String(sid || 1).padStart(3, '0') + String((RD_QURAN_AYAHS[row] || {}).n || row + 1).padStart(3, '0') + '.mp3';
}
function rdQuranLoadRow(row, autoplay){
  if(!(RD_AUDIO && RD_AUDIO.kind === 'quran') || row < 0 || row >= RD_QURAN_AYAHS.length) return;
  if(!RD_QAUDIO) RD_QAUDIO = new Audio();
  RD_QAUDIO.pause();
  RD_QAUDIO.src = API_BASE() + '/api/recite?u=' + encodeURIComponent(rdQuranAudioUrl(row));
  RD_QAUDIO.preload = 'auto'; RD_QAUDIO.playbackRate = RD_QRATE; RD_QAUDIO._row = row;
  RD_QAUDIO.onloadedmetadata = rdQuranUpdateControls;
  RD_QAUDIO.ontimeupdate = rdQuranUpdateControls;
  RD_QAUDIO.onplay = function(){ rdQuranSetActive(row, true); };
  RD_QAUDIO.onpause = function(){ rdQuranUpdateControls(); };
  RD_QAUDIO.onended = function(){
    if(RD_QAUDIO && RD_QAUDIO._row === row && RD_QAUTO && row + 1 < RD_QURAN_AYAHS.length){ rdQuranLoadRow(row + 1, true); }
    else if(RD_QAUDIO && RD_QAUDIO._row === row){ rdQuranSetActive(row, false); var st = document.getElementById('rdQuranStatus'); if(st) st.textContent = '本章诵读完成'; rdQuranUpdateControls(); }
  };
  RD_QAUDIO.onerror = function(){ var st = document.getElementById('rdQuranStatus'); if(st) st.textContent = '音频加载失败，请稍后重试'; rdQuranUpdateControls(); };
  RD_QAUDIO.load();
  RD_QAUDIO_ROW = row; rdQuranSetActive(row, false);
  if(autoplay){ var p = RD_QAUDIO.play(); if(p && p.catch) p.catch(function(){ var st = document.getElementById('rdQuranStatus'); if(st) st.textContent = '请再次点击播放按钮开始诵读'; }); }
}
function rdQuranPlayRow(row, ev){ if(ev && ev.stopPropagation) ev.stopPropagation(); if(RD_QAUDIO && RD_QAUDIO._row === row && !RD_QAUDIO.paused){ RD_QAUDIO.pause(); return; } rdQuranLoadRow(row, true); }
function rdQuranToggle(ev){ if(ev && ev.stopPropagation) ev.stopPropagation(); if(!RD_QURAN_AYAHS.length) return; if(RD_QAUDIO_ROW < 0) return rdQuranLoadRow(0, true); if(RD_QAUDIO && !RD_QAUDIO.paused){ RD_QAUDIO.pause(); } else if(RD_QAUDIO){ RD_QAUDIO.play().catch(function(){}); rdQuranSetActive(RD_QAUDIO_ROW, false); } else rdQuranLoadRow(RD_QAUDIO_ROW, true); }
function rdQuranStop(){ if(RD_QAUDIO){ RD_QAUDIO.pause(); RD_QAUDIO.onended = null; try{ RD_QAUDIO.removeAttribute('src'); RD_QAUDIO.load(); }catch(e){} } RD_QAUDIO = null; rdQuranSetActive(-1, false); }
function rdQuranPrev(){ if(!RD_QURAN_AYAHS.length) return; var n = Math.max(0, (RD_QAUDIO_ROW < 0 ? 0 : RD_QAUDIO_ROW) - 1); rdQuranLoadRow(n, true); }
function rdQuranNext(){ if(!RD_QURAN_AYAHS.length) return; var n = Math.min(RD_QURAN_AYAHS.length - 1, (RD_QAUDIO_ROW < 0 ? -1 : RD_QAUDIO_ROW) + 1); rdQuranLoadRow(n, true); }
function rdQuranSetRate(v){ RD_QRATE = parseFloat(v) || 1; if(RD_QAUDIO) RD_QAUDIO.playbackRate = RD_QRATE; }
function rdQuranSetAuto(v){ RD_QAUTO = !!v; }
function rdQuranScrub(v){ if(RD_QAUDIO && RD_QAUDIO.duration && isFinite(RD_QAUDIO.duration)) RD_QAUDIO.currentTime = (parseInt(v, 10) || 0) / 1000 * RD_QAUDIO.duration; }
function rdGuideList(items){
  if(!Array.isArray(items) || !items.length) return '';
  return '<ul class="rd-guide__list">' + items.map(function(x){ return '<li>' + catEsc(x) + '</li>'; }).join('') + '</ul>';
}
function rdGuideSection(title, body){
  return body ? '<section class="rd-guide__section"><h4>' + catEsc(title) + '</h4>' + body + '</section>' : '';
}
function rdGuideMarkup(b){
  var g = (b && b.ai_guide) || {}, h = '';
  var terms = Array.isArray(g.key_terms) ? g.key_terms : [];
  var sources = Array.isArray(g.sources) ? g.sources : [];
  h += '<article class="rd-guide">';
  h += '<div class="rd-guide__hero"><span class="rd-guide__mark">✦</span><div><b>' + catEsc(b.t || '经典书目') + '</b><small>' + catEsc([b.a, b.y, b.c].filter(Boolean).join(' · ')) + '</small></div></div>';
  h += '<div class="rd-guide__notice"><strong>详细 AI 导读</strong><span>基于公开书目元数据与已核验的官方/学术来源生成。它用于阿拉伯语与经典文本学习，不等于整本书全文，也不是法特瓦。</span></div>';
  h += rdGuideSection('作品概览', '<p>' + catEsc(g.summary || b.intro || '暂无导读。') + '</p>');
  h += rdGuideSection('历史与文本背景', '<p>' + catEsc(g.historical_context || '请回到所用版本的卷首、校勘说明和学术书目核对。') + '</p>');
  h += rdGuideSection('学习目标', rdGuideList(g.study_objectives));
  h += rdGuideSection('建议阅读路径', rdGuideList(g.reading_route));
  if(terms.length){
    h += '<section class="rd-guide__section"><h4>核心阿拉伯语术语</h4><div class="rd-guide__terms">' + terms.map(function(x){ return '<div class="rd-guide__term"><b dir="rtl">' + catEsc(x.ar || '') + '</b><strong>' + catEsc(x.cn || '') + '</strong><span>' + catEsc(x.explanation || '') + '</span></div>'; }).join('') + '</div></section>';
  }
  h += rdGuideSection('跨学派与比较角度', rdGuideList(g.comparative_focus));
  h += rdGuideSection('产品内 AI 讲解规则', '<p>' + catEsc(g.ai_profile || b.ai_profile || '先区分原文、作者观点、后世解释和模型归纳。') + '</p>');
  h += rdGuideSection('证据边界与核验提醒', '<p class="rd-guide__boundary">' + catEsc(g.evidence_boundary || '引用请回到原典、版本和页码核验。') + '</p>');
  if(sources.length){
    h += '<section class="rd-guide__section"><h4>已核验来源</h4><div class="rd-guide__sources">' + sources.map(function(x){ return '<a class="rd-guide__source" href="' + catEsc(x.url || '#') + '" target="_blank" rel="noopener"><strong>' + catEsc(x.title || x.url || '来源') + '</strong><span>' + catEsc(x.why || '') + '</span><em>打开官方/学术来源 ↗</em></a>'; }).join('') + '</div></section>';
  }
  h += '<div class="rd-guide__footer">来源、版本、原文、译文、学派观点与 AI 归纳必须分层核对；现实个案请咨询合格学者和适用法律专业人士。</div></article>';
  return h;
}
function renderRead(){
  var body = document.getElementById('mReaderBody');
  if(!body || !RD_PAGES.length) return;
  try{ rdApplyTheme(); }catch(e){}
  if(RD_PAGE < 0) RD_PAGE = 0;
  if(RD_PAGE > RD_PAGES.length - 1) RD_PAGE = RD_PAGES.length - 1;
  try{ rdSavePosition(); }catch(e){}
  var total = RD_PAGES.length;
  var head = '<div class="rd-head">RD_TITLE</div>';
  var remoteSource = RD_OPENITI ? '<div class="rd-inapp-source">软件内阅读 · ' + catEsc(RD_OPENITI.source || 'OpenITI/KITAB') + ' · 原文按页缓存，AI 可分析当前页</div>' : '';
  var remoteProgress = RD_OPENITI ? '<div id="rdOpenitiProgress" class="rd-openiti-progress" role="status" aria-live="polite"><div class="rd-openiti-progress__top"><span id="rdOpenitiProgressLabel">正在按需读取阿拉伯原文…</span><span id="rdOpenitiProgressMeta">第 ' + (RD_PAGE + 1) + ' 页</span></div><div class="rd-openiti-progress__track"><i id="rdOpenitiProgressFill" style="width:' + Math.round((Number(RD_OPENITI.progress || 0) || 0) * 100) + '%%"></i></div></div>' : '';
  var title = ((document.getElementById('mReaderTitle') || {}).textContent || '').trim();
  var fs = parseInt(localStorage.getItem('nur_rdfont') || '18', 10);
  var isQuran = !!(RD_AUDIO && RD_AUDIO.kind === 'quran' && RD_QURAN_AYAHS.length);
  body.innerHTML = rdBarHtml() +
    '<div class="rd-paper" onclick="if(!rdShouldSuppressClick())rdToggleChrome()">' +
      head.replace('RD_TITLE', catEsc(title)) +
      (isQuran ? rdQuranControlsHtml() : '') +
      '<div class="rd-page' + (window.RD_ISCN ? ' rd-cn' : '') + (isQuran ? ' rd-quran-page' : '') + (RD_ISLAMIC_GUIDE ? ' rd-guide-page' : '') + '" style="font-size:' + (window.RD_ISCN ? Math.max(18, fs + 1) : fs) + 'px">' + (isQuran ? rdQuranPageMarkup() : (RD_ISLAMIC_GUIDE ? rdGuideMarkup(RD_BOOK_META) : rdWords(RD_PAGES[RD_PAGE]))) + '</div>' +
      '<div class="rd-foot">— ' + (RD_PAGE + 1) + ' —</div>' +
      remoteSource +
      remoteProgress +
    '</div>' +
    rdBarHtml();
  rdBindTouch(body.querySelector('.rd-paper'));
  body.scrollTop = 0;
}
function rdGo(d){
  if(RD_OPENITI){
    var next = RD_PAGE + d;
    if(next >= 0 && (!RD_OPENITI.total || next < RD_OPENITI.total)) rdOpenitiFetch(next, true);
    return;
  }
  if(RD_AUDIO && RD_AUDIO.kind === 'quran') rdQuranStop(); RD_PAGE += d; renderRead();
}
function rdJump(){
  var v = prompt('跳到第几页？（1 - ' + RD_PAGES.length + '）');
  if(!v) return;
  var n = parseInt(v, 10);
  if(isNaN(n)) return;
  RD_PAGE = n - 1; renderRead();
}
function rdWords(text){
  return catEsc(text).replace(/([^\s\u0600-\u06FF]+|[\u0600-\u06FF]+(?:[\u064B-\u0652\u0670\u06D6-\u06ED]*))/g, function(w){
    if(!/[\u0600-\u06FF]/.test(w)) return w;
    return '<span class="rd-w" onclick="rdWord(event,this)">' + w + '</span>';
  });
}
function rdBuildToc(){
  try{
    RD_TOC = [];
    if(RD_PAGES.length > 1){
      RD_PAGES.forEach(function(_, i){
        var head = String(RD_PAGES[i] || '').replace(/[ \\t\\r\\n ]+/g, ' ').slice(0, 18);
        RD_TOC.push({name: '第 ' + (i + 1) + ' 页' + (head ? '　' + head : ''), act: 'rdJumpTo(' + i + ')'});
      });
    }
    RD_TOC_TITLE = '本书目录 · 共 ' + RD_PAGES.length + ' 页';
  }catch(e){ RD_TOC = []; RD_TOC_TITLE = '目录'; }
}
// 微信/QQ 内置浏览器检测：提示用系统浏览器打开
document.addEventListener('DOMContentLoaded', function(){
  try{
    var ua = navigator.userAgent || '';
    if(/MicroMessenger|QQ\\//i.test(ua)){
      var bar = document.createElement('div');
      bar.style.cssText = 'position:fixed;top:0;left:0;right:0;z-index:99999;background:#b3261e;color:#fff;font-size:13px;padding:10px 12px;text-align:center;line-height:1.7;box-shadow:0 2px 10px rgba(0,0,0,.3)';
      bar.innerHTML = '⚠️ 正在微信里打开，部分功能会失效！<br>请点右上角 <b>⋯</b> → 选择「<b>在浏览器打开</b>」';
      document.body.appendChild(bar);
    }
  }catch(e){}
});
// 老浏览器兜底：缺少必要能力时给出提示
window.addEventListener('load', function(){
  try{
    if(!window.__NUR_VER && !/[?&]v=/.test(location.search)){
      location.replace(location.pathname + '?v=' + Date.now());
      return;
    }
  }catch(e){}
  try{ if(!('fetch' in window) || !('Promise' in window)){ document.body.innerHTML = '<div style="padding:40px;text-align:center;font-size:15px;color:#b3261e">你的浏览器版本太旧，请用新版 Safari / Chrome 打开</div>'; } }catch(e){}
});
window.addEventListener('popstate', function(){
  try{ var m = document.querySelector('.modal.show'); if(m){ closeModal(m.id); } }catch(e){}
});
function nurHome(){
  try{
    var ms = document.querySelectorAll('.modal.show');
    for(var i=0;i<ms.length;i++){ ms[i].classList.remove('show','full','zen'); }
    document.body.classList.remove('reading');
    try{ if(window.__rdAudio){ window.__rdAudio.pause(); window.__rdAudio=null; } }catch(e){}
    var fb1=document.getElementById('rdFloatBack'); if(fb1) fb1.style.display='none';
    window.scrollTo(0,0);
  }catch(e){}
}
document.addEventListener('DOMContentLoaded', function(){
  try{
    var h = document.createElement('div');
    h.id = 'nurHomeBtn'; h.textContent = '🏠 首页';
    h.style.cssText = 'display:none;position:fixed;right:12px;bottom:84px;z-index:4500;padding:11px 16px;border-radius:999px;background:rgba(15,61,49,.92);color:#f6e7b4;font-size:14px;font-weight:800;box-shadow:0 6px 18px rgba(0,0,0,.25);cursor:pointer';
    h.onclick = nurHome;
    document.body.appendChild(h);
  }catch(e){}
});
function rdFloatBackGo(){ try{ var m = document.querySelector('.modal.show'); if(m){ closeModal(m.id); } }catch(e){} }
document.addEventListener('DOMContentLoaded', function(){
  try{
    var b = document.createElement('div');
    b.id = 'rdFloatBack'; b.textContent = '‹ 返回';
    b.style.cssText = 'position:fixed;left:12px;bottom:84px;z-index:4000;display:none;padding:11px 18px;border-radius:999px;background:rgba(15,61,49,.92);color:#f6e7b4;font-size:15px;font-weight:800;box-shadow:0 6px 18px rgba(0,0,0,.25);cursor:pointer';
    b.onclick = rdFloatBackGo;
    document.body.appendChild(b);
  }catch(e){}
});
function rdStopAudio(){ try{ if(RD_QAUDIO) rdQuranStop(); if(window.__rdAudio){ window.__rdAudio.pause(); try{ window.__rdAudio.src = ''; }catch(e){} window.__rdAudio = null; } }catch(e){} }
function rdSpeak(btn){
  try{
    if(RD_AUDIO && RD_AUDIO.kind === 'quran'){
      if(window.__rdAudio){ rdStopAudio(); return; }
      var rec = RD_RECITERS[RD_RECITER] || RD_RECITERS[0];
      var _rurl = rec.u + String(RD_AUDIO.sid).padStart(3, '0') + '.mp3';
      var au = new Audio(API_BASE() + '/api/recite?u=' + encodeURIComponent(_rurl));
      window.__rdAudio = au;
      au.onended = function(){ window.__rdAudio = null; };
      au.play();
      return;
    }
    if(window.speechSynthesis.speaking){ window.speechSynthesis.cancel(); return; }
    if(window.__rdAudio){ rdStopAudio(); return; }
    var txt = String(RD_PAGES[RD_PAGE] || '').slice(0, 1200);
    if(!txt) return;
    // iPhone/iPad：必须在"点击手势"里同步创建并 play()，否则异步拿到地址后会被系统拦掉
    var au = new Audio();
    window.__rdAudio = au;
    try{ au.play().catch(function(){}); }catch(e){}
    if(btn){ try{ btn.dataset.old = btn.textContent; btn.textContent = '⏳'; }catch(e){} }
    var done = function(){ if(btn && btn.dataset && btn.dataset.old){ try{ btn.textContent = btn.dataset.old; }catch(e){} } };
    var _cjk = false;
    for(var _i = 0; _i < txt.length && _i < 200; _i++){ var _c = txt.charCodeAt(_i); if(_c >= 0x4E00 && _c <= 0x9FFF){ _cjk = true; break; } }
    var _lang = _cjk ? 'zh' : 'ar';
    fetch(API_BASE() + '/api/tts', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({text: txt, lang: _lang})})
      .then(function(r){ return r.json(); })
      .then(function(d){
        if(d && d.url){
          au.src = API_BASE() + d.url;
          au.onended = function(){ window.__rdAudio = null; done(); };
          au.onerror = function(){ window.__rdAudio = null; done(); rdSpeakLocal(txt); };
          au.play().catch(function(){ rdSpeakLocal(txt); });
          setTimeout(done, 1500);
        } else { window.__rdAudio = null; done(); rdSpeakLocal(txt); }
      })
      .catch(function(){ window.__rdAudio = null; done(); rdSpeakLocal(txt); });
  }catch(e){}
}
function rdSpeakLocal(txt){
  try{
    var u = new SpeechSynthesisUtterance(String(txt || '').slice(0, 4000));
    var vs = window.speechSynthesis.getVoices() || [], ar = null;
    for(var i = 0; i < vs.length; i++){ if((vs[i].lang || '').toLowerCase().indexOf('ar') === 0){ ar = vs[i]; break; } }
    if(ar){ u.voice = ar; u.lang = ar.lang; } else { u.lang = 'ar-SA'; }
    u.rate = 0.9;
    window.speechSynthesis.speak(u);
  }catch(e){}
}
function rdFull(btn){
  var m = document.getElementById('mReader');
  if(!m) return;
  m.classList.toggle('full');
  m.classList.remove('zen');
  renderRead();
}
function rdSetWordContext(w){
  var word=String(w||'').replace(/\s+/g,' ').trim().slice(0,180);
  if(!word)return null;
  var ctx=window.NOUR_AI_CONTEXT||null;
  if(!ctx){
    var titleEl=document.getElementById('mReaderTitle');
    var page=Number(window.RD_PAGE||0), pages=window.RD_PAGES||[], text=String(pages[page]||'').trim();
    if(!text)return null;
    ctx={id:'',title:String(titleEl&&titleEl.textContent||'经典阅读').trim()||'经典阅读',page:page+1,total:pages.length||1,text:text.slice(0,3200),source:'',updatedAt:Date.now()};
  }
  ctx.selected=word; ctx.selection=word; ctx.updatedAt=Date.now();
  window.NOUR_AI_CONTEXT=ctx;
  try{if(typeof window.NOUR_SET_READER_SELECTION==='function')window.NOUR_SET_READER_SELECTION(word);}catch(e){}
  try{if(typeof window.NOUR_SYNC_READER_CONTEXT==='function')window.NOUR_SYNC_READER_CONTEXT();}catch(e){}
  return ctx;
}
function rdSendWordToNourAI(w, close){
  var word=String(w||'').replace(/\s+/g,' ').trim().slice(0,180);
  if(!word)return;
  rdSetWordContext(word);
  var question='请分析选中的阿拉伯语词“'+word+'”：给出词根、词形、词性、基本含义，并结合当前阅读页解释它在本页语境中的作用；请区分确定信息和需要核验的信息。';
  try{if(typeof close==='function')close();}catch(e){}
  if(typeof nav==='function')nav('ai');
  var input=document.getElementById('homeAIIn');
  if(!input)return;
  input.value=question;
  if(typeof homeAIInputState==='function')homeAIInputState(input);
  input.focus();
  if(typeof AI_BUSY!=='undefined'&&AI_BUSY)return;
  if(typeof homeAISend==='function')setTimeout(function(){homeAISend();},80);
}
async function rdWord(ev, el){
  ev.stopPropagation(); var w=(el.textContent||'').trim(); if(!w)return;
  rdSetWordContext(w);
  var old=document.querySelector('#rdWordBox'); if(old){old.remove();document.body.classList.remove('rd-word-open');}
  var box=document.createElement('div'); box.id='rdWordBox'; box.className='rd-wordbox'; box.setAttribute('role','dialog'); box.setAttribute('aria-label','阿拉伯语单词解释'); box.setAttribute('aria-describedby','rdWordStatus');
  box.innerHTML='<div class="rd-wordbox-head"><div class="rd-word-ar" dir="rtl" lang="ar">'+catEsc(w)+'</div><div class="rd-word-actions"><button class="rd-word-audio" type="button" title="使用设备阿语声音朗读" aria-label="朗读阿拉伯语">🔊</button><button class="rd-word-save" type="button" title="收藏生词" aria-label="加入生词本">📌</button><button class="rd-word-close" type="button" title="关闭" aria-label="关闭词卡">✕</button></div></div><div class="rd-wordbox-rule"></div><button class="rd-word-ai" type="button" title="让 NOUR AI 分析词根、词形和当前语境">交给 NOUR AI 分析</button><div id="rdWordStatus" class="rd-word-status" aria-live="polite">正在查询本地词典…</div>';
  document.body.appendChild(box); document.body.classList.add('rd-word-open');
  var close=function(){if(box.parentNode)box.remove();document.body.classList.remove('rd-word-open');};
  box.querySelector('.rd-word-close').onclick=close;
  box.querySelector('.rd-word-ai').onclick=function(){rdSendWordToNourAI(w,close);};
  box.querySelector('.rd-word-audio').onclick=function(){dictSpeak(w,this);};
  box.querySelector('.rd-word-save').onclick=function(){try{wbAdd2(w);this.textContent='✅';this.title='已收藏';}catch(e){}};
  try{
    var r=await fetch(API_BASE()+'/api/dict/lookup?w='+encodeURIComponent(_stripTashkeel(w)),{cache:'no-store'}), d=await r.json();
    var st=box.querySelector('.rd-word-status'); if(st){st.outerHTML='<div id="rdWordStatus" class="rd-word-result" aria-live="polite">'+dictWordHtml(d,w)+dictSourceLabel(d.source)+'</div>';}
    if(!d.found){ try{var fr=await fetch(API_BASE()+'/api/dict/free?w='+encodeURIComponent(_stripTashkeel(w)),{cache:'no-store'}), fd=await fr.json();if(fd&&fd.wiki){var ex=document.createElement('div');ex.className='dict-external';ex.innerHTML='<div class="dict-section-title">公开词典补充</div><div class="dict-external-text" dir="auto">'+catEsc(String(fd.wiki).slice(0,900))+'</div><div class="dict-source">Arabic Wiktionary · <a href="https://ar.wiktionary.org/" target="_blank" rel="noopener">查看原词典</a></div>';box.querySelector('.rd-word-result').appendChild(ex);}}catch(e){} }
  }catch(e){var er=box.querySelector('.rd-word-status');if(er)er.textContent='本地词典暂时不可用，请稍后重试。';}
}
function rdTrans(btn){
  var box = document.querySelector('#rdCnBox');
  if(box){ box.parentNode.removeChild(box); btn.textContent = '中译'; return; }
  var txt = RD_PAGES[RD_PAGE] || '';
  if(!txt) return;
  btn.textContent = '翻译中…';
  fetch(API_BASE() + '/api/chat/message', {method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({message: '把下面这段阿拉伯语翻译成简体中文，只输出译文，不要解释：\\n' + txt.slice(0, 1500), session_id: 'rd', token: webToken()})})
  .then(function(r){ return r.json(); })
  .then(function(d){
    var el = document.createElement('div');
    el.id = 'rdCnBox'; el.className = 'rd-cn';
    el.textContent = (d && d.arabic) ? d.arabic : '（翻译失败）';
    var pg = document.querySelector('.rd-page');
    if(pg && pg.parentNode){ pg.parentNode.insertBefore(el, pg.nextSibling); }
    btn.textContent = '收起';
  })
  .catch(function(){ btn.textContent = '中译'; alert('翻译失败，请稍后再试'); });
}
async function showAllSentences(){
  openModal('mSentences');
  var loading = document.getElementById('mSentBody');
  if(loading) loading.innerHTML = '<div style=\"padding:36px;text-align:center;color:#8a8f88\">正在载入句子库…</div>';
  try{ await window.NOUR_loadDataAsset('sentences'); }catch(e){}
  ALL_SENTENCES = window.BUILTIN_SENTENCES || [];
  renderAllS();
  /* The versioned local asset is the normal full-library path.  Only use the
     legacy API as an explicit recovery path when that asset is unavailable. */
  if(!ALL_SENTENCES.length){
    try{
      var r = await fetch(API_BASE() + '/api/sentences', {cache:'no-store'});
      var d = await r.json();
      var list = [];
      Object.keys(d.cats || {}).forEach(function(k){
        (d.cats[k] || []).forEach(function(s){ list.push({a:s.a||s.ar||'', e:s.e||s.en||'', c:s.c||s.cn||'', cat:k}); });
      });
      if(list.length){ ALL_SENTENCES = list; renderAllS(); }
    }catch(e){}
  }
}
function renderAllS(){
  var q = (document.getElementById('mSentSearch').value||'').trim().toLowerCase();
  var list = q ? ALL_SENTENCES.filter(function(s){return s.a.includes(q)||s.e.toLowerCase().includes(q)||s.c.includes(q);}) : ALL_SENTENCES;
  var body = document.getElementById('mSentBody');
  body.innerHTML = '';
  list.forEach(function(s){
    var d = document.createElement('div');
    d.className = 's-item';
    var sa = s.a.replace(/&/g,'&amp;').replace(/'/g,'&#39;').replace(/"/g,'&quot;');
    var se = s.e.replace(/&/g,'&amp;').replace(/'/g,'&#39;').replace(/"/g,'&quot;');
    d.innerHTML = '<div class="s-ar">'+sa+'</div><div class="s-tr">🇬🇧 '+se+'<br>🇨🇳 '+s.c+'</div>'+
      '<div style="display:flex;gap:6px;margin-top:6px;justify-content:flex-end">'+
'<button class="s-btn" onclick="ap(this,0,&#39;'+sa+'&#39;)">🔊</button>'+
      '<button class="s-btn" onclick="ap(this,1,&#39;'+se+'&#39;)">🇬🇧</button>'+
      '</div>';
    body.appendChild(d);
  });
  document.getElementById('mSentCount').textContent = '共 ' + list.length + ' 句';
}
async function showVocab(){
  openModal('mVocab');
  try{ await window.NOUR_loadDataAsset('vocab'); }catch(e){}
  ALL_VOCAB = BUILTIN_VOCAB;
  renderVocab();
  try{
    var r = await fetch(API_BASE() + '/api/vocab');
    var d = await r.json();
    if(d.words && d.words.length){ ALL_VOCAB = d.words; renderVocab(); }
  }catch(e){}
}
function renderVocab(){
  var q = (document.getElementById('mVocabSearch').value||'').trim().toLowerCase();
  var list = q ? ALL_VOCAB.filter(function(v){return v.w.includes(q);}) : ALL_VOCAB;
  var body = document.getElementById('mVocabBody');
  body.innerHTML = '';
  list.slice(0, 500).forEach(function(v){
    var d = document.createElement('div');
    d.className = 'v-item';
    var vw = v.w.replace(/&/g,'&amp;').replace(/'/g,'&#39;').replace(/"/g,'&quot;');
    var m = BUILTIN_VOCAB_MEANINGS || [];
    var mm = null;
    for(var i=0;i<m.length;i++){ if(m[i].w === v.w){ mm = m[i]; break; } }
    var mean = mm ? ('<span class="v-m">'+mm.cn+' · '+mm.en+'</span>') : ('<span class="v-f">出现 '+v.f+' 次</span>');
    d.innerHTML = '<span class="v-ar">'+vw+'</span>'+ mean +
      '<button class="s-btn" style="width:auto;height:26px;font-size:10px" onclick="wbAdd2(&#39;'+vw+'&#39;)">📌 收词</button>' +
      '<button class="s-btn" style="width:26px;height:26px" onclick="ap(this,0,&#39;'+vw+'&#39;)">🔊</button>';
    body.appendChild(d);
  });
  document.getElementById('mVocabCount').textContent = '共 ' + ALL_VOCAB.length + ' 词（显示前500）';
  renderVocabState();
}
async function showLibrary(){
  openModal('mLibrary');
  var arts = BUILTIN_ARTICLES;
  ALL_ARTICLES = arts;
  renderLibrary(arts);
  try{
    var r = await fetch(API_BASE() + '/api/articles');
    var d = await r.json();
    var arts2 = d.articles || [];
    if(arts2.length){ ALL_ARTICLES = arts2; renderLibrary(arts2); }
  }catch(e){}
}




// ===== 📝 测验模式 =====
var quizQ = [];
var quizIdx = 0;
var quizScore = 0;
var quizWrong = [];
function showQuiz(){
  openModal('mQuiz');
  quizQ = buildQuiz();
  quizIdx = 0; quizScore = 0; quizWrong = [];
  renderQuiz();
}
function buildQuiz(){
  var all = (BUILTIN_SENTENCES || []).filter(function(s){ return s.a && s.c && s.e; });
  for(var i = all.length - 1; i > 0; i--){
    var j = Math.floor(Math.random() * (i + 1));
    var t = all[i]; all[i] = all[j]; all[j] = t;
  }
  var qs = [];
  var N = Math.min(10, all.length);
  for(var k = 0; k < N; k++){
    var correct = all[k];
    var opts = [correct];
    while(opts.length < 4){
      var r = all[Math.floor(Math.random() * all.length)];
      if(opts.indexOf(r) < 0) opts.push(r);
    }
    for(var x = opts.length - 1; x > 0; x--){
      var y = Math.floor(Math.random() * (x + 1));
      var t2 = opts[x]; opts[x] = opts[y]; opts[y] = t2;
    }
    qs.push({q: correct, opts: opts});
  }
  return qs;
}
function renderQuiz(){
  var body = document.getElementById('mQuizBody');
  if(quizIdx >= quizQ.length){
    body.innerHTML = '<div style="text-align:center;padding:40px 20px">'+
      '<div style="font-size:46px">📝</div>'+
      '<div style="font-size:18px;font-weight:800;color:#0f3d31;margin-top:10px">测验完成！</div>'+
      '<div style="font-size:15px;color:#1a8a5c;margin-top:12px">得分：<b style="font-size:22px">'+quizScore+'</b> / '+quizQ.length+'</div>'+
      '<div style="font-size:10px;color:#999;margin-top:6px">错题已自动加入间隔复习（闪卡→间隔复习）</div>'+
      (quizWrong.length ? '<div style="font-size:11px;color:#999;margin-top:6px">错题 '+quizWrong.length+' 道</div>' : '')+
      '<div style="display:flex;gap:8px;justify-content:center;margin-top:20px">'+
      '<button class="act-btn" onclick="showQuiz()">▶ 再来一局</button>'+
      '</div></div>';
    document.getElementById('mQuizHead').textContent = '📝 测验';
    return;
  }
  var item = quizQ[quizIdx];
  document.getElementById('mQuizHead').textContent = '📝 测验 · ' + (quizIdx + 1) + ' / ' + quizQ.length + ' · 得分 ' + quizScore;
  var html = '<div style="background:linear-gradient(150deg,#14503e,#0e3529);border-radius:16px;padding:22px;text-align:center;margin-bottom:14px">'+
    '<div class="quran-ayah" style="color:#e8d48b;font-weight:700;text-align:center">' + item.q.a + '</div>'+
    '<button class="s-btn" style="width:auto;padding:4px 12px;margin-top:10px" onclick="ap(this,0,&#39;' + item.q.a.replace(/'/g, '') + '&#39;)">🔊 听题</button>'+
    '</div>'+
    '<div style="font-size:10.5px;color:#999;text-align:center;margin-bottom:12px">请选择正确的中文翻译</div>';
  item.opts.forEach(function(o, i){
    html += '<button class="quiz-opt" id="qo'+i+'" onclick="quizAnswer('+i+',&#39;' + String(o.c).replace(/&#39;/g,'').replace(/'/g,'&#39;').replace(/"/g,'&quot;') + '&#39;)">' + o.c + '</button>';
  });
  body.innerHTML = html;
}
function quizAnswer(i, cn){
  var item = quizQ[quizIdx];
  var btns = document.querySelectorAll('.quiz-opt');
  if(item.q.c === cn){
    quizScore++;
    btns[i].style.background = '#1a8a5c';
    btns[i].style.color = '#fff';
  } else {
    btns[i].style.background = '#c0392b';
    btns[i].style.color = '#fff';
    quizWrong.push(item.q);
    srsAdd('s', item.q.a); // 错题自动进遗忘曲线复习
    for(var x = 0; x < btns.length; x++){
      if(item.opts[x].c === item.q.c){ btns[x].style.background = '#1a8a5c'; btns[x].style.color = '#fff'; }
    }
  }
  setTimeout(function(){ quizIdx++; renderQuiz(); }, 900);
}

// ===== 🃏 闪卡 + 📅 间隔复习（SRS 遗忘曲线） =====
var flashDeck = null; // null = 模式选择
var flashMode = 'sentence';
var flashIdx = 0;
var flashFlipped = false;
var flashKnown = 0;
var flashAgain = [];
var flashDone = false;

// --- SRS 引擎（localStorage）---
var SRS_KEY = 'nur_srs_v1';
var SRS_BOXES = [0, 1, 3, 7, 15, 30];
function srsLoad(){ try{ return JSON.parse(localStorage.getItem(SRS_KEY) || '{}'); }catch(e){ return {}; } }
function srsSave(m){ try{ localStorage.setItem(SRS_KEY, JSON.stringify(m)); }catch(e){} }
function srsToday(){ var d = new Date(); return d.getFullYear() + '-' + String(d.getMonth()+1).padStart(2,'0') + '-' + String(d.getDate()).padStart(2,'0'); }
function srsAddDays(n){ var d = new Date(); d.setDate(d.getDate() + n); return d.getFullYear() + '-' + String(d.getMonth()+1).padStart(2,'0') + '-' + String(d.getDate()).padStart(2,'0'); }
function srsKey(kind, text){ return kind + ':' + String(text || '').replace(/\s+/g, ' ').trim(); }
function srsAdd(kind, text){
  var k = srsKey(kind, text), m = srsLoad();
  if(!m[k]){ m[k] = { box: 1, due: srsAddDays(1), reps: 0, lapses: 0 }; srsSave(m); }
}
function srsAnswer(kind, text, ok){
  var k = srsKey(kind, text), m = srsLoad();
  var r = m[k] || { box: 0, reps: 0, lapses: 0 };
  r.reps = (r.reps || 0) + 1;
  if(ok){ r.box = Math.min(5, (r.box || 0) + 1); }
  else { r.lapses = (r.lapses || 0) + 1; r.box = Math.max(0, (r.box || 0) - 1); }
  r.due = srsAddDays(SRS_BOXES[r.box]);
  m[k] = r; srsSave(m);
}
function srsDue(){
  var m = srsLoad(), t = srsToday(), out = [];
  for(var k in m){ if(m[k].due <= t) out.push(k); }
  return out;
}
function srsDueCount(){ return srsDue().length; }

function shuffleArr(arr){
  var a = arr.slice();
  for(var i = a.length - 1; i > 0; i--){
    var j = Math.floor(Math.random() * (i + 1));
    var t = a[i]; a[i] = a[j]; a[j] = t;
  }
  return a;
}
function meanOf(w){
  var m = BUILTIN_VOCAB_MEANINGS || [];
  for(var i = 0; i < m.length; i++){ if(m[i].w === w) return m[i]; }
  return { w: w, cn: '', en: '' };
}
function buildFlashDeck(m){
  if(m === 'word'){
    var vocab = shuffleArr((BUILTIN_VOCAB || []).slice(0, 300)).slice(0, 12);
    return vocab.map(function(v){ var mm = meanOf(v.w); return { kind:'w', word:v.w, cn:mm.cn, en:mm.en }; });
  }
  var all = shuffleArr((BUILTIN_SENTENCES || []).filter(function(s){ return s.a && s.c; })).slice(0, 12);
  return all.map(function(s){ return { kind:'s', card:s }; });
}
function buildReviewDeck(){
  var sMap = {};
  (BUILTIN_SENTENCES || []).forEach(function(s){ if(s.a) sMap[srsKey('s', s.a)] = s; });
  var cards = [];
  srsDue().forEach(function(k){
    if(k.indexOf('s:') === 0){ var s = sMap[k]; if(s) cards.push({ kind:'s', card:s }); }
    else if(k.indexOf('w:') === 0){ var w = k.slice(2); var mm = meanOf(w); if(mm.w) cards.push({ kind:'w', word:w, cn:mm.cn, en:mm.en }); }
  });
  return shuffleArr(cards);
}
function showFlashcard(){
  openModal('mFlash');
  flashDeck = null;
  flashDone = false;
  renderFlash();
}
async function startFlash(m){
  flashMode = m;
  if(m === 'sentence' || m === 'review'){ try{ await window.NOUR_loadDataAsset('sentences'); }catch(e){} }
  if(m === 'word'){ try{ await window.NOUR_loadDataAsset('vocab'); }catch(e){} }
  flashIdx = 0; flashFlipped = false; flashKnown = 0; flashAgain = []; flashDone = false;
  if(m === 'review'){
    flashDeck = buildReviewDeck();
    if(!flashDeck.length){
      alert('🎉 今天的复习已完成！闪卡答题时点「不会」的会自动进入复习队列（1/3/7/15/30 天）。');
      flashDeck = null;
      renderFlash();
      return;
    }
  } else {
    flashDeck = buildFlashDeck(m);
  }
  renderFlash();
}
function renderFlash(){
  var body = document.getElementById('mFlashBody');
  var head = document.getElementById('mFlashHead');
  if(flashDeck === null){
    var due = srsDueCount();
    head.textContent = '🃏 闪卡 · 选择模式';
    body.innerHTML = '<div style="display:flex;flex-direction:column;gap:10px;padding:6px">'+
      '<div style="font-size:13px;font-weight:800;color:#0f3d31;text-align:center;margin-bottom:2px">选择卡片模式</div>'+
      '<button class="act-btn" style="background:#0f3d31;color:#e8d48b;border:2px solid #c9a84c;padding:14px" onclick="startFlash(&#39;review&#39;)">📅 间隔复习' + (due ? ' · ' + due + ' 张到期' : ' · 今日已完成') + '</button>'+
      '<button class="act-btn" style="padding:12px" onclick="startFlash(&#39;sentence&#39;)">📖 句子闪卡 · 12 张随机</button>'+
      '<button class="act-btn" style="padding:12px" onclick="startFlash(&#39;word&#39;)">🔤 单词闪卡 · 高频词</button>'+
      '<div style="font-size:10px;color:#999;text-align:center;margin-top:4px;line-height:1.6">会/不会 自动记录掌握情况，不会的按 1/3/7/15/30 天遗忘曲线提醒复习</div>'+
      '</div>';
    return;
  }
  if(flashDone){
    head.textContent = '🎉 本局完成';
    body.innerHTML = '<div style="text-align:center;padding:40px 20px">'+
      '<div style="font-size:46px">🎉</div>'+
      '<div style="font-size:18px;font-weight:800;color:#0f3d31;margin-top:10px">本局完成！</div>'+
      '<div style="font-size:14px;color:#555;margin-top:12px">认识 <b style="color:#1a8a5c">'+flashKnown+'</b> / '+flashDeck.length+' 张</div>'+
      '<div style="font-size:12px;color:#999;margin-top:4px">待复习 '+flashAgain.length+' 张 · 已按遗忘曲线排期</div>'+
      '<div style="display:flex;gap:8px;justify-content:center;margin-top:20px">'+
      (flashAgain.length ? '<button class="act-btn" onclick="flashReview()">🔄 重来 '+flashAgain.length+' 张</button>' : '')+
      '<button class="act-btn" onclick="showFlashcard()">▶ 再来一局</button>'+
      '</div></div>';
    return;
  }
  var item = flashDeck[flashIdx];
  head.textContent = '🃏 ' + (flashMode === 'review' ? '复习' : '闪卡') + ' · ' + (flashIdx + 1) + ' / ' + flashDeck.length + ' · 已认识 ' + flashKnown;
  var front = item.kind === 's' ? item.card.a : item.word;
  var backCn = item.kind === 's' ? item.card.c : (item.cn || '—');
  var backEn = item.kind === 's' ? item.card.e : (item.en || '');
  body.innerHTML = '<div id="flashCard" class="flash-card" onclick="flashFlip()">' +
    (flashFlipped
      ? '<div class="flash-back"><div class="flash-cn">🇨🇳 ' + esc(backCn) + '</div>' +
        (backEn ? '<div class="flash-en">🇬🇧 ' + esc(backEn) + '</div>' : '') +
        '<div style="display:flex;gap:8px;margin-top:12px;justify-content:center;flex-wrap:wrap">' +
        '<button class="s-btn" style="width:auto;padding:4px 12px" onclick="speakFlashBack(&#39;zh-CN&#39;)">🔊 中文</button>' +
        (backEn ? '<button class="s-btn" style="width:auto;padding:4px 12px" onclick="speakFlashBack(&#39;en-US&#39;)">🔊 英文</button>' : '') +
        (item.kind === 'w' ? '<button class="s-btn" style="width:auto;padding:4px 12px" onclick="wbAdd2(&#39;' + item.word.replace(/'/g,'') + '&#39;)">📌 收词</button>' : '') +
        '</div>' +
        '<div class="flash-hint">👆 点击翻回</div></div>'
      : '<div class="flash-front"><div class="flash-ar">' + front + '</div>' +
        '<div class="flash-hint">👆 点击翻面</div></div>') +
    '</div>' +
    '<div style="display:flex;gap:10px;margin-top:14px">' +
    '<button class="act-btn" style="flex:1;background:#c0392b" onclick="flashAnswer(false)">❌ 不会</button>' +
    '<button class="act-btn" style="flex:1;background:#1a8a5c" onclick="flashAnswer(true)">✅ 认识</button>' +
    '</div>';
}
function flashFlip(){ flashFlipped = !flashFlipped; renderFlash(); }
function flashAnswer(ok){
  var item = flashDeck[flashIdx];
  if(item){
    if(item.kind === 's'){ srsAdd('s', item.card.a); srsAnswer('s', item.card.a, ok); }
    else { srsAdd('w', item.word); srsAnswer('w', item.word, ok); }
  }
  if(ok) flashKnown++;
  else flashAgain.push(item);
  flashFlipped = false;
  flashIdx++;
  if(flashIdx >= flashDeck.length){ flashDone = true; }
  renderFlash();
}
function flashReview(){
  flashDeck = flashAgain.slice();
  flashIdx = 0; flashFlipped = false; flashKnown = 0; flashAgain = []; flashDone = false;
  renderFlash();
}

function speakFlashBack(lang){
  if(!window.speechSynthesis) return;
  var item = flashDeck[flashIdx];
  if(!item) return;
  var txt = lang === 'zh-CN' ? (item.kind === 's' ? item.card.c : (item.cn || '')) : (item.kind === 's' ? item.card.e : (item.en || ''));
  if(!txt) return;
  window.speechSynthesis.cancel();
  var u = new SpeechSynthesisUtterance(txt);
  u.lang = lang; u.rate = 0.85;
  window.speechSynthesis.speak(u);
}

// ===== 📕 生词本 =====
var WB_KEY = 'nur_wordbook_v1';
function wbLoad(){ try{ return JSON.parse(localStorage.getItem(WB_KEY) || '[]'); }catch(e){ return []; } }
function wbSave(l){ try{ localStorage.setItem(WB_KEY, JSON.stringify(l)); }catch(e){} }
function wbHas(w){ return wbLoad().indexOf(w) >= 0; }
function wbAdd(w){ var l = wbLoad(); if(l.indexOf(w) < 0){ l.unshift(w); wbSave(l); } srsAdd('w', w); updateStats(); }
function wbRemove(w){ var l = wbLoad(); var i = l.indexOf(w); if(i >= 0){ l.splice(i, 1); wbSave(l); } updateStats(); }
function detachModal(id){ var el = document.getElementById(id); if(el && el.parentNode !== document.body) document.body.appendChild(el); return el; }
function showWordBook(){
  detachModal('mWordBook');
  openModal('mWordBook');
  renderWordBook();
}
function renderWordBook(){
  var body = document.getElementById('mWordBookBody');
  if(!body) return;
  var q = ((document.getElementById('mWbSearch') || {}).value || '').trim();
  var list = wbLoad();
  if(q) list = list.filter(function(w){ return w.indexOf(q) >= 0; });
  body.innerHTML = '';
  list.slice(0, 300).forEach(function(w){
    var mm = meanOf(w);
    var d = document.createElement('div');
    d.className = 'v-item';
    var mHtml = mm.cn ? ('<span class="v-m">' + esc(mm.cn + (mm.en ? ' · ' + mm.en : '')) + '</span>') : '<span class="v-f">生词</span>';
    d.innerHTML = '<span class="v-ar">' + esc(w) + '</span>' + mHtml +
      '<button class="s-btn" style="width:26px;height:26px" onclick="ap(this,0,&#39;' + w.replace(/'/g,'&#39;') + '&#39;)">🔊</button>' +
      '<button class="s-btn" style="width:26px;height:26px;background:rgba(192,57,43,.12)" onclick="wbDel(&#39;' + w.replace(/'/g,'&#39;') + '&#39;)">🗑</button>';
    body.appendChild(d);
  });
  var c = document.getElementById('mWordBookCount');
  if(c) c.textContent = '共 ' + wbLoad().length + ' 词' + (q ? '（筛选）' : '');
  if(!list.length){
    body.innerHTML = '<div style="text-align:center;padding:50px 20px;color:#999;font-size:12px;line-height:2">📭 生词本还是空的<br>在词汇表点「📌 收词」，生词自动出现在这里</div>';
  }
}
function wbDel(w){ wbRemove(w); renderWordBook(); }
function wbAdd2(w){
  wbAdd(w);
  renderWordBook();
  try{ renderVocabState(); }catch(e){}
}
function renderVocabState(){
  var wb = wbLoad();
  document.querySelectorAll('#mVocabBody .v-item').forEach(function(it){
    var ar = (it.querySelector('.v-ar') || {}).textContent || '';
    var btns = it.querySelectorAll('button');
    if(btns.length >= 2 && wb.indexOf(ar) >= 0){
      btns[0].textContent = '✅ 已收';
      btns[0].style.background = 'rgba(26,138,92,.2)';
    }
  });
}

// ===== 🔤 字母入门 =====
var ALPH_SEL = null;
var ALPH_QUIZ = [];
var ALPH_QIDX = 0;
var ALPH_QSCORE = 0;
var ALPH_LAST = null;
function showAlphabet(){
  openModal('mAlphabet');
  ALPH_SEL = null;
  ALPH_LAST = null;
  renderAlphabet();
}
function openAlph(ar){
  (BUILTIN_ALPHABET || []).forEach(function(a){ if(a.ar === ar) ALPH_SEL = a; });
  renderAlphabet();
}
function startAlphQuiz(){
  var pool = shuffleArr(BUILTIN_ALPHABET || []);
  ALPH_QUIZ = [];
  for(var k = 0; k < 10; k++){
    var correct = pool[k];
    var opts = [correct];
    while(opts.length < 4){
      var r = (BUILTIN_ALPHABET || [])[Math.floor(Math.random() * 28)];
      if(opts.indexOf(r) < 0) opts.push(r);
    }
    ALPH_QUIZ.push({ letter: correct, opts: shuffleArr(opts) });
  }
  ALPH_QIDX = 0; ALPH_QSCORE = 0;
  ALPH_SEL = 'quiz';
  renderAlphabet();
}
function alphAnswer(btn, oar){
  var q = ALPH_QUIZ[ALPH_QIDX];
  var btns = document.querySelectorAll('#mAlphabetBody .quiz-opt');
  var ok = (oar === q.letter.ar);
  if(ok) ALPH_QSCORE++;
  for(var i = 0; i < btns.length; i++){
    if(btns[i].getAttribute('data-ar') === q.letter.ar){ btns[i].style.background = '#1a8a5c'; btns[i].style.color = '#fff'; }
  }
  if(!ok){ btn.style.background = '#c0392b'; btn.style.color = '#fff'; }
  setTimeout(function(){ ALPH_QIDX++; renderAlphabet(); }, 800);
}
function renderAlphabet(){
  var body = document.getElementById('mAlphabetBody');
  var head = document.getElementById('mAlphabetHead');
  if(!body) return;
  if(ALPH_SEL === null){
    head.textContent = '🔤 字母入门 · 28 字母';
    body.innerHTML = '<div style="display:grid;grid-template-columns:repeat(7,1fr);gap:6px;padding:6px">' +
      (BUILTIN_ALPHABET || []).map(function(a){
        return '<div style="background:#fff;border:1px solid rgba(201,168,76,.3);border-radius:10px;padding:8px 2px;text-align:center;cursor:pointer" onclick="openAlph(&#39;' + a.ar + '&#39;)">' +
          '<div style="font-size:20px;font-weight:800;color:#0f3d31">' + a.ar + '</div>' +
          '<div style="font-size:8px;color:#999;margin-top:2px">' + a.cn + '</div></div>';
      }).join('') + '</div>' +
      '<button class="act-btn" style="margin:12px auto;display:block" onclick="startAlphQuiz()">📝 认读测验</button>';
    return;
  }
  if(ALPH_SEL === 'quiz'){
    var q = ALPH_QUIZ[ALPH_QIDX];
    if(!q){
      head.textContent = '📝 测验完成';
      body.innerHTML = '<div style="text-align:center;padding:40px 20px">' +
        '<div style="font-size:46px">🎉</div>' +
        '<div style="font-size:18px;font-weight:800;color:#0f3d31;margin-top:10px">测验完成！</div>' +
        '<div style="font-size:15px;color:#1a8a5c;margin-top:12px">答对 <b style="font-size:22px">' + ALPH_QSCORE + '</b> / 10</div>' +
        '<div style="display:flex;gap:8px;justify-content:center;margin-top:20px">' +
        '<button class="act-btn" onclick="startAlphQuiz()">▶ 再来一次</button>' +
        '<button class="act-btn" onclick="showAlphabet()">← 字母表</button></div></div>';
      return;
    }
    head.textContent = '📝 认读测验 · ' + (ALPH_QIDX + 1) + ' / 10 · 得分 ' + ALPH_QSCORE;
    body.innerHTML = '<div style="background:linear-gradient(150deg,#14503e,#0e3529);border-radius:16px;padding:24px;text-align:center;margin-bottom:12px">' +
      '<div style="font-size:56px;font-weight:800;color:#e8d48b">' + q.letter.ar + '</div>' +
      '<div style="font-size:10px;color:rgba(255,255,255,.7);margin-top:6px">这个字母怎么读？</div>' +
      '<button class="s-btn" style="width:auto;padding:4px 12px;margin-top:8px" onclick="ap(this,0,&#39;' + q.letter.ar + '&#39;)">🔊 听发音</button></div>' +
      q.opts.map(function(o){
        return '<button class="quiz-opt" data-ar="' + o.ar + '" onclick="alphAnswer(this,&#39;' + o.ar + '&#39;)">' + o.name + ' · ' + o.cn + '</button>';
      }).join('');
    return;
  }
  var a = ALPH_SEL;
  head.textContent = '🔤 ' + a.ar + ' · ' + a.name;
  body.innerHTML = '<button class="s-btn" style="width:auto;padding:4px 10px" onclick="showAlphabet()">← 全部字母</button>' +
    '<div style="text-align:center;padding:8px 0 4px">' +
    '<div style="font-size:64px;font-weight:800;color:#0f3d31">' + a.ar + '</div>' +
    '<div style="font-size:13px;color:#555;margin-top:4px">' + a.name + ' · ' + a.cn + ' · ' + a.tr + '</div>' +
    '<button class="s-btn" style="width:auto;padding:5px 14px;margin-top:8px" onclick="ap(this,0,&#39;' + a.name + '&#39;)">🔊 读字母名</button></div>' +
    '<div style="font-size:12px;font-weight:800;color:#0f3d31;margin:14px 4px 8px">✍️ 四种书写形式</div>' +
    '<div style="display:flex;gap:8px">' + a.forms.map(function(f, i){
      return '<div style="flex:1;background:#fff;border:1px solid rgba(201,168,76,.3);border-radius:10px;padding:12px 4px;text-align:center">' +
        '<div style="font-size:26px;font-weight:800;color:#0f3d31">' + f + '</div>' +
        '<div style="font-size:9px;color:#999;margin-top:3px">' + ['独立','词首','词中','词尾'][i] + '</div></div>';
    }).join('') + '</div>' +
    '<div style="font-size:12px;font-weight:800;color:#0f3d31;margin:14px 4px 8px">📖 示例词</div>' +
    a.ex.map(function(e){
      return '<div style="background:#fff;border:1px solid rgba(201,168,76,.2);border-radius:10px;padding:10px 12px;display:flex;align-items:center;margin-bottom:6px;cursor:pointer" onclick="ap(this,0,&#39;' + e.w + '&#39;)">' +
        '<span style="font-size:18px;font-weight:700;color:#0f3d31;flex:1;text-align:right;direction:rtl">' + e.w + '</span>' +
        '<span style="font-size:11px;color:#555;margin-right:10px">' + e.cn + '</span><span>🔊</span></div>';
    }).join('') +
    '<div style="font-size:9.5px;color:#999;margin:12px 4px;line-height:1.6">提示：大多数字母必须与前后连写；ا د ذ ر ز و 只与前面的字母连写。</div>';
}

// ===== 🎧 听力跟读评测（本地 Whisper 识别 · 离线可用） =====
var LISTEN_LIST = [];
var LISTEN_IDX = 0;
var LISTEN_REC = null;    // MediaRecorder
var LISTEN_CHUNKS = [];
var LISTEN_ITEM = null;
function normArWeb(t){
  return String(t || '').replace(/[\u064B-\u0652\u0670\u0640\u06D6-\u06ED\u0610-\u061A]/g, '').replace(/[^\u0600-\u06FF\s]/g, ' ').replace(/\s+/g, ' ').trim();
}
function arWordsWeb(t){ var s = normArWeb(t); return s ? s.split(' ') : []; }
function gradeByHearingWeb(target, heard){
  var t = arWordsWeb(target), h = arWordsWeb(heard);
  if(!t.length) return 0;
  var hSet = {}; h.forEach(function(w){ hSet[w] = 1; });
  var matched = 0;
  t.forEach(function(w){ if(hSet[w]) matched++; });
  var overlap = matched / t.length;
  var precision = h.length ? matched / h.length : 0;
  return Math.round((overlap * 0.7 + precision * 0.3) * 100);
}
async function showListen(){
  detachModal('mListen');
  openModal('mListen');
  var waiting = document.getElementById('mListenBody');
  if(waiting) waiting.innerHTML = '<div style=\"padding:36px;text-align:center;color:#8a8f88\">正在载入跟读素材…</div>';
  try{ await window.NOUR_loadDataAsset('sentences'); }catch(e){}
  LISTEN_LIST = shuffleArr((window.BUILTIN_SENTENCES || []).filter(function(s){ return (s.ar || s.a) && (s.cn || s.c); })).slice(0, 10);
  LISTEN_IDX = 0;
  renderListen();
}
function renderListen(){
  var body = document.getElementById('mListenBody');
  var head = document.getElementById('mListenHead');
  if(!body) return;
  if(!LISTEN_LIST.length){ body.innerHTML = '<div style="text-align:center;padding:40px;color:#999">暂无句子</div>'; return; }
  var item = LISTEN_LIST[LISTEN_IDX];
  head.textContent = '🎧 跟读评测 · ' + (LISTEN_IDX + 1) + ' / ' + LISTEN_LIST.length;
  body.innerHTML = '<div style="background:linear-gradient(150deg,#14503e,#0e3529);border-radius:16px;padding:20px;text-align:center;margin-bottom:12px">' +
    '<div class="quran-ayah" style="color:#e8d48b;font-weight:700;line-height:1.8">' + item.a + '</div>' +
    '<div style="font-size:11px;color:rgba(255,255,255,.75);margin-top:8px">🇨🇳 ' + esc(item.c) + '</div>' +
    (item.e ? '<div style="font-size:10px;color:rgba(232,212,139,.7);margin-top:4px">🇬🇧 ' + esc(item.e) + '</div>' : '') +
    '</div>' +
    '<div style="display:flex;gap:8px;justify-content:center;margin-bottom:12px;flex-wrap:wrap">' +
    '<button class="act-btn" onclick="speakListen()">🔊 听原声</button>' +
    '<button class="act-btn" id="listenGradeBtn" style="background:#1a8a5c" onclick="startListenGrade()">🎯 跟读评测</button>' +
    '<button class="act-btn" onclick="nextListen(-1)">‹ 上一句</button>' +
    '<div id="listenGradeRes" style="text-align:center;font-size:13px;color:#0f3d31;min-height:20px"></div>' +
    '<div style="font-size:9.5px;color:#999;text-align:center;margin-top:10px;line-height:1.6">点「跟读评测」→ 朗读这句阿语 → 再点一次停止，本地语音识别比对打分（需服务器运行 bash run.sh）</div>';
}
function speakListen(){
  var item = LISTEN_LIST[LISTEN_IDX];
  if(!item || !window.speechSynthesis) return;
  window.speechSynthesis.cancel();
  var u = new SpeechSynthesisUtterance(item.a);
  u.lang = 'ar-SA'; u.rate = 0.7;
  window.speechSynthesis.speak(u);
}
function nextListen(d){
  LISTEN_IDX = Math.min(LISTEN_LIST.length - 1, Math.max(0, LISTEN_IDX + d));
  renderListen();
}
function startListenGrade(){
  var btn = document.getElementById('listenGradeBtn');
  if(!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia || !window.MediaRecorder){
    alert('当前环境不支持录音，请使用 Chrome/Edge 或桌面 App');
    return;
  }
  if(LISTEN_REC && LISTEN_REC.state === 'recording'){
    LISTEN_REC.stop();
    return;
  }
  LISTEN_CHUNKS = [];
  try{
    navigator.mediaDevices.getUserMedia({audio:true}).then(function(stream){
      var mr = new MediaRecorder(stream);
      mr.ondataavailable = function(e){ if(e.data && e.data.size) LISTEN_CHUNKS.push(e.data); };
      mr.onstop = function(){
        stream.getTracks().forEach(function(t){ t.stop(); });
        gradeListenUpload();
      };
      mr.start(250);
      LISTEN_REC = mr;
      if(btn){ btn.textContent = '⏹ 停止并评分'; }
      var res = document.getElementById('listenGradeRes');
      if(res) res.innerHTML = '<span style="color:#1a8a5c">🎤 正在听你说…（读完再点一次）</span>';
    }).catch(function(){
      alert('麦克风权限被拒绝');
    });
  }catch(e){
    alert('无法启动录音：' + e);
  }
}
function gradeListenUpload(){
  var btn = document.getElementById('listenGradeBtn');
  if(btn) btn.textContent = '🎯 跟读评测';
  var item = LISTEN_LIST[LISTEN_IDX];
  var res = document.getElementById('listenGradeRes');
  if(!item || !res) return;
  var blob = new Blob(LISTEN_CHUNKS, {type: 'audio/webm'});
  LISTEN_CHUNKS = [];
  if(blob.size < 2000){ res.innerHTML = '<span style="color:#c0392b">没有录到声音，请重试</span>'; return; }
  res.innerHTML = '<span style="color:#1a8a5c">⏳ 识别评分中…</span>';
  fetch(API_BASE() + '/api/asr', {method:'POST', headers:{'Content-Type':'application/octet-stream', 'X-ASR-Lang':'ar'}, body: blob})
    .then(function(r){ return r.json(); })
    .then(function(d){
      var heard = (d.text || '').trim();
      if(!heard){ res.innerHTML = '<span style="color:#c0392b">没有听清，请再试一次</span>'; return; }
      var score = gradeByHearingWeb(item.a, heard);
      var good = score >= 80;
      res.innerHTML = 'AI评测 <b style="color:' + (good ? '#1a8a5c' : '#c9a84c') + ';font-size:18px">' + score + '</b> 分<br>' +
        '<span style="font-size:10px;color:#999">听到：' + esc(heard) + '</span>';
    })
    .catch(function(){
      res.innerHTML = '<span style="color:#c0392b">识别失败：需要本地服务器（bash run.sh）</span>';
    });
}

// ===== 📜 哲言库（世界典籍 · 阿语 + 中文 + 注释） =====
var HAD_BOOK = 'bukhari';
var HAD_TAG = '';
var HAD_Q = '';
var HAD_CUR = null;
var HAD_BOOKS = [
  ['bukhari', '📕 哲言集 · 布哈里'], ['muslim', '📗 哲言集 · 穆斯利姆'], ['tirmidhi', '📘 哲言集 · 提尔米济'],
    ['abudawud', '📙 哲言集 · 阿布达吾德'], ['nasai', '📔 哲言集 · 奈萨伊'], ['ibnmajah', '📓 哲言集 · 伊本马哲'],
    ['malik', '📒 哲言集 · 马立克'], ['nawawi', '📃 哲言集 · 纳瓦维'],
  ['abudawud', '📙 艾布·达伍德'], ['nasai', '📓 奈萨仪'], ['ibnmajah', '📔 伊本马哲'],
  ['other', '📖 综合'],
];
async function showHadith(){
  openModal('mHadith');
  try{ await window.NOUR_loadDataAsset('hadith'); }catch(e){}
  HAD_CUR = null;
  renderHadith();
}
function renderHadith(){
  var body = document.getElementById('mHadithBody');
  var head = document.getElementById('mHadithHead');
  if(!body) return;
  if(HAD_CUR){
    head.textContent = '📜 ' + HAD_CUR.topic;
    var html = '<div style="display:flex;gap:6px;margin-bottom:10px;flex-wrap:wrap">' +
      '<button class="act-btn" style="padding:6px 10px;font-size:10px" onclick="speakHadith()">🔊 诵读</button>' +
      '<button class="act-btn" style="padding:6px 10px;font-size:10px" onclick="hadReview()">📌 复习</button>' +
      '<button class="act-btn" style="padding:6px 10px;font-size:10px" onclick="HAD_CUR=null;renderHadith()">← 返回</button></div>' +
      '<div style="font-size:15px;font-weight:800;color:#0f3d31;margin-bottom:10px">' + esc(HAD_CUR.topic) + '</div>' +
      '<div style="background:linear-gradient(150deg,#14503e,#0e3529);border-radius:14px;padding:16px;margin-bottom:10px">' +
      '<div class="quran-ayah" style="color:#e8d48b;font-weight:700;line-height:2;text-align:center">' + esc(HAD_CUR.ar) + '</div></div>' +
      '<div style="background:#fff;border:1px solid rgba(201,168,76,.2);border-radius:12px;padding:14px;margin-bottom:10px;font-size:13.5px;line-height:1.9;color:#333">🇨🇳 ' + esc(HAD_CUR.cn) + '</div>';
    if(HAD_CUR.note){
      html += '<div style="background:#fdf6e3;border:1px solid rgba(201,168,76,.35);border-radius:12px;padding:14px;margin-bottom:10px">' +
        '<div style="font-size:12px;font-weight:800;color:#a8892e;margin-bottom:6px">📖 注释注解</div>' +
        '<div style="font-size:12px;line-height:1.8;color:#333">' + esc(HAD_CUR.note) + '</div></div>';
    }
    html += '<div style="font-size:10.5px;color:#999">📚 出处：' + esc(HAD_CUR.book_cn || '') + (HAD_CUR.source_cn ? ' · ' + esc(HAD_CUR.source_cn) : '') + '</div>';
    body.innerHTML = html;
    return;
  }
  var total = (BUILTIN_HADITH || []).length;
  head.textContent = '📜 哲言库 · 共 ' + total + ' 则（世界典籍）';
  var html = '';
  // 今日一训
  var todayPool = (BUILTIN_HADITH || []).filter(function(h){ return h.book === 'other'; });
  if(todayPool.length){
    var d = new Date();
    var seed = d.getFullYear() * 10000 + (d.getMonth() + 1) * 100 + d.getDate();
    var th = todayPool[seed %% todayPool.length];
    html += '<div style="background:linear-gradient(150deg,#14503e,#0e3529);border-radius:12px;padding:12px 14px;margin-bottom:10px;cursor:pointer" onclick="HAD_CUR=BUILTIN_HADITH[' + (BUILTIN_HADITH || []).indexOf(th) + '];renderHadith()">' +
      '<div style="font-size:10.5px;font-weight:800;color:#e8d48b;margin-bottom:4px">📜 今日一训</div>' +
      '<div style="font-size:12px;color:#fff;line-height:1.6">' + esc(th.topic) + '</div>' +
      '<div style="font-size:9px;color:rgba(232,212,139,.8);margin-top:4px">点击阅读 ›</div></div>';
  }
  html += '<div style="display:flex;gap:6px;margin-bottom:10px;flex-wrap:wrap">';
  HAD_BOOKS.forEach(function(b){
    var n = (BUILTIN_HADITH || []).filter(function(h){ return h.book === b[0]; }).length;
    html += '<button class="s-btn" style="width:auto;padding:5px 10px;font-size:10px;' + (HAD_BOOK === b[0] ? 'background:#0f3d31;color:#e8d48b' : '') + '" onclick="setHadBook(&#39;' + b[0] + '&#39;)">' + b[1] + ' ' + n + '</button>';
  });
  html += '</div>';
  html += '<div style="margin-bottom:8px"><button class="act-btn" style="padding:6px 10px;font-size:10px" onclick="hadRandom()">🎲 随机一则</button></div>';
  html += '<input id="mHadithSearch" placeholder="🔍 搜索哲言（标题/正文）..." style="width:100%%;padding:8px 12px;border:1px solid #e0dccf;border-radius:10px;font-size:12px;margin-bottom:8px" oninput="HAD_Q=this.value;renderHadith()">';
  if(HAD_BOOK === 'other'){
    var tagSet = {};
    (BUILTIN_HADITH || []).forEach(function(h){ if(h.book === 'other') tagSet[h.tag || '其他'] = 1; });
    var tagList = Object.keys(tagSet).sort();
    html += '<div style="display:flex;gap:5px;margin-bottom:8px;flex-wrap:wrap">' +
      '<button class="s-btn" style="width:auto;padding:3px 9px;font-size:9px;' + (HAD_TAG === '' ? 'background:#0f3d31;color:#e8d48b' : '') + '" onclick="setHadTag(&#39;&#39;)">全部</button>';
    tagList.forEach(function(t){
      html += '<button class="s-btn" style="width:auto;padding:3px 9px;font-size:9px;' + (HAD_TAG === t ? 'background:#0f3d31;color:#e8d48b' : '') + '" onclick="setHadTag(&#39;' + t + '&#39;)">' + t + '</button>';
    });
    html += '</div>';
  }
  var list = (BUILTIN_HADITH || []).filter(function(h){ return h.book === HAD_BOOK; })
    .filter(function(h){ return HAD_BOOK === 'other' && HAD_TAG ? h.tag === HAD_TAG : true; })
    .filter(function(h){ return HAD_Q ? (h.topic || '').indexOf(HAD_Q) >= 0 || (h.cn || '').indexOf(HAD_Q) >= 0 : true; });
  list.forEach(function(h){
    html += '<div style="display:flex;align-items:center;background:#fff;border:1px solid rgba(201,168,76,.2);border-radius:12px;padding:12px 14px;margin-bottom:7px;cursor:pointer" onclick="HAD_CUR=BUILTIN_HADITH[' + (BUILTIN_HADITH || []).indexOf(h) + '];renderHadith()">' +
      '<span style="flex:1"><b style="font-size:13px;color:#333">' + esc(h.topic) + '</b>' +
      (h.ar ? '<span style="display:block;font-size:11px;color:#c9a84c;direction:rtl;text-align:left;margin-top:2px">' + esc(h.ar) + '</span>' : '') +
      (h.grade ? '<span style="display:block;font-size:9.5px;color:#1a8a5c;margin-top:2px">✅ ' + esc(h.grade) + '</span>' : '') +
      '</span><span style="font-size:16px;color:#c9a84c">›</span></div>';
  });
  if(!list.length) html += '<div style="text-align:center;padding:30px;color:#999;font-size:12px">该部暂无收录</div>';
  body.innerHTML = html;
}
function setHadBook(b){ HAD_BOOK = b; HAD_TAG = ''; renderHadith(); }
function setHadTag(t){ HAD_TAG = t; renderHadith(); }
function hadRandom(){
  var pool = (BUILTIN_HADITH || []).filter(function(h){ return h.book === HAD_BOOK; });
  if(pool.length){ HAD_CUR = pool[Math.floor(Math.random() * pool.length)]; renderHadith(); }
}
function hadReview(){
  if(!HAD_CUR) return;
  srsAdd('s', HAD_CUR.ar);
  alert('✅ 已加入复习：这段哲言会按遗忘曲线提醒你记诵');
}
function speakHadith(){
  if(!HAD_CUR || !window.speechSynthesis) return;
  window.speechSynthesis.cancel();
  var u = new SpeechSynthesisUtterance(HAD_CUR.ar);
  u.lang = 'ar-SA'; u.rate = 0.65;
  window.speechSynthesis.speak(u);
}

// ===== 🕌 每日一句 + 自动宣礼 =====
var PRAY_CITIES = [
  ['西宁', 36.6171, 101.7782], ['格尔木', 36.4027, 94.9029], ['海东', 36.5005, 102.1045],
  ['德令哈', 37.3738, 97.3609], ['共和', 36.2845, 100.6201], ['玉树', 33.0047, 97.0061],
  ['玛沁', 34.4739, 100.2417], ['同仁', 35.5197, 102.0166],
  ['北京', 39.9042, 116.4074], ['上海', 31.2304, 121.4737], ['广州', 23.1291, 113.2644],
  ['深圳', 22.5431, 114.0579], ['乌鲁木齐', 43.8256, 87.6168], ['兰州', 36.0611, 103.8343],
  ['银川', 38.4872, 106.2309], ['西安', 34.3416, 108.9398], ['西宁', 36.6171, 101.7782],
  ['昆明', 25.0389, 102.7183], ['郑州', 34.7466, 113.6254], ['呼和浩特', 40.8424, 111.749],
  ['沈阳', 41.8057, 123.4315], ['成都', 30.5728, 104.0668],
];
var PRAY_CITY = 0;
var PRAY_ATHAN = true;
var PRAY_RECITER = 0;
var ATHAN_RECITERS = [
  { name: '阿卜杜勒·巴西特', desc: '埃及 · 320kbps', url: 'athan/abdulbasit.m4a' },
  { name: '阿法西', desc: '科威特著名宣礼师', url: 'athan/alafasy.m4a' },
  { name: '卡萨布', desc: '320kbps', url: 'athan/kassab.m4a' },
  { name: '阿马迪', desc: '卡塔尔 · 320kbps', url: 'athan/amade.m4a' },
  { name: '萨利赫', desc: '卡塔尔 · 320kbps', url: 'athan/saleh.m4a' },
  { name: '特拉布勒西', desc: '科威特 · 256kbps', url: 'athan/trabulsi.m4a' },
  { name: '明沙维', desc: '埃及 · 128kbps', url: 'athan/minshawi.m4a' },
  { name: '萨阿敦', desc: '128kbps', url: 'athan/saadoun.m4a' },
  { name: '达赫贝', desc: '埃及 · 128kbps', url: 'athan/dahbe.m4a' },
  { name: '苏莱希', desc: '128kbps', url: 'athan/surehi.m4a' },
  { name: '阿瓦德', desc: '宣礼师', url: 'athan/awad.m4a' },
  { name: '利雅得', desc: '沙特 · 128kbps', url: 'athan/riyadh.m4a' },
  { name: '阿克萨古城', desc: '历史古城圣城 · 128kbps', url: 'athan/aqsa.mp3' },
  { name: '麦加禁寺', desc: '禁寺 · 192kbps 高保真', url: 'athan/makkah.mp3' },
];
var PRAY_LAST = '';
var ATHAN_AR = 'الله أكبر الله أكبر، أشهد أن لا إله إلا الله، أشهد أن محمدا رسول الله، حي على الصلاة، حي على الفلاح، الله أكبر الله أكبر، لا إله إلا الله';
var ATHAN_CN = '';
var PRAY_NAMES = [['fajr','晨礼','Fajr'],['sunrise','日出','Sunrise'],['dhuhr','晌礼','Dhuhr'],['asr','晡礼','Asr'],['maghrib','昏礼','Maghrib'],['isha','宵礼','Isha']];

function prayFixHour(a){ return a - 24 * Math.floor(a / 24); }
function praySun(jd){
  var D = jd - 2451545.0;
  var g = 357.529 + 0.98560028 * D; g = g - 360 * Math.floor(g / 360);
  var q = 280.459 + 0.98564736 * D; q = q - 360 * Math.floor(q / 360);
  var L = q + 1.915 * Math.sin(g * Math.PI / 180) + 0.02 * Math.sin(2 * g * Math.PI / 180);
  L = L - 360 * Math.floor(L / 360);
  var e = 23.439 - 0.00000036 * D;
  var RA = 180 / Math.PI * Math.atan2(Math.cos(e * Math.PI / 180) * Math.sin(L * Math.PI / 180), Math.cos(L * Math.PI / 180)) / 15;
  var eqt = q / 15 - prayFixHour(RA);
  var decl = Math.asin(Math.sin(e * Math.PI / 180) * Math.sin(L * Math.PI / 180));
  return { decl: decl, eqt: eqt };
}
function prayTimes(date, lat, lon){
  var tz = 8; // 北京时间
  var jd = date.getTime() / 86400000 + 2440587.5;
  var sp = praySun(jd), decl = sp.decl, eqt = sp.eqt;
  var dhuhr = prayFixHour(12 + tz - lon / 15 - eqt);
  function hA(angle){
    var cosH = (Math.sin(angle * Math.PI / 180) - Math.sin(decl) * Math.sin(lat * Math.PI / 180)) / (Math.cos(decl) * Math.cos(lat * Math.PI / 180));
    return 180 / Math.PI * Math.acos(Math.min(1, Math.max(-1, cosH))) / 15;
  }
  var fajr = prayFixHour(dhuhr - hA(-18));
  var sunrise = prayFixHour(dhuhr - hA(-0.833));
  var maghrib = prayFixHour(dhuhr + hA(-0.833));
  var isha = prayFixHour(dhuhr + hA(-17));
  var alt = Math.atan(1 / (Math.tan(Math.abs(lat * Math.PI / 180 - decl)) + 1));
  var asr = dhuhr + 180 / Math.PI * Math.acos(Math.min(1, Math.max(-1, (Math.sin(alt) - Math.sin(decl) * Math.sin(lat * Math.PI / 180)) / (Math.cos(decl) * Math.cos(lat * Math.PI / 180))))) / 15;
  asr = prayFixHour(asr);
  return { fajr: fajr, sunrise: sunrise, dhuhr: dhuhr, asr: asr, maghrib: maghrib, isha: isha };
}
function prayFmt(h){
  var total = Math.round(h * 60);
  var hh = Math.floor(total / 60) %% 24;
  var mm = total %% 60;
  return String(hh).padStart(2, '0') + ':' + String(mm).padStart(2, '0');
}
// ===== 🎵 AI 阿拉伯音乐生成 =====
var MUSIC_AUDIO = null;
function showMusic(){
  openModal('mMusic');
  var body = document.getElementById('mMusicBody');
  if(!body || body.dataset.ready) return;
  body.dataset.ready = '1';
  var h = '<div style="font-size:12px;font-weight:800;color:#0f3d31;margin-bottom:6px">🎼 描述你想要的音乐</div>';
  h += '<textarea id="mMusicPrompt" style="width:100%%;min-height:64px;border:1px solid rgba(201,168,76,.35);border-radius:12px;padding:10px 12px;font-size:13px;line-height:1.7;color:#333;background:#fff" placeholder="例如：浪漫的阿拉伯情歌，男声演唱，乌德琴和手鼓伴奏"></textarea>';
  h += '<div style="font-size:12px;font-weight:800;color:#0f3d31;margin:10px 0 6px">🎤 歌词语言（可选，AI 自动写歌词）</div><div style="display:flex;flex-wrap:wrap;gap:8px">';
  var langs = [['', '🎹 纯音乐'], ['zh', '🇨🇳 中文'], ['en', '🇬🇧 English'], ['ar', '🇸🇦 العربية']];
  for(var li = 0; li < langs.length; li++){
    h += '<label style="font-size:11.5px;font-weight:700;color:#0f3d31;background:#fff;border:1px solid rgba(201,168,76,.3);border-radius:10px;padding:5px 12px;cursor:pointer"><input type="radio" name="mlang" value="' + langs[li][0] + '"' + (langs[li][0] === '' ? ' checked' : '') + ' style="margin-right:3px">' + langs[li][1] + '</label>';
  }
  h += '</div>';
  h += '<div style="font-size:12px;font-weight:800;color:#0f3d31;margin:10px 0 6px">✨ 快捷灵感</div><div style="display:flex;flex-wrap:wrap;gap:6px">';
  for(var i = 0; i < MUSIC_PRESETS.length; i++){
    h += '<button class="s-btn" style="width:auto;padding:6px 10px;font-size:10.5px" onclick="musicPreset(' + i + ')">' + MUSIC_PRESETS[i].slice(0, 14) + '…</button>';
  }
  h += '</div>';
  h += '<div style="font-size:12px;font-weight:800;color:#0f3d31;margin:12px 0 6px">⏱ 时长</div>';
  h += '<div style="display:flex;gap:8px">';
  var secs = [10, 15, 20, 30, 60];
  for(var j = 0; j < secs.length; j++){
    h += '<label style="font-size:12px;font-weight:700;color:#0f3d31;background:#fff;border:1px solid rgba(201,168,76,.3);border-radius:10px;padding:6px 14px;cursor:pointer"><input type="radio" name="msec" value="' + secs[j] + '"' + (secs[j] === 12 ? '' : '') + (secs[j] === 15 ? ' checked' : '') + ' style="margin-right:4px">' + secs[j] + ' 秒</label>';
  }
  h += '</div>';
  h += '<button id="mMusicBtn" class="act-btn" style="width:100%%;margin-top:14px;padding:12px;font-size:14px" onclick="musicGen()">🎵 生成阿拉伯音乐</button>';
  h += '<button class="act-btn" style="width:100%%;margin-top:8px;padding:12px;font-size:13px;background:#0f3d31;color:#e8d48b" onclick="musicFullSong()">🎶 完整歌曲模式（2分钟 · 约8分钟生成）</button>';
  h += '<button class="act-btn" style="width:100%%;margin-top:8px;padding:12px;font-size:13px;background:linear-gradient(135deg,#14503e,#0e3529);color:#e8d48b;border:1px solid rgba(201,168,76,.4)" onclick="openImageModal()">🖼 AI 画图（描述即出图）</button>';
  h += '<div id="mMusicStatus" style="font-size:11.5px;color:#a8892e;margin-top:10px;line-height:1.7;min-height:18px"></div>';
  h += '<audio id="mMusicAudio" controls style="width:100%%;margin-top:8px;display:none"></audio>';
  h += '<div id="mMusicLyrics" style="background:#fdf6e3;border:1px solid rgba(201,168,76,.35);border-radius:12px;padding:12px;margin-top:10px;display:none"></div>';
  h += '<div style="font-size:10px;color:#8a9c8f;margin-top:12px;line-height:1.7">💡 提示：描述越具体越好——乐器（乌德琴/纳伊笛/达布卡鼓）、风格（木卡姆/苏菲/庆典）、情绪（宁静/欢快/神秘）。首次生成需下载模型，之后更快。</div>';
  body.innerHTML = h;
}
function musicGen(){
  var ta = document.getElementById('mMusicPrompt');
  var p = (ta ? ta.value : '').trim();
  if(!p){ alert('请先输入音乐描述'); return; }
  var secs = 10;
  var rb = document.querySelector('input[name="msec"]:checked');
  if(rb) secs = parseInt(rb.value, 10) || 30;
  var mlang = '';
  var lrb = document.querySelector('input[name="mlang"]:checked');
  if(lrb) mlang = lrb.value;
  var st = document.getElementById('mMusicStatus');
  var btn = document.getElementById('mMusicBtn');
  st.textContent = secs > 45 ? '🎵 AI 正在创作长曲（' + secs + ' 秒）...预计 ' + Math.ceil(secs / 10 * 0.7) + '-2 分钟' : '🎵 AI 正在创作...（' + secs + ' 秒约 ' + Math.ceil(secs / 10 * 0.7) + ' 分钟，请稍候）';
  btn.disabled = true;
  btn.textContent = '⏳ 生成中...';
  fetch(API_BASE() + '/api/music', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({prompt:p, seconds:secs, lang:mlang, token:webToken()})})
    .then(function(r){ return r.json(); })
    .then(function(d){
      if(d.url){
        var url = (API_BASE() === '' ? '' : API_BASE()) + d.url;
        st.textContent = '✅ 生成完成！时长 ' + (d.duration || '?') + ' 秒' + (d.lyrics ? '（含歌词）' : '');
        var ap = document.getElementById('mMusicAudio');
        ap.src = url;
        ap.style.display = 'block';
        ap.play().catch(function(){});
        var lb = document.getElementById('mMusicLyrics');
        if(lb){
          if(d.lyrics){
            lb.style.display = 'block';
            lb.innerHTML = '<div style="font-size:11px;font-weight:800;color:#a8892e;margin-bottom:6px">📜 歌词（AI 创作）</div><div style="font-size:12px;line-height:1.9;color:#333;white-space:pre-wrap">' + esc(d.lyrics) + '</div>' + (d.lyrics_cn ? '<div style="font-size:11px;color:#8a9c8f;margin-top:8px;white-space:pre-wrap">🇨🇳 ' + esc(d.lyrics_cn) + '</div>' : '');
          } else {
            lb.style.display = 'none';
          }
        }
      } else {
        st.textContent = '⚠️ ' + (d.error || '生成失败，请重试');
      }
      btn.disabled = false;
      btn.textContent = '🎵 生成阿拉伯音乐';
    })
    .catch(function(){
      st.textContent = '⚠️ 无法连接 AI 服务器：请确认电脑 App/服务器已运行';
      btn.disabled = false;
      btn.textContent = '🎵 生成阿拉伯音乐';
    });
}
var MUSIC_PRESETS = ['阿拉伯传统音乐，乌德琴与纳伊笛，沉思的木卡姆旋律','宁静的阿拉伯祈祷氛围音乐，笛声悠扬，缓慢冥想','阿拉伯庆典鼓乐，达布卡鼓节奏，欢快热情','沙漠夜晚的阿拉伯旋律，乌德琴独奏，神秘悠远','苏菲旋转舞音乐，纳伊笛与手鼓，空灵神圣'];
function musicFullSong(){
  var rbs = document.querySelectorAll('input[name="msec"]');
  rbs.forEach(function(x){ x.checked = (x.value === '120'); });
  var st = document.getElementById('mMusicStatus');
  if(st) st.textContent = '🎶 完整歌曲模式已选：2 分钟。点「生成」开始（约需 6-10 分钟）';
}
function openImageModal(){ openModal('mImage'); }
async function genImage(){
  var t = document.getElementById('imgPrompt').value.trim();
  var st = document.getElementById('imgStatus');
  var rs = document.getElementById('imgResult');
  if(!t){ st.textContent = '⚠️ 请先描述你想画的画面'; return; }
  st.textContent = '🎨 AI 正在作画，请稍候（10-30秒）...';
  rs.innerHTML = '';
  try{
    var r = await fetch(API_BASE() + '/api/image', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({prompt:t, width:512, height:512})});
    var d = await r.json();
    if(d.url){
      st.textContent = '✅ 完成！长按图片可保存';
      rs.innerHTML = '<img src="' + API_BASE() + d.url + '" style="width:100%%;max-width:380px;border-radius:14px;border:1px solid rgba(201,168,76,.4)">';
    } else {
      st.textContent = '⚠️ ' + (d.error || '生成失败，换个描述试试');
    }
  }catch(e){ st.textContent = '⚠️ 无法连接服务器'; }
}
function musicPreset(i){
  var ta = document.getElementById('mMusicPrompt');
  if(ta && MUSIC_PRESETS[i]) ta.value = MUSIC_PRESETS[i];
}
function showPrayer(){
  openModal('mPrayer');
  try{ PRAY_CITY = parseInt(localStorage.getItem('nur_pray_city') || '0', 10) || 0; }catch(e){}
  try{ PRAY_ATHAN = (localStorage.getItem('nur_pray_athan') || '1') !== '0'; }catch(e){}
  try{ PRAY_RECITER = parseInt(localStorage.getItem('nur_pray_reciter') || '0', 10) || 0; }catch(e){}
  renderPrayer();
}
function renderPrayer(){
  var body = document.getElementById('mPrayerBody');
  var head = document.getElementById('mPrayPrayHead');
  if(!body) return;
  var now = new Date();
  var c = PRAY_CITIES[PRAY_CITY];
  var t = prayTimes(now, c[1], c[2]);
  var curMin = now.getHours() * 60 + now.getMinutes();
  head.textContent = '🕌 每日一句 · ' + c[0];
  var html = '';
  // 下次学习
  var next = null;
  [['fajr','晨礼'],['dhuhr','晌礼'],['asr','晡礼'],['maghrib','昏礼'],['isha','宵礼']].forEach(function(p){
    var tm = Math.round(t[p[0]] * 60);
    if(!next && tm > curMin) next = { name: p[1], tm: tm };
  });
  if(!next) next = { name: '晨礼', tm: Math.round(t.fajr * 60) + 1440 };
  var remain = next.tm - curMin; if(remain < 0) remain += 1440;
  html += '<div style="background:linear-gradient(150deg,#14503e,#0e3529);border-radius:16px;padding:16px;text-align:center;margin-bottom:12px">' +
    '<div style="font-size:10.5px;color:rgba(255,255,255,.7)">下次学习</div>' +
    '<div style="font-size:15px;font-weight:800;color:#e8d48b;margin-top:4px">' + next.name + '</div>' +
    '<div style="font-size:32px;font-weight:800;color:#fff;margin-top:2px">' + prayFmt(next.tm / 60) + '</div>' +
    '<div style="font-size:10.5px;color:rgba(255,255,255,.7);margin-top:4px">还有 ' + Math.floor(remain / 60) + ' 小时 ' + (remain %% 60) + ' 分钟</div></div>';
  // 五时学习
  html += '<div style="background:#fff;border:1px solid rgba(201,168,76,.2);border-radius:12px;padding:4px 12px;margin-bottom:12px">';
  PRAY_NAMES.forEach(function(p){
    html += '<div style="display:flex;align-items:center;padding:10px 0;border-bottom:1px solid rgba(201,168,76,.1)">' +
      '<span style="width:76px;font-size:13.5px;font-weight:700;color:#333">🕌 ' + p[1] + '</span>' +
      '<span style="flex:1;font-size:10.5px;color:#999">' + p[2] + '</span>' +
      '<span style="font-size:15px;font-weight:800;color:' + (Math.abs(curMin - Math.round(t[p[0]] * 60)) < 60 ? '#a8892e' : '#0f3d31') + '">' + prayFmt(t[p[0]]) + '</span></div>';
  });
  html += '</div>';
  // 宣礼开关
  html += '<div style="display:flex;align-items:center;background:#fff;border:1px solid rgba(201,168,76,.2);border-radius:12px;padding:12px 14px;margin-bottom:12px">' +
    '<div style="flex:1"><div style="font-size:13px;font-weight:800;color:#333">🔔 到点自动念宣礼</div>' +
    '<div style="font-size:9.5px;color:#999;margin-top:3px">每日一句到时自动阿语宣礼（需浏览器支持阿语语音）</div></div>' +
    '<button class="act-btn" style="background:' + (PRAY_ATHAN ? '#0f3d31' : '#ccc') + ';color:' + (PRAY_ATHAN ? '#e8d48b' : '#666') + ';padding:8px 18px" onclick="togglePrayAthan()">' + (PRAY_ATHAN ? '开' : '关') + '</button></div>';
  // 宣礼学者选择
  html += '<div style="font-size:13px;font-weight:800;color:#0f3d31;margin-bottom:8px">🎙 宣礼学者</div><div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:8px">';
  ATHAN_RECITERS.forEach(function(r, i){
    html += '<button class="s-btn" style="width:auto;padding:5px 10px;font-size:10px;' + (PRAY_RECITER === i ? 'background:#0f3d31;color:#e8d48b' : '') + '" onclick="setPrayReciter(' + i + ')">' + r.name + '</button>';
  });
  html += '</div><div style="font-size:9px;color:#999;margin-bottom:10px">🎧 已内嵌 15 位专业宣礼师原声音频（巴西特/阿法西/卡萨布/麦加禁寺/麦地那圣寺/阿克萨古城等），离线播放</div>';
  // 宣礼词 + 试听
  html += '<div style="background:#fdf6e3;border:1px solid rgba(201,168,76,.35);border-radius:12px;padding:12px 14px;margin-bottom:12px">' +
    '<div class="quran-ayah" style="color:#0f3d31;font-weight:700;text-align:center">' + ATHAN_AR + '</div>' +
    '<div style="font-size:10px;color:#999;margin-top:8px;line-height:1.6">🇨🇳 ' + ATHAN_CN + '</div>' +
    '<div style="text-align:center;margin-top:10px"><button class="act-btn" onclick="playAthanWeb()">🔊 试听宣礼</button></div></div>';
  // 城市
  html += '<div style="font-size:13px;font-weight:800;color:#0f3d31;margin-bottom:8px">📍 选择城市</div><div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:8px">';
  PRAY_CITIES.forEach(function(c2, i){
    html += '<button class="s-btn" style="width:auto;padding:5px 10px;font-size:10px;' + (PRAY_CITY === i ? 'background:#0f3d31;color:#e8d48b' : '') + '" onclick="setPrayCity(' + i + ')">' + c2[0] + '</button>';
  });
  html += '</div>';
  html += '<div style="font-size:9px;color:#999;line-height:1.5">* 按 MWL 标准（晨礼 18°、宵礼 17°、晡礼影子 1 倍）天文算法离线计算，与主流每日一句表误差约 1-3 分钟</div>';
  body.innerHTML = html;
}
function setPrayCity(i){
  PRAY_CITY = i;
  try{ localStorage.setItem('nur_pray_city', String(i)); }catch(e){}
  renderPrayer();
}
function setPrayReciter(i){
  PRAY_RECITER = i;
  try{ localStorage.setItem('nur_pray_reciter', String(i)); }catch(e){}
  renderPrayer();
  playAthanWeb();
}
function togglePrayAthan(){
  PRAY_ATHAN = !PRAY_ATHAN;
  try{ localStorage.setItem('nur_pray_athan', PRAY_ATHAN ? '1' : '0'); }catch(e){}
  renderPrayer();
}
function playAthanWeb(){
  var r = ATHAN_RECITERS[PRAY_RECITER];
  if(r && r.url){
    if(athanAudio){ athanAudio.pause(); }
    athanAudio = new Audio(r.url);
    athanAudio.onerror = function(){ speechAthan(); };
    athanAudio.play().catch(function(e){
      // 音频不可用 → TTS 兜底
      speechAthan();
    });
    return;
  }
  speechAthan();
}
var athanAudio = null;
function speechAthan(){
  if(!window.speechSynthesis) return;
  window.speechSynthesis.cancel();
  var u = new SpeechSynthesisUtterance(ATHAN_AR);
  u.lang = 'ar-SA'; u.rate = 0.75;
  window.speechSynthesis.speak(u);
  var v = new SpeechSynthesisUtterance(ATHAN_CN);
  v.lang = 'zh-CN'; v.rate = 0.95;
  u.onend = function(){ window.speechSynthesis.speak(v); };
}
// 宣礼检测定时器（每 20 秒）
setInterval(function(){
  if(!PRAY_ATHAN) return;
  var now = new Date();
  var c = PRAY_CITIES[PRAY_CITY];
  var t = prayTimes(now, c[1], c[2]);
  var cur = now.getHours() * 60 + now.getMinutes();
  var todayKey = now.getFullYear() + '-' + now.getMonth() + '-' + now.getDate();
  [['fajr','晨礼'],['dhuhr','晌礼'],['asr','晡礼'],['maghrib','昏礼'],['isha','宵礼']].forEach(function(p){
    var tm = Math.round(t[p[0]] * 60);
    var lk = todayKey + '_' + p[0];
    var last = '';
    try{ last = localStorage.getItem('nur_pray_last') || ''; }catch(e){}
    if(Math.abs(cur - tm) <= 0 && last !== lk){
      try{ localStorage.setItem('nur_pray_last', lk); }catch(e){}
      playAthanWeb();
      alert('🕌 ' + p[1] + '时间到（' + prayFmt(t[p[0]]) + '）\\n\\n' + ATHAN_CN);
    }
  });
}, 20000);

// ===== 📜 历史库（回族 · 穆斯利姆 · 中国穆斯利姆） =====
var HIST_CAT = 'huihui';
var HIST_Q = '';
var HIST_CUR = null;
function setHistCat(cat){ HIST_CAT = cat; HIST_Q = ''; renderHistory(); }
function histFavToggle(){
  if(!HIST_CUR) return;
  try{
    var f = JSON.parse(localStorage.getItem('nur_hist_fav') || '{}');
    if(f[HIST_CUR.title]) delete f[HIST_CUR.title];
    else f[HIST_CUR.title] = 1;
    localStorage.setItem('nur_hist_fav', JSON.stringify(f));
  }catch(e){}
  renderHistory();
}
function histNav(dir){
  var list = (BUILTIN_HISTORY || []).filter(function(a){ return a.cat === HIST_CAT; });
  var i = list.indexOf(HIST_CUR);
  var j = (i + dir + list.length) %% list.length;
  HIST_CUR = list[j];
  renderHistory();
}
function histRandom(){
  var pool = (BUILTIN_HISTORY || []).filter(function(a){ return a.cat === HIST_CAT; });
  if(pool.length){ HIST_CUR = pool[Math.floor(Math.random() * pool.length)]; renderHistory(); }
}
async function showHistory(){
  openModal('mHistory');
  try{ await window.NOUR_loadDataAsset('history'); }catch(e){}
  HIST_CUR = null;
  renderHistory();
}
function renderHistory(){
  var body = document.getElementById('mHistoryBody');
  var head = document.getElementById('mHistoryHead');
  if(!body) return;
  if(HIST_CUR){
    head.textContent = '📜 ' + HIST_CUR.title;
    try{
      var hr = JSON.parse(localStorage.getItem('nur_hist_read') || '{}');
      hr[HIST_CUR.title] = 1;
      localStorage.setItem('nur_hist_read', JSON.stringify(hr));
    }catch(e){}
    body.innerHTML = '<div style="display:flex;gap:6px;margin-bottom:10px;flex-wrap:wrap">' +
      '<button class="act-btn" style="padding:6px 10px;font-size:10px" onclick="speakHistory()">🔊 朗读</button>' +
      '<button class="act-btn" style="padding:6px 10px;font-size:10px" onclick="histFavToggle()">☆ 收藏</button>' +
      '<button class="act-btn" style="padding:6px 10px;font-size:10px" onclick="histNav(-1)">‹ 上一篇</button>' +
      '<button class="act-btn" style="padding:6px 10px;font-size:10px" onclick="histNav(1)">下一篇 ›</button>' +
      '<button class="act-btn" style="padding:6px 10px;font-size:10px" onclick="HIST_CUR=null;renderHistory()">← 列表</button></div>' +
      '<div style="background:#fff;border:1px solid rgba(201,168,76,.2);border-radius:14px;padding:16px 18px;font-size:15px;line-height:2;color:#2b2b2b;text-align:justify">' +
      esc(HIST_CUR.body) + '</div>' +
      '<div style="font-size:13px;font-weight:800;color:#0f3d31;margin:18px 4px 8px">📚 相关文章（' + (HIST_CUR.cat_cn || '') + '）</div>' +
      (BUILTIN_HISTORY || []).filter(function(a){ return a.cat === HIST_CUR.cat && a.title !== HIST_CUR.title; }).slice(0, 5).map(function(a){
        return '<div style="display:flex;align-items:center;background:#fff;border:1px solid rgba(201,168,76,.2);border-radius:10px;padding:10px 12px;margin-bottom:6px;cursor:pointer" onclick="HIST_CUR=BUILTIN_HISTORY[' + (BUILTIN_HISTORY || []).indexOf(a) + '];renderHistory()">' +
          '<span style="flex:1;font-size:12px;color:#333">' + (a.icon || '📜') + ' ' + esc(a.title) + '</span><span style="color:#c9a84c">›</span></div>';
      }).join('');
    return;
  }
  var cats = [['huihui','🌙 回族历史'],['muslim','🕌 穆斯利姆历史'],['cnmuslim','🕋 中国穆斯利姆']];
  var catsHtml = '<div style="display:flex;gap:6px;margin-bottom:10px;flex-wrap:wrap">';
  cats.forEach(function(c){
    catsHtml += '<button class="s-btn" style="width:auto;padding:5px 12px;font-size:11px;' + (HIST_CAT === c[0] ? 'background:#0f3d31;color:#e8d48b' : '') + '" onclick="setHistCat(&#39;' + c[0] + '&#39;)">' + c[1] + '</button>';
  });
  catsHtml += '</div>';
  var list = (BUILTIN_HISTORY || []).filter(function(a){ return a.cat === HIST_CAT; });
  if(HIST_Q) list = list.filter(function(a){ return a.title.indexOf(HIST_Q) >= 0; });
  var histRead = {};
  try{ histRead = JSON.parse(localStorage.getItem('nur_hist_read') || '{}'); }catch(e){}
  var histFav = {};
  try{ histFav = JSON.parse(localStorage.getItem('nur_hist_fav') || '{}'); }catch(e){}
  var total = (BUILTIN_HISTORY || []).length;
  head.textContent = '📜 历史库 · 共 ' + total + ' 篇';
  var html = catsHtml +
    '<div style="display:flex;gap:6px;margin-bottom:8px">' +
    '<button class="act-btn" style="padding:6px 10px;font-size:10px" onclick="histRandom()">🎲 随机一篇</button>' +
    '</div>' +
    '<input id="mHistorySearch" placeholder="🔍 搜索标题..." style="width:100%%;padding:8px 12px;border:1px solid #e0dccf;border-radius:10px;font-size:12px;margin-bottom:10px" oninput="HIST_Q=this.value;renderHistory()">';
  list.forEach(function(a){
    html += '<div style="display:flex;align-items:center;background:#fff;border:1px solid rgba(201,168,76,.2);border-radius:12px;padding:12px 14px;margin-bottom:7px;cursor:pointer" onclick="HIST_CUR=BUILTIN_HISTORY[' + (BUILTIN_HISTORY || []).indexOf(a) + '];renderHistory()">' +
      '<span style="font-size:22px;margin-right:10px">' + (a.icon || '📜') + '</span>' +
      '<span style="flex:1"><b style="font-size:13.5px;color:#333">' + esc(a.title) + '</b>' +
      '<span style="display:block;font-size:10px;color:#999;margin-top:2px">' + (histFav[a.title] ? '⭐ ' : '') + (histRead[a.title] ? '✅ 已读' : a.body.length + ' 字') + '</span></span>' +
      '<span style="font-size:16px;color:#c9a84c">›</span></div>';
  });
  if(!list.length) html += '<div style="text-align:center;padding:30px;color:#999;font-size:12px">暂无文章</div>';
  body.innerHTML = html;
}
function speakHistory(){
  if(!HIST_CUR || !window.speechSynthesis) return;
  window.speechSynthesis.cancel();
  var u = new SpeechSynthesisUtterance(HIST_CUR.body.replace(/[🕌🕋🌙📜]/g, ''));
  u.lang = 'zh-CN'; u.rate = 0.85;
  var vs = window.speechSynthesis.getVoices() || [];
  for(var i = 0; i < vs.length; i++){
    if((vs[i].lang || '').indexOf('zh') === 0){ u.voice = vs[i]; break; }
  }
  window.speechSynthesis.speak(u);
}

// ===== 💬 日常对话（留学生场景 · 每天 10 场景 100 句轮换） =====
var DLG_SCENES = null;   // 全量场景目录
var DLG_TODAY = null;     // 今日推荐场景
var DLG_CUR = null;      // 当前对话场景
var DLG_HIDE = false;    // 隐藏中文
var DLG_TALKING = false;
var DLG_TOPIC = 'all';
function dlgTodayScenes(){
  var d = new Date();
  var seed = d.getFullYear() * 10000 + (d.getMonth() + 1) * 100 + d.getDate();
  var all = (BUILTIN_DIALOGUES || []).slice();
  for(var i = all.length - 1; i > 0; i--){
    var j = (seed + i * 7) %% (i + 1);
    var t = all[i]; all[i] = all[j]; all[j] = t;
  }
  return all.slice(0, 10);
}
function showDialog(){
  var _dialogRoot = document.getElementById('mDialog');
  if(_dialogRoot && _dialogRoot.parentNode !== document.body) document.body.appendChild(_dialogRoot);
  openModal('mDialog');
  if(!DLG_SCENES) DLG_SCENES = (BUILTIN_DIALOGUES || []).slice();
  if(!DLG_TODAY) DLG_TODAY = dlgTodayScenes();
  DLG_TOPIC = 'all';
  DLG_CUR = null;
  renderDialog();
}
var DLG_PLAYING_ALL = false;
function dlgPlayAllScenes(){
  if(DLG_PLAYING_ALL){ // 停止
    DLG_PLAYING_ALL = false;
    if(window.speechSynthesis) window.speechSynthesis.cancel();
    renderDialog();
    return;
  }
  DLG_PLAYING_ALL = true;
  var scenes2 = DLG_TODAY || DLG_SCENES.slice(0, 10);
  var lines = [];
  scenes2.forEach(function(s){
    (s.dialogue || []).forEach(function(r){ lines.push(r.a); lines.push(r.b); });
  });
  var k = 0;
  (function next(){
    if(k >= lines.length || !DLG_PLAYING_ALL || !document.getElementById('mDialogBody')){ DLG_PLAYING_ALL = false; renderDialog(); return; }
    dlgSpeak(lines[k], 0.7);
    k++;
    setTimeout(next, 2600 + lines[k-1].length * 60);
  })();
}
function dlgNextDay(){
  var all = (BUILTIN_DIALOGUES || []).slice();
  for(var i = all.length - 1; i > 0; i--){
    var j = Math.floor(Math.random() * (i + 1));
    var t = all[i]; all[i] = all[j]; all[j] = t;
  }
  DLG_TODAY = all.slice(0, 10);
  DLG_TOPIC = 'today';
  DLG_CUR = null;
  renderDialog();
}
function dlgTopicOf(s){
  var x = String((s && s.scene) || '') + ' ' + String((s && s.scene_ar) || '');
  if(/大学|校园|宿舍|图书馆|报到|课程|考试|老师|学校|جامع|مكتب|درس/.test(x)) return 'study';
  if(/餐|咖啡|购物|超市|市场|饭|食堂|مطعم|سوق|طعام|قهوة/.test(x)) return 'life';
  if(/银行|手机|邮局|医院|看病|药|办卡|بنك|هاتف|مستشفى|صيدلية/.test(x)) return 'service';
  if(/旅行|机场|酒店|火车|出租|方向|旅游|مطار|فندق|سفر|قطار/.test(x)) return 'travel';
  return 'social';
}
function dlgTopicFilter(topic){ DLG_TOPIC = topic || 'all'; DLG_CUR = null; renderDialog(); }
function dlgVisibleScenes(){
  var all = DLG_SCENES || [];
  if(DLG_TOPIC === 'today') return DLG_TODAY || all.slice(0, 10);
  if(DLG_TOPIC === 'all') return all;
  return all.filter(function(s){ return dlgTopicOf(s) === DLG_TOPIC; });
}
function dlgSpeak(txt, rate){
  if(!window.speechSynthesis) return;
  window.speechSynthesis.cancel();
  var u = new SpeechSynthesisUtterance(txt);
  u.lang = 'ar-SA'; u.rate = rate || 0.7;
  window.speechSynthesis.speak(u);
}
function dlgPlayAll(){
  if(!DLG_CUR) return;
  if(DLG_TALKING){ // 再点 = 停止
    DLG_TALKING = false;
    if(window.speechSynthesis) window.speechSynthesis.cancel();
    renderDialog();
    return;
  }
  var lines = [];
  DLG_CUR.dialogue.forEach(function(r, i){ lines.push(r.a); lines.push(r.b); });
  var k = 0;
  DLG_TALKING = true;
  (function next(){
    if(k >= lines.length || DLG_TALKING === false || !document.getElementById('mDialogBody')){ DLG_TALKING = false; renderDialog(); return; }
    dlgSpeak(lines[k], 0.7);
    k++;
    setTimeout(next, 2600 + lines[k-1].length * 60);
  })();
}
function renderDialog(){
  var body = document.getElementById('mDialogBody');
  var head = document.getElementById('mDialogHead');
  if(!body) return;
  if(!DLG_CUR){
    var total = DLG_SCENES.reduce(function(n, s){ return n + (s.dialogue || []).length * 2; }, 0);
    var visible = dlgVisibleScenes();
    var today = DLG_TODAY || DLG_SCENES.slice(0, 10);
    head.textContent = '💬 阿拉伯语对话学习 · ' + DLG_SCENES.length + ' 个场景 · ' + total + ' 句';
    var html = '<div class="dlg-intro"><div class="dlg-intro-mark">محادثة</div><div><strong>阿拉伯语对话学习中心</strong><span>每句都有阿拉伯语原文、中文翻译和朗读练习</span></div></div>' +
      '<div class="dlg-toolbar"><div><b>' + visible.length + '</b><span>个场景</span><i>·</i><b>' + visible.reduce(function(n, s){ return n + (s.dialogue || []).length * 2; }, 0) + '</b><span>句双语练习</span></div><div class="dlg-toolbar-actions"><button class="dlg-tool-btn" onclick="dlgPlayAllScenes()">' + (DLG_PLAYING_ALL ? '⏹ 停止播放' : '▶ 今日连续播放') + '</button><button class="dlg-tool-btn" onclick="dlgNextDay()">🔄 换今日推荐</button></div></div>' +
      '<div class="dlg-topics"><button class="dlg-topic ' + (DLG_TOPIC === 'all' ? 'on' : '') + '" onclick="dlgTopicFilter(\\'all\\')">全部目录</button><button class="dlg-topic ' + (DLG_TOPIC === 'today' ? 'on' : '') + '" onclick="dlgTopicFilter(\\'today\\')">今日推荐</button><button class="dlg-topic ' + (DLG_TOPIC === 'study' ? 'on' : '') + '" onclick="dlgTopicFilter(\\'study\\')">学习校园</button><button class="dlg-topic ' + (DLG_TOPIC === 'life' ? 'on' : '') + '" onclick="dlgTopicFilter(\\'life\\')">生活购物</button><button class="dlg-topic ' + (DLG_TOPIC === 'service' ? 'on' : '') + '" onclick="dlgTopicFilter(\\'service\\')">办事服务</button><button class="dlg-topic ' + (DLG_TOPIC === 'travel' ? 'on' : '') + '" onclick="dlgTopicFilter(\\'travel\\')">旅行出行</button><button class="dlg-topic ' + (DLG_TOPIC === 'social' ? 'on' : '') + '" onclick="dlgTopicFilter(\\'social\\')">日常社交</button></div><div class="dlg-scene-list">';
    if(!visible.length) html += '<div class="dlg-empty">这个主题暂时没有场景</div>';
    visible.forEach(function(s){
      var isToday = today.indexOf(s) >= 0;
      html += '<article class="dlg-scene-card" onclick="dlgOpenScene(' + DLG_SCENES.indexOf(s) + ')"><div class="dlg-scene-icon">' + (s.icon || '💬') + '</div><div class="dlg-scene-copy"><strong>' + esc(s.scene) + '</strong><span class="dlg-scene-ar" dir="rtl">' + esc(s.scene_ar) + '</span><small><b>' + (s.dialogue ? s.dialogue.length * 2 : 0) + '</b> 句双语对话' + (isToday ? ' · <em>今日推荐</em>' : '') + '</small></div><span class="dlg-scene-arrow">›</span></article>';
    });
    html += '</div>';
    body.innerHTML = html;
    return;
  }
  var sc = DLG_CUR;
  var _sidx = DLG_SCENES.indexOf(sc) + 1;
  head.textContent = '💬 ' + _sidx + '/' + DLG_SCENES.length + ' ' + sc.scene + ' · ' + (sc.dialogue ? sc.dialogue.length : 0) + ' 轮有来有往';
  var html = '<div class="dlg-detail-head"><div><span class="dlg-kicker">BILINGUAL CONVERSATION · حوار ثنائي اللغة</span><h2>' + esc(sc.scene) + '</h2><p dir="rtl">' + esc(sc.scene_ar || '') + '</p></div><div class="dlg-detail-actions"><button class="dlg-tool-btn" onclick="dlgPlayAll()">' + (DLG_TALKING ? '⏹ 停止播放' : '🔊 整段播放') + '</button><button class="dlg-tool-btn" onclick="DLG_HIDE=!DLG_HIDE;renderDialog()">' + (DLG_HIDE ? '👁 显示中文' : '🙈 隐藏中文') + '</button><button class="dlg-tool-btn" onclick="DLG_CUR=null;renderDialog()">← 返回目录</button><button class="dlg-tool-btn primary" onclick="dlgNextScene()">下一场景 ›</button></div></div><div class="dlg-learning-note"><span>学习方法</span>先读阿拉伯语，再点击朗读；需要时展开中文翻译，最后点击“跟读”练习。</div><div class="dlg-turn-list">';
  sc.dialogue.forEach(function(r, i){
    html += '<div class="dlg-round-label">第 ' + (i + 1) + ' 轮</div><div class="dlg-turn-group">';
    [['a', r.a, r.a_cn, '#ffffff'], ['b', r.b, r.b_cn, '#fdf6e3']].forEach(function(L){
      html += '<div class="dlg-line-wrap ' + (L[0] === 'b' ? 'reply' : '') + '"><div class="dlg-line-card" onclick="dlgSpeak(' + JSON.stringify(L[1]) + ',0.7)"><div class="dlg-line-label">' + (L[0] === 'a' ? '学习者 · المتعلم' : '对话伙伴 · الشريك') + '</div><div class="dlg-line-ar" dir="rtl" lang="ar">' + L[1] + '</div>' + (DLG_HIDE ? '' : (L[2] ? '<div class="dlg-line-cn">🇨🇳 ' + esc(L[2]) + '</div>' : '')) + '<span class="dlg-speak">🔊</span></div><div class="dlg-line-actions"><button onclick="dlgAddReview(' + JSON.stringify(L[1]) + ')">📌 复习</button><button id="dlgGrade_' + i + '_' + L[0] + '" onclick="dlgGrade(' + JSON.stringify(L[1]) + ',&#39;' + i + '_' + L[0] + '&#39;)">🎯 跟读</button><span id="dlgGradeRes_' + i + '_' + L[0] + '"></span></div></div>';
    });
    html += '</div>';
  });
  html += '</div>';
  body.innerHTML = html;
}
var DLG_GRADE_REC = null;
var DLG_GRADE_CHUNKS = [];
var DLG_GRADE_KEY = null;
function dlgGrade(text, key){
  var btn = document.getElementById('dlgGrade_' + key);
  if(DLG_GRADE_REC){
    // 停止并评分
    DLG_GRADE_REC.stop();
    return;
  }
  if(!navigator.mediaDevices || !window.MediaRecorder){
    alert('当前环境不支持录音，请使用 Chrome/Edge 或桌面 App');
    return;
  }
  DLG_GRADE_CHUNKS = [];
  DLG_GRADE_KEY = key;
  navigator.mediaDevices.getUserMedia({audio:true}).then(function(stream){
    var mr = new MediaRecorder(stream);
    mr.ondataavailable = function(e){ if(e.data && e.data.size) DLG_GRADE_CHUNKS.push(e.data); };
    mr.onstop = function(){
      stream.getTracks().forEach(function(t){ t.stop(); });
      dlgGradeUpload(text, key);
    };
    mr.start(250);
    DLG_GRADE_REC = mr;
    var b = document.getElementById('dlgGrade_' + key);
    if(b) b.textContent = '⏹ 停止';
  }).catch(function(){ alert('麦克风权限被拒绝'); });
}
function dlgGradeUpload(text, key){
  DLG_GRADE_REC = null;
  var b = document.getElementById('dlgGrade_' + key);
  if(b) b.textContent = '🎯 跟读';
  var blob = new Blob(DLG_GRADE_CHUNKS, {type: 'audio/webm'});
  DLG_GRADE_CHUNKS = [];
  if(blob.size < 2000){ return; }
  var box = document.getElementById('dlgGradeRes_' + key);
  if(box) box.innerHTML = '<span style="color:#c9a84c">⏳ 评分中…</span>';
  fetch(API_BASE() + '/api/asr', {method:'POST', headers:{'Content-Type':'application/octet-stream', 'X-ASR-Lang':'ar'}, body: blob})
    .then(function(r){ return r.json(); })
    .then(function(d){
      var heard = (d.text || '').trim();
      var tw = normArWeb(text).split(' ').filter(Boolean);
      var hw = normArWeb(heard).split(' ').filter(Boolean);
      var hs = {}; hw.forEach(function(w){ hs[w] = 1; });
      var matched = 0;
      tw.forEach(function(w){ if(hs[w]) matched++; });
      var score = tw.length ? Math.round((matched / tw.length * 0.7 + (hw.length ? matched / hw.length : 0) * 0.3) * 100) : 0;
      if(box){
        box.innerHTML = 'AI <b style="color:' + (score >= 80 ? '#1a8a5c' : '#c9a84c') + '">' + score + '</b> 分 <span style="font-size:9px;color:#999">' + (heard || '没听清') + '</span>';
      }
    })
    .catch(function(){
      if(box) box.innerHTML = '<span style="color:#c0392b">识别失败：需服务器</span>';
    });
}
function dlgAddReview(txt){
  srsAdd('s', txt);
  alert('✅ 已加入复习：这句会按遗忘曲线提醒你（闪卡→间隔复习）');
}
function dlgNextScene(){
  var cur = DLG_SCENES.indexOf(DLG_CUR);
  DLG_CUR = DLG_SCENES[(cur + 1) %% DLG_SCENES.length];
  DLG_HIDE = false;
  renderDialog();
}
function dlgOpenScene(i){
  DLG_CUR = DLG_SCENES[i];
  DLG_HIDE = false;
  renderDialog();
}

// ===== 💾 数据备份 / 恢复 =====
function exportData(){
  var data = {};
  ['nur_learned','nur_dates','nur_minutes','nur_review','nur_favorites','nur_stats','nur_srs_v1','nur_wordbook_v1'].forEach(function(k){
    var v = localStorage.getItem(k);
    if(v !== null) data[k] = v;
  });
  data._exported = new Date().toISOString();
  var blob = new Blob([JSON.stringify(data, null, 2)], {type:'application/json'});
  var a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'nur-backup-' + todayStr2() + '.json';
  document.body.appendChild(a);
  a.click();
  setTimeout(function(){ URL.revokeObjectURL(a.href); a.remove(); }, 500);
}
function importData(ev){
  var f = ev.target.files && ev.target.files[0];
  if(!f) return;
  var rd = new FileReader();
  rd.onload = function(){
    try{
      var data = JSON.parse(rd.result);
      var n = 0;
      Object.keys(data).forEach(function(k){
        if(k === '_exported') return;
        try{ localStorage.setItem(k, data[k]); n++; }catch(e){}
      });
      alert('✅ 已恢复 ' + n + ' 项数据（连续天数/已学/复习队列/生词本等）');
      updateStats();
    }catch(e){ alert('❌ 备份文件格式错误'); }
    ev.target.value = '';
  };
  rd.readAsText(f);
}


// ===== 🎙 经典选读诵读家 =====
var RECITERS = [
  {label:'🎙 阿法西', path:'Alafasy/mp3/'},
  {label:'🎙 苏达伊斯', path:'Sudais/mp3/'},
  {label:'🎙 阿卜杜勒·巴西特', path:'AbdulBaset/Murattal/mp3/'},
  {label:'🎙 巴西特·穆加瓦德', path:'AbdulBaset/Mujawwad/mp3/'},
  {label:'🎙 沙特里', path:'Shatri/mp3/'},
  {label:'🎙 明沙维', path:'Minshawi/Mujawwad/mp3/'},
  {label:'🎙 舒莱姆', path:'Shuraym/mp3/'}
];
var AUDIO_BASE = 'https://verses.quran.com/';
var currentReciter = -1;
var quranAudio = null;
function setReciter(i){
  currentReciter = i;
  if(quranAudio){ quranAudio.pause(); quranAudio = null; }
  renderReciterRow();
}
function renderReciterRow(){
  var el = document.getElementById('reciterRow');
  if(!el) return;
  var html = '<span style="font-size:10px;color:#999;font-weight:700">🎙 诵读家</span> ';
  var opts = ['🔇 无'].concat(RECITERS.map(function(r){ return r.label; }));
  opts.forEach(function(o, i){
    var on = (currentReciter === i - 1);
    html += '<button class="s-btn" style="width:auto;padding:4px 10px;' + (on ? 'background:#0f3d31;color:#e8d48b' : '') + '" onclick="setReciter(' + (i - 1) + ')">' + o + '</button> ';
  });
  el.innerHTML = html;
}
// 整章诵读家（mp3quran：每章一个完整 mp3）
var FULL_RECITERS = [
  { label: '阿法西', url: 'https://server8.mp3quran.net/afs/' },
  { label: '拉阿德', url: 'https://server8.mp3quran.net/ra3ad/' },
  { label: '哈尼', url: 'https://server8.mp3quran.net/hani/' },
  { label: '阿尤布', url: 'https://server8.mp3quran.net/ayyub/' },
  { label: '曼图里德', url: 'https://server8.mp3quran.net/mtrod/' },
  { label: '诺亚', url: 'https://server8.mp3quran.net/noah/' },
  { label: '萨比尔', url: 'https://server8.mp3quran.net/saber/' },
];
var currentFullReciter = -1;
var fullAudio = null;
var fullTimer = null;
function setFullReciter(i){
  currentFullReciter = i;
  if(fullAudio){ fullAudio.pause(); fullAudio = null; }
  renderFullRow();
}
function renderFullRow(){
  var el = document.getElementById('fullRow');
  if(!el) return;
  var html = '<span style="font-size:10px;color:#999;font-weight:700">📼 整章诵读</span> ';
  var opts = ['🔇 无'].concat(FULL_RECITERS.map(function(r){ return r.label; }));
  opts.forEach(function(o, i){
    var on = (currentFullReciter === i - 1);
    html += '<button class="s-btn" style="width:auto;padding:4px 10px;' + (on ? 'background:#0f3d31;color:#e8d48b' : '') + '" onclick="setFullReciter(' + (i - 1) + ')">' + o + '</button> ';
  });
  el.innerHTML = html;
}
function fmtDur(sec){
  sec = Math.floor(sec || 0);
  var m = Math.floor(sec / 60);
  var s = sec - m * 60;
  return m + ':' + String(s).padStart(2, '0');
}
function playSurahFullWeb(sid){
  var ch = QURAN.filter(function(x){ return x.id === sid; })[0];
  if(!ch) return;
  if(currentFullReciter < 0){ alert('请先选择一位「整章诵读」诵读家'); return; }
  var btn = document.getElementById('fullPlayBtn');
  if(fullAudio && fullAudio._sid === sid){
    fullAudio.pause(); fullAudio = null;
    clearInterval(fullTimer);
    if(btn) btn.textContent = '📼 整章单音频诵读';
    var pv = document.getElementById('fullProg');
    if(pv) pv.textContent = '';
    return;
  }
  // 停止其他播放
  if(quranAudio){ quranAudio.pause(); quranAudio = null; }
  if(ALL_ON){ stopAllPlay(); }
  var r = FULL_RECITERS[currentFullReciter];
  var url = r.url + String(sid).padStart(3, '0') + '.mp3';
  if(fullAudio){ fullAudio.pause(); }
  var a = new Audio(url);
  a._sid = sid;
  fullAudio = a;
  a.play();
  if(btn) btn.textContent = '⏹ 停止整章 · ' + ch.tz;
  var pv = document.getElementById('fullProg');
  if(pv) pv.textContent = '🎧 ' + r.label + ' · ' + ch.tz + ' · 播放中...';
  clearInterval(fullTimer);
  fullTimer = setInterval(function(){
    if(!fullAudio || fullAudio.paused){ return; }
    if(pv) pv.textContent = '🎧 ' + r.label + ' · ' + ch.tz + ' · ' + fmtDur(fullAudio.currentTime) + ' / ' + fmtDur(fullAudio.duration);
  }, 500);
  a.onended = function(){
    clearInterval(fullTimer);
    fullAudio = null;
    if(btn) btn.textContent = '📼 整章单音频诵读';
    if(pv) pv.textContent = '✅ ' + ch.tz + ' 诵读完成';
  };
  a.onerror = function(){
    clearInterval(fullTimer);
    fullAudio = null;
    if(btn) btn.textContent = '📼 整章单音频诵读';
    if(pv) pv.textContent = '⚠️ 音频加载失败，请检查网络';
  };
}
function playAyah(sid, ayahIdx){
  if(currentReciter < 0){ alert('请先选择一位诵读家'); return; }
  var r = RECITERS[currentReciter];
  var key = sid + '_' + ayahIdx;
  if(quranAudio && quranAudio._key === key){
    quranAudio.pause(); quranAudio = null;
    document.querySelectorAll('.rec-btn').forEach(function(b){ b.textContent = '🎙 诵读'; });
    return;
  }
  var url = AUDIO_BASE + r.path + String(sid).padStart(3, '0') + String(ayahIdx + 1).padStart(3, '0') + '.mp3';
  if(quranAudio){ quranAudio.pause(); }
  var a = new Audio(url);
  a._key = key;
  a.play();
  quranAudio = a;
  document.querySelectorAll('.rec-btn').forEach(function(b){ b.textContent = '🎙 诵读'; });
  var btn = document.getElementById('rec_' + key);
  if(btn) btn.textContent = '⏹ 停止';
  a.onended = function(){ quranAudio = null; if(btn) btn.textContent = '🎙 诵读'; };
}

// ===== 🕌 经典选读 =====
var QURAN = [];
var currentSurah = null;
var TAFSIR = [];
var TAFSIR_SURAH = 0;
var TAFSIR_EDITION = 'ar.muyassar';
async function loadTafsir(sid, edition){
  sid = parseInt(sid || 1, 10) || 1;
  edition = edition || TAFSIR_EDITION;
  var hit = TAFSIR.filter(function(x){ return x.surah === sid && x.edition === edition; });
  if(hit.length) return hit;
  try{
    var r = await fetch(API_BASE() + '/api/quran/tafsir?surah=' + sid + '&edition=' + encodeURIComponent(edition));
    var d = await r.json();
    if(!r.ok || !d.ok) throw new Error(d.error || 'tafsir unavailable');
    var rows = (d.ayahs || []).map(function(x){ return {surah:sid, ayah:x.number, text:x.text || '', edition:edition, editionName:d.edition_name || edition, source:d.source_name || 'AlQuran.Cloud', sourceUrl:d.source_url || ''}; });
    TAFSIR = TAFSIR.filter(function(x){ return !(x.surah === sid && x.edition === edition); }).concat(rows);
    return rows;
  }catch(e){ return []; }
}
async function showTafsir(sid){
  sid = parseInt(sid || 1, 10) || 1;
  try{ await window.NOUR_loadDataAsset('quran'); }catch(e){}
  QURAN = window.BUILTIN_QURAN || QURAN || [];
  TAFSIR_SURAH = sid;
  var body = document.getElementById('mQuranBody');
  if(!body){ openModal('mQuran'); body = document.getElementById('mQuranBody'); }
  openModal('mQuran');
  if(!body) return;
  body.innerHTML = '<div style="padding:40px;text-align:center;color:#8a7f72">正在加载经注…</div>';
  var rows = await loadTafsir(sid, TAFSIR_EDITION);
  var s = QURAN.filter(function(x){ return x.id === sid; })[0] || {};
  var h = '<div class="tf-title" dir="rtl">التفسير · ' + catEsc(s.n || '') + ' · ' + catEsc(s.tz || '') + '</div>';
  h += '<div class="tf-source">经注版本：' + catEsc((rows[0] && rows[0].editionName) || 'Tafsir al-Muyassar') + ' · 来源：AlQuran.Cloud · 经注是独立学习资料</div>';
  h += '<div style="display:flex;gap:8px;align-items:center;margin:0 0 10px"><select id="tfSurah" onchange="showTafsir(this.value)" style="flex:1;padding:10px;border-radius:10px;border:1px solid #d9d1bc">';
  h += QURAN.map(function(x){ return '<option value="' + x.id + '"' + (x.id === sid ? ' selected' : '') + '>第 ' + x.id + ' 章 · ' + catEsc(x.n || '') + '</option>'; }).join('');
  h += '</select><select id="tfEdition" onchange="changeTafsirEdition(this.value)" style="flex:1;padding:10px;border-radius:10px;border:1px solid #d9d1bc"><option value="ar.muyassar"' + (TAFSIR_EDITION === 'ar.muyassar' ? ' selected' : '') + '>المیسر</option><option value="ar.jalalayn"' + (TAFSIR_EDITION === 'ar.jalalayn' ? ' selected' : '') + '>الجلالين</option></select></div>';
  h += '<input class="bk-q" id="tfQ" placeholder="搜索本章经注…" oninput="tfFilter(this.value)" style="width:100%%;box-sizing:border-box;margin:0 0 10px">';
  h += '<div id="tfList"></div>';
  body.innerHTML = h;
  tfFilter('');
}
function changeTafsirEdition(edition){ TAFSIR_EDITION = edition || 'ar.muyassar'; showTafsir(TAFSIR_SURAH || 1); }
function tfFilter(q){
  var box = document.getElementById('tfList');
  if(!box) return;
  q = (q || '').trim();
  var sid = TAFSIR_SURAH || 1;
  var s = QURAN.filter(function(x){ return x.id === sid; })[0] || {};
  var list = TAFSIR.filter(function(x){ return x.surah === sid && x.edition === TAFSIR_EDITION && (!q || String(x.ayah).indexOf(q) >= 0 || (x.text || '').indexOf(q) >= 0); });
  box.innerHTML = list.map(function(x){
    var verse = (s.vs || [])[x.ayah - 1] || {};
    return '<article class="tf-item"><div class="tf-h"><b>第 ' + x.ayah + ' 节</b><span>经注 · ' + catEsc(x.editionName || '') + '</span></div><div class="tf-ayah" dir="rtl">' + catEsc(verse.a || '') + '</div><div class="tf-cn">' + catEsc(verse.z || verse.c || '') + '</div><div class="tf-tx" dir="rtl">' + catEsc(x.text || '') + '</div></article>';
  }).join('') || '<div class="srch-tip">本章暂无匹配经注，或上游暂时不可用。</div>';
}
async function surahTafsir(){
  var s = currentSurah;
  if(!s) return;
  var rows = await loadTafsir(s.id, TAFSIR_EDITION);
  RD_AUDIO = null;
  RD_TOC = [];
  RD_TITLE_BACK = true;
  var nm = s.tz + ' · ' + s.n;
  openModal('mReader');
  var tEl = document.getElementById('mReaderTitle');
  if(tEl) tEl.textContent = '经注 · ' + nm;
  var lines = rows.map(function(x){ return 'الآية ' + x.ayah + '\\n' + x.text; });
  RD = null; RD_BOOK_META = null; RD_ISLAMIC_GUIDE = false; RD_OPENITI = null; RD_AUDIO = null; RD_ISCN = false;
  RD_PAGES = [];
  for(var ti = 0; ti < lines.length; ti += 3) RD_PAGES.push(lines.slice(ti, ti + 3).join('\\n\\n'));
  if(!RD_PAGES.length) RD_PAGES = ['（本章经注暂时不可用，请稍后重试）'];
  RD_PAGE = 0;
  renderRead();
}
async function showQuran(){
  try{ await window.NOUR_loadDataAsset('quran'); }catch(e){}
  QURAN = BUILTIN_QURAN || [];
  openModal('mQuran');
  renderQuranList();
}
// ===== 🎧 经典选读整本诵读（114 章连续播放）=====
var ALL_ON = false;
var ALL_POS = { s: 1, a: 0 };
function startAllPlay(fromSurah){
  if(ALL_ON){ stopAllPlay(); return; }
  if(currentReciter < 0){ alert('请先选择一位诵读家'); return; }
  ALL_ON = true;
  ALL_POS = { s: fromSurah, a: 0 };
  renderAllBtn();
  playAllNext();
}
function playAllNext(){
  if(!ALL_ON) return;
  var ch = QURAN.filter(function(x){ return x.id === ALL_POS.s; })[0];
  if(!ch){
    stopAllPlay();
    alert('🎉 整本经典选读诵读完成！');
    return;
  }
  if(ALL_POS.a >= ch.vs.length){
    ALL_POS = { s: ALL_POS.s + 1, a: 0 };
    playAllNext();
    return;
  }
  var r = RECITERS[currentReciter];
  var url = AUDIO_BASE + r.path + String(ALL_POS.s).padStart(3, '0') + String(ALL_POS.a + 1).padStart(3, '0') + '.mp3';
  if(quranAudio){ quranAudio.pause(); }
  var a = new Audio(url);
  var s0 = ALL_POS.s, a0 = ALL_POS.a;
  a.onended = function(){
    if(!ALL_ON) return;
    ALL_POS = { s: s0, a: a0 + 1 };
    renderAllBtn();
    playAllNext();
  };
  a.onerror = function(){
    if(!ALL_ON) return;
    ALL_POS = { s: s0, a: a0 + 1 };
    renderAllBtn();
    playAllNext();
  };
  a.play().catch(function(){});
  quranAudio = a;
  renderAllBtn();
}
function stopAllPlay(){
  ALL_ON = false;
  if(quranAudio){ quranAudio.pause(); quranAudio = null; }
  renderAllBtn();
}
function renderAllBtn(){
  var el = document.getElementById('allPlayBtn');
  if(!el) return;
  if(ALL_ON){
    el.textContent = '⏹ 停止诵读 · 第' + ALL_POS.s + '章 第' + (ALL_POS.a + 1) + '节';
    el.style.background = 'rgba(192,57,43,.15)';
    el.style.color = '#c0392b';
  } else {
    el.textContent = '▶ 整本诵读（114 章连续）';
    el.style.background = 'linear-gradient(135deg,#14503e,#0e3529)';
    el.style.color = '#e8d48b';
  }
}

function renderQuranList(){
  var body = document.getElementById('mQuranBody');
  if(!QURAN || !QURAN.length) QURAN = window.BUILTIN_QURAN || [];
  var q = (document.getElementById('mQuranSearch') ? document.getElementById('mQuranSearch').value : '').trim();
  var list = QURAN;
  if(q){ list = QURAN.filter(function(s){ return (s.n + s.tz + s.t).indexOf(q) >= 0; }); }
  body.innerHTML = '';
  body.innerHTML = '<div style="margin:8px 6px 4px;padding:10px 12px;border-radius:12px;background:#f7f3e9;color:#5a6159;font-size:11px;line-height:1.7">古兰经原文与中文译文分层显示。诵读按钮使用具体诵读家的真人录音；经注请在阅读器底部点 📖 查看。</div><div id="allPlayBtn" style="margin:8px 6px 4px;padding:12px;border-radius:12px;text-align:center;font-size:13px;font-weight:800;cursor:pointer;background:linear-gradient(135deg,#14503e,#0e3529);color:#e8d48b" onclick="startAllPlay(1)">▶ 整本诵读（114 章连续）</div><div style="margin:0 6px 10px;text-align:center"><button class="s-btn" style="width:auto;padding:7px 12px" onclick="showTafsir(1)">📖 打开经注学习</button></div>';
  var readSet = {};
  try{ readSet = JSON.parse(localStorage.getItem('nur_quran_read') || '{}'); }catch(e){}
  list.forEach(function(s){
    var it = document.createElement('div');
    it.className = 's-item' + (readSet[s.id] ? ' s-read' : ''); it.style.cursor = 'pointer';
    it.innerHTML = '<div style="display:flex;align-items:center;gap:8px"><span style="background:#0f3d31;color:#e8d48b;font-size:10px;font-weight:700;border-radius:10px;padding:2px 8px">'+s.id+'</span>'+
      '<span style="font-size:13px;font-weight:700;color:#0f3d31;font-family:AmiriNur,SF Arabic,Geeza Pro,serif">'+s.n+'</span>'+
      '<span style="font-size:10px;color:#999;margin-left:auto">'+(readSet[s.id] ? '✅ 已读' : s.tz+' · '+s.vs.length+' 节')+'</span></div>';
    it.onclick = function(){ openSurah(s); };
    body.appendChild(it);
  });
  document.getElementById('mQuranCount').textContent = '共 ' + list.length + ' 章 · 点击进入';
}
function markQuranRead(id){
  try{
    var r = JSON.parse(localStorage.getItem('nur_quran_read') || '{}');
    r[id] = 1;
    localStorage.setItem('nur_quran_read', JSON.stringify(r));
  }catch(e){}
}
function openSurahById(id){
  var q = QURAN.filter(function(x){ return x.id === id; })[0];
  if(q) openSurah(q);
}
function openSurah(s){
  markQuranRead(s.id);
  currentSurah = s;
  // 跳入牛皮纸阅读页
  rdStopAudio();
  RD = null; RD_BOOK_META = null; RD_ISLAMIC_GUIDE = false; RD_OPENITI = null;
  RD_ISCN = false;
  RD_AUDIO = {kind: 'quran', sid: s.id};
  RD_TOC_TITLE = '经典选读目录';
  RD_TOC = (window.QURAN && QURAN.length ? QURAN : (window.BUILTIN_QURAN || [])).map(function(x){ return {name: x.n + ' · ' + x.tz, act: 'openSurahById(' + x.id + ')'}; });
  var nm = (s.tz || '') + ' · ' + (s.n || '');
  var vs = s.vs || [];
  RD_PAGES = [];
  RD_QURAN_AYAHS = vs;
  RD_QURAN_PAGE_AYAHS = [];
  var per = 5, buf = [];
  function arNum(n){
    var d = '٠١٢٣٤٥٦٧٨٩', out = '';
    String(n).split('').forEach(function(c){ out += (d[parseInt(c, 10)] || c); });
    return out;
  }
  for(var i = 0; i < vs.length; i++){
    var v = vs[i];
    var no = (v.n || (i + 1));
    buf.push((v.a || '') + ' ﴿' + arNum(no) + '﴾' + (((v.z || v.c)) ? ('\\n' + (v.z || v.c)) : ''));
    if(buf.length >= per){ RD_PAGES.push(buf.join('\\n\\n')); RD_QURAN_PAGE_AYAHS.push([]); for(var bi = i - buf.length + 1; bi <= i; bi++) RD_QURAN_PAGE_AYAHS[RD_QURAN_PAGE_AYAHS.length - 1].push(bi); buf = []; }
  }
  if(buf.length){ RD_PAGES.push(buf.join('\\n\\n')); RD_QURAN_PAGE_AYAHS.push([]); for(var bj = vs.length - buf.length; bj < vs.length; bj++) RD_QURAN_PAGE_AYAHS[RD_QURAN_PAGE_AYAHS.length - 1].push(bj); }
  if(!RD_PAGES.length) RD_PAGES = ['（无内容）'];
  RD_PAGE = 0;
  openModal('mReader');
  var tEl = document.getElementById('mReaderTitle');
  if(tEl) tEl.textContent = '经典选读 · ' + nm;
  try{ localStorage.setItem('nur_last_name', '经典选读 · ' + nm); localStorage.setItem('nur_last_act', 'openSurahById(' + s.id + ')'); }catch(e){}
  RD_QAUDIO_ROW = -1; RD_QRATE = 1; RD_QAUTO = true;
  renderRead();
  return;
  var body = document.getElementById('mQuranBody');
  body.innerHTML = '<div style="display:flex;gap:6px;margin-bottom:10px">'+
    '<button class="act-btn" style="padding:6px 10px;font-size:10px" '+(s.id<=1?'disabled':'')+' onclick="openSurahById('+(s.id-1)+')">‹ 上一章</button>'+
    '<button class="act-btn" style="padding:6px 10px;font-size:10px" onclick="renderQuranList()">← 章节列表</button>'+
    '<button class="act-btn" style="padding:6px 10px;font-size:10px" '+(s.id>=114?'disabled':'')+' onclick="openSurahById('+(s.id+1)+')">下一章 ›</button></div>'+
    '<div style="font-size:16px;font-weight:800;color:#0f3d31;text-align:center">🕌 '+s.n+' · '+s.tz+'</div>'+
    '<div style="font-size:10px;color:#999;text-align:center;margin:4px 0 12px">'+s.t+' · '+(s.ty==='meccan'?'麦加章':'麦地那章')+' · '+s.vs.length+' 节</div>'+
    '<div id="reciterRow" style="text-align:center;margin-bottom:8px"></div>'+
    '<div id="fullRow" style="text-align:center;margin-bottom:8px"></div>'+
    '<div style="text-align:center;margin-bottom:10px">'+
      '<button id="fullPlayBtn" class="act-btn" style="padding:7px 16px" onclick="playSurahFullWeb(' + s.id + ')">📼 整章单音频诵读</button>'+
      '<div id="fullProg" style="font-size:10px;color:#a8892e;margin-top:6px"></div>'+
    '</div>';
  s.vs.forEach(function(v, idx){
    var it = document.createElement('div');
    it.className = 's-item';
    var arSafe = v.a.replace(/&/g,'&amp;').replace(/'/g,'&#39;').replace(/"/g,'&quot;');
    it.innerHTML = '<div style="display:flex;gap:10px"><span style="background:#0f3d31;color:#e8d48b;font-size:10px;font-weight:800;border-radius:12px;min-width:22px;text-align:center;padding:3px 6px;height:fit-content;box-shadow:0 2px 6px rgba(15,61,49,.25)">'+(idx+1)+'</span>'+
      '<div style="flex:1"><div class="quran-ayah" style="font-weight:700;color:#0f3d31;text-align:right">'+v.a+'</div>'+
      (v.z ? '<div style="font-size:10.5px;color:#1a5c4a;margin-top:5px">🇨🇳 '+v.z+'</div>' : '')+
      '<div style="display:flex;gap:6px;margin-top:7px;justify-content:flex-end;flex-wrap:wrap">'+
      '<button class="s-btn" onclick="ap(this,0,&#39;'+arSafe+'&#39;)">🔊</button>'+
      '<button class="s-btn" onclick="explainQuran('+s.id+','+idx+')">🔬 逐字分解</button>'+
      (hasTafsir(s.id, idx+1) ? '<button class="s-btn" onclick="toggleTafsir('+s.id+','+idx+')">📖 注释</button>' : '')+
      '<button class="s-btn rec-btn" id="rec_'+s.id+'_'+idx+'" onclick="playAyah('+s.id+','+idx+')">🎙 诵读</button></div>'+
      '<div class="decomp-box" id="dec_'+s.id+'_'+idx+'"></div>'+
      '<div class="tafsir-box" id="taf_'+s.id+'_'+idx+'" style="display:none"></div></div></div>';
    body.appendChild(it);
  });
  document.getElementById('mQuranCount').textContent = '← 点顶部返回';
  renderReciterRow();
  renderFullRow();
}
function hasTafsir(sid, ayah){
  return (BUILTIN_TAFSIR || []).some(function(t){ return t.surah === sid && t.ayah === ayah; });
}
function toggleTafsir(sid, idx){
  var box = document.getElementById('taf_' + sid + '_' + idx);
  if(!box) return;
  if(box.style.display === 'none'){
    var t = (BUILTIN_TAFSIR || []).filter(function(x){ return x.surah === sid && x.ayah === idx + 1; })[0];
    if(t){
      box.innerHTML = '<div style="background:#fdf6e3;border:1px solid rgba(201,168,76,.35);border-radius:10px;padding:10px 12px;margin-top:8px">' +
        '<div style="font-size:10.5px;font-weight:800;color:#a8892e;margin-bottom:5px">📖 注释（' + esc(t.source) + '）</div>' +
        '<div style="font-size:11.5px;line-height:1.9;color:#333">' + esc(t.tafsir) + '</div></div>';
      box.style.display = 'block';
    }
  } else {
    box.style.display = 'none';
  }
}
async function explainQuran(sid, idx){
  var s = QURAN.find(function(x){ return x.id === sid; });
  if(!s) return;
  var ayah = s.vs[idx];
  var box = document.getElementById('dec_' + sid + '_' + idx);
  if(!box) return;
  if(box.dataset.done === '1'){ box.style.display = box.style.display === 'none' ? 'block' : 'none'; return; }
  box.style.display = 'block';
  box.innerHTML = '<div style="text-align:center;padding:16px;color:#999">🧞 AI 正在逐词语法分析...</div>';
  try{
    var r = await fetch(API_BASE() + '/api/chat/message', {method:'POST', headers:{'Content-Type':'application/json'},
      body:JSON.stringify({message:'请对这句经典选读文本做逐词语法分析。要求每个词一行，用竖线分隔 6 个字段：\\n词（保留原文）| 词根 | 词性（اسم名词/فعل动词/حرف介词等）| 语法功能（如主格/宾格/属格/过去式/现在式/人称数）| 中文词义 | 英文词义\\n\\n文本：' + ayah.a, session_id:'quran_'+Date.now(), token:webToken()})});
    var d = await r.json(), txt = d.arabic || '';
    var seen = {};
    var lines = txt.split('\\n');
    var h = '<div style="font-size:10.5px;color:#a8892e;font-weight:700;margin-bottom:8px">🔬 逐词语法分析（点击词可听发音）</div>';
    lines.forEach(function(l){
      var p = l.split('|').map(function(x){ return x.trim(); });
      if(p.length < 3) return;
      var key = p[0].replace(/[\\u064B-\\u0652\\u06D6-\\u06ED]/g, '');
      if(seen[key]) return;
      seen[key] = 1;
      h += '<div style="background:#fff;border:1px solid rgba(201,168,76,.18);border-radius:10px;padding:9px 12px;margin-bottom:7px">'+
        '<div style="display:flex;align-items:center;gap:8px"><b style="font-family:AmiriNur,SF Arabic,Geeza Pro,serif;font-size:15px;color:#0f3d31;direction:rtl;cursor:pointer" onclick="ap(this,0,&#39;'+p[0].replace(/'/g,'&#39;')+'&#39;)">'+esc(p[0])+'</b>'+
        (p[2] ? '<span style="font-size:9px;font-weight:700;color:#a8892e;background:rgba(201,168,76,.12);padding:2px 8px;border-radius:8px;margin-left:auto">'+esc(p[2])+'</span>' : '')+'</div>'+
        '<div style="font-size:10.5px;color:#666;margin-top:4px">词根 '+esc(p[1]||'—')+' · 语法 '+esc(p[3]||'—')+'</div>'+
        '<div style="font-size:10.5px;color:#1a5c4a;margin-top:2px">🇨🇳 '+esc(p[4]||'—')+' &nbsp;·&nbsp; 🇬🇧 '+esc(p[5]||'—')+'</div></div>';
    });
    box.innerHTML = h;
    box.dataset.done = '1';
  }catch(e){
    box.innerHTML = '<div style="text-align:center;padding:14px;color:#999">⚠️ AI 服务未启动，请检查服务器</div>';
  }
}

// ===== 📚 书籍阅读 =====
var BOOKS = [];
var currentBook = null;
async function showBooks(){
  openModal('mLibrary');
  try{ await window.NOUR_loadDataAsset('books'); }catch(e){}
  BOOKS = BUILTIN_BOOKS;
  renderBooks(BOOKS);
  try{
    var r = await fetch(API_BASE() + '/api/books');
    var d = await r.json();
    if(d.books && d.books.length){ BOOKS = d.books; renderBooks(BOOKS); }
  }catch(e){}
}
function renderBooks(books){
  var body = document.getElementById('mLibBody');
  body.innerHTML = '';
  books.forEach(function(b){
    var it = document.createElement('div');
    it.className = 's-item'; it.style.cursor = 'pointer';
    it.innerHTML = '<div style="font-size:14px;font-weight:700;color:#1a5c4a">📕 '+b.title+'</div>'+
      '<div style="font-size:10.5px;color:#999;margin-top:4px">👤 '+b.author+' · '+b.chapters.length+' 章</div>'+
      '<div style="font-size:10px;color:#666;margin-top:3px">'+(b.intro_cn||'').slice(0,60)+'...</div>';
    it.onclick = function(){ openBook(b); };
    body.appendChild(it);
  });
  document.getElementById('mLibCount').textContent = '共 ' + books.length + ' 本书 · 点击进入阅读';
}
function openBook(b){
  currentBook = b;
  var body = document.getElementById('mLibBody');
  body.innerHTML = '<button class="act-btn" style="margin-bottom:10px" onclick="renderBooks(BOOKS)">← 返回书籍列表</button>'+
    '<div style="font-size:15px;font-weight:800;color:#1a5c4a;margin-bottom:4px">📕 '+b.title+'</div>'+
    '<div style="font-size:10.5px;color:#999;margin-bottom:10px">👤 '+b.author+'</div>'+
    '<div style="font-size:11px;color:#666;line-height:1.7;background:#fff;border:1px solid rgba(201,168,76,.15);border-radius:10px;padding:10px 12px;margin-bottom:12px">'+b.intro_cn+'</div>'+
    '<div style="font-size:10px;color:#999;margin-bottom:6px">📑 目录（'+b.chapters.length+' 章）</div>';
  b.chapters.forEach(function(c, i){
    var it = document.createElement('div');
    it.className = 's-item'; it.style.cursor = 'pointer';
    it.innerHTML = '<div style="font-size:12px;font-weight:600;color:#0f3d31">'+(i+1)+'. '+c.t+'</div>'+
      '<div style="font-size:9.5px;color:#999;margin-top:3px">'+c.body.slice(0,45)+'...</div>';
    it.onclick = function(){ openArticle({title: b.title+' · '+c.t, body: c.body, cn: ''}); };
    body.appendChild(it);
  });
  document.getElementById('mLibCount').textContent = '← 点顶部按钮返回列表';
}

function renderLibrary(arts){
  var body = document.getElementById('mLibBody');
  body.innerHTML = '';
  arts.forEach(function(a){
    var it = document.createElement('div');
    it.className = 's-item';
    it.style.cursor = 'pointer';
    it.innerHTML = '<div style="font-size:14px;font-weight:700;color:#1a5c4a">📖 '+a.title+'</div>'+
      '<div style="font-size:10px;color:#999;margin-top:4px">'+a.body.slice(0,60)+'...</div>';
    it.onclick = function(){ openArticle(a); };
    body.appendChild(it);
  });
  document.getElementById('mLibCount').textContent = '共 ' + arts.length + ' 篇文章';
}


// ===== ✂️ 单词拆解（AI 逐词解释）=====
async function explainSentence(ar){
  var body = document.getElementById('mExplainBody');
  body.innerHTML = '<div style="text-align:center;padding:30px;color:#999">🧞 AI 正在逐词拆解...</div>';
  openModal('mExplain');
  try{
    var r = await fetch(API_BASE() + '/api/chat/message', {method:'POST', headers:{'Content-Type':'application/json'},
      body:JSON.stringify({message:'请逐词拆解并解释这句阿拉伯语。格式：每个词一行，先写阿拉伯语单词（去掉音符），再写中文释义和英文释义，如有词性也写上：\\n' + ar, session_id:'explain_'+Date.now(), token:webToken()})});
    var d = await r.json(), txt = d.arabic || '（无回复）';
    var lines = txt.split('\\n').filter(function(l){return l.trim();});
    var h = '<div style="background:linear-gradient(150deg,#14503e,#0e3529);border-radius:12px;padding:12px 16px;margin-bottom:12px"><div style="font-family:AmiriNur,SF Arabic,Geeza Pro,serif;font-size:14px;color:#e8d48b;font-weight:700;direction:rtl;text-align:center;line-height:1.8">'+ar+'</div></div>';
    lines.forEach(function(l){
      if(!l.trim()) return;
      h += '<div style="background:#fff;border:1px solid rgba(201,168,76,.15);border-radius:10px;padding:8px 12px;margin-bottom:6px;font-size:12.5px;line-height:1.7">'+esc(l)+'</div>';
    });
    body.innerHTML = h;
  }catch(e){
    body.innerHTML = '<div style="text-align:center;padding:30px;color:#999">⚠️ AI 服务未启动：请先运行 server.py（终端执行 bash run.sh）</div>';
  }
}

// ===== ✨ AI 写文章 =====
async function aiWrite(topic){
  var body = document.getElementById('mLibBody');
  body.innerHTML = '<div style="text-align:center;padding:30px;color:#999">🧞 AI 正在写关于「'+topic+'」的文章...</div>';
  try{
    var r = await fetch(API_BASE() + '/api/chat/message', {method:'POST', headers:{'Content-Type':'application/json'},
      body:JSON.stringify({message:'请用中文写一篇关于「' + topic + '」的阿拉伯语文章。笔法含蓄委婉，善用比喻意象；自然引用《经典选读》文本（阿语+中文）与哲言（注明出处）；尊重包容不同教法学派观点；结构完整，篇幅充实。', session_id:'article_'+Date.now()})});
    var d = await r.json(), txt = d.arabic || '';
    var lines = txt.split('\\n').filter(function(l){return l.trim();});
    var title = '✨ ' + topic;
    var art = {title: title, body: txt, cn: ''};
    ALL_ARTICLES.unshift(art);
    renderLibrary(ALL_ARTICLES);
    openArticle(art);
  }catch(e){
    body.innerHTML = '<div style="text-align:center;padding:30px;color:#999">⚠️ AI 服务未启动：请先运行 server.py（终端执行 bash run.sh）</div>';
  }
}


// ===== 🔔 复习到期提醒条 =====
function showDueBar(){
  try{
    var dc = srsDueCount();
    var done = localStorage.getItem('nur_due_dismiss_' + todayStr2());
    if(dc > 0 && done !== '1'){
      var bar = document.getElementById('dueBar');
      if(bar){
        bar.style.display = 'flex';
        document.getElementById('dueBarTxt').textContent = '📅 今天有 ' + dc + ' 张卡片到期复习（闪卡→间隔复习）';
      }
    }
  }catch(e){}
}
function dismissDueBar(){
  try{ localStorage.setItem('nur_due_dismiss_' + todayStr2(), '1'); }catch(e){}
  var bar = document.getElementById('dueBar');
  if(bar) bar.style.display = 'none';
}

// ===== 学习统计（localStorage）=====
var LEARN_KEY = 'nur_learned';
var DATES_KEY = 'nur_dates';
var MIN_KEY = 'nur_minutes';
var MIN_DAILY_KEY = 'nur_daily_minutes'; // {date: minutes}
function getDailyMins(){
  try{ return JSON.parse(localStorage.getItem(MIN_DAILY_KEY) || '{}'); }catch(e){ return {}; }
}
function addDailyMins(n){
  var m = getDailyMins();
  var t = todayStr2();
  m[t] = (m[t] || 0) + n;
  try{ localStorage.setItem(MIN_DAILY_KEY, JSON.stringify(m)); }catch(e){}
  return m[t];
}
function todayMins(){
  var m = getDailyMins();
  return m[todayStr2()] || 0;
}
var GOAL = 20;
var GOAL_OPTS = [10, 20, 30, 50, 100];
function getGoal(){
  try{ var g = parseInt(localStorage.getItem('nur_goal') || '20', 10); return (GOAL_OPTS.indexOf(g) >= 0) ? g : 20; }catch(e){ return 20; }
}
function cycleGoal(){
  var g = getGoal();
  var i = GOAL_OPTS.indexOf(g);
  var next = GOAL_OPTS[(i + 1) %% GOAL_OPTS.length];
  try{ localStorage.setItem('nur_goal', String(next)); }catch(e){}
  GOAL = next;
  updateStats();
  var bg = document.getElementById('goalBtn');
  if(bg) bg.textContent = '🎯 目标 ' + next + ' 词';
}
function todayStr2(){ var d = new Date(); return d.getFullYear() + '-' + String(d.getMonth()+1).padStart(2,'0') + '-' + String(d.getDate()).padStart(2,'0'); }
function getLearned(){ try{ return JSON.parse(localStorage.getItem(LEARN_KEY) || '[]'); }catch(e){ return []; } }
function getDates(){ try{ return JSON.parse(localStorage.getItem(DATES_KEY) || '[]'); }catch(e){ return []; } }
function calcStreak2(dates){
  if(!dates || !dates.length) return 0;
  var set = {}; dates.forEach(function(d){ set[d] = 1; });
  var streak = 0, cur = new Date();
  if(!set[todayStr2()]) cur.setDate(cur.getDate() - 1);
  while(true){
    var key = cur.getFullYear() + '-' + String(cur.getMonth()+1).padStart(2,'0') + '-' + String(cur.getDate()).padStart(2,'0');
    if(!set[key]) break;
    streak++; cur.setDate(cur.getDate() - 1);
  }
  return streak;
}
function updateStats(){
  var learned = getLearned().length;
  var spn=document.getElementById('studyLearned');if(spn)spn.textContent=learned;var spb=document.getElementById('studyBar');if(spb)spb.style.width=Math.min(100,Math.round(learned/Math.max(getGoal(),1)*100))+'%%';var sps=document.getElementById('studyStreak');if(sps)sps.textContent=calcStreak2(dates);
  var dates = getDates();
  var streak = calcStreak2(dates);
  var mins = todayMins();
  GOAL = getGoal();
  var pct = Math.min(100, Math.round(learned / GOAL * 100));
  var ring = document.querySelector('.ring-txt b');
  if(ring) ring.textContent = pct + '%%';
  var rows = document.querySelectorAll('.daily-info .d-row b');
  if(rows.length >= 3){
    rows[0].textContent = '连续学习 ' + streak + ' 天';
    rows[1].textContent = '今日学习 ' + mins + ' 分钟';
    rows[2].textContent = '今日目标：学习 ' + GOAL + ' 个单词';
  }
  var gt = document.getElementById('goalTxt');
  if(gt) gt.textContent = (pct >= 100) ? '🎉 今日目标达成！' : (learned + ' / ' + GOAL + ' 单词');
  var gb = document.getElementById('goalBar');
  if(gb) gb.style.width = pct + '%%';
  var s1 = document.querySelector('.stat-card .num');
  if(s1) s1.textContent = learned;
  var fb = document.getElementById('flashBadge');
  if(fb){ var dc = srsDueCount(); fb.textContent = dc ? '（' + dc + ' 到期）' : ''; }
  var wbc = document.getElementById('wbCount');
  if(wbc){ var wl = wbLoad(); wbc.textContent = wl.length ? '（' + wl.length + '）' : ''; }
  var bg = document.getElementById('goalBtn');
  if(bg){ GOAL = getGoal(); bg.textContent = '🎯 目标 ' + GOAL + ' 词'; }
  var cb = document.querySelector('.daily-goal .act-btn');
  if(cb && getLearned().indexOf('checkin') >= 0){ cb.textContent = '✅ 已打卡 (+5分钟)'; cb.style.opacity = '.7'; }
  renderMiniChart();
}
// 近 7 天学习柱状图
function renderMiniChart(){
  var box = document.getElementById('miniChart');
  if(!box) return;
  var m = getDailyMins();
  var days = [];
  for(var i = 6; i >= 0; i--){
    var d = new Date();
    d.setDate(d.getDate() - i);
    var key = d.getFullYear() + '-' + String(d.getMonth()+1).padStart(2,'0') + '-' + String(d.getDate()).padStart(2,'0');
    days.push({ key: key, min: m[key] || 0, wd: '日一二三四五六'[d.getDay()] });
  }
  var max = Math.max(10, Math.max.apply(null, days.map(function(x){ return x.min; })));
  var html = '<div style="font-size:11px;font-weight:700;color:#0f3d31;margin:10px 0 6px">📈 近 7 天学习</div>' +
    '<div style="display:flex;align-items:flex-end;gap:6px;height:64px">';
  days.forEach(function(x){
    var h = Math.max(3, Math.round(x.min / max * 54));
    html += '<div style="flex:1;display:flex;flex-direction:column;align-items:center;justify-content:flex-end">' +
      '<span style="font-size:10.5px;color:#89909a">' + (x.min > 0 ? x.min : '') + '</span>' +
      '<div style="width:70%%;height:' + h + 'px;border-radius:3px;background:' + (x.min > 0 ? 'linear-gradient(180deg,#e8d48b,#c9a84c)' : 'rgba(201,168,76,.15)') + '"></div>' +
      '<span style="font-size:10.5px;color:#89909a;margin-top:3px">' + x.wd + '</span></div>';
  });
  html += '</div>';
  box.innerHTML = html;
}
function checkIn(){
  var today = todayStr2();
  var dates = getDates();
  if(dates.indexOf(today) < 0){ dates.push(today); localStorage.setItem(DATES_KEY, JSON.stringify(dates)); }
  var learned = getLearned();
  if(learned.indexOf('checkin') < 0){ learned.push('checkin'); localStorage.setItem(LEARN_KEY, JSON.stringify(learned)); }
  addDailyMins(5);
  var total = parseInt(localStorage.getItem(MIN_KEY) || '0', 10) + 5;
  localStorage.setItem(MIN_KEY, String(total));
  updateStats();
  var btn = document.querySelector('.daily-goal .act-btn');
  if(btn){ btn.textContent = '✅ 已打卡 (+5分钟)'; btn.style.opacity = '.7'; }
}


// ===== 每日文本/名言：点击切换 =====
var CQ_LAST = -1;
function applyDailySentence(payload){
  var item = payload && payload.item ? payload.item : payload;
  if(!item || !item.a) return false;
  var ar = document.getElementById('qAr'), cn = document.getElementById('qCn'), src = document.getElementById('qSrc');
  if(ar) ar.textContent = item.a || '';
  if(cn) cn.textContent = item.c || item.e || '';
  if(src) src.textContent = '🕯 今日一句' + (payload && payload.date ? ' · ' + payload.date : '');
  return true;
}
function builtinQuoteFallback(){
  var pool = BUILTIN_QUOTES || [];
  if(!pool.length) return;
  var i = Math.floor(Math.random() * pool.length);
  if(i === CQ_LAST && pool.length > 1){ i = (i + 1) %% pool.length; }
  CQ_LAST = i;
  var q = pool[i];
  var ar = document.getElementById('qAr'), cn = document.getElementById('qCn'), src = document.getElementById('qSrc');
  if(ar) ar.textContent = q.a || '';
  if(cn) cn.textContent = q.z || '';
  if(src) src.textContent = '🕯 ' + (q.src || '');
}
function loadDailySentence(withFallback){
  return fetch(API_BASE() + '/api/sentences/daily', {cache:'no-store'}).then(function(r){
    if(!r.ok) throw new Error('daily sentence HTTP ' + r.status);
    return r.json();
  }).then(function(d){
    if(!applyDailySentence(d)) throw new Error('daily sentence empty');
    return d;
  }).catch(function(){
    if(withFallback) builtinQuoteFallback();
    return null;
  });
}
function nextQuote(){ return loadDailySentence(true); }
// ===== 服务器状态检测 =====
function checkServer(){
  var el = document.getElementById('serverStatus');
  if(!el) return;
  loadDailySentence(true).then(function(d){
    if(d){ el.textContent = '🟢 AI 服务在线'; el.className = 'srv-on'; }
    else{ el.textContent = '🔴 AI 服务未启动'; el.className = 'srv-off'; }
  });
}

// 文本按段落拆分渲染（阿语右对齐 / 中文两端对齐）
function renderParas(text, cls){
  var parts = String(text || '').split('\\n');
  var h = '';
  parts.forEach(function(p){
    p = p.trim();
    if(p) h += '<p class="'+cls+'">' + p + '</p>';
  });
  return h;
}
function openArticle(a){
  document.getElementById('mReadTitle').textContent = a.title;
  var body = document.getElementById('mReadBody');
  var ab = a.body.replace(/&/g,'&amp;').replace(/'/g,'&#39;').replace(/"/g,'&quot;');
  body.innerHTML = '<div style="background:linear-gradient(150deg,#14503e,#0e3529);border-radius:16px;padding:22px 20px;color:#fff;margin-bottom:14px">'+
    renderParas(a.body, 'book-para') +
    '</div>'+
    (a.cn ? '<div style="background:#fff;border:1px solid rgba(201,168,76,.15);border-radius:14px;padding:18px">'+
    '<div style="font-size:11px;color:#999;margin-bottom:8px">🇨🇳 中文翻译</div>'+
    renderParas(a.cn, 'book-para-cn') +
    '</div>' : '')+
    '<div style="display:flex;gap:8px;margin-top:12px">'+
    '<button class="act-btn" style="flex:1" onclick="ap(this,0,&#39;'+ab+'&#39;)">🔊 朗读全文</button>'+
    '</div>';
  openModal('mRead');
}

function exportData(){

  var a = document.createElement('a');
  a.href = '/data/data.json'; a.download = 'arabic_data.json';
  document.body.appendChild(a); a.click(); a.remove();
}

// ===== v3.2 弹窗交互与无障碍增强：Esc 关闭 / 点遮罩关闭 / 滚动锁定 / 焦点管理 =====
(function(){
  var _open = openModal, _close = closeModal, _lastFocus = null;
  function lock(){
    if(document.querySelector('.modal.show')) document.body.classList.add('modal-open');
    else document.body.classList.remove('modal-open');
  }
  openModal = function(id){
    _lastFocus = document.activeElement;
    _open(id);
    var el = document.getElementById(id);
    if(el){
      el.setAttribute('role','dialog'); el.setAttribute('aria-modal','true');
      var c = el.querySelector('.m-close');
      if(c){ c.setAttribute('aria-label','关闭'); try{ c.focus({preventScroll:true}); }catch(e){} }
    }
    lock();
  };
  closeModal = function(id){
    _close(id);
    lock();
    if(!document.querySelector('.modal.show')){
      try{ if(_lastFocus && _lastFocus.focus) _lastFocus.focus({preventScroll:true}); }catch(e){}
    }
  };
  function focusables(m){
    return m.querySelectorAll('a[href],button:not([disabled]),input:not([disabled]),select,textarea,[tabindex]:not([tabindex="-1"])');
  }
  document.addEventListener('keydown', function(e){
    var mods = document.querySelectorAll('.modal.show');
    if(e.key === 'Escape' || e.keyCode === 27){
      if(mods.length){ e.preventDefault(); _close(mods[mods.length-1].id); lock(); return; }
      var ap = document.getElementById('ep');
      if(ap && ap.classList.contains('o') && typeof ec === 'function'){ e.preventDefault(); ec(); }
      return;
    }
    if(e.key !== 'Tab' || !mods.length) return;
    var m = mods[mods.length-1], f = focusables(m);
    if(!f.length) return;
    var first = f[0], last = f[f.length-1];
    if(e.shiftKey && (document.activeElement === first || !m.contains(document.activeElement))){ e.preventDefault(); last.focus(); }
    else if(!e.shiftKey && document.activeElement === last){ e.preventDefault(); first.focus(); }
  });
  document.addEventListener('click', function(e){
    var t = e.target;
    if(t && t.classList && t.classList.contains('modal') && t.classList.contains('show')){ _close(t.id); lock(); }
  }, true);
})();

// ===== v4.1 回到顶部浮动按钮 =====
(function(){
  var b = document.createElement('button');
  b.id = 'toTop'; b.type = 'button'; b.title = '回到顶部';
  b.setAttribute('aria-label','回到顶部');
  b.textContent = '\u2191';
  var rm = window.matchMedia && matchMedia('(prefers-reduced-motion:reduce)').matches;
  b.onclick = function(){ window.scrollTo({top:0, behavior: rm ? 'auto' : 'smooth'}); };
  document.body.appendChild(b);
  window.addEventListener('scroll', function(){
    var y = window.scrollY || document.documentElement.scrollTop || 0;
    b.classList.toggle('show', y > 600);
  }, {passive:true});
})();

"""

# ---------- 组装 HTML ----------

# ── 构建时把纸感主题内联进 HTML（绕开 Cloudflare 静态缓存）──
try:
    CSS = CSS + open('data/paper-v3.css', encoding='utf-8').read()
except Exception as _eTHEME:
    print('[主题CSS读取失败]', _eTHEME)

try:
    pass  # mobile.css 已回滚（手机排版乱了，先撤）
except Exception as _eMB:
    print('[移动层读取失败]', _eMB)

# ── 内联移动端顶栏 JS（绕开 CDN 缓存）──
try:
    _mbjs = open('data/mb-v1.js', encoding='utf-8').read()
except Exception:
    _mbjs = ''
# MBAR_INLINE
try:
    CSS = CSS + open('data/ai-mobile.css', encoding='utf-8').read()
    CSS = CSS + open('data/mobile2.css', encoding='utf-8').read()
    CSS = CSS + open('data/ai-view.css', encoding='utf-8').read()
    CSS = CSS + open('data/order-fix.css', encoding='utf-8').read()
    CSS = CSS + open('data/contrast-fix.css', encoding='utf-8').read()  # 对比度修复层（2026-09-22，纯视觉）
    pass  # dual.css 已回滚（用户反馈布局乱了，2026-09-21）
    pass  # ai-page.css 暂缓（入口 JS 未生效，避免 AI 进不去）
    pass  # mobile3.css 已回滚（用户反馈布局乱了，2026-09-21）
except Exception as _eAI:
    print('[AI移动层失败]', _eAI)
try:
    _aijs = open('data/ai-v1.js', encoding='utf-8').read()
except Exception:
    _aijs = ''
try:
    _mb2 = open('data/mb-v1.js', encoding='utf-8').read()
except Exception:
    _mb2 = ''
try:
    _aip = open('data/ai-page.js', encoding='utf-8').read()
except Exception:
    _aip = ''
try:
    _rtv = open('data/realtime-voice.js', encoding='utf-8').read()
except Exception:
    _rtv = ''

try:
    _nvoice = open('data/natural-voice.js', encoding='utf-8').read()
except Exception:
    _nvoice = ''
try:
    _page_analysis_js = open('data/page-analysis.js', encoding='utf-8').read()
except Exception:
    _page_analysis_js = ''
try:
    _islamic_lib_js = open('data/islamic-library.js', encoding='utf-8').read()
except Exception:
    _islamic_lib_js = ''
try:
    _audio_lib_js = open('data/audio-library.js', encoding='utf-8').read()
    _audio_lib_css = open('data/audio-library.css', encoding='utf-8').read()
except Exception:
    _audio_lib_js = ''
    _audio_lib_css = ''


# 底部导航改成 5 列（新增诺尔老师）
if _audio_lib_css:
    CSS += '\n' + _audio_lib_css
CSS = CSS + '.tabbar{grid-template-columns:repeat(5,minmax(0,1fr))!important}'
CSS = CSS + r'''
/* ===== 去 AI 化学习首页：词典、发音、练习优先 ===== */
#page-home #aiSec{display:none!important}
.nour-welcome-title{font-size:29px;font-weight:800;letter-spacing:-.7px;color:#0b0b0c;line-height:1.3}
.nour-welcome-sub{max-width:560px;margin:8px auto 0;color:#6e6e73;font-size:13.5px;line-height:1.85}
.native-quick-row{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin:18px auto 4px;max-width:620px}
.native-quick{display:flex;flex-direction:column;gap:4px;align-items:flex-start;text-align:left;padding:14px 15px;border:1px solid #e3e3e8;border-radius:16px;background:#fff;color:#1d1d1f;cursor:pointer;box-shadow:0 5px 18px rgba(15,61,49,.06);transition:transform .2s ease,box-shadow .2s ease,border-color .2s ease}
.native-quick:hover{transform:translateY(-2px);border-color:#a8c9b3;box-shadow:0 10px 24px rgba(15,81,50,.12)}
.native-quick.primary{background:#0f5132;border-color:#0f5132;color:#fff}
.native-quick b{font-size:14px;line-height:1.3}.native-quick small{font-size:11px;color:#86868b}.native-quick.primary small{color:rgba(255,255,255,.72)}
.dict-loading,.dict-listening,.dict-empty{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:8px;min-height:160px;text-align:center;color:#6e6e73;font-size:13px;line-height:1.8}
.dict-loading i,.dict-listening i{width:28px;height:28px;border:3px solid #dfece2;border-top-color:#0f5132;border-radius:50%;animation:dictspin .8s linear infinite}
.dict-listening i{border-color:#f0dfb0;border-top-color:#a8613a;box-shadow:0 0 0 8px rgba(200,162,74,.10)}
@keyframes dictspin{to{transform:rotate(360deg)}}
.dict-definition{background:linear-gradient(135deg,#f7f3e9,#fff);border:1px solid #e4decd;border-radius:18px;padding:16px;margin-bottom:14px;box-shadow:0 8px 24px rgba(15,61,49,.06)}
.dict-definition-top{display:flex;align-items:center;justify-content:space-between;gap:12px}.dict-word-ar{font-family:var(--ar-font);font-size:32px;line-height:1.3;color:#0f5132}.dict-word-meta{font-size:11px;color:#8e8e93;margin-top:3px}.dict-cn{font-size:20px;font-weight:800;color:#1d1d1f;margin-top:10px}.dict-en{font-size:12px;color:#6e6e73;margin-top:4px}.dict-play,.dict-mini-play{border:1px solid #d5e3d8;background:#fff;color:#0f5132;border-radius:12px;padding:9px 12px;cursor:pointer;font-size:18px}.dict-play.is-speaking,.dict-mini-play.is-speaking{background:#0f5132;color:#fff}.dict-section-title{font-size:12px;font-weight:800;color:#0f5132;margin:16px 0 8px}.dict-chips{display:flex;flex-wrap:wrap;gap:8px}.dict-chips button{display:flex;align-items:baseline;gap:7px;border:1px solid #e2e5e3;background:#fff;border-radius:999px;padding:8px 12px;color:#0f5132;cursor:pointer}.dict-chips b{font-family:var(--ar-font);font-size:16px}.dict-chips span{font-size:11px;color:#6e6e73}.dict-examples article{position:relative;background:#fff;border:1px solid #ececef;border-radius:14px;padding:12px 44px 12px 14px;margin-bottom:8px}.dict-ex-ar{font-family:var(--ar-font);font-size:18px;line-height:1.8}.dict-ex-cn{font-size:12px;color:#6e6e73;line-height:1.6;margin-top:4px}.dict-mini-play{position:absolute;right:10px;top:12px;padding:6px 8px;font-size:14px}.dict-source{font-size:10.5px;color:#8e8e93;line-height:1.6;margin-top:12px}.dict-source a{color:#0a84ff}.dict-noexact{background:#fff8e8;border:1px solid #efdfb8;border-radius:12px;padding:12px;color:#806326;font-size:12px;line-height:1.7}.dict-external{border-top:1px solid #ececef;margin-top:16px;padding-top:2px}.dict-external-text{background:#f7f7f9;border-radius:12px;padding:12px;font-size:12px;line-height:1.8;color:#48484a;max-height:240px;overflow:auto}.rd-wordbox{max-width:560px!important;border-radius:20px!important;box-shadow:0 18px 60px rgba(0,0,0,.22)!important}.rd-word-result{max-height:58vh;overflow:auto}.rd-wordbox .dict-definition{margin-top:8px}.rd-wordbox .dict-source{margin-bottom:8px}
@media(max-width:560px){.native-quick-row{grid-template-columns:1fr;max-width:340px}.native-quick{align-items:flex-start;padding:13px 15px}.nour-welcome-title{font-size:24px}.dict-word-ar{font-size:28px}}
'''

html = (
    '<!DOCTYPE html>\n<html lang="zh-CN" data-theme="light">\n<head>\n<meta charset="UTF-8">\n'
    '<meta name="viewport" content="width=device-width,initial-scale=1.0,maximum-scale=1.0,viewport-fit=cover">\n'
    '<meta name="theme-color" content="#0f3d31">\n'
    '<meta name="description" content="燃灯同学 · 阿拉伯学习平台：句子库、词汇、语法课、听力训练、口语陪练、阿拉伯语阅读、AI 老师——用手机学阿语">\n'
    '<meta name="apple-mobile-web-app-capable" content="yes">\n'
    '<meta name="mobile-web-app-capable" content="yes">\n'
    '<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">\n'
    '<meta name="apple-mobile-web-app-title" content="燃灯者">\n'
    '<meta name="keywords" content="学习阿拉伯语,阿拉伯语学习,阿语入门,阿语语法,阿语听力,阿语翻译,燃灯者,حامل المصباح">\n'
    '<meta name="author" content="燃灯者">\n'
    '<meta property="og:type" content="website">\n'
    '<meta property="og:site_name" content="燃灯同学 · 阿拉伯学习平台">\n'
    '<meta property="og:title" content="燃灯同学 · 阿拉伯学习平台 App">\n'
    '<meta property="og:description" content="学阿拉伯语就用燃灯者：句子库、词汇、经典选读诵读、哲言、世界书库、中文古籍、听力视频、AI 老师——一部手机学阿语。">\n'
    '<meta property="og:url" content="https://xn--dqry4os3s3gb.com/">\n'
    '<meta property="og:image" content="https://xn--dqry4os3s3gb.com/icon-512.png">\n'
    '<meta name="twitter:card" content="summary_large_image">\n'
    '<link rel="canonical" href="https://xn--dqry4os3s3gb.com/">\n'
    '<link rel="icon" href="icon-192.png">\n'
    '<link rel="manifest" href="manifest.webmanifest">\n'
    '<link rel="apple-touch-icon" href="icon-192.png">\n'
    '<title>燃灯同学 · 阿拉伯学习平台</title>\n<style>\n' + CSS + '</style>\n'
    '<script>(function(){try{var t=localStorage.getItem("nur_theme2")||"auto";var d=(t==="dark")||(t==="auto"&&window.matchMedia&&window.matchMedia("(prefers-color-scheme: dark)").matches);if(d)document.documentElement.setAttribute("data-theme","dark");}catch(e){}})();</script>\n'
    '</head>\n<body>\n'
    '<div class="page" id="page-home">'
    '<div id="splash"><div class="sp-lamp"></div>'
    '<div class="sp-ar">نور</div>'
    '<div class="sp-cn">燃 灯 者</div>'
    '<div class="sp-bar"><i></i></div></div>\n'
    '<div class="bg-pattern"></div>\n'
)

# Header
html += (
    '<header class="hdr">'
    '<div class="glow"></div>'
    '<div class="arch-wrap"><div class="arch"></div></div>'
    '<div class="logo">نور</div>'
    ''
    ''
    '<div class="logo-sub">Nour · 阿拉伯语学习</div>'
    '<span class="zh">صامتٌ لكنّه يهدي إلى الطريق</span>'
    '<div style="display:flex;gap:10px;justify-content:center;align-items:center;margin-top:14px;position:relative;z-index:5">' '' '<button id="langBtn" class="lang-btn" onclick="toggleLang()">中文</button>' '</div>\n'
    '</header>\n'
)

# 顶部搜索（苹果图书：搜索独立但常驻顶部）
html += (
    "<style>.donbar{overflow:hidden;white-space:nowrap;background:linear-gradient(90deg,#0f5132,#1d7a4f,#0f5132);color:#f6e7b4;font-size:13px;font-weight:700;padding:10px 0;cursor:pointer;margin:6px 0}"
    ".donbar-in{display:inline-block;padding-left:100%;animation:donmarq 24s linear infinite}"
    "@keyframes donmarq{0%{transform:translateX(0)}100%{transform:translateX(-100%)}}"
    "html[data-theme=\\'dark\\'] .donbar{background:linear-gradient(90deg,#0b2f24,#155c3c,#0b2f24)}"
    "</style>"
    "<div class='donbar' onclick='openDonate()' title='点击支持网站'><div class='donbar-in'>💖 本站由个人自费维护（服务器 · 域名 · AI 全部自掏腰包）· 所有捐款全部用于网站运营与维护 · 感谢每一份心意 · جزاك الله خيرا 💖 点我支持 ｜ 版本 BUILDVER</div></div>"
    '<div class="tk-hero" style="max-width:720px;margin:16px auto 4px;padding:0 18px;text-align:center">'
    '<div class="nour-welcome-title">今天，从一个阿拉伯语单词开始</div>'
    '<div class="nour-welcome-sub">查词、听清发音、读例句，所有基础学习工具都可直接使用，不必先打开 AI。</div>'
    '<div class="native-quick-row">'
    '<button type="button" class="native-quick primary" onclick="openDict()"><b>🔎 查一个词</b><small>释义 · 例句 · 朗读</small></button>'
    '<button type="button" class="native-quick" onclick="showListen()"><b>🔊 听一遍</b><small>阿语原生发音</small></button>'
    '<button type="button" class="native-quick" onclick="showChallenge()"><b>✍️ 练一题</b><small>词汇 · 拼句</small></button>'
    '</div></div>'
    '<section class="vision-cards" aria-label="快速入口">\n<button class="vision-card" type="button" onclick="nav(\'learn\')" aria-label="打开世界图书馆"><span class="vc-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v17H6.5A2.5 2.5 0 0 0 4 22.5z"/><path d="M4 5.5v17M8 7h8M8 11h8M8 15h6"/></svg></span><span class="vc-copy"><strong>世界图书馆</strong><small>典籍、历史与中文古籍</small></span><span class="vc-arrow" aria-hidden="true">›</span></button>\n<button class="vision-card" type="button" onclick="showListen()" aria-label="打开阿拉伯语听读练习"><span class="vc-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M12 3a3 3 0 0 0-3 3v6a3 3 0 0 0 6 0V6a3 3 0 0 0-3-3Z"/><path d="M6 11a6 6 0 0 0 12 0M12 17v4m-4 0h8"/></svg></span><span class="vc-copy"><strong>阿拉伯语口语</strong><small>听读练习与日常表达</small></span><span class="vc-arrow" aria-hidden="true">›</span></button>\n</section>'
    '<div style="max-width:880px;margin:14px auto 6px;padding:0 16px">'
    '<div class="tk-dict" onclick="openDict()" style="background:linear-gradient(135deg,#0f5132,#1d7a4f 60%,#2f9d68);border-radius:18px;padding:16px 18px;box-shadow:0 10px 26px rgba(15,81,50,.28);cursor:pointer;color:#fff">'
    '<div style="display:flex;align-items:center;gap:10px">'
    '<div style="font-size:38px">📖</div>'
    '<div style="flex:1">'
    '<div style="font-size:21px;font-weight:900;letter-spacing:.8px">查阿拉伯语单词</div>'
    '<div style="font-size:13.5px;opacity:.95;margin-top:5px;line-height:1.6">输入阿语 → 中文释义 · 词根 · <b>近义词</b> · <b>反义词</b> · <b>同类词</b> · 例句</div>'
    '</div>'
    '<div style="background:#f6e7b4;color:#0f5132;font-weight:900;font-size:16px;padding:12px 20px;border-radius:999px;white-space:nowrap">开始查 ›</div>'
    '</div></div></div>'
    '<div class="lib-search"><span>🔍</span><input id="libQ" placeholder="搜索句子、词汇、文本、哲言…（回车）" onkeydown="if(event.key===&#39;Enter&#39;){libSearch(this.value)}"></div><div class="lib-acts" style="max-width:880px;margin:10px auto 0;padding:0 16px;display:flex;gap:8px;flex-wrap:wrap;justify-content:center"><button class="act-btn" style="margin:0" onclick="openSearchAll()">🔎 全站搜索</button><button class="act-btn" style="margin:0;background:#c8a24a;color:#fff;border-color:#c8a24a;font-weight:700" onclick="openDonate()">💖 支持网站</button></div>'
    '<div class="home-stats"><div><b id="hsBooks">—</b> 部世界典籍</div><div><b id="hsHistory">—</b> 部世界史书</div>'
    '<div><b id="hsHadith">—</b> 段哲言</div><div><b id="hsReadable">—</b> 部可读全文</div><div><b>6</b> 课语法</div>'
    '<div style="font-size:11px;color:#a8ada6" id="hsTime"></div></div>'
)
# 应用内音频资料库：从首页直接进入，不跳出网页或切换到其他 App。
html += '<div class="home-audio-entry"><button type="button" onclick="showAudioLibrary()"><span>🎧</span><span><b>音频资料库</b><small>FLAC / WAV 无损 · 宣礼 · 系统/真人发音，直接在网页内播放</small></span><strong>打开 ›</strong></button></div>'

# （顶部胶囊导航已移除：功能入口统一在书架/书库/底部标签）


html += (
    '<div class="daily-quote" id="quote">'
    '<div class="quote-card">'
    '<div class="q-ar" id="qAr">العِلْمُ كَنْزٌ لَا يَفْنَىٰ</div>'
    '<div class="q-cn" id="qCn">知识是永不消逝的宝藏</div>'
    '</div></div>\n'
)
html += '<section class="study-progress" id="studyProgress"><div><span>学习进度</span><b id="studyLearned">0</b><small>已掌握词汇</small></div><div class="study-track"><i id="studyBar"></i></div><div class="study-streak"><b id="studyStreak">0</b><span>天连续学习</span></div></section>'



# 首页内容流（YouTube 风：缩略图卡片网格）
_feed = [
    ('🧭', '开始学习', '句子库 · ' + str(TOTAL_SENT) + ' 句', "openModal('mLearn')", '1', ''),
    ('📜', '哲人哲言', '哲人智慧 · 数万条', 'showH6()', '3', ''),
    ('📐', '语法课', '名词 · 动词 · 句式', 'showGrammar()', '4', ''),
    ('⚡', '闯关练习', '词汇 · 语法 · 拼句挑战', 'showChallenge()', '19', ''),
    ('🎧', '听力跟读', '设备发音 · 每天 10 分钟', 'showListen()', '6', ''),
    ('🃏', '闪卡复习', 'SRS 间隔重复', 'showFlashcard()', '7', '<span id="flashBadge" style="color:#c0392b;font-weight:800"></span>'),
    ('📖', '词汇表', '85,602 词 · 词频排序', 'showVocab()', '8', ''),
    ('🔎', '全部句子', '搜索 18k+ 句子', 'showAllSentences()', '9', ''),
    ('🔤', '字母课', '28 个字母 + 测验', 'showAlphabet()', '12', ''),
    ('📝', '测验', '随机抽题 · 计分', 'showQuiz()', '13', ''),
    ('💬', '日常对话', '30 个场景对话', 'showDialog()', '14', ''),
    ('🗺', '文明图谱', '地图 · 主题 · 年代轴线', "openCiv()", '18', ''),
    ('🎙', '日常口语', '场景对话 · 听说练习', 'showDialog()', '15', ''),
    ('🕌', '每日一句', '五时 · 宣礼提醒', 'showPrayer()', '16', ''),
    ('📚', '伊斯兰图书馆', '古兰经 · 六大部 · 法学 · 经注', 'showIslamicLibrary()', '20', ''),
    ('📕', '生词本', '我的收藏', 'showWordBook()', '17', '<span id="wbCount" style="color:#c0392b;font-weight:800"></span>'),
]
_ICONS = {'1':'assets/imgs/quran2.jpg','3':'assets/imgs/hadith.jpg','4':'assets/imgs/quran.jpg','13':'assets/imgs/calligraphy.jpg','15':'assets/imgs/history.jpg','11':'assets/imgs/china.jpg','8':'assets/imgs/manuscript.jpg','7':'assets/imgs/lantern.jpg'}
_cells = ''.join(
    '<div class="card" onclick="%s"><div class="thumb t-%s">%s<span>%s</span></div>'
    '<div class="cbody"><b>%s</b><span>%s%s</span></div></div>' % (act, k, ('<img class="card-img" loading="lazy" src="' + _ICONS.get(k, '') + '" onerror="this.remove()">' if _ICONS.get(k) else ''), ic, tt, sb, extra)
    for (ic, tt, sb, act, k, extra) in _feed)
html += (
    '<div class="hero"><div class="hero-tx">' +
    '<b>燃灯同学 · 阿拉伯学习平台</b>' +
    '<span>已收录 23,835 部世界典籍 · 8,465 部世界史书 · 哲人哲言 40,875 段（均带译文与注释）· 13,185 部可全文阅读</span>' +
    '<em onclick="openLib()">进入图书馆 ›</em></div>' +
    '<div class="hero-art">📚</div></div>'
    '<div id="homeShelves"></div>'
    '<div class="sec-title"><h2>全部内容</h2></div>'
    '<div class="feed" id="learnSec">' + _cells + '</div>'
)

# 分类标题 + 导航
html += (
    '<div class="modal" id="mLearn"><div class="m-head"><span>📚</span><b>学习工作台</b><button class="m-close" onclick="closeModal(\'mLearn\')">✕</button></div><div class="m-body">'
    '<section class="study-workspace-intro" aria-label="今日学习概览">'
    '<div class="study-workspace-copy"><small>今日学习 · 学习工作台</small><h2>从一句真实阿语开始</h2><p>先读原句，再按需要打开语法、词汇、闪卡或跟读；下方句子库和筛选仍保持原路径。</p></div>'
    '<div class="study-workspace-metrics"><div><b id="studyWorkspaceLearned">0</b><span>已掌握词汇</span></div><div><b id="studyWorkspaceStreak">0</b><span>连续学习天数</span></div></div>'
    '<div class="study-workspace-actions"><button type="button" onclick="showGrammar()">语法与词形</button><button type="button" onclick="showVocab()">词汇复习</button><button type="button" onclick="showFlashcard()">闪卡</button><button type="button" onclick="showListen()">听力跟读</button></div>'
    '</section>'
    '<div class="cat-scroll">' + TABS_HTML + '</div>\n'
)

# 句子列表
html += (
    '<div class="list-wrap" style="margin-top:0">'
    '<div class="list-head"><span class="tt" id="listCount">全部 · ' + str(TOTAL_SENT) + ' 句（每类显示前25句）</span></div>' +
    '<div style="display:flex;gap:6px;padding:8px 16px 0;flex-wrap:wrap">' +
    '<button class="s-btn flt on" data-flt="all" style="width:auto;padding:4px 10px;font-size:10px" onclick="setFilter(&#39;all&#39;)">全部</button>' +
    '<button class="s-btn flt" data-flt="learned" style="width:auto;padding:4px 10px;font-size:10px" onclick="setFilter(&#39;learned&#39;)">✅ 已学</button>' +
    '<button class="s-btn flt" data-flt="fav" style="width:auto;padding:4px 10px;font-size:10px" onclick="setFilter(&#39;fav&#39;)">⭐ 收藏</button>' +
    '<button class="s-btn flt" data-flt="review" style="width:auto;padding:4px 10px;font-size:10px" onclick="setFilter(&#39;review&#39;)">📌 复习中</button>' +
    '</div>'
    '<div id="sList">' + ALL_CARDS + '</div>'
    '</div>'
    '</div></div>\n'
)



# AI 智伴（努尔老师）
html += (
    '<section class="ps-ai" id="aiSec">'
    '<div class="ps-ai-card">'
    '<div class="ps-ai-head"><div class="ps-ai-head-l"><div class="ps-ai-avatar"></div><span>努尔老师 · نور</span><span id="aiQuota" style="font-size:11px;color:#8a8f88;margin-left:8px;cursor:pointer" onclick="openPay()" title="点击充值/开通"></span></div><span class="ps-en">写文章·翻译·解经·问答</span><button id="aiVoiceToggle" class="ai-voice-toggle" type="button" onclick="nourToggleAutoVoice()" aria-pressed="false">🔈 人声：关</button></div>'
    '<button class="nour-close" type="button" onclick="closeNourVoice()" aria-label="结束语音对话">完成</button>'
    '<div class="ps-ai-msgs" id="homeAI"><div class="ps-ai-msg bot">السلام عليكم ورحمة الله! السلام عليكم！我是你的阿拉伯语老师「努尔」（نور）。你可以让我陪你练习对话、翻译阿语、解释课文，或者一起解决学习中的问题。</div></div>'
    '<div class="ps-ai-chips" id="homeAIChips"></div>'
    '<div class="ps-ai-input"><div class="home-ai-compose"><textarea id="homeAIIn" rows="1" autocomplete="off" spellcheck="true" aria-label="阿拉伯语学习问题" placeholder="写下你想练习的内容…" oninput="homeAIInputState(this)" onkeydown="homeAIKeydown(event)"></textarea><div class="home-ai-tools"><button type="button" class="home-ai-mode on" id="homeAIFast" onclick="homeAIToggleFast()" title="直接回答，速度更快">快答</button><span class="home-ai-hint">回车发送 · Shift+回车换行</span><span class="home-ai-count" id="homeAICount">就绪</span></div></div><button class="ps-mic" id="homeMic" onclick="homeAIVoice()" title="开始语音练习" aria-label="开始语音练习">🎙</button><button id="homeAISendBtn" class="home-ai-send" onclick="homeAISend()" aria-label="发送问题">发送</button></div>'
    '</div></section>'
)

# 底部导航
html += (
    '<div class="modal" id="mTalk"><div class="m-head"><span>🎙</span><b>阿语口语陪练 · محادثة</b><button class="m-close" onclick="closeModal(\'mTalk\')">✕</button></div><div class="m-body" id="mTalkBody"></div></div>'
    '</div>'
    '<!-- 模态框 --><div class="modal" id="mReader"><div class="m-head"><button class="m-back" onclick="closeModal(\'mReader\')">‹ 返回</button><b id="mReaderTitle">阅读</b><span style="width:52px"></span></div><div class="m-body" id="mReaderBody"></div></div>'
    '<div class="modal" id="mH6"><div class="m-head"><span>📜</span><b>哲人哲言</b><button class="m-close" onclick="closeModal(\'mH6\')">✕</button></div><div class="m-body" id="mH6Body"></div></div>'
    '<div class="page library-page" id="mCat" style="display:none"><div class="m-head"><span>◎</span><b>世界图书馆</b><button class="library-back" onclick="nav(\'home\')">首页</button></div><div class="m-body" id="mCatBody"></div></div>'
    '<div class="modal" id="mSentences"><div class="m-head"><span>📖</span><b>全部句子</b><button class="m-close" onclick="closeModal(\'mSentences\')">✕</button></div><div class="m-search"><input id="mSentSearch" placeholder="🔍 搜索句子..." oninput="renderAllS()"></div><div class="m-body" id="mSentBody"></div><div class="m-count" id="mSentCount"></div></div>'
    "<div class='modal' id='mDict'><div class='m-head' style='padding:16px 18px'><span style='font-size:24px'>📖</span><b style='font-size:19px'>阿语词典 · قاموس</b><button class='m-close' onclick=\"closeModal('mDict')\">✕</button></div>"
    "<div class='m-search' style='gap:10px;padding:12px 16px'><input id='dictQ' placeholder='输入阿拉伯语单词（也可输入中文）' style='font-size:19px;font-weight:700;padding:16px 18px;border-radius:14px;border:2px solid #d9d1bc' onkeydown=\"if(event.key==='Enter')dictSearch()\"><button class='s-btn' style='width:auto;padding:16px 18px;font-size:20px;font-weight:800;border-radius:14px' onclick='dictVoice()' title='语音输入（说阿语）'>🎤</button><button class='s-btn' style='width:auto;padding:16px 22px;font-size:17px;font-weight:800;border-radius:14px' onclick='dictSearch()'>查词</button></div>"
    "<div class='m-body' id='dictBody' style='padding:16px'>"
    "<div style='text-align:center;padding:18px 6px 8px'>"
    "<div style='font-size:46px;line-height:1'>📖</div>"
    "<div style='font-size:16px;font-weight:800;color:#0f5132;margin-top:10px'>输入阿语单词，查中文意思</div>"
    "<div style='font-size:12.5px;color:#8a8f88;margin-top:6px;line-height:1.8'>同时给出 <b>词根</b> · <b>近义词</b> · <b>反义词</b> · <b>同类词</b> · <b>例句</b></div>"
    "<div style='font-size:12px;color:#a8ada6;margin:16px 0 8px'>试试这些词 👇</div>"
    "<div style='display:flex;gap:8px;justify-content:center;flex-wrap:wrap'>"
    "<span onclick=\"dictTry('كِتَاب')\" style='padding:10px 16px;background:#fff;border:1px solid #e0d8c4;border-radius:999px;font-family:var(--ar-font);font-size:18px;color:#0f5132;cursor:pointer;box-shadow:0 2px 8px rgba(15,81,50,.06)'>كِتَاب</span>"
    "<span onclick=\"dictTry('مَاء')\" style='padding:10px 16px;background:#fff;border:1px solid #e0d8c4;border-radius:999px;font-family:var(--ar-font);font-size:18px;color:#0f5132;cursor:pointer;box-shadow:0 2px 8px rgba(15,81,50,.06)'>مَاء</span>"
    "<span onclick=\"dictTry('ذَهَبَ')\" style='padding:10px 16px;background:#fff;border:1px solid #e0d8c4;border-radius:999px;font-family:var(--ar-font);font-size:18px;color:#0f5132;cursor:pointer;box-shadow:0 2px 8px rgba(15,81,50,.06)'>ذَهَبَ</span>"
    "<span onclick=\"dictTry('كَبِير')\" style='padding:10px 16px;background:#fff;border:1px solid #e0d8c4;border-radius:999px;font-family:var(--ar-font);font-size:18px;color:#0f5132;cursor:pointer;box-shadow:0 2px 8px rgba(15,81,50,.06)'>كَبِير</span>"
    "</div></div></div></div>"
    "<div class='modal' id='mGrammar'><div class='m-head'><span>📐</span><b id='mGramHead'>语法课</b><button class='m-close' onclick=\"closeModal('mGrammar')\">✕</button></div><div class='m-body' id='mGramBody' style='padding:14px'></div></div>"
    "<div class='modal' id='mBelt'><div class='m-head'><span>\U0001F4F0</span><b>一带一路 · 中阿合作</b><button class='m-close' onclick=\"closeModal('mBelt')\">\u2715</button></div><div class='m-body' id='mBeltBody' style='padding:14px'></div></div>"
    "<div class='modal' id='mDonate'><div class='m-head'><span>❤️</span><b>支持燃灯者</b><button class='m-close' onclick=\"closeModal('mDonate')\">✕</button></div><div class='m-body' style='padding:18px;text-align:center'>"
    "<div style='font-size:13px;color:#5a6159;line-height:2'>这个网站是<b>个人自费</b>在维护（服务器 · 域名 · AI）。<br>你的心意会变成 <b>AI 额度</b>，让灯继续亮着 🕯<br><br>如果它帮到了你，欢迎用一份心意<br>让它继续亮下去 🕯</div>"
    "<div id='donAmts' style='display:flex;gap:8px;justify-content:center;flex-wrap:wrap;margin:18px 0'></div>"
    "<button onclick='donShowQr()' style='width:100%;max-width:300px;padding:13px;background:#c8a24a;color:#fff;font-weight:800;font-size:15px;border:0;border-radius:12px;cursor:pointer'>💳 扫码支持</button>"
    "<div id='donQrBox' style='display:none;margin-top:16px'></div>"
    "<div style='margin-top:16px;font-size:11px;color:#a8ada6'>支持全凭自愿，感谢每一份心意 \u00b7 جزاك الله خيرا</div>"
    "</div></div>"
    '<style>body.locked .page,body.locked .tabbar{display:none!important}body.locked{overflow:hidden}</style>'
    "<div id='mLock' style='position:fixed;inset:0;z-index:12000;display:none;flex-direction:column;align-items:center;justify-content:center;padding:26px;background:linear-gradient(165deg,#fbf8f1,#efe7d5);text-align:center'>"
    "<div style='font-size:46px;line-height:1'>🪔</div>"
    "<div style='font-size:26px;font-weight:800;color:#0f5132;margin-top:10px'>燃灯者</div>"
    "<div style='font-family:var(--ar-font);font-size:20px;color:#8a7f72;margin-top:2px'>حامل المصباح</div>"
    "<div style='font-size:13px;color:#5a6159;margin:18px 0 16px;max-width:300px;line-height:1.7'>燃灯同学 · 阿拉伯学习平台<br><span style='font-size:11px;color:#9aa09a'>付费进入后，全部内容与 AI 都免费</span></div>"
    "<input id='lockCode' type='hidden' value=''>"
    "<div id='lockMsg' style='margin-top:12px;font-size:13px;color:#b4553a;min-height:20px;max-width:320px;line-height:1.6'></div>"
    "<div style='margin-top:18px;font-size:12px;color:#8a8f88'>付费后即可进入 👇</div>"
    "<div style='margin-top:2px;font-size:11px;color:#a8ada6'>（随缘支持 · 不想支持就点「免费进入」✓）</div>"
    "<button onclick='lockContact()' style='margin-top:8px;width:100%;max-width:320px;padding:13px;font-size:15px;font-weight:800;color:#fff;background:#c8a24a;border:0;border-radius:14px;cursor:pointer'>🙋 我想拥有这款学习平台</button>"
        "<div style='margin-top:14px;width:100%;max-width:320px;border-top:1px dashed #e5decc;padding-top:12px'>"
    "<input id='entryCode' type='hidden' value=''><div id='entryMsg' style='display:none'></div>"
    "<div id='lockPayBox' style='display:none;margin-top:14px;width:100%;max-width:320px;background:#fff;border:1px solid #e5decc;border-radius:14px;padding:14px;text-align:center'>"
    "<div style='font-size:12px;color:#5a6159;line-height:1.8;margin-bottom:8px'>本站由站长个人自费维护（服务器 · 域名 · AI 接口 每月都要花钱）<br>免费试用：<b>查词 200 次</b> · 书库 / 句子 / 听力 随便用<br>想无限用：<b>会员 ¥15/月</b> · <b>永久卡 ¥299</b> · 加微信 <b>YsuF0202</b></div>"
    "<div style='font-size:12px;color:#b4553a;margin-bottom:6px'>请如实填写你实际付了多少钱（会员费自愿支持 · 最低 ¥10）</div>"
    "<input id='lockAmtIn' type='number' min='1' step='1' placeholder='我付了 ___ 元' style='width:100%;box-sizing:border-box;padding:13px;border:2px solid #d9d1bc;border-radius:12px;text-align:center;font-size:16px;font-weight:700;margin-bottom:10px'>"
    "<img id='lockQr' src='data/pay_qr.png?v=3' style='display:none;max-width:200px;border-radius:10px;border:1px solid #eee7d8' onerror=\"this.style.display='none';document.getElementById('lockQrTip').style.display=''\">"
    "<div id='lockQrTip' style='display:none;font-size:11px;color:#a8ada6'>收款码加载失败，请联系管理员</div>"
    "<button id='lockShowBtn' onclick='lockShowQr()' style='width:100%;margin-top:6px;padding:13px;background:#c8a24a;color:#fff;font-weight:800;font-size:15px;border:0;border-radius:12px;cursor:pointer'>📷 点这里显示收款码</button>"
    "<div id='lockPayRest' style='display:none'>"
    "<input id='lockPayNote' placeholder='付款备注（选填，如你的微信号）' style='width:100%;box-sizing:border-box;margin-top:10px;padding:10px;border:1px solid #d9d1bc;border-radius:10px;font-size:13px'>"
    "<button onclick='lockClaim()' style='width:100%;margin-top:8px;padding:12px;background:#0f5132;color:#fff;font-weight:800;font-size:14px;border:0;border-radius:12px;cursor:pointer'>✅ 我已付款</button>"
    "<div id='lockPayMsg' style='margin-top:8px;font-size:12px;color:#5a6159;min-height:16px'></div>"
    "</div>"
    "</div>"
    "<div style='margin-top:28px;font-size:11px;color:#a8ada6'>设备码 <b id='lockDev'>—</b> · <span onclick='copyDev()' style='color:#0f5132;text-decoration:underline;cursor:pointer'>复制</span></div>"
    "<div style='margin-top:6px;font-size:11px;color:#a8ada6'>燃灯同学 · 阿拉伯学习平台</div>"
    '</div>'
    "<div class='modal' id='mDonate'><div class='m-head'><span>❤️</span><b>支持燃灯者</b><button class='m-close' onclick=\"closeModal('mDonate')\">✕</button></div>"
    "<div class='m-body' style='padding:18px;text-align:center'>"
    "<div style='font-size:13px;color:#5a6159;line-height:2'>这个网站是<b>个人自费</b>在维护：<br>服务器 · 域名 · AI 费用，全部自捐腰包。<br><b>所有捐款全部用于网站运营与维护</b> 🕯<br><br>如果它帮到了你，欢迎用一份心意<br>让它继续亮下去。</div>"
    "<div id='donAmts' style='display:flex;gap:8px;justify-content:center;flex-wrap:wrap;margin:18px 0'></div>"
    "<button onclick='donShowQr()' style='width:100%;max-width:300px;padding:13px;background:#c8a24a;color:#fff;font-weight:800;font-size:15px;border:0;border-radius:12px;cursor:pointer'>💳 扫码支持</button>"
    "<div id='donQrBox' style='display:none;margin-top:16px'></div>"
    "<div style='margin-top:16px;font-size:11px;color:#a8ada6'>支持全凭自愿，感谢每一份心意 · جزاك الله خيرا</div>"
    "</div></div>"
    "<div class='modal' id='mVid'><div class='m-head'><span>🎬</span><b>阿语听力 · 视频</b><button class='m-close' onclick=\"closeModal('mVid')\">✕</button></div>"
    "<div id='vidPlay' style='display:none;background:#111'></div>"
    "<div class='m-search' id='vidCats' style='flex-wrap:wrap;gap:6px'></div>"
    "<input id='vidQ' placeholder='🔍 搜索视频标题 / 频道...' oninput='vidFilter()' style='margin:0 12px 8px;width:calc(100% - 24px);padding:10px 12px;border:1px solid #e5decc;border-radius:10px;box-sizing:border-box'>"
    "<div class='m-body' id='vidBody'></div></div>"
    "<div class='modal' id='mSearch'><div class='m-head'><span>🔎</span><b>全站搜索</b><button class='m-close' onclick=\"closeModal('mSearch')\">✕</button></div>"
    "<div class='m-search'><input id='sq' placeholder='搜索句子 / 词汇 / 哲言 / 经典选读 / 书库…' onkeydown=\"if(event.key==='Enter')doSearchAll()\"><button class='s-btn' style='width:auto;padding:8px 14px' onclick='doSearchAll()'>搜索</button></div>"
    "<div class='m-body' id='sRes' style='padding:8px 12px'></div></div>"
    "<div class='modal' id='mPay'><div class='m-head'><span>💳</span><b>开通会员 / 充值</b><button class='m-close' onclick=\"closeModal('mPay')\">✕</button></div>"
    "<div class='m-body' style='padding:14px'>"
    "<div id='payMine' style='background:#f7f3e9;border:1px solid #e5decc;border-radius:12px;padding:12px;margin-bottom:12px;font-size:13px;color:#12735a'>加载中…</div>"
    "<div id='payPlans'></div>"
    "<div style='font-size:12px;color:#5a6159;margin:10px 0 6px'>① 选择付款金额（<b>到账 AI 额度 = 付款额 × 50%</b>，例：付 ¥30 → 到账 ¥15）</div>"
    "<div id='payAmt' style='display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px'></div>"
    "<div style='font-size:12px;color:#5a6159;margin:10px 0 6px'>或：用<b>激活码 / 充值码</b>直接兑换（一个码只能用一次）</div>"
    "<div style='display:flex;gap:8px'><input id='payCode' placeholder='XXXX-XXXX-XXXX' style='flex:1;padding:12px;border:2px solid #d9d1bc;border-radius:12px;font-family:ui-monospace,monospace;text-align:center' onkeydown=\"if(event.key==='Enter')redeemCode()\"><button class='s-btn' style='width:auto;padding:12px 16px;background:#0f5132;color:#fff;font-weight:700;border:0;border-radius:12px' onclick='redeemCode()'>兑换</button></div>"
    "<div id='payMsg' style='margin-top:10px;font-size:13px;min-height:18px'></div>"
    "<div id='payQr' style='margin-top:14px;text-align:center'></div>"
    "<div style='margin-top:14px;border-top:1px dashed #e5decc;padding-top:12px'>"
    "<div style='font-size:13px;color:#12735a;font-weight:700;margin-bottom:6px'>③ 已付款？点下面按钮通知管理员开通</div>"
    "<input id='payNote' placeholder='付款备注（可填你的微信号 / 订单号，选填）' style='width:100%;padding:10px;border:1px solid #d9d1bc;border-radius:10px;font-size:13px;margin-bottom:8px'>"
    "<button onclick='claimPaid()' style='width:100%;padding:13px;background:#c8a24a;color:#fff;font-weight:800;font-size:15px;border:0;border-radius:12px;cursor:pointer'>✅ 我已付款，通知开通</button>"
    "<div id='payMsg2' style='margin-top:8px;font-size:13px;min-height:18px'></div>"
    "</div>"
    "</div></div>"
    '<div class="modal" id="mInstall"><div class="m-head"><span>📲</span><b>安装到手机 / 电脑</b><button class="m-close" onclick="closeModal(\'mInstall\')">✕</button></div><div class="m-body" style="padding:14px"><div style="background:#f7f3e9;border:1px solid #e5decc;border-radius:12px;padding:12px;margin-bottom:10px"><b>📱 iPhone / iPad</b><div style="font-size:12px;color:#12735a;line-height:1.8;margin-top:4px">用 <b>Safari</b> 打开本页 → 点底部「分享」⬆️ → 选「<b>添加到主屏幕</b>」→ 完成。桌面出现「燃灯者」图标，点开即全屏 App。</div></div><div style="background:#f7f3e9;border:1px solid #e5decc;border-radius:12px;padding:12px;margin-bottom:10px"><b>🤖 安卓</b><div style="font-size:12px;color:#12735a;line-height:1.8;margin-top:4px">用 <b>Chrome</b> 打开本页 → 点右上角「⋮」→ 选「<b>安装应用 / 添加到主屏幕</b>」→ 确认。</div></div><div style="background:#f7f3e9;border:1px solid #e5decc;border-radius:12px;padding:12px;margin-bottom:10px"><b>💻 电脑</b><div style="font-size:12px;color:#12735a;line-height:1.8;margin-top:4px">Chrome / Edge 打开后，地址栏右侧会出现「安装」图标，点一下即变成独立窗口应用。</div></div><div style="background:#0f5132;color:#f6e7b4;border-radius:12px;padding:12px;text-align:center"><div style="font-size:11px;opacity:.8">分享给别人 · شارك التطبيق</div><div style="font-size:15px;font-weight:700;margin-top:4px">https://燃灯同学.com</div></div></div></div>'
    '<div class="modal" id="mVocab"><div class="m-head"><span>📚</span><b>词汇表</b><button class="m-close" onclick="closeModal(\'mVocab\')">✕</button></div><div class="m-search"><input id="mVocabSearch" placeholder="🔍 搜索词汇..." oninput="renderVocab()"></div><div class="m-body" id="mVocabBody"></div><div class="m-count" id="mVocabCount"></div></div>'
'<div class="modal" id="mLibrary"><div class="m-head"><span>📚</span><b>图书馆 · 阿拉伯语文章</b><button class="m-close" onclick="closeModal(\'mLibrary\')">✕</button></div>' + '<div class="m-search" style="gap:6px;flex-wrap:wrap"><span style="font-size:10px;color:#999;white-space:nowrap">✨ AI 写文章:</span><button class="s-btn" style="width:auto;padding:4px 10px" onclick="aiWrite(\'القهوة\')">☕ 咖啡</button><button class="s-btn" style="width:auto;padding:4px 10px" onclick="aiWrite(\'رمضان\')">✈️ 旅行</button><button class="s-btn" style="width:auto;padding:4px 10px" onclick="aiWrite(\'السفر\')">✈️ 旅行</button><button class="s-btn" style="width:auto;padding:4px 10px" onclick="aiWrite(\'القدس\')">🕌 历史古城</button><button class="s-btn" style="width:auto;padding:4px 10px" onclick="aiWrite(\'العلم\')">🔬 科学</button><button class="s-btn" style="width:auto;padding:4px 10px" onclick="aiWrite(\'الربيع\')">🌸 春天</button></div>' + '<div class="m-body" id="mLibBody"></div><div class="m-count" id="mLibCount"></div></div>'
    '<div class="modal" id="mExplain"><div class="m-head"><span>✂️</span><b>单词拆解 · AI 逐词解释</b><button class="m-close" onclick="closeModal(\'mExplain\')">✕</button></div><div class="m-body" id="mExplainBody" style="padding:16px"></div></div>' +
    '<div class="modal" id="mQuran"><div class="m-head"><span>🕌</span><b>经典选读 · 114 章</b><button class="m-close" onclick="closeModal(\'mQuran\')">✕</button></div><div class="m-search"><input id="mQuranSearch" placeholder="🔍 搜索章节..." oninput="renderQuranList()"></div><div class="m-body" id="mQuranBody"></div><div class="m-count" id="mQuranCount"></div></div>' +
    '<div class="modal" id="mFlash"><div class="m-head"><span>🃏</span><b id="mFlashHead">闪卡</b><button class="m-close" onclick="closeModal(\'mFlash\')">✕</button></div><div class="m-body" id="mFlashBody"></div></div>' +
    '<div class="modal" id="mQuiz"><div class="m-head"><span>📝</span><b id="mQuizHead">测验</b><button class="m-close" onclick="closeModal(\'mQuiz\')">✕</button></div><div class="m-body" id="mQuizBody"></div></div>' +
    '<div class="modal" id="mWordBook"><div class="m-head"><span>📕</span><b>生词本</b><button class="m-close" onclick="closeModal(\'mWordBook\')">✕</button></div><div class="m-search"><input id="mWbSearch" placeholder="🔍 搜索生词..." oninput="renderWordBook()"></div><div class="m-body" id="mWordBookBody"></div><div class="m-count" id="mWordBookCount"></div></div>' +
    '<div class="modal" id="mAlphabet"><div class="m-head"><span>🔤</span><b id="mAlphabetHead">字母入门</b><button class="m-close" onclick="closeModal(\'mAlphabet\')">✕</button></div><div class="m-body" id="mAlphabetBody" style="padding:16px"></div></div>' +
    '<div class="modal" id="mListen"><div class="m-head"><span>🎧</span><b id="mListenHead">跟读评测</b><button class="m-close" onclick="closeModal(\'mListen\')">✕</button></div><div class="m-body" id="mListenBody" style="padding:16px"></div></div>' +
    '<div class="modal" id="mTheme"><div class="m-head"><span>◐</span><b>外观设置</b><button class="m-close" onclick="closeModal(\'mTheme\')">✕</button></div><div class="m-body" id="mThemeBody" style="padding:16px"></div></div>' +
    '<div class="modal" id="mChallenge"><div class="m-head"><span>⚡</span><b id="mChallengeHead">阿拉伯语闯关</b><button class="m-close" onclick="closeModal(\'mChallenge\')">✕</button></div><div class="m-body" id="mChallengeBody"></div></div>' +
    '<div class="modal" id="mDialog"><div class="m-head"><span>💬</span><b id="mDialogHead">日常对话</b><button class="m-close" onclick="closeModal(\'mDialog\')">✕</button></div><div class="m-body" id="mDialogBody" style="padding:16px"></div></div>' +
    '<div class="modal" id="mHistory"><div class="m-head"><span>📜</span><b id="mHistoryHead">历史库</b><button class="m-close" onclick="closeModal(\'mHistory\')">✕</button></div><div class="m-body" id="mHistoryBody" style="padding:16px"></div></div>' +
    '<div class="modal" id="mHadith"><div class="m-head"><span>📜</span><b id="mHadithHead">哲言库</b><button class="m-close" onclick="closeModal(\'mHadith\')">✕</button></div><div class="m-body" id="mHadithBody" style="padding:16px"></div></div>' +
    '<div class="modal" id="mPrayer"><div class="m-head"><span>🕌</span><b id="mPrayPrayHead">每日一句</b><button class="m-close" onclick="closeModal(\'mPrayer\')">✕</button></div><div class="m-body" id="mPrayerBody" style="padding:16px"></div></div>' +
    '<div class="modal" id="mLogin"><div class="m-head"><span>🔑</span><b>登录 / 注册</b><button class="m-close" onclick="closeModal(\'mLogin\')">✕</button></div><div class="m-body" style="padding:16px">' +
    '<input id="lUser" placeholder="用户名" style="width:100%;box-sizing:border-box;border:1px solid rgba(201,168,76,.35);border-radius:10px;padding:10px 12px;font-size:13px;margin-bottom:10px;background:#fff">' +
    '<input id="lPass" type="password" placeholder="密码（至少 4 位）" style="width:100%;box-sizing:border-box;border:1px solid rgba(201,168,76,.35);border-radius:10px;padding:10px 12px;font-size:13px;margin-bottom:12px;background:#fff">' +
    '<button class="act-btn" style="width:100%;padding:12px;font-size:14px" onclick="webAuth(\'login\')">🔑 登录</button>' +
    '<button class="act-btn" style="width:100%;padding:12px;font-size:14px;margin-top:8px;background:#fff;color:#0f3d31;border:1px solid rgba(201,168,76,.4)" onclick="webAuth(\'register\')">✨ 注册新账号</button>' +
    '<button class="act-btn" style="width:100%;padding:12px;font-size:14px;margin-top:8px;background:linear-gradient(135deg,#a8892e,#c9a84c);color:#fff;border:none" onclick="webActivate()">👑 输入激活码开通会员</button>' +
    '<div style="font-size:10.5px;color:#999;margin-top:12px;line-height:1.7">普通用户每日 AI 对话 20 次；开通会员无限使用。</div></div></div>' +
    '<div class="modal" id="mMusic"><div class="m-head"><span>🎵</span><b>AI 阿拉伯音乐</b><button class="m-close" onclick="closeModal(\'mMusic\')">✕</button></div><div class="m-body" id="mMusicBody" style="padding:16px"></div></div>' +
    '<div class="modal" id="mImage"><div class="m-head"><span>🖼</span><b>AI 画图</b><button class="m-close" onclick="closeModal(\'mImage\')">✕</button></div><div class="m-body" style="padding:16px">' +
    '<textarea id="imgPrompt" placeholder="描述你想画的画面，例如：暮色中的古城，新月挂在天边，阿拉伯艺术风格，水墨意境" style="width:100%%;box-sizing:border-box;border:1px solid rgba(201,168,76,.35);border-radius:10px;padding:12px;font-size:13px;min-height:70px;background:#fff"></textarea>' +
    '<button class="act-btn" style="width:100%%;padding:12px;font-size:14px;margin-top:10px" onclick="genImage()">🎨 生成图片（约10-30秒）</button>' +
    '<div id="imgStatus" style="font-size:11.5px;color:#a8892e;margin-top:10px;min-height:18px"></div>' +
    '<div id="imgResult" style="margin-top:10px;text-align:center"></div>' +
    '<div style="font-size:10px;color:#8a9c8f;margin-top:10px;line-height:1.7">💡 支持中文描述，越具体越好看。生成后可长按图片保存。</div></div></div>' +
    '<div class="modal" id="mRead"><div class="m-head"><span>📖</span><b id="mReadTitle">文章</b><button class="m-close" onclick="closeModal(\'mRead\')">✕</button></div><div class="m-body" id="mReadBody"></div></div>'
    '</div>'
    '<div class="page" id="page-me" style="display:none">'
    '<div class="pg-h">我的燃灯</div><div class="pg-wrap profile-wrap">'
    '<div id="meBox" class="profile-card"></div>'
    '<section id="profileActivity" class="profile-card profile-activity"></section>'
    '<section class="profile-card profile-settings"><h2>学习与设置</h2>'
    '<button class="profile-link" onclick="updateStats()"><span>学业成就</span><b>›</b></button>'
    '<button class="profile-link" onclick="showThemeSettings()"><span>外观设置</span><b>›</b></button>'
    '<button class="profile-link" onclick="showWordBook()"><span>生词本</span><b>›</b></button>'
    '<button class="profile-link" onclick="showListen()"><span>跟读练习</span><b>›</b></button>'
    '<button class="profile-link" onclick="webLogout()"><span>退出登录</span><b>›</b></button>'
    '</section></div></div>'
    '<div class="page" id="page-search" style="display:none">'
    '<div class="pg-h">查单词 &amp; 句子查询</div><div class="pg-wrap search-wrap">'
    '<label class="search-label" for="sQ">搜索阿拉伯语、中文或书名</label>'
    '<input class="srch-big" id="sQ" placeholder="输入 كلمة 或中文释义…" onkeydown="if(event.key===&#39;Enter&#39;){doSearch()}">'
    '<div class="search-tools"><button onclick="searchTool(&quot;vocab&quot;)">查单词</button><button onclick="searchTool(&quot;analysis&quot;)">句子分析</button><button onclick="searchTool(&quot;translate&quot;)">全文翻译</button></div>'
    '<div class="srch-chips"><button class="chip on" data-s="all" onclick="sPick(this)">全部</button><button class="chip" data-s="sent" onclick="sPick(this)">句子</button><button class="chip" data-s="vocab" onclick="sPick(this)">词汇</button><button class="chip" data-s="quran" onclick="sPick(this)">经典文本</button><button class="chip" data-s="lib" onclick="sPick(this)">藏书</button></div>'
    '<div id="sRes"><div class="srch-tip">输入阿拉伯语或中文，搜索词汇、例句与馆藏。</div></div>'
    '</div></div>'
    '<div class="page" id="page-civ" style="display:none">'
    '<div class="pg-h">世界文明图谱</div>'
    '<div class="pg-wrap" id="civWrap"></div>'
    '</div>'
    '<nav class="tabbar">'
    '<button class="tb on" data-tab="home" onclick="nav(\'home\')"><span class="t-ic"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v17H6.5A2.5 2.5 0 0 0 4 22.5z"/><path d="M4 5.5v17M8 7h8M8 11h8"/></svg></span><span class="t-nm">首页</span></button>'
    '<button class="tb" data-tab="learn" onclick="nav(\'learn\')"><span class="t-ic"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v17H6.5A2.5 2.5 0 0 0 4 22.5z"/><path d="M4 5.5v17M8 7h8M8 11h8M8 15h6"/></svg></span><span class="t-nm">世界图书馆</span></button>'
    '<button class="tb" data-tab="search" onclick="nav(\'search\')"><span class="t-ic"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="10.8" cy="10.8" r="6.3"/><path d="m16 16 4.5 4.5"/></svg></span><span class="t-nm">搜索</span></button>'
    '<button class="tb" data-tab="wordbook" onclick="showWordBook()" aria-label="生词本"><span class="t-ic"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 3.5h12v17l-6-3.5-6 3.5z"/></svg></span><span class="t-nm">生词本</span></button>'
    '<button class="tb" data-tab="me" onclick="nav(\'me\')"><span class="t-ic"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="8" r="3.3"/><path d="M5 21a7 7 0 0 1 14 0"/></svg></span><span class="t-nm">我的</span></button>'
    '</nav>\n'
)


# ===== 内置数据（离线可用：全部句子/词汇表/文章）=====
import re as _re
_bdata = json.load(open(DIR / 'data' / 'categorized.json', encoding='utf-8'))
_bsent = [{'a': it['ar'], 'e': it['en'], 'c': it['cn'], 'cat': it['cat'], 'py': it.get('py', '')} for it in _bdata]
_AR = _re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]+')
_TASH = _re.compile(r'[\u064B-\u0652\u0670\u0640\u06D6-\u06ED]')
_freq = {}
for _it in _bdata:
    for _raw in (_AR.findall(_it['ar']) or []):
        _w = _TASH.sub('', _raw)
        if len(_w) >= 2:
            _freq[_w] = _freq.get(_w, 0) + 1
_bvocab = sorted([{'w': _w, 'f': _n} for _w, _n in _freq.items()], key=lambda x: -x['f'])
_barts = [{'title': _v['title'], 'body': _v['body'], 'cn': _v['cn']} for _v in json.load(open(DIR / 'data' / 'articles.json', encoding='utf-8')).values()]
_bbooks = json.load(open(DIR / 'data' / 'books.json', encoding='utf-8'))
_bquotes = json.loads(open(DIR / 'data' / 'quotes.json', encoding='utf-8').read())
_qf = DIR / 'data' / 'quranData.js'
if not _qf.exists():
    _qf = DIR / 'app' / 'src' / 'quranData.js'
_bquran = json.loads(open(_qf, encoding='utf-8').read().split('module.exports = ')[1].rstrip().rstrip(';'))
_vmf = DIR / 'data' / 'vocab_meanings.json'
if not _vmf.exists():
    _vmf = DIR / 'app' / 'src' / 'vocabData.js'
_bvm_raw = open(_vmf, encoding='utf-8').read()
if 'module.exports = ' in _bvm_raw:
    _bvmean = json.loads(_bvm_raw.split('module.exports = ')[1].rstrip().rstrip(';'))
else:
    _bvmean = json.loads(_bvm_raw)
if isinstance(_bvmean, dict):
    _bvmean = [{'w': k, 'cn': v.get('cn', ''), 'en': v.get('en', '')} for k, v in _bvmean.items()]
_balph = [{'ar': 'ا', 'name': 'أَلِف', 'cn': '艾利夫', 'tr': 'alif', 'forms': ['ا', 'ا', 'ـا', 'ـا'], 'ex': [{'w': 'أَنَا', 'cn': '我'}]}, {'ar': 'ب', 'name': 'بَاء', 'cn': '巴', 'tr': 'ba', 'forms': ['ب', 'بـ', 'ـبـ', 'ـب'], 'ex': [{'w': 'بَيْت', 'cn': '房子'}]}, {'ar': 'ت', 'name': 'تَاء', 'cn': '塔', 'tr': 'ta', 'forms': ['ت', 'تـ', 'ـتـ', 'ـت'], 'ex': [{'w': 'تَفَّاحَة', 'cn': '苹果'}]}, {'ar': 'ث', 'name': 'ثَاء', 'cn': '萨(咬舌)', 'tr': 'tha', 'forms': ['ث', 'ثـ', 'ـثـ', 'ـث'], 'ex': [{'w': 'ثَلَاثَة', 'cn': '三'}]}, {'ar': 'ج', 'name': 'جِيم', 'cn': '吉姆', 'tr': 'jim', 'forms': ['ج', 'جـ', 'ـجـ', 'ـج'], 'ex': [{'w': 'جَمَل', 'cn': '骆驼'}]}, {'ar': 'ح', 'name': 'حَاء', 'cn': '哈(喉)', 'tr': 'ha', 'forms': ['ح', 'حـ', 'ـحـ', 'ـح'], 'ex': [{'w': 'حَبِيب', 'cn': '亲爱的'}]}, {'ar': 'خ', 'name': 'خَاء', 'cn': '哈(小舌)', 'tr': 'kha', 'forms': ['خ', 'خـ', 'ـخـ', 'ـخ'], 'ex': [{'w': 'خُبْز', 'cn': '面包'}]}, {'ar': 'د', 'name': 'دَال', 'cn': '达勒', 'tr': 'dal', 'forms': ['د', 'د', 'ـد', 'ـد'], 'ex': [{'w': 'دَرْس', 'cn': '课程'}]}, {'ar': 'ذ', 'name': 'ذَال', 'cn': '扎勒', 'tr': 'dhal', 'forms': ['ذ', 'ذ', 'ـذ', 'ـذ'], 'ex': [{'w': 'ذَهَب', 'cn': '金子'}]}, {'ar': 'ر', 'name': 'رَاء', 'cn': '拉', 'tr': 'ra', 'forms': ['ر', 'ر', 'ـر', 'ـر'], 'ex': [{'w': 'رَجُل', 'cn': '男人'}]}, {'ar': 'ز', 'name': 'زَاي', 'cn': '扎伊', 'tr': 'zay', 'forms': ['ز', 'ز', 'ـز', 'ـز'], 'ex': [{'w': 'زَهْرَة', 'cn': '花'}]}, {'ar': 'س', 'name': 'سِين', 'cn': '辛', 'tr': 'sin', 'forms': ['س', 'سـ', 'ـسـ', 'ـس'], 'ex': [{'w': 'سَلَام', 'cn': '平安'}]}, {'ar': 'ش', 'name': 'شِين', 'cn': '欣', 'tr': 'shin', 'forms': ['ش', 'شـ', 'ـشـ', 'ـش'], 'ex': [{'w': 'شَمْس', 'cn': '太阳'}]}, {'ar': 'ص', 'name': 'صَاد', 'cn': '萨德', 'tr': 'sad', 'forms': ['ص', 'صـ', 'ـصـ', 'ـص'], 'ex': [{'w': 'صَبَاح', 'cn': '早晨'}]}, {'ar': 'ض', 'name': 'ضَاد', 'cn': '达德', 'tr': 'dad', 'forms': ['ض', 'ضـ', 'ـضـ', 'ـض'], 'ex': [{'w': 'ضَوْء', 'cn': '光'}]}, {'ar': 'ط', 'name': 'طَاء', 'cn': '塔(重)', 'tr': 'ta', 'forms': ['ط', 'طـ', 'ـطـ', 'ـط'], 'ex': [{'w': 'طَعَام', 'cn': '食物'}]}, {'ar': 'ظ', 'name': 'ظَاء', 'cn': '扎(重)', 'tr': 'za', 'forms': ['ظ', 'ظـ', 'ـظـ', 'ـظ'], 'ex': [{'w': 'ظَرْف', 'cn': '信封'}]}, {'ar': 'ع', 'name': 'عَيْن', 'cn': '艾因', 'tr': 'ayn', 'forms': ['ع', 'عـ', 'ـعـ', 'ـع'], 'ex': [{'w': 'عَيْن', 'cn': '眼睛'}]}, {'ar': 'غ', 'name': 'غَيْن', 'cn': '盖因', 'tr': 'ghayn', 'forms': ['غ', 'غـ', 'ـغـ', 'ـغ'], 'ex': [{'w': 'غُرْفَة', 'cn': '房间'}]}, {'ar': 'ف', 'name': 'فَاء', 'cn': '法', 'tr': 'fa', 'forms': ['ف', 'فـ', 'ـفـ', 'ـف'], 'ex': [{'w': 'فِيل', 'cn': '大象'}]}, {'ar': 'ق', 'name': 'قَاف', 'cn': '嘎夫', 'tr': 'qaf', 'forms': ['ق', 'قـ', 'ـقـ', 'ـق'], 'ex': [{'w': 'قَلَم', 'cn': '笔'}]}, {'ar': 'ك', 'name': 'كَاف', 'cn': '卡夫', 'tr': 'kaf', 'forms': ['ك', 'كـ', 'ـكـ', 'ـك'], 'ex': [{'w': 'كِتَاب', 'cn': '书'}]}, {'ar': 'ل', 'name': 'لَام', 'cn': '拉姆', 'tr': 'lam', 'forms': ['ل', 'لـ', 'ـلـ', 'ـل'], 'ex': [{'w': 'لَيْل', 'cn': '夜晚'}]}, {'ar': 'م', 'name': 'مِيم', 'cn': '米姆', 'tr': 'mim', 'forms': ['م', 'مـ', 'ـمـ', 'ـم'], 'ex': [{'w': 'مَاء', 'cn': '水'}]}, {'ar': 'ن', 'name': 'نُون', 'cn': '努恩', 'tr': 'nun', 'forms': ['ن', 'نـ', 'ـنـ', 'ـن'], 'ex': [{'w': 'نَجْم', 'cn': '星星'}]}, {'ar': 'ه', 'name': 'هَاء', 'cn': '哈', 'tr': 'ha', 'forms': ['ه', 'هـ', 'ـهـ', 'ـه'], 'ex': [{'w': 'هِلَال', 'cn': '新月'}]}, {'ar': 'و', 'name': 'وَاو', 'cn': '瓦乌', 'tr': 'waw', 'forms': ['و', 'و', 'ـو', 'ـو'], 'ex': [{'w': 'وَرْدَة', 'cn': '玫瑰'}]}, {'ar': 'ي', 'name': 'يَاء', 'cn': '雅', 'tr': 'ya', 'forms': ['ي', 'يـ', 'ـيـ', 'ـي'], 'ex': [{'w': 'يَد', 'cn': '手'}]}]

_bdialog = json.load(open(DIR / 'data' / 'dialogues.json', encoding='utf-8'))
_bhistory = []
_hf = DIR / 'data' / 'history.json'
if _hf.exists():
    _bhistory = json.load(open(_hf, encoding='utf-8'))
_bhadith = []
_hdf = DIR / 'data' / 'hadith_all.json'
if not _hdf.exists():
    _hdf = DIR / 'data' / 'hadith.json'
if _hdf.exists():
    _bhadith = json.load(open(_hdf, encoding='utf-8'))
_btafsir = []
_tsf = DIR / 'data' / 'tafsir.json'
if _tsf.exists():
    _btafsir = json.load(open(_tsf, encoding='utf-8'))
# 大块数据写独立文件（页面秒开，数据并行加载）
# 内容层去宗教化：过滤宗教类句子与词条（用户要求纯语言学习）
_BAD = ("阿拉伯", "学习", "（已移除）", "阿拉伯人", "清真", "典籍", "格言", "朝觐", "斋戒", "先知", "圣人", "经注", "经文", "教法", "宗教", "天使", "末日", "天堂", "地狱", "（已移除）", "使者", "圣门", "圣妻", "主命", "功修")
def _clean(arr):
    out = []
    for x in arr:
        if not isinstance(x, dict):
            out.append(x); continue
        blob = " ".join(str(x.get(k, "")) for k in ("cn", "zh", "en", "ar", "t", "w", "cat_cn", "cat"))
        if any(w in blob for w in _BAD):
            continue
        out.append(x)
    return out
_bdata = _clean(_bdata)
_btafsir = []
_bvocab = [x for x in _bvocab if not any(w in str(x.get("w", "")) for w in ("الله", "محمد", "الإسلام"))]
print("  去宗教化后：句子 %d 条，哲言 %d 条" % (len(_bdata), len(_bhadith)))

for _vn, _vd in [('BUILTIN_SENTENCES', _bsent), ('BUILTIN_BOOKS', _bbooks), ('BUILTIN_QURAN', _bquran), ('BUILTIN_HADITH', _bhadith), ('BUILTIN_VOCAB', _bvocab), ('BUILTIN_HISTORY', _bhistory)]:
    _fn = DIR / 'data' / ('builtin_' + _vn[8:].lower() + '.js')
    _fn.write_text('window.' + _vn + ' = ' + json.dumps(_vd, ensure_ascii=False) + ';\n', encoding='utf-8')
    print('  拆分', _fn.name, '%.1f MB' % (_fn.stat().st_size / 1048576))

try:
    _bgrammar = json.load(open(DIR / 'data' / 'grammar.json', encoding='utf-8'))
except Exception:
    _bgrammar = []
try:
    _bmorph = json.load(open(DIR / 'data' / 'morphology.json', encoding='utf-8'))
except Exception:
    _bmorph = []
BUILTIN_JS = (
    'var BUILTIN_SENTENCES = [];\n'
    'var BUILTIN_VOCAB = [];\n'
    'window.NOUR_ASSET_VERSION = ' + json.dumps(ASSET_VERSION) + ';\n'
    'window.NOUR_DATA_ASSETS = {sentences: \"data/builtin_sentences.js\", books: \"data/builtin_books.js\", quran: \"data/builtin_quran.js\", hadith: \"data/builtin_hadith.js\", vocab: \"data/builtin_vocab.js\", history: \"data/builtin_history.js\"};\n'
    'window.NOUR_DATA_GLOBALS = {sentences: \"BUILTIN_SENTENCES\", books: \"BUILTIN_BOOKS\", quran: \"BUILTIN_QURAN\", hadith: \"BUILTIN_HADITH\", vocab: \"BUILTIN_VOCAB\", history: \"BUILTIN_HISTORY\"};\n'
    'window.NOUR_DATA_PROMISES = window.NOUR_DATA_PROMISES || {};\n'
    'window.NOUR_loadDataAsset = function(kind){\n'
    '  var key = String(kind || \"\");\n'
    '  var globalName = window.NOUR_DATA_GLOBALS[key];\n'
    '  if(globalName && Array.isArray(window[globalName]) && window[globalName].length) return Promise.resolve(window[globalName]);\n'
    '  if(window.NOUR_DATA_PROMISES[key]) return window.NOUR_DATA_PROMISES[key];\n'
    '  var base = window.NOUR_DATA_ASSETS[key];\n'
    '  if(!base) return Promise.reject(new Error(\"unknown data asset\"));\n'
    '  window.NOUR_DATA_PROMISES[key] = new Promise(function(resolve,reject){\n'
    '    var tag = document.createElement(\"script\"); tag.async = true;\n'
    '    tag.src = base + \"?v=\" + encodeURIComponent(window.NOUR_ASSET_VERSION || \"\");\n'
    '    tag.onload = function(){ resolve(globalName ? (window[globalName] || []) : true); };\n'
    '    tag.onerror = function(){ delete window.NOUR_DATA_PROMISES[key]; reject(new Error(\"data asset failed: \" + key)); };\n'
    '    document.head.appendChild(tag);\n'
    '  });\n'
    '  return window.NOUR_DATA_PROMISES[key];\n'
    '};\n'
    'var BUILTIN_ARTICLES = ' + json.dumps(_barts, ensure_ascii=False) + ';\n'
    'var BUILTIN_BOOKS = [];\n'
    'var BUILTIN_QURAN = [];\n'
    'var BUILTIN_VOCAB_MEANINGS = ' + json.dumps(_bvmean, ensure_ascii=False) + ';\n'
    'var BUILTIN_QUOTES = ' + json.dumps(_bquotes, ensure_ascii=False) + ';\n'
    'var BUILTIN_ALPHABET = ' + json.dumps(_balph, ensure_ascii=False) + ';\n'
    'var BUILTIN_DIALOGUES = ' + json.dumps(_bdialog, ensure_ascii=False) + ';\n'
    'var BUILTIN_HISTORY = [];\n'
    'var BUILTIN_HADITH = [];\n'
    'var BUILTIN_TAFSIR = ' + json.dumps(_btafsir, ensure_ascii=False) + ';\n'
    'var BUILTIN_GRAMMAR = ' + json.dumps(_bgrammar, ensure_ascii=False) + ';\n'
    'var BUILTIN_MORPH = ' + json.dumps(_bmorph, ensure_ascii=False) + ';\n'
    'function showInstall(){openModal("mInstall");}\n'
    "function devId(){try{var d=localStorage.getItem('nur_devid');if(!d){d='d'+Math.random().toString(36).slice(2,10)+Date.now().toString(36);localStorage.setItem('nur_devid',d);}return d;}catch(e){return 'nur-dev';}}\n"
    "function lockApp(msg){var L=document.getElementById('mLock');if(!L)return;L.style.display='flex';document.body.classList.add('locked');var e=document.getElementById('lockDev');if(e)e.textContent=devId();var m=document.getElementById('lockMsg');if(m&&msg)m.textContent=msg;}\n"
    "function unlockApp(){var L=document.getElementById('mLock');if(L)L.style.display='none';document.body.classList.remove('locked');setTimeout(refreshQuota,300);setInterval(refreshQuota,120000);}\n"
    "var KIND_CN={sentences:'\U0001F4AC 句子',vocab:'\U0001F4DA 词汇',articles:'\U0001F4DD 文章',dialogues:'\U0001F399 会话',quotes:'\u2728 名言',tafsir:'\U0001F54C 注释',hadith:'\U0001F4DC 哲言',hadith_api:'\U0001F4DC 哲言分类',history:'\U0001F3DB 历史文学',civ:'\U0001F30D 文明图谱',rulers:'\U0001F451 君主',islamic:'\U0001F4D6 书库',books:'\U0001F4D7 精选书'};\n"
    "async function entryUse(){var m=document.getElementById('entryMsg');var c=((document.getElementById('entryCode')||{}).value||'').trim().toUpperCase();if(!c){if(m)m.textContent='请输入凭证';return;}if(m){m.style.color='#5a6159';m.textContent='验证中…';}try{var r=await fetch(API_BASE()+'/api/unlock/use',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({device_id:devId(),code:c})});var d=await r.json();if(d.ok){try{localStorage.setItem('nur_token',d.token);}catch(e){}if(m){m.style.color='#0f5132';m.textContent='✅ '+(d.msg||'解锁成功')+'，正在进入…';}setTimeout(function(){licenseGate();},700);}else if(m){m.style.color='#b4553a';m.textContent='❌ '+(d.msg||'解锁码无效');}}catch(e){if(m){m.style.color='#b4553a';m.textContent='无法连接服务器';}}}\n"
    "var LOCK_AMT=10;function lockPay(){var b=document.getElementById('lockPayBox');if(b)b.style.display='';var q=document.getElementById('lockQr');if(q)q.style.display='none';var r=document.getElementById('lockPayRest');if(r)r.style.display='none';var sb=document.getElementById('lockShowBtn');if(sb)sb.style.display='';var m=document.getElementById('lockPayMsg');if(m)m.textContent='先点下面按钮看收款码';var a=document.getElementById('lockAmtIn');if(a)setTimeout(function(){a.focus();},200);}\n"
    "function lockShowQr(){var q=document.getElementById('lockQr');if(q)q.style.display='';var r=document.getElementById('lockPayRest');if(r)r.style.display='';var sb=document.getElementById('lockShowBtn');if(sb)sb.style.display='none';var m=document.getElementById('lockPayMsg');if(m)m.textContent='扫码付款后，填上金额 → 点「我已付款」';}\n"
    "async function lockClaim(){var m=document.getElementById('lockPayMsg');var n=(document.getElementById('lockPayNote')||{}).value||'';var amt=parseInt(((document.getElementById('lockAmtIn')||{}).value||'').replace(/[^0-9]/g,''),10);if(!amt||amt<1){m.style.color='#b4553a';m.textContent='请先填上你实际付了多少钱';return;}m.style.color='#5a6159';m.textContent='提交中…';try{var r=await fetch(API_BASE()+'/api/pay/claim',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({kind:'sub',device_id:devId(),amount:amt,note:n})});var d=await r.json();if(d.ok){if(d.code){m.style.color='#0f5132';m.textContent='✅ 开通成功！正在进入…';var el=document.getElementById('lockCode');if(el)el.value=d.code;setTimeout(function(){doUnlock();},700);}else{m.style.color='#0f5132';m.textContent='✅ 付款已记录！站长确认到账后，解锁码会自动出现在这里…';lockPoll();}}else{m.style.color='#b4553a';m.textContent='❌ '+(d.msg||'提交失败');}}catch(e){m.style.color='#b4553a';m.textContent='⚠️ 无法连接服务器';}}\n"
    "var LOCK_T=0;function lockPoll(){if(LOCK_T)return;LOCK_T=setInterval(async function(){try{var r=await fetch(API_BASE()+'/api/pay/status?device_id='+encodeURIComponent(devId()));var d=await r.json();var m=document.getElementById('lockPayMsg');var el=document.getElementById('entryCode');if(d&&d.code){clearInterval(LOCK_T);LOCK_T=0;if(el)el.value=d.code;if(m){m.style.color='#0f5132';m.textContent='🔑 站长已确认到账！你的解锁码：'+d.code+'（已自动填入，正在进入…）';}setTimeout(function(){entryUse();},900);}else if(m&&m.textContent.indexOf('等待')<0){m.style.color='#8a6d3b';m.textContent='⏳ 已提交，等待站长确认到账…（确认后自动进入）';}}catch(e){}},6000);}\n"
    "var VID_ALL=[],VID_CAT='',VID_TITLE='';\n"
    "function openVideos(){openModal('mVid');loadVideos('');}\n"
    "async function loadVideos(cat){VID_CAT=cat||'';var b=document.getElementById('vidBody');var c=document.getElementById('vidCats');b.innerHTML='<div style=padding:12px;color:#8a8f88>加载中…</div>';try{var r=await fetch(API_BASE()+'/api/videos'+(VID_CAT?('?cat='+VID_CAT):''));var d=await r.json();if(!d.ok)return;VID_ALL=d.videos||[];if(c)c.innerHTML='<button class=s-btn style=width:auto;padding:6px 12px onclick=loadVideos(\"\")>全部</button>'+(d.cats||[]).map(function(x){return '<button class=s-btn style=width:auto;padding:6px 12px onclick=loadVideos(\"'+x.id+'\")>'+x.icon+' '+x.name+'</button>';}).join('');renderVids();}catch(e){b.innerHTML='<div style=padding:12px;color:#b4553a>加载失败，请重试</div>';}}\n"
    "function vidFilter(){renderVids();}\n"
    "function renderVids(){var b=document.getElementById('vidBody');var q=((document.getElementById('vidQ')||{}).value||'').trim().toLowerCase();var v=VID_ALL.filter(function(x){return !q||((x.t||'')+(x.ch||'')).toLowerCase().indexOf(q)>=0;});if(!v.length){b.innerHTML='<div style=padding:14px;color:#8a8f88>没有找到视频</div>';return;}b.innerHTML='<div style=padding:4px 12px 6px;font-size:12px;color:#8a8f88>共 '+v.length+' 个视频 · 点击播放</div>'+v.map(function(x){return '<div onclick=playVid(this) data-id='+x.id+' data-t='+encodeURIComponent(x.t||'')+' style=display:flex;gap:10px;padding:8px 12px;border-bottom:1px solid #f0ebdd;cursor:pointer>'+'<img loading=lazy src='+API_BASE()+'/api/thumb?id='+x.id+' style=width:118px;height:66px;object-fit:cover;border-radius:8px;background:#efe9dd;flex:0 0 auto>'+'<div style=flex:1;min-width:0><div style=font-size:13px;font-weight:600;line-height:1.35>'+esc(x.t||'')+'</div><div style=font-size:11px;color:#8a8f88;margin-top:3px>'+esc(x.ch||'')+'</div><div style=font-size:11px;color:#0f5132;margin-top:2px>⏱ '+(x.dur||'—')+'</div></div></div>';}).join('');}\n"
    "function playVid(el){var id=el.getAttribute('data-id');var t=decodeURIComponent(el.getAttribute('data-t')||'');var box=document.getElementById('vidPlay');box.style.display='block';box.innerHTML='<div style=display:flex;justify-content:space-between;align-items:center;padding:8px 12px;background:#0f3d31;color:#f6e7b4><b style=font-size:13px>▶ 播放中</b><span style=font-size:12px;cursor:pointer onclick=closeVid()>✕ 收起</span></div>'+'<div style=position:relative;width:100%;padding-top:56.25%;background:#000><iframe src=https://www.youtube.com/embed/'+id+'?autoplay=1&rel=0 style=position:absolute;top:0;left:0;width:100%;height:100%;border:0 allow=autoplay;encrypted-media allowfullscreen></iframe></div>'+'<div style=padding:8px 12px;font-size:11px;color:#8a8f88>若打不开（YouTube 在国内需科学上网）→ <a target=_blank style=color:#0f5132 href=https://search.bilibili.com/all?keyword='+encodeURIComponent(t)+'>去 B 站搜同名</a></div>';box.scrollIntoView?box.scrollIntoView():0;}\n"
    "function closeVid(){var b=document.getElementById('vidPlay');if(b){b.innerHTML='';b.style.display='none';}}\n"
    "var DON_AMT=10;function openDonate(){openModal('mDonate');var b=document.getElementById('donAmts');if(b){b.innerHTML='';[10,20,40,100].forEach(function(v){var x=document.createElement('button');x.textContent='¥'+v;x.style.cssText='padding:11px 18px;border:2px solid #d9d1bc;border-radius:12px;background:#fff;color:#0f5132;font-weight:800;font-size:15px;cursor:pointer';x.onclick=function(){DON_AMT=v;Array.prototype.forEach.call(b.children,function(c){c.style.background='#fff';c.style.color='#0f5132';});x.style.background='#0f5132';x.style.color='#fff';var q=document.getElementById('donQrBox');if(q&&q.style.display!=='none')donShowQr();};b.appendChild(x);});}var q=document.getElementById('donQrBox');if(q){q.style.display='none';q.innerHTML='';}var fb=(b&&b.children&&b.children[0]);if(fb){DON_AMT=parseInt((fb.textContent||'').replace(/[^0-9]/g,''),10)||10;fb.style.background='#0f5132';fb.style.color='#fff';}}\n"
    "function donShowQr(){var q=document.getElementById('donQrBox');if(!q)return;q.style.display='';q.innerHTML='<div style=font-size:13px;color:#12735a;font-weight:700;margin-bottom:8px>扫码支持 ¥'+DON_AMT+'</div><img src=data/pay_qr.png?v=3 style=max-width:230px;border-radius:12px;border:1px solid #eee7d8><div style=margin-top:12px><button onclick=donDone() style=padding:11px 20px;background:#0f5132;color:#fff;font-weight:800;border:0;border-radius:12px;cursor:pointer>\u2705 我已完成支持</button></div><div id=donMsg style=margin-top:10px;font-size:13px;min-height:18px></div>';}\n"
    "async function donDone(){var m=document.getElementById('donMsg');if(m){m.style.color='#5a6159';m.textContent='记录中…';}try{var r=await fetch(API_BASE()+'/api/pay/claim',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({kind:'donate',device_id:devId(),amount:DON_AMT,note:'心意支持'})});var d=await r.json();if(m){m.style.color='#0f5132';m.textContent=(d.auto?'🙏 感谢支持！额度已到账。':'🙏 感谢支持！站长确认后额度会立刻到账。');}refreshQuota();}catch(e){if(m){m.style.color='#b4553a';m.textContent='记录失败，但心意已收到，谢谢！';}}}\n"
    "function openDict(){openModal('mDict');setTimeout(function(){try{if(typeof hsDictInit==='function')hsDictInit();}catch(e){}var i=document.getElementById('dictQ');if(i)i.focus();},260);}\n"
    "function _stripTashkeel(t){var out='';var s=String(t||'');for(var i=0;i<s.length;i++){var c=s.charCodeAt(i);if(c>=0x064B&&c<=0x0652)continue;if(c===0x0670||c===0x0640)continue;out+=s.charAt(i);}return out.trim();}\n"
    "function dictTry(w){var i=document.getElementById('dictQ');if(i)i.value=w;dictSearch();}\n"
    r'''function dictSpeak(text, btn){
  try{
    if(!window.speechSynthesis) return;
    if(window.speechSynthesis.speaking){ window.speechSynthesis.cancel(); return; }
    var u = new SpeechSynthesisUtterance(String(text || ''));
    var vs = window.speechSynthesis.getVoices() || [], pick = null;
    for(var i=0;i<vs.length;i++){ if((vs[i].lang || '').toLowerCase().indexOf('ar') === 0){ pick = vs[i]; break; } }
    u.lang = pick ? pick.lang : 'ar-SA'; if(pick) u.voice = pick; u.rate = .78; u.pitch = 1;
    if(btn){ u.onstart=function(){btn.classList.add('is-speaking');}; u.onend=function(){btn.classList.remove('is-speaking');}; }
    window.speechSynthesis.speak(u);
  }catch(e){}
}
function dictVoice(){
  var b=document.getElementById('dictBody'), SR=window.SpeechRecognition||window.webkitSpeechRecognition;
  if(!SR){ if(b)b.innerHTML='<div class="dict-empty"><b>此浏览器没有语音识别</b><span>请直接输入阿拉伯语单词。朗读按钮仍可使用系统阿语声音。</span></div>'; return; }
  try{
    var r=new SR(); r.lang='ar-SA'; r.interimResults=true; r.maxAlternatives=3;
    if(b)b.innerHTML='<div class="dict-listening"><i></i><b>正在听，请说一个阿拉伯语单词</b><span>说完会自动查词，不会发送给 AI。</span></div>';
    r.onresult=function(e){
      var t=''; for(var i=0;i<e.results.length;i++){ if(e.results[i][0])t+=e.results[i][0].transcript; }
      t=String(t||'').trim(); var inp=document.getElementById('dictQ'); if(inp)inp.value=t;
      if(e.results[e.results.length-1].isFinal && t)dictSearch();
    };
    r.onerror=function(){if(b)b.innerHTML='<div class="dict-empty"><b>没有听清</b><span>请允许麦克风权限，再按一次🎙；也可以手动输入。</span></div>';};
    r.onend=function(){}; r.start();
  }catch(e){if(b)b.innerHTML='<div class="dict-empty"><b>语音输入暂时不可用</b><span>请手动输入阿语单词。</span></div>';}
}
function dictSourceLabel(src){ return '<div class="dict-source">来源：'+esc(src || '燃灯同学本地词库')+' · 非 AI 查询</div>'; }
function dictWordHtml(d, q){
  var m=d && d.meaning || {}, h='', shown=q || (d && d.word) || '';
  if(m.cn || m.en){
    h+='<section class="dict-definition"><div class="dict-definition-top"><div><div class="dict-word-ar" dir="rtl" lang="ar">'+esc(shown)+'</div><div class="dict-word-meta">'+esc(d.normalized || shown)+'</div></div><button class="dict-play" type="button" onclick="dictSpeak(decodeURIComponent(\''+encodeURIComponent(shown)+'\'),this)" aria-label="朗读阿拉伯语">🔊</button></div><div class="dict-cn">'+esc(m.cn || '—')+'</div>'+(m.en?'<div class="dict-en">'+esc(m.en)+'</div>':'')+'</section>';
  } else { h+='<div class="dict-noexact">暂未找到固定释义，下面先给出例句和公开词典补充。</div>'; }
  if(d && d.matches && d.matches.length){ h+='<div class="dict-section-title">相近词形</div><div class="dict-chips">'+d.matches.map(function(x){var w=x.w||'';return '<button type="button" onclick="dictTry(decodeURIComponent(\''+encodeURIComponent(w)+'\'))"><b dir="rtl">'+esc(w)+'</b><span>'+esc(x.cn||x.en||'')+'</span></button>';}).join('')+'</div>'; }
  if(d && d.examples && d.examples.length){ h+='<div class="dict-section-title">例句</div><div class="dict-examples">'+d.examples.map(function(x){var ar=x.ar||'';return '<article><div class="dict-ex-ar" dir="rtl" lang="ar">'+esc(ar)+'</div><div class="dict-ex-cn">'+esc(x.cn||x.en||'')+'</div><button type="button" class="dict-mini-play" onclick="dictSpeak(decodeURIComponent(\''+encodeURIComponent(ar)+'\'),this)">🔊</button></article>';}).join('')+'</div>'; }
  return h || '<div class="dict-empty"><b>暂时没有匹配</b><span>试试输入不带音符的词形，例如 كتاب、سلام、مدرسة。</span></div>';
}
function dictRenderExternal(text, q){
  var b=document.getElementById('dictBody'); if(!b || !text) return;
  var old=document.getElementById('dictExternal'); if(old)old.remove();
  var sec=document.createElement('section'); sec.id='dictExternal'; sec.className='dict-external';
  sec.innerHTML='<div class="dict-section-title">公开词典补充</div><div class="dict-external-text" dir="auto">'+esc(String(text).slice(0,1200))+'</div><div class="dict-source">Arabic Wiktionary · 仅作公开词典来源展示 · <a href="https://ar.wiktionary.org/" target="_blank" rel="noopener">查看原词典</a></div>';
  b.appendChild(sec);
}
function dictSearch(){
  var q=((document.getElementById('dictQ')||{}).value||'').trim(), b=document.getElementById('dictBody');
  if(!b)return; if(!q){b.innerHTML='<div class="dict-empty"><b>请输入一个阿拉伯语单词</b><span>可以带或不带音符，也可以按🎙说出来。</span></div>';return;}
  b.innerHTML='<div class="dict-loading"><i></i><span>正在查本地词典…</span></div>';
  var key=_stripTashkeel(q);
  fetch(API_BASE()+'/api/dict/lookup?w='+encodeURIComponent(key),{cache:'no-store'}).then(function(r){return r.json();}).then(function(d){
    b.innerHTML=dictWordHtml(d,q)+dictSourceLabel(d.source);
    if(!d.found || !((d.meaning||{}).cn)){
      return fetch(API_BASE()+'/api/dict/free?w='+encodeURIComponent(key),{cache:'no-store'}).then(function(r){return r.json();}).then(function(x){if(x&&x.wiki)dictRenderExternal(x.wiki,q);}).catch(function(){});
    }
  }).catch(function(){b.innerHTML='<div class="dict-empty"><b>本地词典暂时不可用</b><span>请检查网络后重试；朗读仍可在设备本地进行。</span></div>';});
}
    '''
    "function openSearchAll(){openModal('mSearch');setTimeout(function(){var i=document.getElementById('sq');if(i)i.focus();},250);}\n"
    "async function doSearchAll(){var q=(document.getElementById('sq').value||'').trim();var b=document.getElementById('sRes');if(q.length<2){b.innerHTML='<div class=\\\'muted\\\' style=\\\'padding:12px\\\'>请输入至少 2 个字</div>';return;}b.innerHTML='<div style=\\\'padding:12px;color:#8a8f88\\\'>搜索中…</div>';try{var r=await fetch(API_BASE()+'/api/search',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({q:q,token:webToken()})});var d=await r.json();renderSearchResults(d,q);}catch(e){b.innerHTML='<div style=\\\'padding:12px;color:#b4553a\\\'>无法连接服务器</div>';}}\n"
    "function renderSearchResults(d,q){var b=document.getElementById('sRes');var items=d.items||[];var h='';if(d.locked){h+='<div style=\\\'background:#fff7e6;border:1px solid #eadfc0;border-radius:10px;padding:10px;margin-bottom:10px;font-size:12px;color:#8a6d3b\\\'>\U0001F512 '+(d.msg||'开通 AI 会员后可搜索全部内容')+' <button class=\\\'s-btn\\\' style=\\\'width:auto;padding:4px 10px;margin-left:6px\\\' onclick=\\\'closeModal(&quot;mSearch&quot;);openPay()\\\'>立即开通</button></div>';}if(!items.length){h+='<div style=\\\'padding:12px;color:#8a8f88\\\'>没有找到「'+esc(q)+'」</div>';b.innerHTML=h;return;}var g={};items.forEach(function(x){(g[x.k]=g[x.k]||[]).push(x);});Object.keys(g).forEach(function(k){h+='<div style=\\\'margin:10px 0 4px;font-size:12px;color:#0f5132;font-weight:700\\\'>'+(KIND_CN[k]||k)+' · '+g[k].length+'</div>';g[k].forEach(function(x){h+='<div style=\\\'background:#fff;border:1px solid #eee7d8;border-radius:10px;padding:10px;margin-bottom:6px\\\'><div style=\\\'font-family:var(--ar-font);font-size:16px\\\'>'+esc(x.ar||'')+'</div><div style=\\\'font-size:12px;color:#5a6159;margin-top:3px\\\'>'+esc(x.zh||'')+'</div></div>';});});b.innerHTML=h;}\n"
    "async function claimPaid(){var m=document.getElementById('payMsg2');var n=(document.getElementById('payNote')||{}).value||'';m.style.color='#5a6159';m.textContent='提交中…';try{var r=await fetch(API_BASE()+'/api/pay/claim',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({token:webToken(),device_id:devId(),amount:PAY_AMT,note:n})});var d=await r.json();if(d.ok){m.style.color='#0f5132';m.textContent='\u2705 '+d.msg+'（一般几分钟内到账）';}else{m.style.color='#b4553a';m.textContent='\u274C '+(d.msg||'提交失败');}}catch(e){m.style.color='#b4553a';m.textContent='\u26A0\uFE0F 无法连接服务器';}}\n"
    "var PAY_AMT=30;function setPayAmt(v){PAY_AMT=v;var b=document.getElementById('payAmt');if(b)Array.prototype.forEach.call(b.children,function(el){var on=(parseFloat(el.textContent.replace(/[^0-9.]/g,''))===v);el.style.background=on?'#0f5132':'#fff';el.style.color=on?'#fff':'#0f5132';el.style.borderColor=on?'#0f5132':'#d9d1bc';});var t=document.getElementById('payRatio');if(t)t.textContent='付 ¥'+v+' → 到账 AI 额度 ¥'+(v*0.5).toFixed(2);}\n"
    "function openPay(){openModal('mPay');loadPayInfo();}\n"
    "async function loadPayInfo(){var m=document.getElementById('payMine');try{var r=await fetch(API_BASE()+'/api/me/usage?token='+encodeURIComponent(webToken()));var d=await r.json();if(d.ok){if(d.quota>0){m.innerHTML='我的 AI 额度：<b>\uFFE5'+(d.used||0).toFixed(3)+'</b> / \uFFE5'+d.quota+'\u3000剩余 <b>\uFFE5'+d.left.toFixed(3)+'</b>'+(d.until?'<br>会员至 '+d.until:'');}else{m.innerHTML='\U0001F513 当前为<b>基础版</b>（尚未开通 AI）<br><span style=font-size:12px;color:#8a8f88>开通会员后可用：AI 老师 · 全站搜索 · 朗读跟读</span>';}}else{m.textContent=d.msg||'未激活';}}catch(e){m.textContent='无法连接服务器';}fetch(API_BASE()+'/api/plans').then(function(r){return r.json()}).then(function(d){if(!d.ok)return;var h='<div style=\\\'font-size:12px;color:#5a6159;margin:4px 0 6px\\\'>套餐（联系管理员购买）</div>';(d.plans||[]).forEach(function(p){h+='<div style=\\\'display:flex;justify-content:space-between;align-items:center;background:#fff;border:1px solid #eee7d8;border-radius:10px;padding:10px;margin-bottom:6px\\\'><div><b>'+p.name+'</b><div style=\\\'font-size:11px;color:#8a8f88\\\'>'+p.days+' 天 · 含 AI 额度 \uFFE5'+p.quota+'</div></div><div style=\\\'color:#0f5132;font-weight:800\\\'>\uFFE5'+p.price+'</div></div>';});var pa=document.getElementById('payAmt');if(pa){var amts=(d.pay&&d.pay.amounts)||[30,60,100];pa.innerHTML='';amts.forEach(function(v){var b=document.createElement('button');b.textContent='¥'+v;b.style.cssText='padding:10px 16px;border:2px solid #d9d1bc;border-radius:12px;background:#fff;color:#0f5132;font-weight:800;font-size:14px;cursor:pointer';b.onclick=function(){setPayAmt(v);};pa.appendChild(b);});var rt=document.createElement('div');rt.id='payRatio';rt.style.cssText='width:100%;font-size:12px;color:#12735a;margin-top:4px';pa.appendChild(rt);setPayAmt(amts[0]);}document.getElementById('payPlans').innerHTML=h;var qr=document.getElementById('payQr');if(d.pay_qr){qr.innerHTML='<div style=\\\'font-size:12px;color:#5a6159;margin-bottom:6px\\\'>扫码付款后联系管理员开通</div><img src=\\\'data/pay_qr.png\\\' style=\\\'max-width:220px;border-radius:10px;border:1px solid #eee7d8\\\'>';}else{qr.innerHTML='<div style=\\\'font-size:12px;color:#a8ada6\\\'>（收款码未设置：把收款码图发给管理员即可显示）</div>';}}).catch(function(){});}\n"
    "async function redeemCode(){var el=document.getElementById('payCode');var c=(el.value||'').trim().toUpperCase().replace(/[^A-Z0-9]/g,'');if(c.length===12)c=c.slice(0,4)+'-'+c.slice(4,8)+'-'+c.slice(8);var m=document.getElementById('payMsg');if(!c){m.style.color='#b4553a';m.textContent='请输入激活码/充值码';return;}m.style.color='#5a6159';m.textContent='验证中…';try{var r=await fetch(API_BASE()+'/api/vip/activate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({code:c,device_id:devId()})});var d=await r.json();if(d.ok){if(d.token){try{localStorage.setItem('nur_token',d.token);}catch(e){}}m.style.color='#0f5132';m.textContent='\u2705 '+(d.msg||'成功');loadPayInfo();refreshQuota();}else{m.style.color='#b4553a';m.textContent='\u274C '+(d.msg||'无效');}}catch(e){m.style.color='#b4553a';m.textContent='\u26A0\uFE0F 无法连接服务器';}}\n"
    "function refreshQuota(){try{var t=webToken();if(!t)return;fetch(API_BASE()+'/api/me/usage?token='+encodeURIComponent(t)).then(function(r){return r.json()}).then(function(d){var e=document.getElementById('aiQuota');if(!e||!d||!d.ok)return;e.textContent='AI 额度 ￥'+(d.paid_left||0).toFixed(2)+((d.paid_left||0)<=1?' ⚠️':'');e.style.display=''}).catch(function(){})}catch(e){}}\n"
    "function copyDev(){try{navigator.clipboard.writeText(devId());var m=document.getElementById('lockMsg');if(m){m.style.color='#0f5132';m.textContent='设备码已复制，发给管理员';}}catch(e){}}\n"
    "async function licenseGate(){\n"
    "  try{\n"
    "    var r=await fetch(API_BASE()+'/api/access/status?device_id='+encodeURIComponent(devId())+'&token='+encodeURIComponent(webToken()));\n"
    "    var st=await r.json();\n"
    "    if(st&&(st.active===true||st.unlocked===true||st.paid===true||((st.days_left||0)>0))){unlockApp();setTimeout(refreshQuota,500);return;}\n"
    "  }catch(e){}\n"
    "  lockApp('🔒 进入需要解锁码 · 自愿支持 · 最低 ¥10 · 付款后联系站长开通（下方按钮可申请）');\n"
    "}\n"
    "async function doUnlock(){var el=document.getElementById('lockCode');var c=(el&&el.value||'').trim().toUpperCase().replace(/[^A-Z0-9]/g,'');if(c.length===12)c=c.slice(0,4)+'-'+c.slice(4,8)+'-'+c.slice(8);if(el)el.value=c;var m=document.getElementById('lockMsg');if(!c){if(m)m.textContent='请输入激活码';return;}if(m){m.style.color='#5a6159';m.textContent='正在验证…';}try{var r=await fetch(API_BASE()+'/api/vip/activate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({code:c,device_id:devId()})});var d=await r.json();if(d.ok){try{if(d.token)localStorage.setItem('nur_token',d.token);localStorage.setItem('nur_username',d.username||'');localStorage.setItem('nur_vip','1');}catch(e){}if(m){m.style.color='#0f5132';m.textContent='✅ '+(d.msg||'激活成功，正在进入…');}setTimeout(function(){location.reload();},800);}else{if(m){m.style.color='#b4553a';m.textContent='❌ '+(d.msg||'激活码无效');}}}catch(e){if(m){m.style.color='#b4553a';m.textContent='⚠️ 无法连接服务器，请稍后重试';}}}\n"
)

# 构建期统计 → data/stats.json（首页实时数据的一部分）
try:
    _stats = {'sentences': len(_bdata), 'vocab': len(_bvocab), 'articles': len(_barts),
              'dialogues': len(_bdialog), 'quran': len(_bquran), 'hadith': len(_bhadith),
              'tafsir': len(_btafsir), 'history_articles': len(_bhistory),
              'quotes': len(_bquotes)}
    json.dump(_stats, open(DIR / 'data' / 'stats.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('OK stats.json:', _stats)
except Exception as _e:
    print('stats.json fail:', _e)

# JS
# 版本信息 footer
from datetime import datetime as _dt
_built = _dt.now().strftime('%Y-%m-%d %H:%M')
footer = (
    '<div class="app-footer" style="text-align:center;padding:18px 16px 80px;font-size:10px;color:#9a9f9c">'
    '<div style="margin-bottom:10px"><button class="act-btn" style="margin:0 4px" onclick="showInstall()">📲 安装到手机</button> <button class="act-btn" style="margin:0 4px" onclick="exportData()">💾 导出备份</button> <label class="act-btn" style="display:inline-block;cursor:pointer;margin:0 4px">📂 导入备份<input type="file" accept=".json" style="display:none" onchange="importData(event)"></label></div>' + '<div id="serverStatus" style="font-weight:700;margin-bottom:4px">··· 检测服务器 ···</div>'
    'حاملُ المِصباح، صامتٌ لكنّه يهدي إلى الطريق · 燃灯者 &nbsp;|&nbsp; v%s &nbsp;|&nbsp; 句子 %d 句 · 词汇 %d 词 · 文章 %d 篇 · 对话 %d 场景 &nbsp;|&nbsp; 构建 %s'
    '</div>'
    % (APP_VERSION, len(_bsent), len(_bvocab), len(_barts), len(_bdialog), _built)
)
html = html.replace('BUILDVER', _built)
html = html.replace('<head>', '<head><script>window.__NUR_BUILD="' + _built + '";</script>', 1)

_hide_old = """<style>
/* 隐藏旧的「全部内容」板块（用户要求：只留干净的分类+封面网格） */
.feed,.sec-title,.shelf-row,.book-row{display:none!important}
</style>"""
html = html.replace('</body>', _hide_old + '</body>', 1)

try:
    _nourjs = open('data/nour-voice-v2.js', encoding='utf-8').read()
except Exception:
    _nourjs = ''
if _nourjs:
    html = html.replace('</body>', '<script>' + _nourjs + '</script></body>', 1)
# NOUR_VOICE_INLINE
pass  # ai-v1.js 已停用（它拦截 scrollTo，导致页面滑不动 ✗）
if _mb2:
    html = html.replace('</body>', '<script>' + _mb2 + '</script></body>', 1)
pass  # ai-page.js 已停用：旧版本会把 #aiSec 搬进弹层，破坏全屏导航。
pass  # 顶栏 JS 已回滚
if _rtv:
    html = html.replace('</body>', '<script>' + _rtv + '</script></body>', 1)
# ── 内联听力合并脚本（绕开 CDN 缓存）──
try:
    html = html.replace('</body>', '<script>' + open('data/merge-listen.js', encoding='utf-8').read() + '</script></body>', 1)
except Exception as _eML:
    print('[听力合并脚本失败]', _eML)
# MERGE_LISTEN done


html = html.replace('<head>', '<head>\n<script>window.__NUR_VER="' + _built + '";</script>', 1)
_guard = ("<script>"
 "window.__NUR_ERR='';"
 "window.onerror=function(m,src,l){window.__NUR_ERR=String(m);try{var b=document.getElementById('nurErrBar');"
 "if(!b){b=document.createElement('div');b.id='nurErrBar';b.style.cssText='position:fixed;top:0;left:0;right:0;z-index:99999;background:#b3261e;color:#fff;font-size:12px;padding:8px 10px;word-break:break-all;line-height:1.6';document.body.appendChild(b);}"
 "b.textContent='⚠️ 页面出错（请把这句话发给管理员）：'+m+' @'+l;}catch(e){}return false;};"
 "setTimeout(function(){try{var s=document.getElementById('splash');if(s&&s.parentNode)s.parentNode.removeChild(s);"
 "try{document.body.classList.remove('locked');}catch(e){}"
 "if(!document.querySelector('.page')&&!window.__NUR_ERR){var d=document.createElement('div');d.style.cssText='position:fixed;bottom:8px;left:8px;right:8px;z-index:99998;background:#0f5132;color:#f6e7b4;font-size:12px;padding:8px;border-radius:10px;text-align:center';d.textContent='若内容没出来，请下拉刷新一次';document.body.appendChild(d);}"
 "}catch(e){}},6000);"
 "</script>")
html = html.replace('<head>', '<head>' + _guard, 1)

html += footer + '<script>\n' + BUILTIN_JS + (JS % json.dumps(CAT_NAMES, ensure_ascii=False)) + '\n</script>\n<script>try{var _sp=document.getElementById("splash");if(_sp){_sp.classList.add("hide");setTimeout(function(){try{if(_sp.parentNode)_sp.parentNode.removeChild(_sp);}catch(e){}},600);}}catch(e){}try{document.body.classList.add("app-in");}catch(e){}try{renderShelves();}catch(e){}try{applyTheme();}catch(e){}try{applyLang();}catch(e){}try{showDueBar();}catch(e){}try{updateStats();}catch(e){}try{renderFavState();}catch(e){}try{checkServer();}catch(e){}try{licenseGate();}catch(e){}try{loadHomeStats();}catch(e){}try{setInterval(loadHomeStats,300000);}catch(e){}</script>\n</body>' + ''.join('<script defer src=\"data/' + _asset + '?v=' + ASSET_VERSION + '\"></script>' for _asset in ['course.js','belt.js','views2.js','contact.js','dictlimit.js','freeentry.js','permlock.js','audiostop.js','reader-plus.js']) + '\n</html>'

# 完整 footer 拼接后再注入：此时 HTML 才真正包含 </body>。
if _rtv:
    html = html.replace('</body>', '<script>' + _rtv + '</script></body>', 1)
if _nvoice:
    html = html.replace('</body>', '<script>' + _nvoice + '</script></body>', 1)
try:
    _elite_ui_js = open('data/elite-ui.js', encoding='utf-8').read()
except Exception as _elite_js_err:
    _elite_ui_js = ''
    print('elite-ui.js 注入失败:', _elite_js_err)
if _elite_ui_js:
    html = html.replace('</body>', '<script>' + _elite_ui_js + '</script></body>', 1)
try:
    _challenge_js = open(DIR / 'data' / 'challenge.js', encoding='utf-8').read()
except Exception as _challenge_js_err:
    _challenge_js = ''
    print('challenge.js 注入失败:', _challenge_js_err)
if _challenge_js:
    html = html.replace('</body>', '<script>' + _challenge_js + '</script></body>', 1)
if _page_analysis_js:
    html = html.replace('</body>', '<script>' + _page_analysis_js + '</script></body>', 1)
if _islamic_lib_js:
    html = html.replace('</body>', '<script>' + _islamic_lib_js + '</script></body>', 1)
if _audio_lib_js:
    html = html.replace('</body>', '<script>' + _audio_lib_js + '</script></body>', 1)
try:
    _product_shell_js_path = DIR / 'data' / 'nour-product-shell.js'
    _product_shell_js = _product_shell_js_path.read_text(encoding='utf-8') if _product_shell_js_path.exists() else ''
except Exception as _product_shell_js_err:
    _product_shell_js = ''
    print('nour-product-shell.js 读取失败:', _product_shell_js_err)
if _product_shell_js:
    html = html.replace('</body>', '<script>' + _product_shell_js + '</script></body>', 1)
# 经典扩展索引：追加发现/路径 UI，不替换旧书库、古兰经或六大部。
try:
    _classic_cur_css = (DIR / 'data' / 'nour-library-curation.css').read_text(encoding='utf-8')
except Exception as _classic_css_err:
    _classic_cur_css = ''
    print('经典索引 CSS 读取失败:', _classic_css_err)
if _classic_cur_css:
    html = html.replace('</head>', '<style id=\"nour-library-curation-css\">' + _classic_cur_css + '</style></head>', 1)
try:
    _classic_cur_js = (DIR / 'data' / 'nour-library-curation.js').read_text(encoding='utf-8')
except Exception as _classic_js_err:
    _classic_cur_js = ''
    print('经典索引 JS 读取失败:', _classic_js_err)
if _classic_cur_js:
    html = html.replace('</body>', '<script>' + _classic_cur_js + '</script></body>', 1)
# NOUR 阅读上下文桥接：把当前书/页/正文传给现有 AI 请求，不替换原请求逻辑。
try:
    _reader_context_js_path = DIR / 'data' / 'nour-reader-context.js'
    _reader_context_js = _reader_context_js_path.read_text(encoding='utf-8') if _reader_context_js_path.exists() else ''
except Exception as _reader_context_js_err:
    _reader_context_js = ''
    print('nour-reader-context.js 读取失败:', _reader_context_js_err)
if _reader_context_js:
    html = html.replace('</body>', '<script>' + _reader_context_js + '</script></body>', 1)
# NOUR 全屏工作区适配：只包装 nav/openModal/closeModal，所有原业务函数继续复用。
try:
    _focus_js_path = DIR / 'data' / 'nour-focus-workspace.js'
    _focus_js = _focus_js_path.read_text(encoding='utf-8') if _focus_js_path.exists() else ''
except Exception as _focus_js_err:
    _focus_js = ''
    print('nour-focus-workspace.js 读取失败:', _focus_js_err)
if _focus_js:
    html = html.replace('</body>', '<script>' + _focus_js + '</script></body>', 1)
# 首页精修 v2：缩短首屏的重复品牌信息，把主要视线留给学习入口。
_home_finish_css = r'''<style id="home-finish-v4">
:root{--vision-bg:#0b1021;--vision-panel:rgba(255,255,255,.075);--vision-panel-strong:rgba(20,34,54,.82);--vision-line:rgba(226,232,240,.15);--vision-text:#f4f1e9;--vision-muted:#a6b0c2;--vision-gold:#e8c96b;--vision-gold-soft:#f4df9b;--vision-emerald:#26b38d;--vision-blue:#89b9df;--vision-radius:20px;--cream:#0b1021;--ink:#f4f1e9;--white:#111a29;--card:#101c2c;--muted:#a6b0c2;--green:#1b8068;--green-d:#125c4b;--green-l:#26b38d;--gold:#cda94f;--gold-l:#f0da91;--gold-d:#a47c28;--line:rgba(226,232,240,.14);--lib-line:rgba(226,232,240,.15);--lib-bg:#0b1021;--ap-bg:#0b1021;--ap-card:#111a29;--ap-text:#f4f1e9;--ap-text2:#a6b0c2}
html,body{min-height:100%;background:#0b1021!important;color:var(--vision-text)!important;color-scheme:dark;font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Helvetica Neue",Arial,sans-serif!important;-webkit-font-smoothing:antialiased}
html[data-theme="light"] body,html[data-theme="dark"] body{background-color:#0b1021!important;background-image:radial-gradient(ellipse 78% 46% at 50% 30%,rgba(14,74,82,.32),transparent 72%),radial-gradient(circle at 12% 78%,rgba(6,79,80,.18),transparent 30%),radial-gradient(circle at 88% 14%,rgba(195,145,45,.10),transparent 25%)!important;color:var(--vision-text)!important}
body{padding-bottom:104px!important;overflow-x:hidden!important;background-image:radial-gradient(ellipse 78% 46% at 50% 30%,rgba(14,74,82,.32),transparent 72%),radial-gradient(circle at 12% 78%,rgba(6,79,80,.18),transparent 30%),radial-gradient(circle at 88% 14%,rgba(195,145,45,.10),transparent 25%)!important}
#page-home{position:relative;isolation:isolate;min-height:100vh;background:transparent!important;color:var(--vision-text)!important}
.bg-pattern{position:fixed!important;inset:0!important;z-index:-1!important;opacity:.24!important;background-image:radial-gradient(circle at 13% 18%,rgba(255,255,255,.8) 0 1px,transparent 1.7px),radial-gradient(circle at 74% 42%,rgba(243,214,139,.7) 0 1px,transparent 1.8px),radial-gradient(circle at 56% 84%,rgba(255,255,255,.55) 0 .8px,transparent 1.8px),radial-gradient(ellipse 60% 40% at 50% 55%,rgba(13,87,73,.12),transparent 72%)!important;background-size:173px 181px,239px 227px,311px 277px,100% 100%!important}
.bg-pattern:before{opacity:.10!important;background-image:url("data:image/svg+xml,%3Csvg width='84' height='84' viewBox='0 0 84 84' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' stroke='%23e8c96b' stroke-opacity='.55' stroke-width='.65'%3E%3Cpath d='M42 2 82 42 42 82 2 42zM42 15 69 42 42 69 15 42zM42 28 56 42 42 56 28 42zM2 42h13m54 0h13M42 2v13m0 54v13'/%3E%3C/g%3E%3C/svg%3E")!important;background-size:84px 84px!important}
/* 品牌栏与首屏舞台 */
#page-home>.hdr{display:block!important;order:1!important;position:relative!important;padding:22px 16px 12px!important;background:transparent!important;text-align:center!important;overflow:visible!important;box-shadow:none!important}
.hdr:before,.hdr .glow,.hdr .arch-wrap{display:none!important;content:none!important}
.hdr .logo{display:block!important;font-family:AmiriNur,SF Arabic,Geeza Pro,serif!important;font-size:27px!important;line-height:1.25!important;letter-spacing:.02em!important;font-weight:700!important;background:linear-gradient(110deg,#fff0bc,#d6ad50 45%,#fff3cb)!important;-webkit-background-clip:text!important;background-clip:text!important;-webkit-text-fill-color:transparent!important;text-shadow:0 0 26px rgba(232,201,107,.26)!important}
.hdr .logo-sub{margin-top:4px!important;color:rgba(238,241,247,.76)!important;font-size:12px!important;letter-spacing:.08em!important}
.hdr .zh{display:none!important}
.hdr>div[style*="display:flex"]{margin-top:11px!important;gap:8px!important}
.hdr .ai-btn,.hdr .lang-btn{min-height:40px!important;padding:8px 14px!important;border:1px solid var(--vision-line)!important;border-radius:999px!important;background:rgba(255,255,255,.07)!important;color:#eff1f6!important;box-shadow:inset 0 1px rgba(255,255,255,.08),0 8px 26px rgba(0,0,0,.18)!important;font-size:13px!important;font-weight:600!important;backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px)}
.donbar,.hero,.home-stats{display:none!important}
#page-home>.tk-hero{order:2!important;position:relative!important;isolation:isolate!important;width:min(1120px,calc(100% - 36px))!important;min-height:475px!important;margin:6px auto 16px!important;padding:28px 24px!important;box-sizing:border-box!important;overflow:hidden!important;text-align:center!important;border:1px solid rgba(228,233,245,.14)!important;border-radius:28px!important;background:radial-gradient(ellipse 78% 70% at 50% 52%,rgba(19,57,69,.43),transparent 72%),linear-gradient(145deg,rgba(16,29,47,.92),rgba(8,16,31,.84))!important;box-shadow:inset 0 1px rgba(255,255,255,.08),0 24px 64px rgba(0,0,0,.27)!important}
.tk-hero:before{content:''!important;position:absolute!important;z-index:0!important;left:50%!important;top:53%!important;width:min(68vw,355px)!important;aspect-ratio:1!important;border-radius:50%!important;transform:translate(-50%,-50%)!important;pointer-events:none!important;background:radial-gradient(circle at 47% 43%,rgba(255,222,137,.42) 0 2%,rgba(243,190,76,.2) 12%,rgba(18,145,113,.18) 31%,rgba(9,22,39,0) 67%),radial-gradient(circle,transparent 57%,rgba(243,208,121,.38) 58%,rgba(255,231,164,.12) 59%,transparent 61%)!important;filter:drop-shadow(0 0 42px rgba(207,158,64,.23))!important;animation:lanternBreathe 4s ease-in-out infinite!important}
.tk-hero:after{content:'نور'!important;position:absolute!important;z-index:0!important;top:53%!important;left:50%!important;width:100%!important;transform:translate(-50%,-50%)!important;pointer-events:none!important;direction:rtl!important;font-family:AmiriNur,SF Arabic,Geeza Pro,serif!important;font-size:clamp(38px,7vw,78px)!important;font-weight:700!important;line-height:1.25!important;white-space:nowrap!important;color:#f3dc9e!important;text-shadow:0 1px 0 #6d5425,0 2px 0 rgba(56,42,17,.7),0 5px 18px rgba(246,202,89,.64),0 0 48px rgba(232,185,66,.52)!important;opacity:.95!important}
@keyframes lanternBreathe{0%,100%{opacity:.82;filter:drop-shadow(0 0 30px rgba(207,158,64,.18));scale:.98}50%{opacity:1;filter:drop-shadow(0 0 48px rgba(232,194,92,.35));scale:1.04}}
.tk-hero>div:first-child{position:absolute!important;z-index:2!important;top:24px!important;left:14px!important;right:14px!important;max-width:none!important;margin:0!important;color:#f6f2e9!important;font-size:clamp(25px,3.4vw,38px)!important;font-weight:650!important;line-height:1.22!important;letter-spacing:-.035em!important;text-align:center!important;text-shadow:0 2px 18px rgba(0,0,0,.35)!important}
.tk-hero>div:nth-child(2){position:absolute!important;z-index:2!important;bottom:88px!important;left:16px!important;right:16px!important;max-width:50ch!important;margin:0 auto!important;color:rgba(226,233,243,.76)!important;font-size:14px!important;line-height:1.8!important;text-align:center!important}
.tk-acts{position:absolute!important;z-index:3!important;left:12px!important;right:12px!important;bottom:23px!important;display:flex!important;justify-content:center!important;gap:10px!important;margin:0!important;flex-wrap:wrap!important}
.tk-acts button,.tk-acts span{min-height:46px!important;display:inline-flex!important;align-items:center!important;justify-content:center!important;padding:10px 18px!important;border:1px solid rgba(236,227,201,.25)!important;border-radius:999px!important;background:rgba(255,255,255,.08)!important;color:#f2eee4!important;font-size:13.5px!important;font-weight:600!important;cursor:pointer!important;box-shadow:inset 0 1px rgba(255,255,255,.09)!important;backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px);transition:transform .2s ease,background .2s ease,box-shadow .2s ease!important}
.tk-acts button:first-child,.tk-acts span:first-child{border-color:rgba(251,220,139,.74)!important;background:linear-gradient(135deg,#f4dc98,#cda84e)!important;color:#172334!important;box-shadow:0 8px 28px rgba(207,166,71,.22),inset 0 1px rgba(255,255,255,.55)!important}
.tk-acts button:hover,.tk-acts span:hover{transform:translateY(-2px)!important;box-shadow:0 10px 30px rgba(205,168,78,.22)!important}
.tk-acts button,.tk-acts span{gap:8px!important}.v-action-icon{width:16px!important;height:16px!important;flex:none!important;stroke:currentColor!important;fill:none!important;stroke-width:1.7!important;stroke-linecap:round!important;stroke-linejoin:round!important}.tabbar .tb .t-ic svg{width:19px!important;height:19px!important;stroke:currentColor!important;fill:none!important;stroke-width:1.55!important;stroke-linecap:round!important;stroke-linejoin:round!important;filter:none!important}
/* 每日语法与词汇两张悬浮玻璃卡 */
#page-home>.vision-cards{order:3!important;display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:12px!important;width:min(900px,calc(100% - 36px))!important;margin:0 auto 18px!important}
.vision-card{min-height:88px!important;display:flex!important;align-items:center!important;gap:13px!important;padding:15px 17px!important;text-align:left!important;border:1px solid rgba(223,231,243,.14)!important;border-radius:18px!important;background:linear-gradient(135deg,rgba(255,255,255,.10),rgba(255,255,255,.045))!important;color:var(--vision-text)!important;box-shadow:inset 0 1px rgba(255,255,255,.09),0 12px 30px rgba(0,0,0,.18)!important;backdrop-filter:blur(22px);-webkit-backdrop-filter:blur(22px);cursor:pointer!important;transition:transform .2s ease,border-color .2s ease,background .2s ease!important}
.vision-card:hover{transform:translateY(-3px)!important;border-color:rgba(236,204,119,.38)!important;background:linear-gradient(135deg,rgba(255,255,255,.13),rgba(255,255,255,.055))!important}
.vc-icon{width:42px!important;height:42px!important;flex:none!important;display:grid!important;place-items:center!important;border:1px solid rgba(237,206,122,.23)!important;border-radius:13px!important;background:rgba(224,186,86,.10)!important;color:var(--vision-gold-soft)!important}
.vc-icon svg{width:21px!important;height:21px!important;stroke:currentColor!important;fill:none!important;stroke-width:1.6!important;stroke-linecap:round!important;stroke-linejoin:round!important}
.vc-copy{display:grid!important;gap:3px!important;min-width:0!important}.vc-copy strong{color:#f5f1e7!important;font-size:14px!important;font-weight:620!important}.vc-copy small{color:var(--vision-muted)!important;font-size:11.5px!important;line-height:1.4!important}.vc-arrow{margin-left:auto!important;color:rgba(241,218,151,.72)!important;font-size:17px!important}
/* 搜索、每日一句与书架 */
#page-home>.lib-search{order:4!important;display:block!important;position:relative!important;width:min(900px,calc(100% - 36px))!important;max-width:900px!important;margin:0 auto 10px!important;padding:0!important}
.lib-search>span{margin:15px 0 0 16px!important;color:#cfb568!important}.lib-search input{height:50px!important;padding-left:44px!important;border:1px solid rgba(227,232,243,.16)!important;border-radius:15px!important;background:rgba(255,255,255,.075)!important;color:#f6f2e9!important;font-size:15px!important;box-shadow:inset 0 1px rgba(255,255,255,.07),0 12px 30px rgba(0,0,0,.16)!important;backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px)}.lib-search input::placeholder{color:rgba(214,221,234,.56)!important}.lib-search input:focus{border-color:rgba(235,204,119,.5)!important;box-shadow:0 0 0 4px rgba(232,201,107,.1),0 14px 32px rgba(0,0,0,.2)!important}
#page-home>.lib-acts{order:4!important;display:flex!important;justify-content:center!important;gap:8px!important;width:min(900px,calc(100% - 36px))!important;max-width:900px!important;margin:0 auto 12px!important;padding:0!important}.lib-acts .act-btn{min-height:40px!important;padding:8px 13px!important;border:1px solid rgba(225,232,244,.14)!important;border-radius:999px!important;background:rgba(255,255,255,.055)!important;color:#e8e9eb!important;font-size:12.5px!important;font-weight:550!important;backdrop-filter:blur(14px)}
#page-home>#quote{order:5!important;width:min(900px,calc(100% - 36px))!important;max-width:900px!important;margin:4px auto 18px!important;padding:0!important}.daily-quote{width:100%!important;max-width:100%!important;margin:0!important;padding:0!important}
html[data-theme="light"] .daily-quote .quote-card,html[data-theme="dark"] .daily-quote .quote-card{position:relative!important;padding:20px 22px!important;border:1px solid rgba(228,234,244,.14)!important;border-radius:18px!important;background:linear-gradient(135deg,rgba(255,255,255,.085),rgba(255,255,255,.035))!important;color:#f2eee6!important;box-shadow:inset 0 1px rgba(255,255,255,.08),0 10px 32px rgba(0,0,0,.16)!important;backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px)}
.daily-quote .quote-card:before{color:rgba(235,203,117,.26)!important}.daily-quote .q-ar{color:#f2d98d!important;text-shadow:0 0 18px rgba(219,182,91,.16)!important}.daily-quote .q-cn{color:rgba(233,237,244,.82)!important}.daily-quote .q-src{color:rgba(231,207,146,.68)!important}.daily-quote .q-switch{color:#e5c675!important}.daily-quote .q-belt{border:1px solid rgba(227,202,133,.13)!important;border-radius:10px!important;background:rgba(239,206,126,.07)!important;color:#e9d18c!important}
#page-home>#homeShelves{order:6!important;width:min(1320px,calc(100% - 36px))!important;max-width:1320px!important;margin:0 auto 36px!important;padding:4px 0 26px!important;border:1px solid rgba(228,234,244,.12)!important;border-radius:24px!important;background:linear-gradient(155deg,rgba(17,30,49,.84),rgba(8,17,32,.74))!important;box-shadow:inset 0 1px rgba(255,255,255,.06),0 24px 60px rgba(0,0,0,.2)!important;overflow:hidden!important;backdrop-filter:blur(22px);-webkit-backdrop-filter:blur(22px)}
#homeShelves .hs-h1,#homeShelves .hs-h2,#homeShelves .hs-dict-btn{display:none!important}#homeShelves .hs-body{display:block!important}
#homeShelves .hs-rail{display:flex!important;flex-direction:row!important;flex-wrap:wrap!important;gap:8px!important;width:100%!important;max-width:100%!important;margin:0!important;padding:18px 22px 15px!important;box-sizing:border-box!important;border:0!important;border-bottom:1px solid rgba(230,234,242,.09)!important;background:transparent!important}
#homeShelves .hs-rail .chip{width:auto!important;max-width:100%!important;flex:0 0 auto!important;white-space:nowrap!important;min-height:40px!important;display:inline-flex!important;align-items:center!important;justify-content:center!important;padding:8px 14px!important;border:1px solid rgba(226,232,242,.13)!important;border-radius:999px!important;background:rgba(255,255,255,.045)!important;color:#d7deea!important;font-size:13px!important;font-weight:550!important;box-shadow:none!important;transition:background .18s ease,border-color .18s ease,color .18s ease!important}
#homeShelves .hs-rail .chip-i{display:none!important}#homeShelves .hs-rail .chip.on{border-color:rgba(240,210,130,.55)!important;background:rgba(222,183,87,.14)!important;color:#f1d98f!important}
#homeShelves .hs-main{width:100%!important;min-width:0!important;margin:0!important}#homeShelves .hs-sec{min-height:66px!important;padding:0 24px!important;border:0!important;border-bottom:1px solid rgba(230,234,242,.08)!important;background:transparent!important}#homeShelves .hs-sec h3{color:#f4f1e9!important;font-size:20px!important;font-weight:640!important;letter-spacing:-.02em!important}#homeShelves .hs-cnt{color:#a8b2c2!important;font-size:12px!important}
#homeShelves .hs-grid{gap:22px 18px!important;padding:22px 24px 32px!important}#homeShelves .hs-grid .bkcard{padding:9px!important;border:1px solid rgba(232,237,246,.08)!important;border-radius:17px!important;background:rgba(255,255,255,.035)!important;box-shadow:inset 0 1px rgba(255,255,255,.045)!important;transition:transform .22s ease,border-color .22s ease,background .22s ease!important}#homeShelves .hs-grid .bkcard:hover{transform:translateY(-4px)!important;border-color:rgba(237,203,114,.34)!important;background:rgba(255,255,255,.065)!important}
#homeShelves .hs-grid .bkcov{border:1px solid rgba(238,206,123,.52)!important;border-radius:8px 11px 11px 8px!important;background:linear-gradient(105deg,#06101d 0 5%,#0e2436 6%,#173146 46%,#0c1c2d 100%)!important;box-shadow:inset 4px 0 0 rgba(238,206,123,.28),inset 0 0 28px rgba(230,194,98,.10),0 15px 28px rgba(0,0,0,.36)!important;transform:perspective(700px) rotateY(-3deg)!important;transition:transform .24s ease,box-shadow .24s ease!important}
#homeShelves .hs-grid .bkcard:hover .bkcov{transform:perspective(700px) rotateY(0) translateY(-2px)!important;box-shadow:inset 4px 0 0 rgba(238,206,123,.4),inset 0 0 34px rgba(230,194,98,.15),0 23px 40px rgba(0,0,0,.42)!important}
#homeShelves .bk-ttl,#homeShelves .bkname{color:#f0dfa9!important;text-shadow:0 1px 10px rgba(227,190,93,.18)!important}#homeShelves .bk-sub,#homeShelves .bk-gloss,#homeShelves .bkcat{color:rgba(226,231,239,.68)!important}#homeShelves .bk-line,#homeShelves .bk-rule{background:rgba(232,201,107,.68)!important}
/* 其它内容面板和浮层延续暗色玻璃系统 */
#page-home>.sec-title,#page-home>.feed{order:7!important;width:min(1320px,calc(100% - 36px))!important;margin-right:auto!important;margin-left:auto!important;color:#f4f1e9!important}#page-home>.feed .card{border:1px solid rgba(228,234,244,.12)!important;border-radius:17px!important;background:rgba(255,255,255,.055)!important;color:#f4f1e9!important;box-shadow:0 12px 28px rgba(0,0,0,.16)!important;backdrop-filter:blur(16px)}
#page-home>.modal{background:rgba(2,8,18,.74)!important;backdrop-filter:blur(18px) saturate(135%)!important}#page-home .m-head{border-color:rgba(228,234,244,.12)!important;background:rgba(15,27,44,.94)!important;color:#f4f1e9!important;backdrop-filter:blur(24px)}#page-home .m-body{background:#0d1727!important;color:#e8eaf0!important}
#page-home input,#page-home select,#page-home textarea{border-color:rgba(225,232,243,.18)!important;background:rgba(255,255,255,.07)!important;color:#f2eee7!important}#page-home input::placeholder,#page-home textarea::placeholder{color:rgba(210,218,231,.55)!important}
#hsSupTop,#permBoxHome{color:#e9e6df!important}#hsSupTop .sup-card,#permBoxHome{border:1px solid rgba(227,202,133,.16)!important;border-radius:18px!important;background:rgba(255,255,255,.055)!important;color:#e9e6df!important;box-shadow:0 12px 28px rgba(0,0,0,.18)!important;backdrop-filter:blur(18px)}
html[data-theme="light"] .tabbar,html[data-theme="dark"] .tabbar{position:fixed!important;z-index:1000!important;left:50%!important;right:auto!important;bottom:calc(14px + env(safe-area-inset-bottom,0px))!important;width:min(480px,calc(100% - 32px))!important;padding:8px 10px!important;transform:translateX(-50%)!important;display:flex!important;border:1px solid rgba(232,237,246,.17)!important;border-radius:22px!important;background:rgba(18,31,50,.76)!important;box-shadow:0 16px 44px rgba(0,0,0,.38),inset 0 1px rgba(255,255,255,.12)!important;backdrop-filter:blur(32px) saturate(150%)!important;-webkit-backdrop-filter:blur(32px) saturate(150%)!important}
.tabbar .tb{min-height:48px!important;color:rgba(229,234,242,.62)!important}.tabbar .tb .t-ic{font-size:19px!important;filter:none!important}.tabbar .tb .t-nm{font-size:10.5px!important;color:inherit!important}.tabbar .tb.on{color:#f1d88b!important}.tabbar .tb.on .t-ic{filter:drop-shadow(0 0 9px rgba(235,199,97,.64))!important;transform:translateY(-2px)}.tabbar .tb.on .t-nm{color:#f1d88b!important}
button:focus-visible,a:focus-visible,[role="button"]:focus-visible,[onclick]:focus-visible{outline:2px solid rgba(239,211,133,.9)!important;outline-offset:3px!important}
@media(max-width:700px){.hdr{padding:18px 12px 10px!important}.hdr .logo{font-size:24px!important}.hdr>div[style*="display:flex"]{margin-top:8px!important}.tk-hero{width:calc(100% - 24px)!important;min-height:440px!important;margin:6px auto 13px!important;border-radius:23px!important}.tk-hero:before{width:min(76vw,310px)!important;top:50%!important}.tk-hero:after{top:50%!important;font-size:clamp(34px,9vw,52px)!important}.tk-hero>div:first-child{top:22px!important;left:10px!important;right:10px!important;font-size:27px!important}.tk-hero>div:nth-child(2){bottom:84px!important;font-size:13px!important;line-height:1.7!important}.tk-acts{bottom:19px!important;gap:8px!important}.tk-acts button,.tk-acts span{min-height:44px!important;padding:9px 14px!important;font-size:12.5px!important}.vision-cards{width:calc(100% - 24px)!important;gap:9px!important;margin-bottom:14px!important}.vision-card{min-height:82px!important;gap:9px!important;padding:12px 10px!important;border-radius:16px!important}.vc-icon{width:35px!important;height:35px!important;border-radius:11px!important}.vc-icon svg{width:18px!important;height:18px!important}.vc-copy strong{font-size:12.5px!important}.vc-copy small{font-size:10.5px!important}.vc-arrow{font-size:14px!important}.lib-search,#page-home>.lib-acts{width:calc(100% - 24px)!important}.lib-search input{height:46px!important;font-size:14px!important}#page-home>#quote{width:calc(100% - 24px)!important;margin-bottom:14px!important}#page-home>#homeShelves{width:calc(100% - 16px)!important;border-radius:20px!important}#homeShelves .hs-rail{gap:7px!important;padding:14px 12px 13px!important}#homeShelves .hs-rail .chip{min-height:38px!important;padding:7px 11px!important;font-size:12px!important}#homeShelves .hs-sec{min-height:58px!important;padding:0 15px!important}#homeShelves .hs-sec h3{font-size:18px!important}#homeShelves .hs-grid{gap:16px 11px!important;padding:16px 12px 26px!important}#page-home>.sec-title,#page-home>.feed{width:calc(100% - 24px)!important}}
@media(max-width:380px){.tk-hero{min-height:420px!important}.vision-card{gap:7px!important;padding:10px 8px!important}.vc-copy small{font-size:10px!important}.tk-acts{gap:6px!important}.tk-acts button,.tk-acts span{padding:9px 11px!important}}

#page-home .tk-acts button>span{display:inline!important;min-height:0!important;padding:0!important;border:0!important;border-radius:0!important;background:none!important;color:inherit!important;font:inherit!important;box-shadow:none!important;transform:none!important;transition:none!important}
html[data-theme="light"] #page-home .hdr .ai-btn,html[data-theme="light"] #page-home .hdr .lang-btn,html[data-theme="dark"] #page-home .hdr .ai-btn,html[data-theme="dark"] #page-home .hdr .lang-btn{border:1px solid rgba(226,232,240,.15)!important;background:rgba(255,255,255,.07)!important;color:#eff1f6!important;box-shadow:inset 0 1px rgba(255,255,255,.08),0 8px 26px rgba(0,0,0,.18)!important}
@media(prefers-reduced-motion:reduce){.tk-hero:before{animation:none!important}.vision-card,.tk-acts button,.tk-acts span,#homeShelves .hs-grid .bkcard,#homeShelves .bkcov{transition:none!important}.vision-card:hover,.tk-acts button:hover{transform:none!important}}

/* Nour：以阿文书法为中心的 AI 入口与明确导航 */
#page-home .hdr .logo{font-family:AmiriNur,SF Arabic,Geeza Pro,serif!important;font-size:38px!important;line-height:1.05!important}
#page-home .hdr .logo-sub{font-size:12px!important;letter-spacing:.12em!important}
#page-home .hdr .ai-btn{display:none!important}
#page-home>.tk-hero{min-height:475px!important}
#page-home .tk-hero:after{content:none!important}
#page-home .tk-hero>div:first-child{font-size:clamp(25px,3.4vw,36px)!important}
#page-home .tk-hero>div:nth-child(2){top:81px!important;bottom:auto!important;font-size:13px!important}
#page-home .tk-hero .tk-acts{display:none!important}
.nour-orb{position:absolute!important;z-index:4!important;left:50%!important;top:55%!important;transform:translate(-50%,-50%)!important;width:clamp(190px,28vw,242px)!important;aspect-ratio:1!important;padding:0!important;border:1px solid rgba(255,226,152,.65)!important;border-radius:50%!important;background:radial-gradient(circle at 35% 27%,rgba(255,249,218,.92),rgba(238,200,100,.84) 13%,rgba(164,126,42,.86) 30%,rgba(14,88,72,.88) 56%,rgba(5,17,33,.96) 78%)!important;box-shadow:inset -18px -24px 38px rgba(0,0,0,.42),inset 10px 10px 30px rgba(255,247,207,.3),0 0 38px rgba(238,200,100,.32),0 0 74px rgba(32,167,132,.18)!important;display:flex!important;flex-direction:column!important;align-items:center!important;justify-content:center!important;gap:0!important;cursor:pointer!important;color:#fff0b5!important;animation:nourOrbBreathe 4s ease-in-out infinite!important;backdrop-filter:blur(3px)!important}
.nour-orb:before{content:'';position:absolute;inset:10px;border:1px solid rgba(255,243,197,.38);border-radius:50%;pointer-events:none}
.nour-orb-ar{font-family:AmiriNur,SF Arabic,Geeza Pro,serif!important;font-size:clamp(76px,12vw,104px)!important;font-weight:700!important;line-height:1.05!important;text-shadow:0 2px 0 #715822,0 6px 22px rgba(255,225,145,.75),0 0 36px rgba(255,233,166,.45)!important}
.nour-orb-en{font-size:12px!important;letter-spacing:.22em!important;text-transform:uppercase!important;color:rgba(255,246,214,.9)!important;text-shadow:0 1px 10px rgba(0,0,0,.5)!important}
.nour-orb-hint{margin-top:9px!important;font-size:10px!important;color:rgba(255,246,214,.7)!important}
@keyframes nourOrbBreathe{0%,100%{box-shadow:inset -18px -24px 38px rgba(0,0,0,.42),inset 10px 10px 30px rgba(255,247,207,.3),0 0 30px rgba(238,200,100,.25),0 0 58px rgba(32,167,132,.14);scale:.985}50%{box-shadow:inset -18px -24px 38px rgba(0,0,0,.38),inset 10px 10px 34px rgba(255,247,207,.38),0 0 48px rgba(238,200,100,.44),0 0 86px rgba(32,167,132,.26);scale:1.025}}
#page-home>.vision-cards{position:relative!important;z-index:5!important;width:min(760px,calc(100% - 36px))!important;gap:14px!important;margin:-94px auto 22px!important}
.vision-card{min-height:82px!important}
.nour-live{position:fixed!important;z-index:1400!important;left:50%!important;bottom:calc(84px + env(safe-area-inset-bottom,0px))!important;transform:translateX(-50%)!important;width:min(620px,calc(100% - 24px))!important;max-width:none!important;margin:0!important;padding:0!important;display:block!important;filter:drop-shadow(0 18px 44px rgba(0,0,0,.5))!important}
.nour-live .ps-ai-card{display:block!important;max-height:min(72vh,680px)!important;overflow:hidden!important;border:1px solid rgba(236,210,135,.34)!important;border-radius:22px!important;background:rgba(14,27,44,.96)!important;box-shadow:0 24px 80px rgba(0,0,0,.5)!important}
.nour-live .ps-ai-head{padding-right:74px!important;background:rgba(19,43,57,.98)!important;color:#f7e7b1!important}
.nour-live .ps-ai-msgs{height:min(36vh,330px)!important;max-height:min(36vh,330px)!important;min-height:120px!important;background:rgba(6,16,30,.8)!important}
.nour-live .ps-ai-msg.bot{background:rgba(255,255,255,.09)!important;color:#f4f1e9!important}
.nour-live .ps-ai-input{display:flex!important;flex-direction:row!important;align-items:center!important;background:rgba(7,16,29,.95)!important}
.nour-live .ps-ai-input button{min-width:48px!important;min-height:44px!important;padding:8px 12px!important}
.nour-live .ps-ai-input button:not(.ps-mic){display:none!important}
.nour-close{position:absolute!important;z-index:10!important;right:12px!important;top:10px!important;min-height:38px!important;padding:7px 12px!important;border:1px solid rgba(242,218,157,.26)!important;border-radius:999px!important;background:rgba(255,255,255,.07)!important;color:#f4e4b0!important;cursor:pointer!important}
@media(max-width:700px){#page-home>.tk-hero{min-height:440px!important}.tk-hero>div:nth-child(2){top:75px!important;font-size:12px!important}.vision-cards{margin-top:-78px!important}.nour-orb{top:54%!important;width:clamp(185px,58vw,224px)!important}.nour-orb-ar{font-size:84px!important}.nour-live{bottom:calc(78px + env(safe-area-inset-bottom,0px))!important}.nour-live .ps-ai-msgs{height:30vh!important;max-height:30vh!important}}
@media(prefers-reduced-motion:reduce){.nour-orb{animation:none!important}}
.tabbar{position:fixed!important;z-index:12000!important;left:50%!important;right:auto!important;bottom:calc(14px + env(safe-area-inset-bottom,0px))!important;width:min(480px,calc(100% - 32px))!important;transform:translateX(-50%)!important;display:flex!important}
@media(max-width:700px){.tabbar{bottom:calc(10px + env(safe-area-inset-bottom,0px))!important;width:calc(100% - 24px)!important}}
body.reading .tabbar{display:flex!important;position:fixed!important;z-index:12000!important;left:50%!important;right:auto!important;bottom:calc(14px + env(safe-area-inset-bottom,0px))!important;transform:translateX(-50%)!important;width:min(480px,calc(100% - 32px))!important}

/* 四个独立页面：深曜石、琥珀金与翡翠绿 */
/* 首页收敛：书架只在图书馆、查找只在搜索，移除重复快捷卡片与推广 */
#page-home>.lib-search,#page-home>.lib-acts,#page-home>.vision-cards,#page-home>#homeShelves,#page-home>.sec-title,#page-home>.feed,#page-home>#aiSec{display:none!important}
#page-home>.tk-hero{min-height:440px!important;margin:18px auto 20px!important}
#page-home>#quote{order:3!important;margin:0 auto 14px!important}
#page-home>.study-progress{order:4!important;margin-bottom:120px!important}
.app-footer{display:none!important}
#page-home .donbar,#page-home .sup-card,#page-home .hs-support,#page-home .support-website{display:none!important}

#page-home>.lib-acts{display:none!important}#page-home .tk-dict{display:none!important}#page-home>div:has(>.tk-dict){display:none!important}

:root{--vision-bg:#0f0f0f;--vision-panel:rgba(255,255,255,.055);--vision-panel-strong:rgba(21,24,25,.88);--vision-line:rgba(236,221,178,.12);--vision-text:#f5f2ea;--vision-muted:#a4a39c;--vision-gold:#e4c878;--vision-emerald:#36b68d;--cream:#0f0f0f;--ink:#f5f2ea;--white:#151616;--card:#171818;--muted:#a4a39c;--green:#16795c;--green-d:#11543f;--green-l:#36b68d;--gold:#d2b35d;--gold-l:#ead99f;--line:rgba(255,255,255,.1);--lib-line:rgba(255,255,255,.1);--lib-bg:#0f0f0f;--ap-bg:#0f0f0f;--ap-card:#171818;--ap-text:#f5f2ea;--ap-text2:#a4a39c}
html,body,html[data-theme="light"] body,html[data-theme="dark"] body{background-color:#0f0f0f!important;color:#f5f2ea!important;color-scheme:dark}
body,html[data-theme="light"] body,html[data-theme="dark"] body{background-image:radial-gradient(ellipse 70% 42% at 50% 22%,rgba(13,72,54,.20),transparent 72%),radial-gradient(circle at 85% 72%,rgba(157,119,41,.075),transparent 32%)!important}
.donbar,#hsSupTop,#permBoxHome,.sup-card,.lib-acts{display:none!important}
.page{min-height:calc(100vh - 96px)!important;background:transparent!important;color:#f5f2ea!important}
.page .pg-h{position:sticky!important;top:0!important;z-index:9!important;padding:22px clamp(20px,5vw,72px) 16px!important;border:0!important;background:rgba(15,15,15,.76)!important;color:#f5f2ea!important;font-size:26px!important;font-weight:650!important;letter-spacing:-.03em!important;backdrop-filter:blur(24px)!important}
.pg-wrap{width:min(920px,calc(100% - 40px))!important;margin:0 auto!important;padding:8px 0 128px!important}
#page-home .tk-hero{background:radial-gradient(ellipse 78% 70% at 50% 52%,rgba(16,67,54,.29),transparent 72%),linear-gradient(145deg,rgba(25,27,26,.86),rgba(15,15,15,.94))!important;border-color:rgba(229,207,145,.12)!important}
#page-home .vision-card,#page-home .quote-card,.study-progress{background:linear-gradient(145deg,rgba(255,255,255,.075),rgba(255,255,255,.025))!important;border:1px solid rgba(255,255,255,.085)!important;border-radius:18px!important;box-shadow:inset 0 1px rgba(255,255,255,.055),0 18px 48px rgba(0,0,0,.20)!important}
#page-home>#quote{order:5!important}
.daily-quote .q-ar{font-size:clamp(25px,4vw,36px)!important;line-height:1.8!important;color:#ead99f!important;text-align:center!important}
.daily-quote .q-cn{font-size:15px!important;text-align:center!important;color:rgba(245,242,234,.76)!important}
.daily-quote .q-src,.daily-quote .q-switch,.daily-quote .q-belt{display:none!important}
.study-progress{order:6!important;width:min(900px,calc(100% - 36px))!important;margin:0 auto 24px!important;padding:16px 20px!important;display:flex!important;align-items:center!important;gap:16px!important;color:#f5f2ea!important}
.study-progress>div:first-child{display:grid!important;grid-template-columns:auto auto;column-gap:8px;align-items:center}.study-progress>div:first-child span{grid-column:1/-1;color:#aaa99f;font-size:12px}.study-progress b{font-size:20px;color:#ead99f}.study-progress small{font-size:11px;color:#aaa99f}.study-track{height:4px;flex:1;border-radius:9px;background:rgba(255,255,255,.1);overflow:hidden}.study-track i{display:block;height:100%;border-radius:9px;background:linear-gradient(90deg,#16795c,#e4c878);transition:width .3s}.study-streak{display:grid;text-align:center}.study-streak span{font-size:10px;color:#aaa99f}
.library-page{position:relative!important;display:none;min-height:100vh!important;padding:0 0 116px!important;background:#0f0f0f!important;color:#f5f2ea!important}
.library-page .m-head{position:sticky!important;top:0!important;z-index:12!important;display:flex!important;align-items:center!important;justify-content:center!important;min-height:72px!important;padding:12px 24px!important;border:0!important;border-bottom:1px solid rgba(255,255,255,.07)!important;background:rgba(15,15,15,.84)!important;color:#f5f2ea!important;backdrop-filter:blur(28px)!important}
.library-page .m-head b{font-size:22px!important;font-weight:650!important;letter-spacing:-.02em!important}.library-page .m-head>span{position:absolute;left:24px;color:#e5c978;font-size:22px}.library-back{position:absolute;right:22px;border:0;border-radius:999px;background:rgba(255,255,255,.07);padding:9px 15px;color:#f1dda0;font-size:13px}
.library-page .m-body{width:min(1160px,calc(100% - 28px))!important;min-height:calc(100vh - 150px)!important;margin:0 auto!important;padding:20px 4px 40px!important;background:transparent!important;color:#f5f2ea!important;overflow:visible!important}
.library-page .lib-tabs{position:sticky!important;top:72px!important;z-index:8!important;display:flex!important;justify-content:center!important;gap:9px!important;padding:12px 8px 18px!important;background:rgba(15,15,15,.86)!important;backdrop-filter:blur(20px)!important}
.library-page .lib-tabs .lt{padding:9px 17px!important;border:1px solid rgba(255,255,255,.1)!important;border-radius:999px!important;background:rgba(255,255,255,.045)!important;color:#b4b3ad!important}.library-page .lib-tabs .lt.on{border-color:rgba(228,200,120,.48)!important;background:rgba(228,200,120,.12)!important;color:#ead99f!important}
.library-page .bk-side,.library-page .bk-main,.library-page .bk-grid,.library-page .bkcard{color:#f5f2ea!important}.library-page .bkcard{border-color:rgba(255,255,255,.08)!important;background:rgba(255,255,255,.035)!important;border-radius:14px!important}.library-page .bk-ttl,.library-page .bkname{color:#ead99f!important}.library-page .bk-sub,.library-page .bk-gloss,.library-page .bkcat{color:#a4a39c!important}.library-page .bk-cite,.library-page .citation,.library-page .source-citation{display:none!important}
.profile-wrap,.search-wrap{padding-top:10px!important}.profile-card{margin:0 0 14px!important;padding:20px!important;border:1px solid rgba(255,255,255,.085)!important;border-radius:19px!important;background:linear-gradient(145deg,rgba(255,255,255,.065),rgba(255,255,255,.025))!important;box-shadow:inset 0 1px rgba(255,255,255,.05),0 14px 34px rgba(0,0,0,.16)!important}
.profile-identity{display:flex;align-items:center;gap:16px}.profile-avatar{width:58px;height:58px;display:grid;place-items:center;border-radius:50%;background:radial-gradient(circle at 32% 25%,#f7e5aa,#bd9c4c 38%,#176c53 76%,#10241d);color:#fff5d4;font-family:AmiriNur,serif;font-size:35px;box-shadow:0 0 30px rgba(207,174,87,.18)}.profile-greeting{font-size:19px;font-weight:650}.profile-level{margin-top:6px;color:#aaa99f;font-size:12px;letter-spacing:.04em}.profile-card h2{margin:0 0 12px;font-size:16px;font-weight:620}.footprint-list{display:grid;gap:0}.footprint-row{display:flex;align-items:center;gap:12px;padding:12px 0;border-top:1px solid rgba(255,255,255,.065)}.footprint-mark{width:34px;height:34px;display:grid;place-items:center;border-radius:10px;background:rgba(228,200,120,.09);color:#ead99f}.footprint-row b{display:block;font-size:13px;font-weight:550}.footprint-row small{display:block;margin-top:4px;color:#99988f;font-size:11px}.empty-footprint{margin:0;color:#99988f;font-size:13px}.profile-link{width:100%;display:flex;justify-content:space-between;align-items:center;padding:14px 0;border:0;border-top:1px solid rgba(255,255,255,.065);background:none;color:#eeeae0;text-align:left;font:inherit}.profile-link b{color:#b7a46c;font-size:21px;font-weight:400}
.search-label{display:block;margin:0 0 10px;color:#aaa99f;font-size:12px}.search-wrap .srch-big{width:100%!important;height:58px!important;padding:0 19px!important;border:1px solid rgba(255,255,255,.1)!important;border-radius:16px!important;background:rgba(255,255,255,.055)!important;color:#f5f2ea!important;font-size:17px!important;box-shadow:none!important}.search-wrap .srch-big::placeholder{color:#77776f!important}.search-tools{display:flex;gap:9px;margin:14px 0 20px}.search-tools button{flex:1;min-height:46px;border:1px solid rgba(255,255,255,.09);border-radius:13px;background:rgba(255,255,255,.045);color:#dedbd2;font-size:13px}.search-tools button:first-child{border-color:rgba(228,200,120,.3);color:#ead99f}.search-wrap .srch-chips{display:flex;gap:8px;overflow:auto;padding:0 0 15px}.search-wrap .chip{border:1px solid rgba(255,255,255,.09)!important;background:rgba(255,255,255,.035)!important;color:#b4b3ad!important}.search-wrap .chip.on{border-color:rgba(228,200,120,.45)!important;background:rgba(228,200,120,.12)!important;color:#ead99f!important}.search-wrap .srch-tip{padding:18px 0;color:#99988f}
.search-assist-result{margin-top:10px;padding:16px;border:1px solid rgba(255,255,255,.08);border-radius:16px;background:rgba(255,255,255,.045);color:#eeeae0;font-size:14px;line-height:1.9}.profile-help{padding:10px 0;color:#aaa99f;font-size:12px;line-height:1.7}
.ai-page{position:relative!important;display:none;min-height:100vh!important;padding:5vh 18px 124px!important;background:#0f0f0f!important;color:#f5f2ea!important}.ai-page.nour-live{position:relative!important;left:auto!important;bottom:auto!important;transform:none!important;width:100%!important;max-width:none!important;margin:0!important;filter:none!important}.ai-page .ps-ai-card{display:block!important;width:min(760px,100%)!important;max-height:none!important;margin:0 auto!important;overflow:hidden!important;border:1px solid rgba(236,210,135,.22)!important;border-radius:24px!important;background:linear-gradient(145deg,rgba(255,255,255,.07),rgba(255,255,255,.025))!important;box-shadow:0 24px 70px rgba(0,0,0,.28)!important}.ai-page .ps-ai-head{padding:18px 68px 18px 20px!important;border-bottom:1px solid rgba(255,255,255,.08)!important;background:rgba(255,255,255,.035)!important;color:#ead99f!important}.ai-page .ps-ai-msgs{height:min(56vh,560px)!important;max-height:min(56vh,560px)!important;min-height:240px!important;background:transparent!important}.ai-page .ps-ai-msg.bot{background:rgba(255,255,255,.06)!important;color:#f5f2ea!important}.ai-page .ps-ai-input{display:flex!important;flex-direction:row!important;align-items:center!important;background:rgba(0,0,0,.22)!important}.ai-page .nour-close{position:absolute!important;top:calc(5vh + 14px)!important;right:max(26px,calc((100vw - 760px)/2 + 14px))!important}.ai-page .ps-ai{display:block!important}.ai-page .ps-ai-input button:not(.ps-mic){display:inline-flex!important}.ai-page .ps-ai-input input{flex:1!important}@media(max-width:700px){.ai-page{padding:16px 12px 114px!important}.ai-page .ps-ai-msgs{height:58vh!important;max-height:58vh!important;min-height:220px!important}.ai-page .nour-close{top:25px!important;right:25px!important}}
.tabbar{background:rgba(22,23,22,.82)!important;border-color:rgba(255,255,255,.11)!important}.tabbar .tb.on,.tabbar .tb.on .t-nm{color:#ead99f!important}
@media(max-width:700px){.page .pg-h{padding:18px 20px 13px!important;font-size:23px!important}.pg-wrap{width:calc(100% - 28px)!important}.library-page .m-head{min-height:64px!important}.library-page .m-head b{font-size:19px!important}.library-page .m-body{width:calc(100% - 20px)!important}.library-page .lib-tabs{top:64px!important}.study-progress{width:calc(100% - 24px)!important;gap:10px!important;padding:14px!important}.search-tools{gap:7px}.search-tools button{font-size:12px}}
</style>'''
# 高级产品主题：在旧样式之后注入，确保全屏页面、导航和 AI 工作区统一。
html = html.replace('</head>', _home_finish_css + '</head>', 1)

# 顶层页面视觉系统：从独立 CSS 读取，便于后续迭代且不碰内置数据。
try:
    _app_css_path = DIR / 'data' / 'app-pages.css'
    if _app_css_path.exists():
        _app_css = '<style id="nour-os-pages">' + _app_css_path.read_text(encoding='utf-8') + '</style>'
        html = html.replace('</head>', _app_css + '</head>', 1)
except Exception as _app_css_err:
    print('app-pages.css 注入失败:', _app_css_err)
try:
    _elite_css_path = DIR / 'data' / 'elite-ui.css'
    if _elite_css_path.exists():
        _elite_css = '<style id="nour-elite-ui">' + _elite_css_path.read_text(encoding='utf-8') + '</style>'
        html = html.replace('</head>', _elite_css + '</head>', 1)
except Exception as _elite_css_err:
    print('elite-ui.css 注入失败:', _elite_css_err)
try:
    _elite_ai_css_path = DIR / 'data' / 'elite-ai-input.css'
    if _elite_ai_css_path.exists():
        _elite_ai_css = '<style id="nour-elite-ai-input">' + _elite_ai_css_path.read_text(encoding='utf-8') + '</style>'
        html = html.replace('</head>', _elite_ai_css + '</head>', 1)
except Exception as _elite_ai_css_err:
    print('elite-ai-input.css 注入失败:', _elite_ai_css_err)
try:
    _dialogue_css_path = DIR / 'data' / 'arabic-dialogue.css'
    if _dialogue_css_path.exists():
        _dialogue_css = '<style id="nour-arabic-dialogue">' + _dialogue_css_path.read_text(encoding='utf-8') + '</style>'
        html = html.replace('</head>', _dialogue_css + '</head>', 1)
except Exception as _dialogue_css_err:
    print('arabic-dialogue.css 注入失败:', _dialogue_css_err)
try:
    _challenge_css_path = DIR / 'data' / 'challenge.css'
    if _challenge_css_path.exists():
        _challenge_css = '<style id="nour-challenge">' + _challenge_css_path.read_text(encoding='utf-8') + '</style>'
        html = html.replace('</head>', _challenge_css + '</head>', 1)
except Exception as _challenge_css_err:
    print('challenge.css 注入失败:', _challenge_css_err)
try:
    _reader_css_path = DIR / 'data' / 'reader-polish.css'
    if _reader_css_path.exists():
        _reader_css = '<style id="nour-reader-polish">' + _reader_css_path.read_text(encoding='utf-8') + '</style>'
        html = html.replace('</head>', _reader_css + '</head>', 1)
except Exception as _reader_css_err:
    print('reader-polish.css 注入失败:', _reader_css_err)
try:
    _page_analysis_css_path = DIR / 'data' / 'page-analysis.css'
    if _page_analysis_css_path.exists():
        _page_analysis_css = '<style id="nour-page-analysis">' + _page_analysis_css_path.read_text(encoding='utf-8') + '</style>'
        html = html.replace('</head>', _page_analysis_css + '</head>', 1)
except Exception as _page_analysis_css_err:
    print('page-analysis.css 注入失败:', _page_analysis_css_err)
try:
    _openiti_stream_css_path = DIR / 'data' / 'openiti-stream.css'
    if _openiti_stream_css_path.exists():
        _openiti_stream_css = '<style id="nour-openiti-stream">' + _openiti_stream_css_path.read_text(encoding='utf-8') + '</style>'
        html = html.replace('</head>', _openiti_stream_css + '</head>', 1)
except Exception as _openiti_stream_css_err:
    print('openiti-stream.css 注入失败:', _openiti_stream_css_err)
try:
    _islamic_lib_css_path = DIR / 'data' / 'islamic-library.css'
    if _islamic_lib_css_path.exists():
        _islamic_lib_css = '<style id="nour-islamic-library">' + _islamic_lib_css_path.read_text(encoding='utf-8') + '</style>'
        html = html.replace('</head>', _islamic_lib_css + '</head>', 1)
except Exception as _islamic_lib_css_err:
    print('islamic-library.css 注入失败:', _islamic_lib_css_err)

# 圆角收敛层：在所有样式之后注入，确保覆盖生效（2026-09-26 · 纯视觉）
try:
    _radius_css_path = DIR / 'data' / 'radius-scale.css'
    if _radius_css_path.exists():
        _radius_css = '<style id="nour-radius-scale">' + _radius_css_path.read_text(encoding='utf-8') + '</style>'
        html = html.replace('</head>', _radius_css + '</head>', 1)
except Exception as _radius_css_err:
    print('radius-scale.css 注入失败:', _radius_css_err)

# NOUR 产品壳视觉层：新信息架构覆盖旧页面，但不删除旧节点。
try:
    _product_shell_css_path = DIR / 'data' / 'nour-product-shell.css'
    if _product_shell_css_path.exists():
        _product_shell_css = '<style id="nour-product-shell">' + _product_shell_css_path.read_text(encoding='utf-8') + '</style>'
        html = html.replace('</head>', _product_shell_css + '</head>', 1)
except Exception as _product_shell_css_err:
    print('nour-product-shell.css 注入失败:', _product_shell_css_err)
# NOUR Apple Books 式阅读窗口：独立覆盖层，不修改旧阅读业务逻辑。
try:
    _reader_window_css_path = DIR / 'data' / 'nour-reader-window.css'
    if _reader_window_css_path.exists():
        _reader_window_css = '<style id="nour-reader-window">' + _reader_window_css_path.read_text(encoding='utf-8') + '</style>'
        html = html.replace('</head>', _reader_window_css + '</head>', 1)
except Exception as _reader_window_css_err:
    print('nour-reader-window.css 注入失败:', _reader_window_css_err)
# NOUR AI 视觉精修层：仅覆盖工作区样式，不替换现有 AI API 或发送函数。
try:
    _ai_polish_css_path = DIR / 'data' / 'nour-ai-polish.css'
    if _ai_polish_css_path.exists():
        _ai_polish_css = '<style id="nour-ai-polish">' + _ai_polish_css_path.read_text(encoding='utf-8') + '</style>'
        html = html.replace('</head>', _ai_polish_css + '</head>', 1)
except Exception as _ai_polish_css_err:
    print('nour-ai-polish.css 注入失败:', _ai_polish_css_err)
# NOUR 日夜主题与双向文字隔离层：必须在所有旧视觉层之后注入。
try:
    _nour_theme_css_path = DIR / 'data' / 'nour-theme.css'
    if _nour_theme_css_path.exists():
        _nour_theme_css = '<style id="nour-theme-contract">' + _nour_theme_css_path.read_text(encoding='utf-8') + '</style>'
        html = html.replace('</head>', _nour_theme_css + '</head>', 1)
except Exception as _nour_theme_css_err:
    print('nour-theme.css 注入失败:', _nour_theme_css_err)
# NOUR 全屏工作区：功能点击后进入单一、可读、可返回的视口，不改业务逻辑。
try:
    _focus_css_path = DIR / 'data' / 'nour-focus-workspace.css'
    if _focus_css_path.exists():
        _focus_css = '<style id="nour-focus-workspace">' + _focus_css_path.read_text(encoding='utf-8') + '</style>'
        html = html.replace('</head>', _focus_css + '</head>', 1)
except Exception as _focus_css_err:
    print('nour-focus-workspace.css 注入失败:', _focus_css_err)
# NOUR 全局界面契约层：统一焦点、触控、响应式留白与动效，不改业务逻辑。
try:
    _interface_polish_css_path = DIR / 'data' / 'nour-interface-polish.css'
    if _interface_polish_css_path.exists():
        _interface_polish_css = '<style id="nour-interface-polish">' + _interface_polish_css_path.read_text(encoding='utf-8') + '</style>'
        html = html.replace('</head>', _interface_polish_css + '</head>', 1)
except Exception as _interface_polish_css_err:
    print('nour-interface-polish.css 注入失败:', _interface_polish_css_err)
# ===== PWA：manifest + 图标（输出到同目录）=====
import shutil as _sh
try:
    _mf = {
        "name": "燃灯者 · حامل المصباح",
        "short_name": "燃灯者",
        "description": "阿拉伯语学习：句子库、词汇、经典选读、哲言、听力跟读、AI 老师",
        "start_url": "./",
        "scope": "./",
        "display": "standalone",
        "orientation": "portrait",
        "background_color": "#0f3d31",
        "theme_color": "#0f3d31",
        "lang": "zh-CN",
        "icons": [
            {"src": "icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any maskable"},
            {"src": "icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"},
        ],
    }
    (DIR / 'manifest.webmanifest').write_text(json.dumps(_mf, ensure_ascii=False, indent=2), encoding='utf-8')
    for _f in ('icon-192.png', 'icon-512.png'):
        _src = DIR / 'assets' / 'icons' / _f
        if _src.exists():
            _sh.copyfile(_src, DIR / _f)
    print('✅ PWA manifest + 图标已生成')
except Exception as _e:
    print('⚠️ PWA 生成失败:', _e)

out = DIR / 'arabic_learning.html'
if len(sys.argv) > 1:
    out = Path(sys.argv[1])
out.write_text(html, encoding='utf-8')
print(f'✅ 高级版主页生成: {out.stat().st_size/1024:.0f}KB')
print(f'   句子: {TOTAL_SENT} | 单词: {TOTAL_WORDS} | 分类: {TOTAL_CATS}')
