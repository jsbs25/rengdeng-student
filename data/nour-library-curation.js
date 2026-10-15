/* NOUR classic discovery: additive UI over the existing world library. */
(function () {
  'use strict';
  if (window.__NOUR_CLASSIC_DISCOVERY__) return;
  window.__NOUR_CLASSIC_DISCOVERY__ = true;

  var state = { collection: '', q: '', page: 0, size: 18, total: 0, items: [], paths: [], meta: {}, loading: false };
  var labels = { quran: '古兰经学与经注', hadith: '圣训学', fiqh: '伊斯兰法学', usul: '法源学', language: '阿拉伯语言与修辞', history: '历史与传记', aqida: '信仰与教义', literature: '文学与古典' };
  function q(sel, root) { return (root || document).querySelector(sel); }
  function esc(v) { return String(v == null ? '' : v).replace(/[&<>"']/g, function (c) { return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]; }); }
  function api() { return typeof window.API_BASE === 'function' ? window.API_BASE() : ''; }
  function mount() {
    var body = q('#mCatBody');
    if (!body) return;
    var panel = q('#nourClassicPanel');
    if (!panel || panel.parentNode !== body) {
      panel = document.createElement('section');
      panel.id = 'nourClassicPanel';
      panel.className = 'nour-classic-panel';
      body.insertBefore(panel, body.firstChild || null);
    }
    render(panel);
    if (!state.items.length && !state.loading) load();
  }
  function render(panel) {
    var meta = state.meta || {};
    var counts = meta.counts || {};
    var categories = [''].concat(Object.keys(labels));
    var filters = categories.map(function (key) {
      var text = key ? labels[key] : '全部经典';
      var count = key ? (counts[key] || 0) : (meta.total || state.total || 0);
      return '<button type="button" class="nour-classic-filter' + (state.collection === key ? ' is-active' : '') + '" data-classic-collection="' + esc(key) + '"><span>' + esc(text) + '</span><small>' + count.toLocaleString() + '</small></button>';
    }).join('');
    var pathHtml = state.paths.length ? '<div class="nour-path-list">' + state.paths.map(function (path) {
      return '<article class="nour-path-card"><div class="nour-path-index">' + esc(path.ar || 'NOUR PATH') + '</div><h3>' + esc(path.title || '') + '</h3><p>' + esc(path.summary || '') + '</p><div class="nour-path-steps">' + (path.steps || []).map(function (x, i) { return '<span><b>' + (i + 1) + '</b>' + esc(x) + '</span>'; }).join('') + '</div><button type="button" class="nour-path-ai" data-classic-path="' + esc(path.id) + '">交给 NOUR AI 规划</button></article>';
    }).join('') + '</div>' : '';
    var cards = state.loading ? '<div class="nour-classic-status">正在读取本地索引…</div>' : (state.items.length ? state.items.map(card).join('') : '<div class="nour-classic-status">没有匹配的书目。索引只收纳本地 Shamela 可读条目。</div>');
    panel.innerHTML = '<div class="nour-classic-head"><div><div class="nour-classic-kicker">NOUR · CLASSICS DISCOVERY</div><h1>阿拉伯经典与学术索引</h1><p>从现有真实书目池发现文学、语言、古兰经学、圣训学、法学与法源学作品。卡片只保存元数据，点开仍在站内按需阅读。</p></div><div class="nour-classic-count"><b>' + (meta.total || state.total || 0).toLocaleString() + '</b><span>条可读发现</span></div></div>' +
      '<div class="nour-classic-notice"><span>索引说明</span><p>分类依据是书名与本地目录关键词推断，不代表作者自证、版本考订或教法裁决；来源和版本请打开原文后核对。</p></div>' +
      '<div class="nour-classic-toolbar"><div class="nour-classic-filters">' + filters + '</div><div class="nour-classic-search"><input id="nourClassicQuery" value="' + esc(state.q) + '" placeholder="搜索阿拉伯书名或学科" aria-label="搜索经典索引"><button type="button" data-classic-search>查找</button></div></div>' +
      '<section class="nour-path-section"><div class="nour-classic-section-title"><div><span>READING PATHS</span><h2>从一个主题开始阅读</h2></div><small>路径来自本地索引，不声称 AI 已读完整书</small></div>' + pathHtml + '</section>' +
      '<section class="nour-classic-books"><div class="nour-classic-section-title"><div><span>REAL OPEN TEXT ENTRIES</span><h2>可直接进入的阿拉伯原文</h2></div><small>第 ' + (state.page + 1) + ' 页 · 共 ' + (state.total || 0).toLocaleString() + ' 条</small></div><div class="nour-classic-grid">' + cards + '</div><div class="nour-classic-pager"><button type="button" data-classic-prev ' + (state.page <= 0 ? 'disabled' : '') + '>上一页</button><button type="button" data-classic-next ' + ((state.page + 1) * state.size >= state.total ? 'disabled' : '') + '>下一页</button></div></section>';
    bind(panel);
  }
  function card(item) {
    var id = String(item.id || '');
    return '<article class="nour-classic-card" data-classic-id="' + esc(id) + '"><div class="nour-classic-cover"><span>ق</span><small>' + esc(item.collection_label || '阿拉伯典籍') + '</small></div><div class="nour-classic-copy" dir="rtl"><h3>' + esc(item.title_ar || item.title || '') + '</h3><p dir="ltr">' + esc(item.collection_label || '') + ' · Shamela 可读条目</p></div><div class="nour-classic-card-actions"><button type="button" class="nour-classic-read" data-classic-read="' + esc(id) + '">站内阅读</button><a href="' + esc(item.source_url || '') + '" target="_blank" rel="noopener" data-classic-source>来源 ↗</a></div></article>';
  }
  function bind(panel) {
    Array.prototype.forEach.call(panel.querySelectorAll('[data-classic-collection]'), function (b) { b.addEventListener('click', function () { state.collection = b.getAttribute('data-classic-collection') || ''; state.page = 0; load(); }); });
    var input = q('#nourClassicQuery', panel), search = q('[data-classic-search]', panel);
    if (search) search.addEventListener('click', function () { state.q = input ? input.value.trim() : ''; state.page = 0; load(); });
    if (input) input.addEventListener('keydown', function (e) { if (e.key === 'Enter') { state.q = input.value.trim(); state.page = 0; load(); } });
    Array.prototype.forEach.call(panel.querySelectorAll('[data-classic-read]'), function (b) { b.addEventListener('click', function () { var id = b.getAttribute('data-classic-read'); if (id && typeof window.openReadById === 'function') window.openReadById(id, 'shamela'); }); });
    Array.prototype.forEach.call(panel.querySelectorAll('[data-classic-path]'), function (b) { b.addEventListener('click', function () { askPath(b.getAttribute('data-classic-path')); }); });
    var prev = q('[data-classic-prev]', panel), next = q('[data-classic-next]', panel);
    if (prev) prev.addEventListener('click', function () { if (state.page > 0) { state.page -= 1; load(); } });
    if (next) next.addEventListener('click', function () { if ((state.page + 1) * state.size < state.total) { state.page += 1; load(); } });
  }
  async function load() {
    state.loading = true; mount();
    try {
      var url = api() + '/api/library/classics?collection=' + encodeURIComponent(state.collection) + '&q=' + encodeURIComponent(state.q) + '&page=' + state.page + '&size=' + state.size;
      var r = await fetch(url, { cache: 'no-store' });
      var d = await r.json();
      if (!r.ok || !d.ok) throw new Error(d.error || 'index unavailable');
      state.items = d.items || []; state.total = Number(d.total || 0); state.paths = d.reading_paths || []; state.meta = d.meta || {}; state.loading = false;
    } catch (e) { state.items = []; state.total = 0; state.loading = false; }
    mount();
  }
  function askPath(id) {
    var path = state.paths.filter(function (x) { return x.id === id; })[0];
    if (!path) return;
    var input = q('#homeAIIn');
    var text = '请根据 NOUR 现有书库为我规划这条阅读路径：' + path.title + '。步骤：' + (path.steps || []).join(' → ') + '。只使用书库中可核验的书目元数据；请把“书目事实”“学习性建议”和“需要回到原文核对的内容”分开，不要编造作者、页码、经训编号或法特瓦。';
    if (typeof window.nav === 'function') window.nav('ai');
    setTimeout(function () { var el = q('#homeAIIn'); if (el) { el.value = text; if (typeof window.homeAIInputState === 'function') window.homeAIInputState(el); el.focus(); } }, 120);
  }
  function wrapNav() {
    if (window.__NOUR_CLASSIC_NAV_WRAPPED__ || typeof window.nav !== 'function') return;
    var original = window.nav;
    window.nav = function (tab) { var result = original.apply(this, arguments); if (tab === 'learn') setTimeout(mount, 260); return result; };
    window.__NOUR_CLASSIC_NAV_WRAPPED__ = true;
  }
  function start() {
    wrapNav();
    setTimeout(mount, 500);
    var body = q('#mCatBody');
    if (body && window.MutationObserver) new MutationObserver(function () { if (!q('#nourClassicPanel', body)) mount(); }).observe(body, { childList: true });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else setTimeout(start, 0);
})();

/* NOUR fiqh reading room: four-school comparison over the real catalog. */
(function () {
  'use strict';
  if (window.__NOUR_FIQH_READING_ROOM__) return;
  window.__NOUR_FIQH_READING_ROOM__ = true;
  var state = { schools: [], focus: 'hanafi', loading: false, error: '', mounted: false };
  function q(sel, root) { return (root || document).querySelector(sel); }
  function esc(v) { return String(v == null ? '' : v).replace(/[&<>"']/g, function (c) { return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]; }); }
  function api() { return typeof window.API_BASE === 'function' ? window.API_BASE() : ''; }
  function findSchool(id) { return state.schools.filter(function (x) { return x.id === id; })[0] || null; }
  function schoolText(s) { return s ? (s.name + ' · ' + s.ar) : '四大学派'; }
  function mount() {
    var panel = q('#nourClassicPanel');
    if (!panel) return;
    var room = q('#nourFiqhReadingRoom', panel);
    if (!room) {
      room = document.createElement('section');
      room.id = 'nourFiqhReadingRoom';
      room.className = 'nour-fiqh-room';
      panel.insertBefore(room, panel.firstChild || null);
      state.mounted = true;
    }
    render(room);
    if (!state.schools.length && !state.loading) load();
  }
  function render(room) {
    var active = findSchool(state.focus) || state.schools[0];
    var tabs = state.schools.map(function (s) {
      return '<button type="button" class="nour-fiqh-school-tab' + (active && active.id === s.id ? ' is-active' : '') + '" data-fiqh-school="' + esc(s.id) + '"><span>' + esc(s.name) + '</span><small dir="rtl">' + esc(s.ar) + ' · ' + Number(s.count || 0).toLocaleString() + ' 条</small></button>';
    }).join('');
    var compare = state.loading ? '<div class="nour-fiqh-state">正在读取四学派真实书目…</div>' : state.error ? '<div class="nour-fiqh-state">四学派书目暂时无法加载：' + esc(state.error) + '</div>' : (state.schools.length ? state.schools.map(schoolCard).join('') : '<div class="nour-fiqh-state">暂时没有可展示的学派条目。</div>');
    room.innerHTML = '<div class="nour-fiqh-head"><div><div class="nour-fiqh-kicker">FIQH READING ROOM · 四学派阅读室</div><h2>从哈乃斐经典进入，再横向比较四种传统</h2><p>下面的数量和书名来自现有 8,794 条目录与公开学派标签。卡片只做阅读导航；标签是元数据线索，不把模型归纳当成学派裁决。</p></div><div class="nour-fiqh-head-mark" aria-hidden="true">فقه</div></div>' +
      '<div class="nour-fiqh-tabs" role="tablist" aria-label="四大学派">' + tabs + '</div>' +
      '<div class="nour-fiqh-focus"><div><span class="nour-fiqh-focus-kicker">当前入口</span><strong>' + esc(active ? schoolText(active) : '哈乃斐学派 · الحنفية') + '</strong><p>' + esc(active ? active.lens : '优先查看哈乃斐法学与法源学作品，再回到四学派原典做局部比较。') + '</p></div><div class="nour-fiqh-focus-actions"><button type="button" data-fiqh-catalog="hanafi">打开哈乃斐目录</button><button type="button" class="is-quiet" data-fiqh-ai>交给 NOUR AI 比较</button></div></div>' +
      '<div class="nour-fiqh-school-grid">' + compare + '</div>' +
      '<div class="nour-fiqh-notice"><b>证据层级</b><span>原文与版本页 &gt; 作者/注疏明确表述 &gt; 学派传承说明 &gt; 模型归纳。每个条目的“来源”按钮都会打开它自己的公开书目或原文入口；没有站内正文的作品不会伪装成已内置全文。</span></div>';
    bind(room);
  }
  function schoolCard(s) {
    var list = (s.items || []).map(function (item) {
      var title = item.t || '未命名书目';
      var readable = !!item.in_app;
      return '<article class="nour-fiqh-book" data-fiqh-id="' + esc(item.id) + '"><div class="nour-fiqh-book-copy" dir="rtl"><h4>' + esc(title) + '</h4><p dir="ltr">' + esc(item.a || '') + (item.y ? ' · ' + esc(item.y) : '') + '</p></div><div class="nour-fiqh-book-meta"><span class="nour-fiqh-badge ' + (readable ? 'is-read' : 'is-guide') + '">' + esc(item.reading_label || (readable ? '站内原文' : '书目导读 / 官方入口')) + '</span><button type="button" data-fiqh-open="' + esc(item.id) + '">' + (readable ? '站内阅读' : '打开导读') + '</button>' + (item.u ? '<a href="' + esc(item.u) + '" target="_blank" rel="noopener noreferrer" data-fiqh-source>来源 ↗</a>' : '') + '</div></article>';
    }).join('');
    return '<article class="nour-fiqh-school-card' + (s.id === state.focus ? ' is-focus' : '') + '"><header><div><span>' + esc(s.name) + '</span><strong dir="rtl">' + esc(s.ar) + '</strong></div><b>' + Number(s.count || 0).toLocaleString() + '<small> 条</small></b></header><p class="nour-fiqh-lens">' + esc(s.lens || '') + '</p><div class="nour-fiqh-books">' + (list || '<span class="nour-fiqh-empty">暂无条目</span>') + '</div><button type="button" class="nour-fiqh-more" data-fiqh-catalog="' + esc(s.id) + '">在世界书库查看全部 ' + esc(s.name) + '</button></article>';
  }
  function register(item) {
    try {
      window.NUR_ISLAMIC_BOOKS = window.NUR_ISLAMIC_BOOKS || {};
      window.NUR_ISLAMIC_BOOKS[item.id] = item;
    } catch (e) {}
  }
  function openItem(id) {
    var found = null;
    state.schools.some(function (s) { return (s.items || []).some(function (x) { if (x.id === id) { found = x; return true; } return false; }); });
    if (!found || !id) return;
    register(found);
    try {
      if (found.read_id && typeof window.openReadById === 'function') {
        return window.openReadById(found.read_id, found.reader_type || 'shamela');
      }
      if (found.in_app && typeof window.openIslamicBook === 'function') return window.openIslamicBook(id);
      if (typeof window.openIslamicGuide === 'function') return window.openIslamicGuide(id);
      if (found.u) window.open(found.u, '_blank', 'noopener');
    } catch (e) { if (found.u) window.location.href = found.u; }
  }
  function selectSchool(id) { if (!findSchool(id)) return; state.focus = id; try { window.NOUR_FIQH_SCHOOL = id; window.localStorage.setItem('nur_fiqh_school', id); } catch (e) {} mount(); }
  function openCatalog(id) {
    state.focus = id || 'hanafi';
    try { window.CAT_SCHOOL = state.focus; window.CAT_CUR = '全部'; window.CAT_TAG = ''; window.CAT_Q = ''; window.CAT_PAGE = 0; } catch (e) {}
    if (typeof window.catSchoolPick === 'function') { window.catSchoolPick(state.focus); return; }
    if (typeof window.showCatalog === 'function') window.showCatalog();
  }
  function askAI() {
    var input = q('#homeAIIn');
    var active = findSchool(state.focus);
    var prompt = '请围绕燃灯同学书库中的真实目录，做一次四大学派学习性比较。当前入口是' + (active ? active.name + '（' + active.ar + '）' : '哈乃斐学派') + '。请区分原文、作者/注疏、各学派传承、证据层级和模型归纳；只引用能从书目或当前原文核验的内容，不能编造页码、经训编号或现实法特瓦。';
    if (typeof window.nav === 'function') window.nav('ai');
    setTimeout(function () { var el = q('#homeAIIn'); if (el) { el.value = prompt; if (typeof window.homeAIInputState === 'function') window.homeAIInputState(el); el.focus(); } }, 140);
  }
  function bind(room) {
    Array.prototype.forEach.call(room.querySelectorAll('[data-fiqh-school]'), function (b) { b.addEventListener('click', function () { selectSchool(b.getAttribute('data-fiqh-school')); }); });
    Array.prototype.forEach.call(room.querySelectorAll('[data-fiqh-open]'), function (b) { b.addEventListener('click', function () { openItem(b.getAttribute('data-fiqh-open')); }); });
    Array.prototype.forEach.call(room.querySelectorAll('[data-fiqh-catalog]'), function (b) { b.addEventListener('click', function () { openCatalog(b.getAttribute('data-fiqh-catalog')); }); });
    var ai = q('[data-fiqh-ai]', room); if (ai) ai.addEventListener('click', askAI);
  }
  async function load() {
    state.loading = true; state.error = ''; mount();
    try {
      var r = await fetch(api() + '/api/library/fiqh-schools?size=5', { cache: 'no-store' });
      var d = await r.json();
      if (!r.ok || !d.ok) throw new Error(d.error || 'fiqh index unavailable');
      state.schools = d.schools || []; state.loading = false;
    } catch (e) { state.loading = false; state.error = String(e && e.message || e); }
    mount();
  }
  function wrapNav() {
    if (window.__NOUR_FIQH_NAV_WRAPPED__ || typeof window.nav !== 'function') return;
    var original = window.nav;
    window.nav = function (tab) { var result = original.apply(this, arguments); if (tab === 'learn') setTimeout(mount, 300); return result; };
    window.__NOUR_FIQH_NAV_WRAPPED__ = true;
  }
  function start() {
    try { var saved = window.localStorage.getItem('nur_fiqh_school'); if (saved && /^(hanafi|maliki|shafii|hanbali)$/.test(saved)) state.focus = saved; } catch (e) {}
    wrapNav(); setTimeout(mount, 650);
    var body = q('#mCatBody'); if (body && window.MutationObserver) new MutationObserver(function () { if (q('#nourClassicPanel', body) && !q('#nourFiqhReadingRoom', body)) mount(); }).observe(body, { childList: true, subtree: true });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else setTimeout(start, 0);
})();
