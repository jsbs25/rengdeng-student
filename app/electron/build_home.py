#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成高级阿拉伯语学习主页"""
import json, sys
from collections import OrderedDict
from pathlib import Path

DIR = Path(__file__).parent
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
            '<div class="s-card" data-cat="%s">'
            '<div class="s-ar">%s</div>'
            '<div class="s-tr"><div class="s-en">🇬🇧 %s</div><div class="s-cn">🇨🇳 %s</div></div>'
            '<div class="s-btns">'
            '<button class="s-btn" onclick="ap(this,0,\'%s\')">🔊</button>'
            '<button class="s-btn" onclick="ap(this,1,\'%s\')">🇬🇧</button>'
            '<button class="s-btn" onclick="explainSentence(\'%s\')" title="逐词拆解">✂️</button>'
            '</div></div>'
            % (cat, ar, item['en'], item['cn'], ar_safe, en_safe, ar_safe)
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

# ---------- 每日经文/名言（按日期从混合池挑选） ----------
import datetime as _dt
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
.hdr{position:relative;padding:26px 20px 34px;text-align:center;overflow:hidden;
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
.hdr .logo{font-family:serif;font-size:30px;font-weight:700;color:var(--gold-l);letter-spacing:1px;text-shadow:0 2px 18px rgba(0,0,0,.35),0 0 30px rgba(201,168,76,.25)}
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
.ring .ring-txt span{font-size:8px;color:var(--muted)}
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
  box-shadow:0 4px 18px rgba(15,61,49,.06);transition:transform .2s ease}
.stat-card:active{transform:scale(.96)}
.stat-card .ic{font-size:20px;margin-bottom:4px}
.stat-card .num{font-size:24px;font-weight:800;color:var(--green-d);letter-spacing:-.5px}
.stat-card .lb{font-size:10px;color:var(--muted);margin-top:2px}

/* ===== 功能入口 ===== */
.entr-row{max-width:640px;margin:14px auto 0;padding:0 16px;display:flex;flex-direction:column;gap:10px}
.entr{position:relative;display:flex;align-items:center;gap:14px;background:var(--white);border-radius:18px;padding:14px 16px;
  border:1px solid rgba(201,168,76,.18);box-shadow:0 4px 18px rgba(15,61,49,.05);cursor:pointer;transition:transform .18s ease;overflow:hidden}
.entr:active{transform:scale(.97)}
.entr::after{content:'';position:absolute;top:0;bottom:0;right:0;width:4px;background:linear-gradient(180deg,var(--gold),transparent)}
.entr .e-ic{width:48px;height:48px;border-radius:14px;display:flex;align-items:center;justify-content:center;font-size:22px;flex-shrink:0;
  background:linear-gradient(135deg,rgba(201,168,76,.14),rgba(201,168,76,.05));border:1px solid rgba(201,168,76,.2)}
.entr .e-tx{flex:1}
.entr .e-tx b{display:block;font-size:14px;color:var(--ink)}
.entr .e-tx span{display:block;font-size:10.5px;color:var(--muted);margin-top:2px}
.entr .e-go{font-size:18px;color:var(--gold)}

/* ===== 功能按钮 ===== */
.action-row{max-width:640px;margin:12px auto 0;padding:0 16px;display:flex;gap:8px}
.act-btn{flex:1;padding:9px 8px;border-radius:12px;border:1px solid rgba(201,168,76,.35);background:linear-gradient(135deg,#1a5c4a,#0f3d31);color:var(--gold-l);font-size:11px;font-weight:700;cursor:pointer;text-align:center;transition:transform .15s}
.act-btn:active{transform:scale(.95)}
.flash-card{min-height:260px;border-radius:22px;cursor:pointer;display:flex;align-items:center;justify-content:center;padding:26px;box-shadow:0 8px 24px rgba(15,61,49,.12)}
.flash-front{background:linear-gradient(150deg,#14503e,#0e3529);border-radius:22px;width:100%;min-height:260px;display:flex;align-items:center;justify-content:center;flex-direction:column;position:relative}
.flash-back{background:#fff;border:2px solid #c9a84c;border-radius:22px;width:100%;min-height:260px;display:flex;align-items:center;justify-content:center;flex-direction:column;position:relative}
.flash-ar{font-family:serif;font-size:23px;font-weight:800;color:#e8d48b;direction:rtl;text-align:center;line-height:1.9;padding:0 12px}
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
.v-item .v-ar{font-family:serif;font-size:15px;font-weight:700;color:var(--green-d);flex:1;text-align:right;direction:rtl}
.v-item .v-f{font-size:10px;color:var(--muted);background:rgba(201,168,76,.1);padding:2px 8px;border-radius:8px}
.s-item{background:#fff;border:1px solid rgba(201,168,76,.12);border-radius:10px;padding:10px 12px;margin-bottom:6px}
.s-item .s-ar{font-family:serif;font-size:15px;font-weight:700;color:var(--green-d);text-align:right;direction:rtl}
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
.cat-tab .ct-ar{font-size:9px;color:var(--muted)}
.cat-tab.on{background:linear-gradient(135deg,var(--green-d),var(--green));border-color:rgba(201,168,76,.5);box-shadow:0 6px 20px rgba(15,61,49,.25);animation:ripple .5s ease}
.cat-tab.on .ct-nm{color:#fff}
.cat-tab.on .ct-ar{color:rgba(255,255,255,.65)}
@keyframes ripple{0%{transform:scale(1)}40%{transform:scale(.94)}100%{transform:scale(1)}}

/* ===== 句子列表 ===== */
.list-wrap{max-width:640px;margin:12px auto 0;padding:0 16px}
.list-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px}
.list-head .tt{font-size:12px;color:var(--muted)}
.s-card{background:var(--white);border:1px solid rgba(201,168,76,.12);border-radius:14px;padding:12px 14px;margin-bottom:8px;
  box-shadow:0 2px 10px rgba(15,61,49,.04);animation:fadeUp .4s ease both}
@keyframes fadeUp{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
.s-card .s-ar{font-family:serif;font-size:16px;font-weight:700;text-align:right;direction:rtl;color:var(--green-d);line-height:1.7}
.s-card .s-tr{margin-top:6px;padding-top:6px;border-top:1px dashed rgba(201,168,76,.25)}
.s-card .s-en{font-size:10.5px;color:#6b7270;direction:ltr;text-align:left}
.s-card .s-cn{font-size:10.5px;color:var(--green);direction:ltr;text-align:left;margin-top:2px}
.s-card .s-btns{display:flex;gap:6px;margin-top:8px;justify-content:flex-end}
.s-btn{width:30px;height:30px;border-radius:50%;border:1px solid rgba(201,168,76,.3);background:#fff;color:var(--muted);font-size:11px;
  cursor:pointer;display:flex;align-items:center;justify-content:center;transition:all .15s}
.s-btn:hover{background:var(--gold-l);border-color:var(--gold);color:var(--green-d)}
.s-btn.on{background:var(--gold);color:#fff;border-color:var(--gold-d)}

/* ===== 每日一句 ===== */
.daily-quote{max-width:640px;margin:16px auto 0;padding:0 16px}
.quote-card{background:linear-gradient(150deg,#14503e,#0e3529);border-radius:20px;padding:22px;text-align:center;position:relative;overflow:hidden;color:#fff}
.quote-card::before{content:'❝';position:absolute;top:4px;left:14px;font-size:64px;color:rgba(232,212,139,.18);font-family:serif}
.quote-card::after{content:'❞';position:absolute;bottom:0;right:14px;font-size:64px;color:rgba(232,212,139,.18);font-family:serif}
.quote-card .q-ar{font-family:serif;font-size:19px;font-weight:700;direction:rtl;color:var(--gold-l);line-height:1.9;position:relative;z-index:1}
.quote-card .q-cn{font-size:12px;color:rgba(255,255,255,.8);margin-top:8px;position:relative;z-index:1}
.quote-card .q-src{font-size:9.5px;color:rgba(232,212,139,.65);margin-top:8px;position:relative;z-index:1;letter-spacing:.5px}
.quote-card{cursor:pointer;transition:transform .15s}
.quote-card:active{transform:scale(.985)}
.quote-card .q-switch{position:absolute;bottom:8px;right:14px;font-size:9px;color:rgba(232,212,139,.5);z-index:1;letter-spacing:.5px}
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
.ef-msg .ar{font-family:serif;font-weight:700;font-size:12.5px;direction:rtl;text-align:right;display:block;line-height:1.6}
.ef-msg .tr{font-size:9.5px;color:var(--muted);display:block;margin-top:2px}
.ef-inp{display:flex;gap:5px;padding:8px;border-top:1px solid #eee;background:#fff}
.ef-inp input{flex:1;padding:8px 12px;border:1px solid #ddd;border-radius:18px;font-size:11px;outline:0;text-align:right}
.ef-inp input:focus{border-color:var(--gold)}
.ef-inp button{width:34px;height:34px;border-radius:50%;border:0;background:linear-gradient(135deg,var(--gold),var(--gold-d));color:#fff;cursor:pointer;font-size:13px;display:flex;align-items:center;justify-content:center}

/* ===== 底部导航 ===== */
.tabbar{position:fixed;bottom:0;left:0;right:0;z-index:1000;background:rgba(255,255,255,.88);backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px);
  border-top:1px solid rgba(201,168,76,.15);display:flex;padding:8px 6px calc(8px + env(safe-area-inset-bottom))}
.tabbar .tb{flex:1;display:flex;flex-direction:column;align-items:center;gap:2px;padding:5px 0;border:0;background:none;cursor:pointer;color:var(--muted);transition:color .2s}
.tabbar .tb .t-ic{font-size:20px;transition:transform .2s}
.tabbar .tb .t-nm{font-size:9px}
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
  .tabbar .tb{font-size:9px}
  .elf-btn{width:50px;height:50px;bottom:66px;right:12px}
  .action-row{flex-wrap:wrap;gap:6px}
  .act-btn{flex:1 1 45%;padding:8px 6px;font-size:10.5px}
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
.entr-row{display:grid;grid-template-columns:1fr 1fr;gap:12px;max-width:640px}
.entr{flex-direction:column;text-align:center;gap:8px;padding:18px 12px;border-radius:20px;border:1px solid rgba(201,168,76,.22);background:linear-gradient(160deg,#ffffff,#fbf7ee);box-shadow:0 6px 20px rgba(15,61,49,.06);transition:transform .18s,box-shadow .18s}
.entr:hover{transform:translateY(-3px);box-shadow:0 10px 28px rgba(15,61,49,.12)}
.entr .e-ic{width:54px;height:54px;border-radius:16px;font-size:25px;background:linear-gradient(135deg,rgba(201,168,76,.16),rgba(201,168,76,.06));border:1px solid rgba(201,168,76,.25);margin:0 auto}
.entr .e-tx b{font-size:13.5px}
.entr .e-tx span{font-size:10px}
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
  font-family:'Noto Naskh Arabic','Amiri','Scheherazade New','Geeza Pro','Arial',serif;
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
.s-card{transition:transform .15s}
.s-card:active{transform:scale(.985)}
.act-btn{box-shadow:0 2px 6px rgba(15,61,49,.15)}
.s-item{transition:transform .12s}
.s-item:active{transform:scale(.99)}
.modal{box-shadow:0 10px 40px rgba(15,61,49,.25)}
</style>
'''

JS = """
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
      (pts[2] ? '<span class="tr" style="color:#5a7f9e">🇬🇧 ' + esc(pts[2]) + '</span>' : '') + '</div>';
  }
  d.appendChild(m); d.scrollTop = d.scrollHeight; return m;
}
// API 地址：只有从 8080 服务打开才同源；file:// 双击或其他端口都显式指向 8080
function API_BASE(){
  if(location.protocol === 'http:' && location.port === '8080') return '';
  return 'http://localhost:8080';
}
function esc(s){ if(!s) return ''; return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
var AI_BUSY = false;
async function es(){
  var i = document.getElementById('ei'), t = i.value.trim();
  if(!t || AI_BUSY) return;
  i.value = ''; em(1, t);
  AI_BUSY = true;
  var sb = document.getElementById('eiSend');
  if(sb) sb.disabled = true;
  try{
    var r = await fetch(API_BASE() + '/api/chat/message', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({message:t, session_id:SID})});
    var d = await r.json(), a = d.arabic || d, pts = (a||'').split('\\n');
    var mb = em(0, a), sp = mb.querySelector('.ar'), txt = pts[0] || '';
    // 打字机效果（em 已渲染中英翻译，这里只重写阿语，不重复追加）
    sp.textContent = '';
    for(var i2=0;i2<txt.length;i2+=2){
      sp.textContent = txt.slice(0, i2 + 2);
      await new Promise(function(r2){setTimeout(r2, 12);});
    }
    if(window.speechSynthesis){
      var u = new SpeechSynthesisUtterance(txt);
      u.lang = 'ar-SA'; u.rate = .7;
      window.speechSynthesis.speak(u);
    }
  }catch(e){
    em(0, '⚠️ AI 服务未启动\\n请先运行服务器：终端执行 bash run.sh，或 python3 server.py');
  }
  AI_BUSY = false;
  if(sb) sb.disabled = false;
}

// ===== 底部导航 =====
function nav(tab){
  document.querySelectorAll('.tabbar .tb').forEach(function(t){t.classList.remove('on');});
  var el = document.querySelector('.tabbar .tb[data-tab="'+tab+'"]');
  if(el) el.classList.add('on');
  var secs = document.querySelectorAll('.tab-sec');
  secs.forEach(function(s){ s.classList.remove('hidden-sec'); });
  // 简单处理：首页显示全部，其他tab滚动到对应位置
  document.getElementById('home').scrollIntoView({behavior:'smooth'});
  if(tab === 'ai'){ document.getElementById('ep').classList.add('o'); document.getElementById('eb').classList.add('h'); }
}


// ===== 全部句子 & 词汇表 & 图书馆（内置数据优先，服务器后台增强）=====
var ALL_SENTENCES = [];
var ALL_VOCAB = [];
var ALL_ARTICLES = [];
function openModal(id){document.getElementById(id).classList.add('show');}
function closeModal(id){document.getElementById(id).classList.remove('show');}
async function showAllSentences(){
  openModal('mSentences');
  ALL_SENTENCES = BUILTIN_SENTENCES;
  renderAllS();
  try{
    var r = await fetch(API_BASE() + '/api/sentences');
    var d = await r.json();
    var list = [];
    Object.keys(d.cats || {}).forEach(function(k){
      (d.cats[k] || []).forEach(function(s){ list.push({a:s.a||s.ar||'', e:s.e||s.en||'', c:s.c||s.cn||'', cat:k}); });
    });
    if(list.length){ ALL_SENTENCES = list; renderAllS(); }
  }catch(e){}
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
      '<button class="s-btn" style="width:26px;height:26px" onclick="ap(this,0,&#39;'+vw+'&#39;)">🔊</button>';
    body.appendChild(d);
  });
  document.getElementById('mVocabCount').textContent = '共 ' + ALL_VOCAB.length + ' 词（显示前500）';
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
    for(var x = 0; x < btns.length; x++){
      if(item.opts[x].c === item.q.c){ btns[x].style.background = '#1a8a5c'; btns[x].style.color = '#fff'; }
    }
  }
  setTimeout(function(){ quizIdx++; renderQuiz(); }, 900);
}

// ===== 🃏 闪卡 =====
var flashDeck = [];
var flashIdx = 0;
var flashFlipped = false;
var flashKnown = 0;
var flashAgain = [];
var flashDone = false;
async function showFlashcard(){
  openModal('mFlash');
  flashDeck = buildFlashDeck();
  flashIdx = 0; flashFlipped = false; flashKnown = 0; flashAgain = []; flashDone = false;
  renderFlash();
}
function buildFlashDeck(){
  var all = (BUILTIN_SENTENCES || []).filter(function(s){ return s.a && s.c; });
  for(var i = all.length - 1; i > 0; i--){
    var j = Math.floor(Math.random() * (i + 1));
    var t = all[i]; all[i] = all[j]; all[j] = t;
  }
  return all.slice(0, 12);
}
function renderFlash(){
  var body = document.getElementById('mFlashBody');
  var head = document.getElementById('mFlashHead');
  if(flashDone){
    head.textContent = '🎉 本局完成';
    body.innerHTML = '<div style="text-align:center;padding:40px 20px">'+
      '<div style="font-size:46px">🎉</div>'+
      '<div style="font-size:18px;font-weight:800;color:#0f3d31;margin-top:10px">本局完成！</div>'+
      '<div style="font-size:14px;color:#555;margin-top:12px">认识 <b style="color:#1a8a5c">'+flashKnown+'</b> / '+flashDeck.length+' 张</div>'+
      '<div style="font-size:12px;color:#999;margin-top:4px">待复习 '+flashAgain.length+' 张</div>'+
      '<div style="display:flex;gap:8px;justify-content:center;margin-top:20px">'+
      (flashAgain.length ? '<button class="act-btn" onclick="flashReview()">🔄 复习 '+flashAgain.length+' 张</button>' : '')+
      '<button class="act-btn" onclick="showFlashcard()">▶ 再来一局</button>'+
      '</div></div>';
    return;
  }
  var card = flashDeck[flashIdx];
  head.textContent = '🃏 闪卡 · ' + (flashIdx + 1) + ' / ' + flashDeck.length + ' · 已认识 ' + flashKnown;
  body.innerHTML = '<div id="flashCard" class="flash-card" onclick="flashFlip()">' +
    (flashFlipped
      ? '<div class="flash-back"><div class="flash-cn">🇨🇳 ' + esc(card.c) + '</div>' +
        (card.e ? '<div class="flash-en">🇬🇧 ' + esc(card.e) + '</div>' : '') +
        '<div class="flash-hint">👆 点击翻回</div></div>'
      : '<div class="flash-front"><div class="flash-ar">' + card.a + '</div>' +
        '<div class="flash-hint">👆 点击翻面</div></div>') +
    '</div>' +
    '<div style="display:flex;gap:10px;margin-top:14px">' +
    '<button class="act-btn" style="flex:1;background:#c0392b" onclick="flashAnswer(false)">❌ 不会</button>' +
    '<button class="act-btn" style="flex:1;background:#1a8a5c" onclick="flashAnswer(true)">✅ 认识</button>' +
    '</div>';
}
function flashFlip(){ flashFlipped = !flashFlipped; renderFlash(); }
function flashAnswer(ok){
  if(ok) flashKnown++;
  else flashAgain.push(flashDeck[flashIdx]);
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


// ===== 🎙 古兰经诵读家 =====
var RECITERS = [
  {label:'🎙 阿法西', path:'Alafasy/mp3/'},
  {label:'🎙 苏达伊斯', path:'Sudais/mp3/'},
  {label:'🎙 阿卜杜勒·巴西特', path:'AbdulBaset/Murattal/mp3/'}
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

// ===== 🕌 古兰经 =====
var QURAN = [];
var currentSurah = null;
async function showQuran(){
  QURAN = BUILTIN_QURAN || [];
  openModal('mQuran');
  renderQuranList();
}
function renderQuranList(){
  var body = document.getElementById('mQuranBody');
  var q = (document.getElementById('mQuranSearch') ? document.getElementById('mQuranSearch').value : '').trim();
  var list = QURAN;
  if(q){ list = QURAN.filter(function(s){ return (s.n + s.tz + s.t).indexOf(q) >= 0; }); }
  body.innerHTML = '';
  list.forEach(function(s){
    var it = document.createElement('div');
    it.className = 's-item'; it.style.cursor = 'pointer';
    it.innerHTML = '<div style="display:flex;align-items:center;gap:8px"><span style="background:#0f3d31;color:#e8d48b;font-size:10px;font-weight:700;border-radius:10px;padding:2px 8px">'+s.id+'</span>'+
      '<span style="font-size:13px;font-weight:700;color:#0f3d31;font-family:serif">'+s.n+'</span>'+
      '<span style="font-size:10px;color:#999;margin-left:auto">'+s.tz+' · '+s.vs.length+' 节</span></div>';
    it.onclick = function(){ openSurah(s); };
    body.appendChild(it);
  });
  document.getElementById('mQuranCount').textContent = '共 ' + list.length + ' 章 · 点击进入';
}
function openSurah(s){
  currentSurah = s;
  var body = document.getElementById('mQuranBody');
  body.innerHTML = '<button class="act-btn" style="margin-bottom:10px" onclick="renderQuranList()">← 返回章节列表</button>'+
    '<div style="font-size:16px;font-weight:800;color:#0f3d31;text-align:center">🕌 '+s.n+' · '+s.tz+'</div>'+
    '<div style="font-size:10px;color:#999;text-align:center;margin:4px 0 12px">'+s.t+' · '+(s.ty==='meccan'?'麦加章':'麦地那章')+' · '+s.vs.length+' 节</div>'+
    '<div id="reciterRow" style="text-align:center;margin-bottom:12px"></div>';
  s.vs.forEach(function(v, idx){
    var it = document.createElement('div');
    it.className = 's-item';
    var arSafe = v.a.replace(/&/g,'&amp;').replace(/'/g,'&#39;').replace(/"/g,'&quot;');
    it.innerHTML = '<div style="display:flex;gap:10px"><span style="background:#0f3d31;color:#e8d48b;font-size:10px;font-weight:800;border-radius:12px;min-width:22px;text-align:center;padding:3px 6px;height:fit-content;box-shadow:0 2px 6px rgba(15,61,49,.25)">'+(idx+1)+'</span>'+
      '<div style="flex:1"><div class="quran-ayah" style="font-weight:700;color:#0f3d31;text-align:right">'+v.a+'</div>'+
      (v.z ? '<div style="font-size:10.5px;color:#1a5c4a;margin-top:5px">🇨🇳 '+v.z+'</div>' : '')+
      '<div style="display:flex;gap:6px;margin-top:7px;justify-content:flex-end">'+
      '<button class="s-btn" onclick="ap(this,0,&#39;'+arSafe+'&#39;)">🔊</button>'+
      '<button class="s-btn" onclick="explainQuran('+s.id+','+idx+')">🔬 逐字分解</button>'+
      '<button class="s-btn rec-btn" id="rec_'+s.id+'_'+idx+'" onclick="playAyah('+s.id+','+idx+')">🎙 诵读</button></div>'+
      '<div class="decomp-box" id="dec_'+s.id+'_'+idx+'"></div></div></div>';
    body.appendChild(it);
  });
  document.getElementById('mQuranCount').textContent = '← 点顶部返回';
  renderReciterRow();
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
      body:JSON.stringify({message:'请对这句古兰经经文做逐词语法分析。要求每个词一行，用竖线分隔 6 个字段：\\n词（保留原文）| 词根 | 词性（اسم名词/فعل动词/حرف介词等）| 语法功能（如主格/宾格/属格/过去式/现在式/人称数）| 中文词义 | 英文词义\\n\\n经文：' + ayah.a, session_id:'quran_'+Date.now()})});
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
        '<div style="display:flex;align-items:center;gap:8px"><b style="font-family:serif;font-size:15px;color:#0f3d31;direction:rtl;cursor:pointer" onclick="ap(this,0,&#39;'+p[0].replace(/'/g,'&#39;')+'&#39;)">'+esc(p[0])+'</b>'+
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
      body:JSON.stringify({message:'请逐词拆解并解释这句阿拉伯语。格式：每个词一行，先写阿拉伯语单词（去掉音符），再写中文释义和英文释义，如有词性也写上：\\n' + ar, session_id:'explain_'+Date.now()})});
    var d = await r.json(), txt = d.arabic || '（无回复）';
    var lines = txt.split('\\n').filter(function(l){return l.trim();});
    var h = '<div style="background:linear-gradient(150deg,#14503e,#0e3529);border-radius:12px;padding:12px 16px;margin-bottom:12px"><div style="font-family:serif;font-size:14px;color:#e8d48b;font-weight:700;direction:rtl;text-align:center;line-height:1.8">'+ar+'</div></div>';
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
      body:JSON.stringify({message:'اكتب مقالا قصيرا عن ' + topic + ' بالعربية الفصحى مع الترجمة الصينية في النهاية.', session_id:'article_'+Date.now()})});
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


// ===== 学习统计（localStorage）=====
var LEARN_KEY = 'nur_learned';
var DATES_KEY = 'nur_dates';
var MIN_KEY = 'nur_minutes';
var GOAL = 20;
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
  var dates = getDates();
  var streak = calcStreak2(dates);
  var mins = parseInt(localStorage.getItem(MIN_KEY) || '0', 10);
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
  if(gt) gt.textContent = learned + ' / ' + GOAL + ' 单词';
  var gb = document.getElementById('goalBar');
  if(gb) gb.style.width = pct + '%%';
  var s1 = document.querySelector('.stat-card .num');
  if(s1) s1.textContent = learned;
}
function checkIn(){
  var today = todayStr2();
  var dates = getDates();
  if(dates.indexOf(today) < 0){ dates.push(today); localStorage.setItem(DATES_KEY, JSON.stringify(dates)); }
  var learned = getLearned();
  if(learned.indexOf('checkin') < 0){ learned.push('checkin'); localStorage.setItem(LEARN_KEY, JSON.stringify(learned)); }
  var mins = parseInt(localStorage.getItem(MIN_KEY) || '0', 10) + 5;
  localStorage.setItem(MIN_KEY, String(mins));
  updateStats();
  var btn = document.querySelector('.daily-goal .act-btn');
  if(btn){ btn.textContent = '✅ 已打卡 (+5分钟)'; btn.style.opacity = '.7'; }
}


// ===== 每日经文/名言：点击切换 =====
var CQ_LAST = -1;
function nextQuote(){
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
// ===== 服务器状态检测 =====
function checkServer(){
  var el = document.getElementById('serverStatus');
  if(!el) return;
  fetch(API_BASE() + '/api/sentences', {cache:'no-store'}).then(function(r){
    if(r.ok){ el.textContent = '🟢 AI 服务在线'; el.style.color = '#1a8a5c'; }
    else{ el.textContent = '🔴 AI 服务未启动'; el.style.color = '#c0392b'; }
  }).catch(function(){
    el.textContent = '🔴 AI 服务未启动'; el.style.color = '#c0392b';
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

"""

# ---------- 组装 HTML ----------
html = (
    '<!DOCTYPE html>\\n<html>\\n<head>\\n<meta charset="UTF-8">\\n'
    '<meta name="viewport" content="width=device-width,initial-scale=1.0,maximum-scale=1.0">\\n'
    '<title>حامل المصباح | 燃灯者 · 无声却引人归途</title>\\n<style>\\n' + CSS + '</style>\\n</head>\\n<body>\\n'
    '<div class="bg-pattern"></div>\\n'
)

# Header
html += (
    '<header class="hdr">'
    '<div class="glow"></div>'
    '<div class="arch-wrap"><div class="arch"></div></div>'
    '<div class="logo">حامل المصباح</div>'
    '<div class="logo-sub">燃灯者 · 无声却引人归途</div>'
    '<span class="zh">صامتٌ لكنّه يهدي إلى الطريق</span>'
    '</header>\\n'
)

# 每日经文/名言（顶部，点击切换）
html += (
    '<div class="daily-quote" id="quote">'
    '<div class="quote-card" onclick="nextQuote()" title="点击换一条">'
    '<div class="q-ar" id="qAr">' + DAILY_AR + '</div>'
    '<div class="q-cn" id="qCn">' + DAILY_CN + '</div>'
    '<div class="q-src" id="qSrc">🕯 ' + DAILY_SRC + '</div>'
    '<div class="q-switch">🔄 点击换一条</div>'
    '</div></div>\\n'
)

# 每日学习
html += (
    '<section class="daily-mod" id="home">'
    '<div class="daily-card">'
    '<div class="daily-head">'
    '<div class="ring"><svg width="84" height="84">'
    '<defs><linearGradient id="goldGrad" x1="0" y1="0" x2="1" y2="1">'
    '<stop offset="0" stop-color="#c9a84c"/><stop offset="1" stop-color="#e8d48b"/></linearGradient></defs>'
    '<circle class="ring-bg" cx="42" cy="42" r="35"/><circle class="ring-fg" cx="42" cy="42" r="35"/>'
    '</svg><div class="ring-txt"><b>35%</b><span>今日</span></div></div>'
    '<div class="daily-info">'
    '<div class="d-row"><span class="lb">🔥</span><b>连续学习 7 天</b></div>'
    '<div class="d-row"><span class="lb">⏱</span><b>今日学习 15 分钟</b></div>'
    '<div class="d-row"><span class="lb">🎯</span><b>今日目标：学习 20 个单词</b></div>'
    '</div></div>'
    '<div class="daily-goal"><div class="g-head"><span>今日进度</span><span id="goalTxt">0 / 20 单词</span></div>'
    '<div class="g-bar"><i id="goalBar"></i></div>'
    '<button class="act-btn" style="margin-top:10px" onclick="checkIn()">✅ 打卡学习</button></div>'
    '</div></section>\\n'
)

# 数据卡片
html += (
    '<div class="action-row"><button class="act-btn" onclick="showAllSentences()">📖 全部句子</button><button class="act-btn" onclick="showLibrary()">📚 图书馆</button><button class="act-btn" onclick="showVocab()">📚 词汇表</button><button class="act-btn" onclick="showBooks()">📕 书籍</button><button class="act-btn" onclick="showQuran()">🕌 古兰经</button><button class="act-btn" onclick="showFlashcard()">🃏 闪卡</button><button class="act-btn" onclick="showQuiz()">📝 测验</button></div>'
    '<div class="stat-row">'
    '<div class="stat-card" onclick="nav(2)"><div class="ic">📖</div><div class="num stat-num" data-num="%d">0</div><div class="lb">已学习句子</div></div>'
    '<div class="stat-card" onclick="nav(2)"><div class="ic">📚</div><div class="num stat-num" data-num="%d">0</div><div class="lb">掌握词汇</div></div>'
    '<div class="stat-card" onclick="nav(2)"><div class="ic">🕌</div><div class="num stat-num" data-num="%d">0</div><div class="lb">学习分类</div></div>'
    '</div>\\n' % (TOTAL_SENT, TOTAL_WORDS, TOTAL_CATS)
)

# 功能入口
html += (
    '<div class="entr-row">'
    '<div class="entr" onclick="alert(\'🎧 听力训练即将上线\\n每天10分钟阿拉伯语听力\')"><div class="e-ic">🎧</div>'
    '<div class="e-tx"><b>听力训练</b><span>每天 10 分钟 · 阿语听力</span></div><div class="e-go">›</div></div>'
    '<div class="entr" onclick="ec()"><div class="e-ic">🗣</div>'
    '<div class="e-tx"><b>AI 口语陪练</b><span>和 AI 阿拉伯语老师对话</span></div><div class="e-go">›</div></div>'
    '<div class="entr" onclick="document.getElementById(\'quote\').scrollIntoView({behavior:\'smooth\'})"><div class="e-ic">📖</div>'
    '<div class="e-tx"><b>每日一句</b><span>每天推荐一句经典阿拉伯语</span></div><div class="e-go">›</div></div>'
    '</div>\\n'
)

# 分类标题 + 导航
html += (
    '<div class="sec-title"><h2>📚 学习分类</h2></div>'
    '<div class="cat-scroll">' + TABS_HTML + '</div>\\n'
)

# 句子列表
html += (
    '<div class="list-wrap">'
    '<div class="list-head"><span class="tt" id="listCount">全部 · ' + str(TOTAL_SENT) + ' 句（每类显示前25句）</span></div>'
    '<div id="sList">' + ALL_CARDS + '</div>'
    '</div>\\n'
)


# AI 小精灵
html += (
    '<div class="elf">'
    '<div class="elf-panel" id="ep">'
    '<div class="elf-hd"><span>🧞</span><b>AI 阿拉伯语老师</b><span class="bd">DeepSeek</span>'
    '<button class="cl" onclick="ec()">✕</button></div>'
    '<div class="elf-body" id="em">'
    '<div class="ef-msg bot"><div class="bb"><span class="ar">أَهْلًا بِكَ يَا صَدِيقِي!</span>'
    '<span class="tr">亲爱的朋友，欢迎你来学习！翻译 · 纠错 · 发音 · 情景练习，我都能帮你 🧞</span></div></div>'
    '</div>'
    '<div class="ef-inp"><input id="ei" placeholder="输入阿语/中文/英语..." onkeydown="if(event.key===\'Enter\')es()">'
    '<button id="eiSend" onclick="es()">➤</button></div>'
    '</div>'
    '<button class="elf-btn" id="eb" onclick="ec()">🧞</button>'
    '</div>\\n'
)

# 底部导航
html += (
    '<!-- 模态框 --><div class="modal" id="mSentences"><div class="m-head"><span>📖</span><b>全部句子</b><button class="m-close" onclick="closeModal(\'mSentences\')">✕</button></div><div class="m-search"><input id="mSentSearch" placeholder="🔍 搜索句子..." oninput="renderAllS()"></div><div class="m-body" id="mSentBody"></div><div class="m-count" id="mSentCount"></div></div>'
    '<div class="modal" id="mVocab"><div class="m-head"><span>📚</span><b>词汇表</b><button class="m-close" onclick="closeModal(\'mVocab\')">✕</button></div><div class="m-search"><input id="mVocabSearch" placeholder="🔍 搜索词汇..." oninput="renderVocab()"></div><div class="m-body" id="mVocabBody"></div><div class="m-count" id="mVocabCount"></div></div>'
'<div class="modal" id="mLibrary"><div class="m-head"><span>📚</span><b>图书馆 · 阿拉伯语文章</b><button class="m-close" onclick="closeModal(\'mLibrary\')">✕</button></div>' + '<div class="m-search" style="gap:6px;flex-wrap:wrap"><span style="font-size:10px;color:#999;white-space:nowrap">✨ AI 写文章:</span><button class="s-btn" style="width:auto;padding:4px 10px" onclick="aiWrite(\'القهوة\')">☕ 咖啡</button><button class="s-btn" style="width:auto;padding:4px 10px" onclick="aiWrite(\'رمضان\')">🌙 斋月</button><button class="s-btn" style="width:auto;padding:4px 10px" onclick="aiWrite(\'السفر\')">✈️ 旅行</button><button class="s-btn" style="width:auto;padding:4px 10px" onclick="aiWrite(\'القدس\')">🕌 耶路撒冷</button><button class="s-btn" style="width:auto;padding:4px 10px" onclick="aiWrite(\'العلم\')">🔬 科学</button><button class="s-btn" style="width:auto;padding:4px 10px" onclick="aiWrite(\'الربيع\')">🌸 春天</button></div>' + '<div class="m-body" id="mLibBody"></div><div class="m-count" id="mLibCount"></div></div>'
    '<div class="modal" id="mExplain"><div class="m-head"><span>✂️</span><b>单词拆解 · AI 逐词解释</b><button class="m-close" onclick="closeModal(\'mExplain\')">✕</button></div><div class="m-body" id="mExplainBody" style="padding:16px"></div></div>' +
    '<div class="modal" id="mQuran"><div class="m-head"><span>🕌</span><b>古兰经 · 114 章</b><button class="m-close" onclick="closeModal(\'mQuran\')">✕</button></div><div class="m-search"><input id="mQuranSearch" placeholder="🔍 搜索章节..." oninput="renderQuranList()"></div><div class="m-body" id="mQuranBody"></div><div class="m-count" id="mQuranCount"></div></div>' +
    '<div class="modal" id="mFlash"><div class="m-head"><span>🃏</span><b id="mFlashHead">闪卡</b><button class="m-close" onclick="closeModal(\'mFlash\')">✕</button></div><div class="m-body" id="mFlashBody"></div></div>' +
    '<div class="modal" id="mQuiz"><div class="m-head"><span>📝</span><b id="mQuizHead">测验</b><button class="m-close" onclick="closeModal(\'mQuiz\')">✕</button></div><div class="m-body" id="mQuizBody"></div></div>' +
    '<div class="modal" id="mRead"><div class="m-head"><span>📖</span><b id="mReadTitle">文章</b><button class="m-close" onclick="closeModal(\'mRead\')">✕</button></div><div class="m-body" id="mReadBody"></div></div>'
    '<nav class="tabbar">'
    '<button class="tb on" data-tab="home" onclick="nav(\'home\')"><span class="t-ic">🏠</span><span class="t-nm">首页</span></button>'
    '<button class="tb" data-tab="learn" onclick="nav(\'learn\')"><span class="t-ic">📚</span><span class="t-nm">学习</span></button>'
    '<button class="tb" data-tab="listen" onclick="nav(\'listen\')"><span class="t-ic">🎧</span><span class="t-nm">听力</span></button>'
    '<button class="tb" data-tab="ai" onclick="nav(\'ai\')"><span class="t-ic">🤖</span><span class="t-nm">AI老师</span></button>'
    '<button class="tb" data-tab="me" onclick="nav(\'me\')"><span class="t-ic">👤</span><span class="t-nm">我的</span></button>'
    '</nav>\\n'
)


# ===== 内置数据（离线可用：全部句子/词汇表/文章）=====
import re as _re
_bdata = json.load(open(DIR / 'data' / 'categorized.json', encoding='utf-8'))
_bsent = [{'a': it['ar'], 'e': it['en'], 'c': it['cn'], 'cat': it['cat']} for it in _bdata]
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
_bvmean = json.loads(open('app/src/vocabData.js', encoding='utf-8').read().split('module.exports = ')[1].rstrip().rstrip(';'))
BUILTIN_JS = (
    'var BUILTIN_SENTENCES = ' + json.dumps(_bsent, ensure_ascii=False) + ';\n'
    'var BUILTIN_VOCAB = ' + json.dumps(_bvocab, ensure_ascii=False) + ';\n'
    'var BUILTIN_ARTICLES = ' + json.dumps(_barts, ensure_ascii=False) + ';\n'
    'var BUILTIN_BOOKS = ' + json.dumps(_bbooks, ensure_ascii=False) + ';\n'
    'var BUILTIN_QURAN = ' + json.dumps(_bquran, ensure_ascii=False) + ';\n'
    'var BUILTIN_VOCAB_MEANINGS = ' + json.dumps(_bvmean, ensure_ascii=False) + ';\n'
    'var BUILTIN_QUOTES = ' + json.dumps(_bquotes, ensure_ascii=False) + ';\n'
)

# JS
# 版本信息 footer
from datetime import datetime as _dt
_built = _dt.now().strftime('%Y-%m-%d %H:%M')
footer = (
    '<div style="text-align:center;padding:18px 16px 80px;font-size:10px;color:#9a9f9c">'
    '<div id="serverStatus" style="font-weight:700;margin-bottom:4px">··· 检测服务器 ···</div>'
    'حاملُ المِصباح، صامتٌ لكنّه يهدي إلى الطريق · 燃灯者 &nbsp;|&nbsp; 句子 %d 句 · 词汇 %d 词 · 文章 %d 篇 &nbsp;|&nbsp; 构建 %s'
    '</div>'
    % (len(_bsent), len(_bvocab), len(_barts), _built)
)
html += footer + '<script>\n' + BUILTIN_JS + (JS % json.dumps(CAT_NAMES, ensure_ascii=False)) + '\n</script>\n<script>checkServer();updateStats();</script>\n</body>\n</html>'

out = DIR / 'arabic_learning.html'
if len(sys.argv) > 1:
    out = Path(sys.argv[1])
out.write_text(html, encoding='utf-8')
print(f'✅ 高级版主页生成: {out.stat().st_size/1024:.0f}KB')
print(f'   句子: {TOTAL_SENT} | 单词: {TOTAL_WORDS} | 分类: {TOTAL_CATS}')
