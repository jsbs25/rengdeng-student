/* 首页内容区（重建版）：点左侧分类 → 内容在书架下方切换 */
var HS_TAB = 0;

function hsGo(i, el){
  try{
    HS_TAB = parseInt(i, 10) || 0;
    var rail = document.getElementById('tkSeg');
    if(rail) Array.prototype.forEach.call(rail.querySelectorAll('.chip'), function(c){ c.classList.remove('on'); });
    if(el) el.classList.add('on');
    hsRender();
  }catch(e){}
}
function hsTitle(t, sub){
  var e = document.getElementById('hsSecTitle'); if(e) e.textContent = t;
  var s = document.getElementById('hsSecSub'); if(s) s.textContent = sub || '';
}
function hsSet(html){
  try{
    var d = document.getElementById('mDict');
    if(d && d.classList.contains('inline') && window.__DICT_HOME){
      window.__DICT_HOME.appendChild(d); d.classList.remove('inline');
    }
  }catch(e){}
  var g = document.getElementById('tkBooks'); if(g) g.innerHTML = html;
}
function hsLoad(msg){ hsSet('<div class="hs-load">' + (msg || '载入中…') + '</div>'); }

function hsRender(){
  try{ if(typeof hsToday === 'function') hsToday(); }catch(e){}
  var K = window.HS_K || [];
  var x = K[HS_TAB] || K[0] || {};
  var key = x.k || 'books';
  if(key === 'books') return hsBooks();
  if(key === 'library') return hsLibrary();
  if(key === 'quran') return hsQuran();
  if(key === 'h6') return hsH6();
  if(key === 'intro') return hsIntro();
  if(key === 'grammar') return hsSubjectBooks('grammar');
  if(key === 'morph') return hsSubjectBooks('morph');
  if(key === 'talk') return hsTalk();
  if(key === 'listen') return hsListen();
  if(key === 'sent') return hsSent();
  if(key === 'belt') return hsBelt();
  if(key === 'dict') return hsDictInline();
  if(key === 'search') return hsSearch();
  return hsBooks();
}

/* 书卡 */
function hsCoverCard(b){
  var t = String((b && b.t) || '');
  var id = String((b && b.id) || '');
  var rt = String((b && b.rt) || 'shamela');
  var isCN = !!(b && b.cn);
  var isZY = !!(b && b.zy);
  var short = t.length > 20 ? (t.slice(0, 20) + '…') : t;
  var short2 = t.length > 28 ? (t.slice(0, 28) + '…') : t;
  // 统一精装封面配色（按类别分色系，像一套出版社丛书）
  var PAL = isCN ? ['#0e3b2a','#14342e','#1f3a2d','#2b2a24','#3a2f28','#243b34']
          : (isZY ? ['#3f6f7a','#2f6f9f','#4e7f96','#7d93a6']
                  : ['#0f5132','#14805a','#1d6f5a','#255f4a','#166534','#0d4f3a']);
  var c = PAL[(t.length + id.length) % PAL.length];
  var cat = isCN ? '中文古籍' : (isZY ? '六大部' : '阿拉伯典籍');
  var csrc = (window.__COVERS && window.__COVERS[t]) ? window.__COVERS[t] : (API_BASE() + '/api/cover?t=' + encodeURIComponent(t));
  var img = '<img class="bkimg" src="' + csrc + '" alt="" loading="lazy" onerror="this.remove()">';
  var typo = ''
    + '<div class="bk-face">'
    +   '<div class="bk-line"></div>'
    +   '<div class="bk-orn">❖</div>'
    +   '<div class="bk-ttl"' + (isCN ? ' data-cn="1"' : '') + ' dir="' + (isCN ? 'ltr' : 'rtl') + '">' + short + '</div>'
    +   '<div class="bk-rule"></div>'
    +   '<div class="bk-sub">' + (isCN ? '古典名著' : (isZY ? '圣训六部' : '阿拉伯典籍')) + '</div>'
    + '</div>';
  return '<div data-bid="' + id + '" data-rt="' + rt + '" class="bkcard" onclick="tkOpen(this)">'
    + '<div class="bkcov" style="background:linear-gradient(165deg,' + c + ' 0%,#061d14 100%)">'
    + typo + img
    + '<div class="bk-gloss"></div>'
    + '</div>'
    + '<b class="bkname">' + short2 + '</b><span class="bkcat">' + cat + '</span></div>';
}


var HS_NOVELS = [
  ['红楼梦','005817'], ['三国演义','004434'], ['水浒传','005465'], ['西游记','006024'],
  ['聊斋志异','005878'], ['镜花缘','006179'], ['儒林外史','004608'], ['封神演义','004990'],
  ['儿女英雄传','004609'], ['花月痕','005900'], ['海上花魅影','005523'], ['隋唐演义','006210']
];

function hsSupport(){
  return '<div class="sup-card" onclick="openDonate()">'
    + '<span class="sup-heart">💖</span>'
    + '<span class="sup-b"><b>支持燃灯同学</b>'
    + '<em>一盏灯，一份心意 · 用于服务器与 AI</em></span>'
    + '<span class="sup-btn">支持 ›</span></div>';
}

function hsRow(icon, t, sub, act, head){
  return '<div class="hs-row' + (head ? ' hs-head' : '') + '" ' + (act ? ('onclick="' + act + '"') : '') + '>'
    + '<span class="hs-row-i">' + (icon || '•') + '</span>'
    + '<span class="hs-row-b"><b>' + t + '</b>' + (sub ? ('<em>' + sub + '</em>') : '') + '</span>'
    + '<span class="hs-row-a">›</span></div>';
}

function hsPick(pool, n){
  var a = pool.slice(), out = [];
  for(var i = 0; i < n && a.length; i++){
    out.push(a.splice(Math.floor(Math.random() * a.length), 1)[0]);
  }
  return out;
}

async function hsBooks(){
  hsTitle('书架', '每次打开都不一样');
  hsLoad('载入书库…');
  var novels = [], lit = [];
  try{ var d1 = await (await fetch(API_BASE() + '/data/library/novels_pool.json?t=' + Date.now())).json();
       novels = (d1.items || []); }catch(e){}
  try{ var d2 = await (await fetch(API_BASE() + '/data/library/lit_pool.json?t=' + Date.now())).json();
       lit = (d2.items || []); }catch(e){}
  if(!novels.length && !lit.length){ hsSet('<div class="hs-load">书库载入失败</div>'); return; }
  var _novCov = novels.filter(function(x){ return x.cov; });
  var _litCov = lit.filter(function(x){ return x.cov; });
  var novP = hsPick(_novCov.length >= 12 ? _novCov : novels, 12);
  var litP = hsPick(_litCov.length >= 12 ? _litCov : lit, 12);
  var cnEl = document.getElementById('hsSecSub');
  if(cnEl) cnEl.textContent = '共 ' + (novels.length + lit.length).toLocaleString() + ' 本';
  hsSet(hsRow('📖', '古典名著', '从 ' + novels.length.toLocaleString() + ' 本里随机挑 12 本 · 每次不同', "openReadById('" + (novP[0] ? novP[0].id : '005817') + "','cn')", 1)
    + novP.map(hsCoverCard).join('')
    + hsRow('🌍', '文学作品', '阿拉伯语 + 中文 · 从 ' + lit.length.toLocaleString() + ' 本里随机挑 12 本', '', 1)
    + litP.map(hsCoverCard).join('')
    + hsRow('🔄', '换一批', '重新随机 24 本', 'hsRender()', 1)
    + hsRow('📚', '更多书目', '世界书库：阿语 23,835 · 中文 15,699', "hsGo(1, document.querySelectorAll('#tkSeg .chip')[1])", 1)
    + hsSupport());
}


async function hsLibrary(){
  hsTitle('世界书库', '阿拉伯 · 历史 · 中国古籍');
  hsLoad('载入书库…');
  var items = [];
  try{ var d = await (await fetch(API_BASE() + '/api/catalog?page=0&size=60')).json();
       (d.items || []).filter(function(b){ return b.r; }).slice(0, 40).forEach(function(b){
         items.push({ t: b.t, id: (b.r||{}).id, rt: (b.r||{}).t || 'shamela' });
       }); }catch(e){}
  try{ var d2 = await (await fetch(API_BASE() + '/api/cnbooks?size=40')).json();
       (d2.books || d2.items || []).slice(0, 40).forEach(function(b){
         items.push({ t: b.title, id: b.id, rt: 'cn', cn: true });
       }); }catch(e){}
  if(!items.length){ hsSet('<div class="hs-load">暂无书目</div>'); return; }
  hsSet(hsRow('🕌', '六大部（圣训六部合集）', '34,153 段 · 阿语原典 + 中文', 'showH6()')
    + items.map(hsCoverCard).join('') + hsSupport());
}

async function hsQuran(){
  try{ await window.NOUR_loadDataAsset('quran'); }catch(e){}
  hsTitle('古兰经与经注', '114 章 · 阿拉伯原文 · 中文译文 · 真人诵读');
  var Q = window.BUILTIN_QURAN || [];
  var h = hsRow('🕌', '古兰经 · 114 章', '逐章阅读原文与中文译文，点开后可播放真人诵读', 'showQuran()', 1);
  h += hsRow('📖', '按章查看经注', '独立显示阿拉伯语经注版本，不混入经文原文', 'showTafsir(1)', 1);
  h += hsRow('🎙', '真人诵读选择', '阅读器内选择诵读家，保持经文与音频分层', 'showQuran()', 1);
  if(Q.length){
    h += '<div class="ghint" style="grid-column:1/-1;margin:10px 0 2px">热门章节 · 点开直接学习</div>';
    h += Q.slice(0, 8).map(function(s){
      return '<div class="bkcard" onclick="openSurahById(' + s.id + ')"><div class="bkcov" style="background:linear-gradient(150deg,#14503e,#071d16)"><div class="bktitle" style="font-family:var(--ar-font)">' + catEsc(s.n || '') + '</div></div><b class="bkname">' + catEsc(s.tz || '') + '</b><span class="bkcat">' + (s.vs || []).length + ' 节 · ' + catEsc(s.ty === 'meccan' ? '麦加章' : '麦地那章') + '</span></div>';
    }).join('');
  }
  hsSet(h);
}


async function hsH6(){
  try{ openModal('mH6'); }catch(e){}
  hsTitle('六大部', '圣训六部合集 · 阿语原典 + 中文');
  hsLoad('载入六大部…');
  var d = null;
  try{ d = await (await fetch(API_BASE() + '/data/hadith/index.json')).json(); }catch(e){}
  if(!d || !(d.books || []).length){ hsSet('<div class="hs-load">载入失败</div>'); return; }
  var cols = ['#14503e','#0f5132','#2f6f9f','#4e7f96','#8a6d2b','#3f6f7a'];
  hsSet((d.books || []).map(function(x, i){
    return '<div class="bkcard" onclick="openH6Book(\'' + x.key + '\')">'
      + '<div class="bkcov" style="background:linear-gradient(150deg,' + cols[i % cols.length] + ',#0a2b1f)">'
      + '<div class="bktitle" style="font-family:var(--ar-font)">' + x.ar + '</div></div>'
      + '<b class="bkname">' + x.cn + '</b><span class="bkcat">' + x.n + ' 段</span></div>';
  }).join(''));
}

async function hsIntro(){
  try{ await window.NOUR_loadDataAsset('vocab'); }catch(e){}
  hsTitle('阿拉伯语入门', '字母 · 发音 · 基础词汇');
  hsLoad('载入…');
  var A = window.BUILTIN_ALPHABET || [];
  var V = window.BUILTIN_VOCAB || [];
  var M = window.BUILTIN_VOCAB_MEANINGS || {};
  var h = '';
  A.slice(0, 28).forEach(function(x){
    var ar = x.ar || x.letter || '';
    return h += '<div class="hs-row"><span class="hs-row-i" style="font-family:var(--ar-font);font-size:20px">' + ar + '</span>'
      + '<span class="hs-row-b"><b>' + (x.name || x.cn || '') + '</b><em>' + (x.sound || x.py || '') + '</em></span>'
      + '<span class="hs-row-a"><button class="s-btn" style="width:auto;padding:4px 9px" onclick="ap(this,0,&#39;' + ar + '&#39;)">🔊</button></span></div>';
  });
  if(V.length){
    h += '<div class="ghint" style="grid-column:1/-1;margin-top:12px">高频词（点 🔊 听发音）</div>';
    V.slice(0, 40).forEach(function(v){
      var ar = v.w || v.a || '';
      var cn = M[ar] || v.c || '';
      if(!ar) return;
      h += '<div class="hs-row"><span class="hs-row-i" style="font-family:var(--ar-font);font-size:18px">' + ar + '</span>'
        + '<span class="hs-row-b"><b style="font-weight:600">' + cn + '</b></span>'
        + '<span class="hs-row-a"><button class="s-btn" style="width:auto;padding:4px 9px" onclick="dictPick(&#39;' + ar + '&#39;)">查</button>'
        + '<button class="s-btn" style="width:auto;padding:4px 9px" onclick="ap(this,0,&#39;' + ar + '&#39;)">🔊</button></span></div>';
    });
  }
  hsSet(h || '<div class="hs-load">暂无内容</div>');
}

function hsGrammar(d, title, sub){
  hsTitle(title, sub);
  window.__HS_LESSONS = d;
  if(!d.length){ hsSet('<div class="hs-load">暂无课程</div>'); return; }
  hsSet(d.map(function(x, i){
    return hsRow('📘', x.title, (x.title_ar || '') + ' · ' + ((x.points || []).length) + ' 个要点', 'hsLesson(' + i + ')');
  }).join(''));
}

function hsLesson(i){
  var d = window.__HS_LESSONS || [];
  var x = d[i]; if(!x) return;
  var back = hsRow('‹', '返回课程列表', '', 'hsRender()');
  var h = back + '<div class="hs-detail"><div class="hs-dt"><b>' + x.title + '</b><span>' + (x.title_ar || '') + '</span></div>'
    + '<div class="hs-di">' + x.intro + '</div><table class="gtable">';
  (x.points || []).forEach(function(p){
    h += '<tr><td class="gar">' + p.ar + '</td><td class="gcn">' + p.cn
      + (p.note ? ('<div class="gnote">' + p.note + '</div>') : '') + '</td>'
      + '<td class="gsp"><button class="s-btn gspk" onclick="ap(this,0,&#39;' + p.ar + '&#39;)">🔊</button></td></tr>';
  });
  h += '</table>' + (x.tip ? ('<div class="gtip">💡 ' + x.tip + '</div>') : '') + '</div>';
  hsSet(h);
}

function hsTalk(){
  hsTitle('日常口语', '场景对话 · 阿中对照');
  var D = window.BUILTIN_DIALOGUES || [];
  window.__HS_TALK = D;
  if(!D.length){ hsSet('<div class="hs-load">暂无对话</div>'); return; }
  hsSet(D.map(function(x, i){
    return hsRow(x.icon || '🗣', x.scene, (x.scene_ar || '') + ' · ' + ((x.dialogue || []).length) + ' 句', 'hsTalkItem(' + i + ')');
  }).join(''));
}

function hsTalkItem(i){
  var D = window.__HS_TALK || [];
  var x = D[i]; if(!x) return;
  var h = hsRow('‹', '返回场景列表', '', 'hsTalk()');
  h += '<div class="hs-detail"><div class="hs-dt"><b>' + x.scene + '</b><span>' + (x.scene_ar || '') + '</span></div>';
  (x.dialogue || []).forEach(function(l){
    var ar = l.a || '';
    h += '<div class="hs-line"><div class="hs-line-ar" dir="rtl">' + ar + '</div>'
      + (l.c ? ('<div class="hs-line-cn">' + l.c + '</div>') : '')
      + '<button class="s-btn" style="width:auto;padding:4px 9px;margin-top:4px" onclick="ap(this,0,&#39;' + ar + '&#39;)">🔊</button></div>';
  });
  hsSet(h + '</div>');
}

function hsListen(){
  hsTitle('听力训练', '随机句子 · 点击 🔊 跟读');
  var S = (window.BUILTIN_SENTENCES || []).filter(function(s){ return s.a && (s.c || s.e); });
  if(!S.length){ hsSet('<div class="hs-load">暂无句子</div>'); return; }
  var pick = [];
  for(var i = 0; i < 24 && i < S.length; i++){ pick.push(S[Math.floor(Math.random() * S.length)]); }
  hsSet(pick.map(function(s){
    return '<div class="hs-row"><span class="hs-row-i" style="font-family:var(--ar-font);font-size:17px">' + s.a + '</span>'
      + '<span class="hs-row-b"><em>' + (s.c || '') + '</em></span>'
      + '<span class="hs-row-a"><button class="s-btn" style="width:auto;padding:4px 9px" onclick="ap(this,0,&#39;' + s.a + '&#39;)">🔊</button></span></div>';
  }).join(''));
}

var HS_CATS = [
  ['greeting','问候寒暄','🖐'], ['daily','日常用语','☀️'], ['family','家庭亲友','👨‍👩‍👧'],
  ['food','就餐饮食','🍽'], ['travel','出行旅游','🧳'], ['shopping','逛街购物','🛍'],
  ['study','学校学习','📚'], ['work','工作职场','💼'], ['weather','天气气候','🌤'],
  ['health','看病健康','🩺'], ['hobby','兴趣爱好','🎨'], ['jordan_greet','约旦·问候','🇯🇴'],
  ['jordan_daily','约旦·日常','🇯🇴'], ['jordan_airport','约旦·机场','✈️'], ['jordan_hotel','约旦·住宿','🏨'],
  ['jordan_food','约旦·吃饭','🍽'], ['jordan_shop','约旦·购物','🛍'], ['jordan_dir','约旦·问路','🧭'],
  ['jordan_campus','约旦·校园','🎓'], ['jordan_emerg','约旦·应急','🚑'], ['jordan_social','约旦·社交','🤝']
];

function hsSent(){
  hsTitle('句子库', '按场景分类 · 点开看句子');
  var S = window.BUILTIN_SENTENCES || [];
  window.__HS_SENT = S;
  var cnt = {};
  S.forEach(function(s){ cnt[s.cat] = (cnt[s.cat] || 0) + 1; });
  var h = HS_CATS.map(function(c){
    var n = cnt[c[0]] || 0;
    return n ? hsRow(c[2], c[1], n + ' 句', "hsSentCat('" + c[0] + "','" + c[1] + "')") : '';
  }).join('');
  h += hsRow('📦', '其它常用句', (cnt['other'] || 0) + ' 句', "hsSentCat('other','其它常用句')");
  hsSet(h);
}

function hsSentCat(cat, name){
  var S = window.__HS_SENT || [];
  var all = S.filter(function(s){ return s.cat === cat; });
  window.__HS_SCAT = { cat: cat, name: name, all: all, n: 200 };
  var list = all.slice(0, 200);
  hsTitle(name, '共 ' + all.length + ' 句 · 显示前 ' + list.length + ' 句');
  var h = hsRow('‹', '返回分类', '', 'hsSent()');
  h += list.map(function(s){
    return '<div class="hs-row"><span class="hs-row-i" style="font-family:var(--ar-font);font-size:17px">' + s.a + '</span>'
      + '<span class="hs-row-b"><em>' + (s.c || '') + '</em></span>'
      + '<span class="hs-row-a"><button class="s-btn" style="width:auto;padding:4px 9px" onclick="ap(this,0,&#39;' + s.a + '&#39;)">🔊</button></span></div>';
  }).join('');
  if(all.length > list.length){
    h += hsRow('⬇️', '加载更多', '还有 ' + (all.length - list.length) + ' 句', 'hsSentMore()');
  }
  hsSet(h);
}

function hsSentMore(){
  var st = window.__HS_SCAT; if(!st) return;
  st.n += 200;
  var list = st.all.slice(0, st.n);
  hsTitle(st.name, '共 ' + st.all.length + ' 句 · 显示前 ' + list.length + ' 句');
  var h = hsRow('‹', '返回分类', '', 'hsSent()');
  h += list.map(function(s){
    return '<div class="hs-row"><span class="hs-row-i" style="font-family:var(--ar-font);font-size:17px">' + s.a + '</span>'
      + '<span class="hs-row-b"><em>' + (s.c || '') + '</em></span>'
      + '<span class="hs-row-a"><button class="s-btn" style="width:auto;padding:4px 9px" onclick="ap(this,0,&#39;' + s.a + '&#39;)">🔊</button></span></div>';
  }).join('');
  if(st.all.length > list.length) h += hsRow('⬇️', '加载更多', '还有 ' + (st.all.length - list.length) + ' 句', 'hsSentMore()');
  hsSet(h);
}

async function hsBelt(){
  hsTitle('中阿要闻', '每小时自动抓取真新闻');
  hsLoad('读取最新资讯…');
  var d = null;
  try{ d = await (await fetch(API_BASE() + '/data/beltroad.json')).json(); }catch(e){}
  var items = (d && d.items) || [];
  if(!items.length){ hsSet('<div class="hs-load">暂无数据</div>'); return; }
  hsSet(items.slice(0, 30).map(function(x){
    return '<div class="belt-card"><div class="belt-b"><div class="belt-cn">' + x.title + '</div>'
      + (x.ar ? ('<div class="belt-ar" dir="rtl">' + x.ar + '</div>') : '')
      + '<div class="belt-meta">' + (x.source || '') + (x.pub ? (' · ' + x.pub) : '')
      + (x.link ? (' <a class="belt-link" href="' + x.link + '" target="_blank" rel="noopener">原文 ›</a>') : '') + '</div></div></div>';
  }).join(''));
}

/* ===== 查词典（内嵌：左输入 / 右答案） ===== */
function hsDictInline(){
  hsTitle('查词典', '左边输入 · 右边出答案');
  var g = document.getElementById('tkBooks');
  var md = document.getElementById('mDict');
  if(g && md){
    window.__DICT_HOME = window.__DICT_HOME || md.parentNode;
    g.innerHTML = '';
    md.classList.add('inline');
    md.classList.remove('show');
    g.appendChild(md);
    try{ hsDictInit(); }catch(e){}
    setTimeout(function(){ var q = document.getElementById('dictQ'); if(q) try{ q.focus(); }catch(e){} }, 180);
  }
}

function hsDictInit(){
  var q = document.getElementById('dictQ');
  if(!q) return;
  var wrap = q.parentNode;
  try{ wrap.style.position = 'relative'; }catch(e){}
  if(!document.getElementById('dictSug')){
    var d = document.createElement('div');
    d.id = 'dictSug'; d.className = 'dict-sug';
    wrap.appendChild(d);
  }
  if(!document.getElementById('dictRecents')){
    var r = document.createElement('div');
    r.id = 'dictRecents'; r.className = 'dict-recents';
    try{ wrap.parentNode.appendChild(r); }catch(e){}
  }
  if(!q.dataset.ac){
    q.dataset.ac = '1';
    q.setAttribute('autocomplete', 'off');
    q.addEventListener('input', function(){ dictSuggest(); });
    q.addEventListener('blur', function(){ setTimeout(function(){ var b = document.getElementById('dictSug'); if(b) b.classList.remove('on'); }, 180); });
  }
  dictRecents();
}

function _dbKey(s){ try{ if(typeof _stripTashkeel === 'function') return _stripTashkeel(s); }catch(e){} return s; }

function dictSuggest(){
  var q = document.getElementById('dictQ');
  var box = document.getElementById('dictSug');
  if(!q || !box) return;
  var v = (q.value || '').trim();
  var seq = (window.__DICT_SUG_SEQ || 0) + 1;
  window.__DICT_SUG_SEQ = seq;
  if(v.length < 1){ box.innerHTML = ''; box.classList.remove('on'); return; }
  function render(items){
    if(seq !== window.__DICT_SUG_SEQ) return;
    items = (items || []).filter(function(x){return x && (x.w || x.normalized);}).slice(0, 8);
    if(!items.length){ box.innerHTML = ''; box.classList.remove('on'); return; }
    box.innerHTML = items.map(function(x){
      var w = String(x.w || x.normalized || '');
      var label = String(x.cn || x.en || '');
      return '<div class="dict-sug-i" onmousedown="dictPick(decodeURIComponent(\''
        + encodeURIComponent(w) + '\'))"><b dir="rtl" lang="ar">'
        + esc(w) + '</b><em>' + esc(label) + '</em></div>';
    }).join('');
    box.classList.add('on');
  }
  var local = [];
  var M = window.BUILTIN_VOCAB_MEANINGS || {};
  var V = window.BUILTIN_VOCAB || [];
  var key = _dbKey(v);
  Object.keys(M).some(function(w){
    if((w.indexOf(v) === 0 || _dbKey(w).indexOf(key) === 0) && local.length < 8){
      local.push({w:w, cn:(M[w] && (M[w].cn || M[w].en)) || ''});
    }
    return local.length >= 8;
  });
  for(var i = 0; i < V.length && local.length < 8; i++){
    var vw = (V[i] && (V[i].w || V[i].a || V[i].ar)) || '';
    if(vw && (vw.indexOf(v) === 0 || _dbKey(vw).indexOf(key) === 0)){
      if(!local.some(function(x){return x.w === vw;})) local.push({w:vw, cn:''});
    }
  }
  render(local);
  try{
    fetch(API_BASE() + '/api/dict/suggest?q=' + encodeURIComponent(v) + '&limit=8', {cache:'no-store'})
      .then(function(r){return r.json();})
      .then(function(d){ if(seq !== window.__DICT_SUG_SEQ) return; render((d && d.items && d.items.length) ? d.items : local); })
      .catch(function(){ render(local); });
  }catch(e){ render(local); }
}
function dictPick(w){
  var q = document.getElementById('dictQ');
  if(q) q.value = w;
  var box = document.getElementById('dictSug'); if(box){ box.classList.remove('on'); box.innerHTML = ''; }
  try{ if(typeof dictSearch === 'function') dictSearch(); }catch(e){}
  dictRemember(w);
}

function dictRemember(w){
  try{
    var a = JSON.parse(localStorage.getItem('nur_dict_hist') || '[]');
    a = a.filter(function(x){ return x !== w; });
    a.unshift(w);
    localStorage.setItem('nur_dict_hist', JSON.stringify(a.slice(0, 8)));
  }catch(e){}
  dictRecents();
}

function dictRecents(){
  var box = document.getElementById('dictRecents');
  if(!box) return;
  var a = [];
  try{ a = JSON.parse(localStorage.getItem('nur_dict_hist') || '[]'); }catch(e){}
  if(!a.length){
    box.innerHTML = '<div class="dr-t">常用词快查</div><div class="dr-c">'
      + ['كِتاب','ماء','ذَهَبَ','كَبير','عِلْم','قَلَم'].map(function(w){
          return '<span onmousedown="dictPick(&#39;' + w + '&#39;)">' + w + '</span>';
        }).join('') + '</div>';
    return;
  }
  box.innerHTML = '<div class="dr-t">最近查询</div><div class="dr-c">' + a.map(function(w){
    return '<span onmousedown="dictPick(&#39;' + w + '&#39;)">' + w + '</span>';
  }).join('') + '</div>';
}

/* ===== 全站搜索（栏目 + 大搜索框） ===== */
function hsSearch(){
  hsTitle('搜索', '书名 · 句子 · 词汇 · 全文');
  hsSet('<div class="srch-box"><span class="srch-bi">🔍</span>'
    + '<input id="hsQ" placeholder="输入关键词，回车搜索…" onkeydown="if(event.key===&#39;Enter&#39;){hsDoSearch()}" oninput="hsSearchSoon()" autocomplete="off">'
    + '<button class="srch-bt" onclick="hsDoSearch()">搜索</button></div>'
    + '<div class="srch-tips">试试：三国演义 · 红楼梦 · تاريخ · كِتاب</div>'
    + '<div id="hsSrchHist" class="dict-recents" style="padding:12px 0 0"></div>'
    + '<div id="hsRes" class="srch-res"></div>');
  setTimeout(function(){ var i = document.getElementById('hsQ'); if(i) try{ i.focus(); }catch(e){} }, 250);
  setTimeout(function(){ try{ hsSearchRecents(); }catch(e){} }, 280);
}

async function hsDoSearch(){
  var q = (document.getElementById('hsQ') || {}).value || '';
  var box = document.getElementById('hsRes');
  if(!box) return;
  if(q.trim().length < 1){ box.innerHTML = ''; return; }
  box.innerHTML = '<div class="hs-load">搜索中…</div>';
  try{
    var tk = ''; try{ tk = (typeof webToken === 'function') ? webToken() : ''; }catch(e){}
    var r = await fetch(API_BASE() + '/api/search', {method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({q: q, token: tk})});
    var d = await r.json();
    hsSearchRows(d, q);
    if(q.trim().length >= 2){ hsSearchRemember(q.trim()); try{ hsSearchRecents(); }catch(e){} }
  }catch(e){ box.innerHTML = '<div class="hs-load">搜索失败，请重试</div>'; }
}

function hsSearchRows(d, q){
  var box = document.getElementById('hsRes');
  if(!box) return;
  var items = (d && d.items) || [];
  if(!items.length){
    box.innerHTML = '<div class="srch-empty"><div class="se-t">没搜到「' + esc(q) + '」</div>'
      + '<div class="se-d">全站搜索会搜：<b>书名</b>（中文古籍 / 阿拉伯典籍）· <b>句子</b> · <b>词汇</b> · <b>六大部</b></div>'
      + '<div class="se-g">试试这些：</div><div class="dr-c">'
      + ['三国演义','红楼梦','聊斋志异','史记','论语','كتاب','تاريخ','السلام عليكم','你好','学习'].map(function(w){
          return '<span onclick="hsSearchPick(this)">' + w + '</span>';
        }).join('') + '</div>'
      + '<div class="se-n">小提示：搜<b>书名</b>最容易出结果 ✓ 搜阿语词请连拼音一起输（如 kitab）✓</div></div>';
    return;
  }
  var KIND = {cnbook:'中文古籍', arbook:'阿拉伯典籍', hadith:'六大部', islamic:'世界书库',
              sentence:'句子', vocab:'词汇', article:'文章', cnword:'📖 中文词释义'};
  var g = {};
  items.forEach(function(x){ (g[x.k] = g[x.k] || []).push(x); });
  var h = '';
  Object.keys(g).forEach(function(k){
    h += '<div class="srch-h">' + (KIND[k] || k) + ' · ' + g[k].length + '</div>';
    g[k].slice(0, 40).forEach(function(x){
      var rt = x.rt || 'shamela';
      var act = (x.k === 'cnword') ? ("closeModal('mSearch');hsGo(HK_DICT_IDX(), document.querySelectorAll('#tkSeg .chip')[HK_DICT_IDX()]);setTimeout(function(){var q=document.getElementById('dictQ');if(q){q.value='" + x.zh + "';dictSearch();}},420)")
              : (x.k === 'cnbook') ? ("openReadById('" + x.key + "','cn')")
              : (x.k === 'arbook') ? ("openReadById('" + x.key + "','" + rt + "')")
              : (x.k === 'hadith') ? "showH6()" : '';
      h += '<div class="hs-row" ' + (act ? ('onclick="' + act + '"') : '') + '>'
        + '<span class="hs-row-i">' + (x.k === 'cnbook' ? '📜' : (x.k === 'hadith' ? '🕌' : '📖')) + '</span>'
        + '<span class="hs-row-b"><b dir="auto">' + esc(x.ar || x.zh || '') + '</b>'
        + (x.zh && x.ar ? ('<em>' + esc(x.zh) + '</em>') : '')
        + (x.cat ? ('<em>' + esc(x.cat) + '</em>') : '') + '</span>'
        + '<span class="hs-row-a">›</span></div>';
    });
  });
  box.innerHTML = h;
}

function srchNoop(){}
function renderSearchResults(d, q){
  var b = document.getElementById('sRes');
  if(b) return hsSearchRows(d, q);
}

var _hsT = null;
function hsSearchSoon(){
  if(_hsT) clearTimeout(_hsT);
  _hsT = setTimeout(function(){
    var q = (document.getElementById('hsQ') || {}).value || '';
    if(q.trim().length >= 1) hsDoSearch();
    else { var b = document.getElementById('hsRes'); if(b) b.innerHTML = ''; }
  }, 320);
}
function hsSearchRemember(q){
  try{
    var a = JSON.parse(localStorage.getItem('nur_srch_hist') || '[]');
    a = a.filter(function(x){ return x !== q; });
    a.unshift(q);
    localStorage.setItem('nur_srch_hist', JSON.stringify(a.slice(0, 8)));
  }catch(e){}
}
function hsSearchRecents(){
  var el = document.getElementById('hsSrchHist');
  if(!el) return;
  var a = [];
  try{ a = JSON.parse(localStorage.getItem('nur_srch_hist') || '[]'); }catch(e){}
  if(!a.length){ el.innerHTML = ''; return; }
  el.innerHTML = '<div class="dr-t">最近搜索</div><div class="dr-c">' + a.map(function(w){
    return '<span onclick="hsSearchPick(this)">' + esc(w) + '</span>';
  }).join('') + '</div>';
}
function hsSearchPick(el){
  var q = (el.textContent || '').trim();
  var i = document.getElementById('hsQ');
  if(i){ i.value = q; hsDoSearch(); }
}

async function hsBigSearch(){
  var q = (document.getElementById('hsBigQ') || {}).value || '';
  if(q.trim().length < 1) return;
  var wrap = document.getElementById('hsBigBox');
  var res = document.getElementById('hsBigRes');
  if(wrap){
    wrap.classList.add('split');
    if(!res){ res = document.createElement('div'); res.id = 'hsBigRes'; res.className = 'hs-bigres'; wrap.appendChild(res); }
    res.innerHTML = '<div class="hs-load">搜索中…</div>';
    try{
      var tk = ''; try{ tk = (typeof webToken === 'function') ? webToken() : ''; }catch(e){}
      var r = await fetch(API_BASE() + '/api/search', {method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({q: q, token: tk})});
      var d = await r.json();
      var old = document.getElementById('hsRes');
      var holder = res;
      if(old){ old.id = 'hsResTmp'; }
      res.id = 'hsRes';
      hsSearchRows(d, q);
      res.id = 'hsBigRes';
      if(old){ old.id = 'hsRes'; }
    }catch(e){ res.innerHTML = '<div class="hs-load">搜索失败</div>'; }
  }
}

/* ===== 首屏渲染 / 顺序 / 内嵌（boot） ===== */
(function(){
  function boot(){
    try{
      if(!window.HS_K) return;
      var _home = document.getElementById('page-home');
      if(_home){
        // 标记「查阿拉伯语单词」块
        Array.prototype.forEach.call(_home.children, function(el){
          if(el.tagName === 'DIV' && !el.id && (el.textContent || '').indexOf('查阿拉伯语单词') >= 0 && !el.querySelector('.modal')){
            el.classList.add('hs-dictblock');
          }
        });
        // 💖 支持卡置顶（滚动条下面）
        if(!document.getElementById('hsSupTop')){
          var w = document.createElement('div');
          w.id = 'hsSupTop'; w.className = 'hs-suptop';
          w.innerHTML = hsSupport();
          var don = document.querySelector('.donbar');
          if(don && don.parentNode === _home){ _home.insertBefore(w, don.nextSibling); }
          else { _home.insertBefore(w, _home.firstChild); }
        }
        Array.prototype.forEach.call(document.querySelectorAll('.hs-grid .sup-card'), function(el){
          if(el.parentNode) el.parentNode.removeChild(el);
        });
        // 「查阿拉伯语单词」块 → 点击即展开内嵌词典（左输入 / 右答案）
        try{
          var _blk = _home.querySelector('.hs-dictblock');
          if(_blk && !_blk.dataset.bound){
            _blk.dataset.bound = '1';
            _blk.style.cursor = 'pointer';
            _blk.addEventListener('click', function(ev){
              if(ev.target && (ev.target.id === 'dictQ' || ev.target.closest && ev.target.closest('#mDict'))) return;
              try{ hsDictInline(); }catch(e){}
            });
          }
        }catch(e){}
      }
      // 努尔老师：显示今日免费剩余次数
      try{
        var _ai = document.getElementById('aiSec');
        if(_ai && !document.getElementById('aiQuotaBadge')){
          var _b = document.createElement('div');
          _b.id = 'aiQuotaBadge'; _b.className = 'ai-quota-badge';
          var _h = _ai.querySelector('.ps-ai-card') || _ai;
          _h.insertBefore(_b, _h.firstChild);
          fetch(API_BASE() + '/api/ai/quota?device_id=' + encodeURIComponent((typeof devId === 'function') ? devId() : 'anon'))
            .then(function(r){ return r.json(); })
            .then(function(d){
              if(!d || !d.ok) return;
              _b.innerHTML = d.vip
                ? '<span class="aq-v">会员</span> 无限对话 ✓'
                : ('今日免费剩余 <b>' + d.left + '</b> / ' + d.cap + ' 次' + (d.left <= 0 ? (' · <span class="aq-go" onclick="openDonate()">💖 支持解锁无限 ›</span>') : ''));
            }).catch(function(){});
        }
      }catch(e){}
      // 顶部大搜索框（放在大标题下面）
      try{
        if(!document.getElementById('hsBigBox')){
          var _hh = document.querySelector('header.hdr');
          if(_hh && _hh.parentNode){
            var _bb = document.createElement('div');
            _bb.id = 'hsBigBox';
            _bb.innerHTML = '<div class="hbb"><span class="hbb-i">🔍</span>'
              + '<input id="hsBigQ" placeholder="全站搜索：书名 · 句子 · 词汇 · 六大部 · 今日要闻…" autocomplete="off">'
              + '<button class="hbb-b" onclick="hsBigSearch()">搜索</button></div>'
              + '<div id="hsBigRes" class="hs-bigres" style="display:none"></div>';
            _hh.parentNode.insertBefore(_bb, _hh.nextSibling);
            var _ii = _bb.querySelector('input');
            if(_ii) _ii.addEventListener('keydown', function(ev){ if(ev.key === 'Enter'){ hsBigSearch(); } });
          }
        }
      }catch(e){}
      if(typeof hsToday === 'function') hsToday();
      if(typeof hsRender === 'function') hsRender();
    }catch(e){}
  }
  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', function(){ setTimeout(boot, 260); });
  else setTimeout(boot, 260);
  window.addEventListener('load', function(){ setTimeout(boot, 600); });
  setTimeout(boot, 1800);
})();

/* ===== 语法 / 词法：右边一堆相关书籍（从库里检索） ===== */
var HS_SUBJ = {
  grammar: { t: '语法', sub: 'النحو · 语法书 · 例句 · 讲解', ar: ['النحو', 'قواعد', 'إعراب', 'نحو', 'شرح'], cn: ['语法'] },
  morph:   { t: '词法', sub: 'الصرف · 词根 · 派生 · 构词',     ar: ['الصرف', 'صرف', 'اشتقاق', 'الميزان'], cn: ['词法'] }
};

async function hsSubjectBooks(kind){
  var cfg = HS_SUBJ[kind] || HS_SUBJ.grammar;
  hsTitle(cfg.t, cfg.sub);
  hsLoad('正在检索相关书籍…');
  var found = [];
  var seen = {};
  try{
    var r = await fetch(API_BASE() + '/data/library/' + (kind === 'grammar' ? 'grammar_books.json' : 'morph_books.json'));
    if(r.ok){ var d = await r.json(); found = (d.items || []); }
  }catch(e){}
  if(!found.length){
    for(var i = 0; i < cfg.ar.length; i++){
      try{
        var r2 = await fetch(API_BASE() + '/api/search', {method:'POST', headers:{'Content-Type':'application/json'},
          body: JSON.stringify({q: cfg.ar[i]})});
        var d2 = await r2.json();
        (d2.items || []).forEach(function(x){
          if(x.k !== 'arbook' && x.k !== 'cnbook') return;
          var key = x.key + x.k;
          if(seen[key]) return;
          seen[key] = 1;
          found.push({ t: x.ar || x.zh, id: x.key, rt: (x.k === 'cnbook' ? 'cn' : (x.rt || 'shamela')), cn: (x.k === 'cnbook') });
        });
      }catch(e){}
    }
  }
  if(!found.length){
    hsSet('<div class="hs-load">没有找到相关书籍（服务器还在建索引）</div>');
    return;
  }
  var cnEl = document.getElementById('hsSecSub'); if(cnEl) cnEl.textContent = found.length + ' 本';
  window.__HS_SUBJ = { kind: kind, cfg: cfg, all: found, n: 60 };
  hsSubjRender();
}

function hsSubjRender(){
  var st = window.__HS_SUBJ; if(!st) return;
  var list = st.all.slice(0, st.n);
  hsTitle(st.cfg.t, '共 ' + st.all.length + ' 本 · 已显示 ' + list.length + ' 本');
  var h = hsRow('📘', st.cfg.t + '书籍', '共 ' + st.all.length + ' 本 · 点开即读', '', 1)
    + list.map(hsCoverCard).join('');
  if(st.all.length > list.length){
    h += hsRow('⬇️', '加载更多', '还有 ' + (st.all.length - list.length) + ' 本', 'hsSubjMore()');
  }
  h += hsSupport();
  hsSet(h);
}

function hsSubjMore(){
  var st = window.__HS_SUBJ; if(!st) return;
  st.n += 60;
  hsSubjRender();
}

/* 旧的课程列表仍保留（在下方「课程」入口可用） */
function hsGrammarList(kind){
  if(kind === 'morph') hsGrammar(window.BUILTIN_MORPH || [], '词法课', '词根 · 派生 · 构词');
  else hsGrammar(window.BUILTIN_GRAMMAR || [], '语法课', '一课一个主题');
}

/* ===== 词典增强：中文词也能查（点开给释义/近反义/例句） ===== */
(function(){
  function isCN(t){ return /[\u4e00-\u9fff]/.test(t) && !/[\u0600-\u06FF]/.test(t); }
  function ready(){
    if(typeof dictSearch !== 'function'){ return false; }
    if(dictSearch.__cn){ return true; }
    var orig = dictSearch;
    function cnRender(d, w){
      var b = document.getElementById('dictBody');
      if(!b) return;
      var x = (d && d.data) || {};
      function chips(arr, cls){
        if(!arr || !arr.length) return '';
        return '<span class="dc-wrap">' + arr.map(function(v){
          return '<span class="dc-chip" onmousedown="dictPick(\'' + v + '\')">' + v + '</span>';
        }).join('') + '</span>';
      }
      var h = '<div class="dcn">'
        + '<div class="dcn-h"><b>' + (x.word || w) + '</b>'
        + (x.pinyin ? ('<span class="dcn-py">' + x.pinyin + '</span>') : '')
        + (x.pos ? ('<span class="dcn-pos">' + x.pos + '</span>') : '') + '</div>'
        + (x.meaning ? ('<div class="dcn-m">' + x.meaning + '</div>') : '')
        + (x.detail ? ('<div class="dcn-d">' + x.detail + '</div>') : '')
        + (x.syn && x.syn.length ? ('<div class="dcn-l">近义词</div>' + chips(x.syn)) : '')
        + (x.ant && x.ant.length ? ('<div class="dcn-l">反义词</div>' + chips(x.ant)) : '')
        + (x.sent && x.sent.length ? ('<div class="dcn-l">例句</div>' + x.sent.map(function(t){
            return '<div class="dcn-s">' + t + '</div>';
          }).join('')) : '')
        + (x.note ? ('<div class="dcn-note">💡 ' + x.note + '</div>') : '')
        + '</div>';
      b.innerHTML = h;
    }
    var wrapped = async function(){
      var q = ((document.getElementById('dictQ') || {}).value || '').trim();
      var b = document.getElementById('dictBody');
      if(isCN(q) && b){
        b.innerHTML = '<div style="color:#8a8f88;padding:16px">正在解释「' + q + '」…</div>';
        try{
          var r = await fetch(API_BASE() + '/api/dict/cn?w=' + encodeURIComponent(q));
          var d = await r.json();
          if(d && d.ok){ cnRender(d, q); dictRemember(q); return; }
        }catch(e){}
      }
      return orig.apply(this, arguments);
    };
    wrapped.__cn = 1;
    try{ window.dictSearch = wrapped; }catch(e){}
    try{ dictSearch = wrapped; }catch(e){}
    return true;
  }
  var n = 0;
  var t = setInterval(function(){ n++; if(ready() || n > 40) clearInterval(t); }, 150);
})();

function HK_DICT_IDX(){
  var K = window.HS_K || [];
  for(var i = 0; i < K.length; i++){ if(K[i].k === 'dict') return i; }
  return 0;
}

/* ============================================================
   努尔老师 · 全屏页面入口
   不再创建/搬移任何 modal 或 ai-view，统一交给 nav('ai') 管理。
   ============================================================ */
(function(){
  function openAI(){
    if(typeof window.nav === 'function') window.nav('ai');
    var box = document.getElementById('homeAI');
    if(box) setTimeout(function(){ box.scrollTop = box.scrollHeight; }, 80);
  }
  function closeAI(){
    if(typeof window.nav === 'function') window.nav('home');
  }
  window.openNurAI = openAI;
  window.closeNurAI = closeAI;
  function addEntry(){
    var rail = document.getElementById('tkSeg') || document.querySelector('.hs-rail');
    if(!rail || rail.querySelector('[data-ai-entry]')) return;
    var b = document.createElement('button');
    b.className = 'chip'; b.type = 'button'; b.setAttribute('data-ai-entry','1');
    b.innerHTML = '<span class="chip-i">🤖</span>努尔老师';
    b.onclick = function(){ openAI(); };
    rail.appendChild(b);
  }
  function boot(){ addEntry(); }
  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
  [1200, 3000, 7000].forEach(function(t){ setTimeout(boot, t); });
})();


/* ===== 7C 词典 → 课程关联：只显示现有 grammar/morphology 课程 ===== */
(function(){
  if(window.__NOUR_DICT_LESSON_WRAP) return;
  window.__NOUR_DICT_LESSON_WRAP = true;
  function escv(v){ try{return typeof esc === 'function' ? esc(String(v||'')) : String(v||'').replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];});}catch(e){return '';} }
  function render(q, d, seq){
    if(seq !== window.__NOUR_DICT_LESSON_SEQ) return;
    var b=document.getElementById('dictBody'); if(!b) return;
    var old=document.getElementById('dictLessons'); if(old) old.remove();
    var items=(d&&d.items)||[], h='<section id="dictLessons" class="dict-lessons">'
      + '<div class="dict-section-title">学习关联</div>'
      + '<div class="dict-lessons-note">来自本地语法课与词法课 · 不把课程示例当作固定释义</div>';
    if(!items.length){
      h+='<div class="dict-lesson-empty">暂无明确命中的本地课程条目。可继续交给 NOUR AI 分析词根、词形和当前语境。</div></section>';
      b.appendChild(document.createRange().createContextualFragment(h)); return;
    }
    items.slice(0,6).forEach(function(x){
      var kind=x.kind==='morph'?'词法课':'语法课';
      var id=escv(x.id), fn=x.kind==='morph'?"showMorph('"+id+"')":"showGrammar('"+id+"','grammar')";
      var terms=(x.matched_terms||[]).slice(0,3).map(function(t){return '<b dir="rtl" lang="ar">'+escv(t)+'</b>';}).join(' · ');
      h+='<article class="dict-lesson-item"><div class="dict-lesson-copy"><div><span class="dict-lesson-kind">'+kind+'</span><strong>'+escv(x.title)+'</strong></div>'
        +(x.title_ar?'<div class="dict-lesson-ar" dir="rtl" lang="ar">'+escv(x.title_ar)+'</div>':'')
        +'<div class="dict-lesson-match">'+escv(x.match_type||'课程关联')+(terms?'：'+terms:'')+'</div>'
        +(x.intro?'<div class="dict-lesson-intro">'+escv(x.intro)+'</div>':'')
        +'</div><button type="button" class="dict-lesson-open" onclick="'+fn+'">打开课程</button></article>';
    });
    h+='</section>';
    b.appendChild(document.createRange().createContextualFragment(h));
  }
  function load(q){
    q=String(q||'').trim();
    var seq=(window.__NOUR_DICT_LESSON_SEQ||0)+1; window.__NOUR_DICT_LESSON_SEQ=seq;
    if(!q || !/[\u0600-\u06ff]/.test(q)) return;
    var tries=0;
    function waitResult(){
      var b=document.getElementById('dictBody');
      if(!b) return;
      var loading=b.querySelector('.dict-loading');
      if(loading && tries++<30){setTimeout(waitResult,120);return;}
      fetch(API_BASE()+'/api/dict/lesson?w='+encodeURIComponent(q)+'&limit=6',{cache:'no-store'})
        .then(function(r){return r.json();}).then(function(d){render(q,d,seq);})
        .catch(function(){render(q,{items:[]},seq);});
    }
    setTimeout(waitResult,160);
  }
  function attach(){
    if(typeof window.dictSearch!=='function') return false;
    if(window.dictSearch.__lesson) return true;
    var orig=window.dictSearch;
    var wrapped=function(){
      var q=((document.getElementById('dictQ')||{}).value||'').trim();
      var out=orig.apply(this,arguments); load(q); return out;
    };
    wrapped.__lesson=true;
    window.dictSearch=wrapped;
    try{dictSearch=wrapped;}catch(e){}
    return true;
  }
  var n=0, t=setInterval(function(){n++;if(attach()||n>40)clearInterval(t);},150);
  if(document.readyState!=='loading') attach();
  else document.addEventListener('DOMContentLoaded',attach);
})();
