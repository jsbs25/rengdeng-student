/* ============================================================================
   燃灯同学 Rengdeng Student · 自适应工作模式层 (Adaptive Workspace v1)
   ----------------------------------------------------------------------------
   设计哲学：界面随任务自然变形，而非固定导航。
   - 发现 (discover)：保留现有编辑式四屏首页（默认，不改动）
   - 阅读 (read)    ：内容成为视觉中心，界面退后
   - 研习 (study)   ：围绕今日学习目标组织课程 / 单词 / 练习
   - 探究 (explore) ：知识关系图谱 + 相关实体自然展开
   ----------------------------------------------------------------------------
   约束：用户可控制、可记忆、不收集行为数据、不自动覆盖用户设置。
   本层仅做呈现与切换，所有业务动作复用现有全局函数，不改后端逻辑。
   ============================================================================ */
(function () {
  'use strict';
  if (window.__NOUR_ADAPTIVE_WORKSPACE__) return;
  window.__NOUR_ADAPTIVE_WORKSPACE__ = true;

  var MODES = [
    { id: 'discover', label: '发现', hint: '编辑式首页' },
    { id: 'read', label: '阅读', hint: '沉浸阅读' },
    { id: 'study', label: '研习', hint: '今日学习' },
    { id: 'explore', label: '探究', hint: '知识关系' }
  ];

  function q(s, r) { return (r || document).querySelector(s); }
  function qa(s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); }
  function esc(v) {
    return String(v == null ? '' : v).replace(/[&<>"']/g, function (c) {
      return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c];
    });
  }
  function call(name) {
    var a = Array.prototype.slice.call(arguments, 1);
    try { if (typeof window[name] === 'function') return window[name].apply(window, a); } catch (e) {}
  }
  function bind(el, fn) { if (el) el.addEventListener('click', function (ev) { ev.preventDefault(); fn(); }); }

  function readToday() {
    var ar = q('#qAr'), cn = q('#qCn');
    var arText = (ar && String(ar.textContent || '').trim()) || 'العِلْمُ كَنْزٌ لَا يَفْنَىٰ';
    var cnText = (cn && String(cn.textContent || '').trim()) || '知识是永不消逝的宝藏';
    return { ar: arText, cn: cnText };
  }

  function icon(kind) {
    if (kind === 'book') return '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 4.5A2.5 2.5 0 0 1 7.5 2H20v18H7.5A2.5 2.5 0 0 0 5 22.5z"/><path d="M5 4.5v18M9 6h7M9 10h7M9 14h5"/></svg>';
    if (kind === 'study') return '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 5.5A2.5 2.5 0 0 1 7.5 3H20v16H7.5A2.5 2.5 0 0 0 5 21.5z"/><path d="M5 5.5v16M9 7h7M9 11h7"/><path d="m9 15 1.7 1.7L14 13.5"/></svg>';
    if (kind === 'spark') return '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2l1.8 6.2L20 10l-6.2 1.8L12 18l-1.8-6.2L4 10l6.2-1.8z"/><path d="M19 17v5M16.5 19.5h5"/></svg>';
    if (kind === 'map') return '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="6" cy="6" r="2.4"/><circle cx="18" cy="6" r="2.4"/><circle cx="12" cy="18" r="2.4"/><path d="M7.6 7.8 10.6 16M16.4 7.8 13.4 16M6 6l12 0M18 6l-6 12M6 6l6 12"/></svg>';
    if (kind === 'read') return '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 5c-2.8-1.6-6-1.6-8.8 0L3 5v14l.2-.1C6 17.4 9.2 17.4 12 19c2.8-1.6 6-1.6 8.8 0l.2.1V5l-.2-.1C18 3.4 14.8 3.4 12 5z"/></svg>';
    return '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="10.8" cy="10.8" r="6.3"/><path d="m16 16 4.5 4.5"/></svg>';
  }

  function buildSwitcher(home) {
    var bar = document.createElement('div');
    bar.className = 'nour-workspace-switcher';
    bar.setAttribute('role', 'tablist');
    bar.setAttribute('aria-label', '工作模式');
    MODES.forEach(function (m) {
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'nour-workspace-mode';
      b.setAttribute('role', 'tab');
      b.setAttribute('data-workspace-mode', m.id);
      b.setAttribute('aria-label', m.label + ' · ' + m.hint);
      b.innerHTML = '<span class="ic">' + icon(m.id === 'discover' ? 'search' : m.id) + '</span><span class="lb">' + esc(m.label) + '</span>';
      b.addEventListener('click', function () { setMode(m.id); });
      bar.appendChild(b);
    });
    home.insertBefore(bar, home.firstChild);
  }

  function buildPanels(home) {
    var today = readToday();
    var wrap = document.createElement('div');
    wrap.className = 'nour-workspace-panels';

    // 阅读模式：内容成为视觉中心
    var read = document.createElement('section');
    read.className = 'nour-mode-panel nour-mode-read';
    read.setAttribute('data-mode-panel', 'read');
    read.innerHTML =
      '<div class="nour-read-focus">' +
        '<div class="nour-read-kicker"><span>今日原句</span><span class="ar" lang="ar" dir="rtl">آية اليوم</span></div>' +
        '<p class="nour-read-ar" lang="ar" dir="rtl">' + esc(today.ar) + '</p>' +
        '<p class="nour-read-cn">' + esc(today.cn) + '</p>' +
        '<div class="nour-read-meta">' +
          '<button type="button" class="nour-mode-action" data-go="sentences">打开句子库</button>' +
          '<button type="button" class="nour-mode-action" data-go="dict">查词与词根</button>' +
          '<button type="button" class="nour-mode-action" data-go="library">回到书库</button>' +
        '</div>' +
      '</div>';

    // 研习模式：围绕今日目标
    var study = document.createElement('section');
    study.className = 'nour-mode-panel nour-mode-study';
    study.setAttribute('data-mode-panel', 'study');
    study.innerHTML =
      '<div class="nour-mode-head"><div><span class="kicker">Study</span><h2>今日阿拉伯语研习</h2><p>围绕目标组织课程、单词与练习，减少复杂仪表盘。</p></div></div>' +
      '<div class="nour-study-grid">' +
        '<button type="button" class="nour-study-task" data-go="vocab"><span class="ic">' + icon('study') + '</span><span class="c"><strong>词汇复习</strong><small>今日 24 个高频词 · SRS 间隔复习</small></span><span class="go">›</span></button>' +
        '<button type="button" class="nour-study-task" data-go="grammar"><span class="ic">' + icon('book') + '</span><span class="c"><strong>语法课程</strong><small>名词与词根 · 一节核心课</small></span><span class="go">›</span></button>' +
        '<button type="button" class="nour-study-task" data-go="flash"><span class="ic">' + icon('read') + '</span><span class="c"><strong>闪卡复习</strong><small>错题 5 题 · 巩固记忆</small></span><span class="go">›</span></button>' +
        '<button type="button" class="nour-study-task" data-go="listen"><span class="ic">' + icon('spark') + '</span><span class="c"><strong>听力跟读</strong><small>原生阿语发音 · 10 分钟</small></span><span class="go">›</span></button>' +
      '</div>';

    // 探究模式：知识关系图谱
    var explore = document.createElement('section');
    explore.className = 'nour-mode-panel nour-mode-explore';
    explore.setAttribute('data-mode-panel', 'explore');
    explore.innerHTML =
      '<div class="nour-mode-head"><div><span class="kicker">Explore</span><h2>知识关系图谱</h2><p>让知识之间的联系变得直观，从一点自然发现相关词汇、书籍、人物与历史。</p></div></div>' +
      '<div class="nour-explore-grid">' +
        '<div class="nour-map" aria-label="知识关系图谱示意图">' +
          '<svg viewBox="0 0 640 300" role="img">' +
            '<line class="e" x1="320" y1="50" x2="170" y2="140"/><line class="e" x1="320" y1="50" x2="470" y2="140"/>' +
            '<line class="e" x1="170" y1="140" x2="110" y2="230"/><line class="e" x1="170" y1="140" x2="260" y2="230"/>' +
            '<line class="e" x1="470" y1="140" x2="410" y2="230"/><line class="e" x1="470" y1="140" x2="540" y2="230"/>' +
            '<circle class="nr" cx="320" cy="50" r="24"/><circle class="nc" cx="320" cy="50" r="6"/>' +
            '<text class="ar" x="320" y="57" text-anchor="middle">نور</text><text class="t" x="320" y="88" text-anchor="middle">燃灯同学</text>' +
            '<circle class="nr" cx="170" cy="140" r="18"/><circle class="nc" cx="170" cy="140" r="4"/>' +
            '<text x="170" y="145" text-anchor="middle">阿拉伯语</text>' +
            '<circle class="nr" cx="470" cy="140" r="18"/><circle class="nc" cx="470" cy="140" r="4"/>' +
            '<text x="470" y="145" text-anchor="middle">世界图书馆</text>' +
            '<circle class="nr" cx="110" cy="230" r="14"/><text x="110" y="234" text-anchor="middle">词汇</text>' +
            '<circle class="nr" cx="260" cy="230" r="14"/><text x="260" y="234" text-anchor="middle">语法</text>' +
            '<circle class="nr" cx="410" cy="230" r="14"/><text x="410" y="234" text-anchor="middle">古兰经</text>' +
            '<circle class="nr" cx="540" cy="230" r="14"/><text x="540" y="234" text-anchor="middle">历史</text>' +
          '</svg>' +
        '</div>' +
        '<div class="nour-explore-side">' +
          '<button type="button" class="nour-explore-chip" data-go="library"><span class="ar" lang="ar" dir="rtl">المكتبة</span><span>世界图书馆</span></button>' +
          '<button type="button" class="nour-explore-chip" data-go="quran"><span class="ar" lang="ar" dir="rtl">القرآن</span><span>古兰经选读</span></button>' +
          '<button type="button" class="nour-explore-chip" data-go="ai"><span class="ar" lang="ar" dir="rtl">نور</span><span>努尔 AI 伴读</span></button>' +
          '<button type="button" class="nour-explore-chip" data-go="history"><span>历史文献</span><span class="sub">8,400+ 史书</span></button>' +
        '</div>' +
      '</div>';

    wrap.appendChild(read);
    wrap.appendChild(study);
    wrap.appendChild(explore);
    home.appendChild(wrap);

    qa('[data-go="sentences"]', wrap).forEach(function (b) { bind(b, function () { call('showAllSentences'); }); });
    qa('[data-go="dict"]', wrap).forEach(function (b) { bind(b, function () { call('openDict'); }); });
    qa('[data-go="library"]', wrap).forEach(function (b) { bind(b, function () { call('nav', 'learn'); }); });
    qa('[data-go="vocab"]', wrap).forEach(function (b) { bind(b, function () { call('showVocab'); }); });
    qa('[data-go="grammar"]', wrap).forEach(function (b) { bind(b, function () { call('showGrammar'); }); });
    qa('[data-go="flash"]', wrap).forEach(function (b) { bind(b, function () { call('showFlashcard'); }); });
    qa('[data-go="listen"]', wrap).forEach(function (b) { bind(b, function () { call('showListen'); }); });
    qa('[data-go="quran"]', wrap).forEach(function (b) { bind(b, function () { call('showQuran'); }); });
    qa('[data-go="ai"]', wrap).forEach(function (b) { bind(b, function () { call('nav', 'ai'); }); });
    qa('[data-go="history"]', wrap).forEach(function (b) { bind(b, function () { call('openModal', 'mHistory'); }); });
  }

  function setMode(id, silent) {
    var allowed = { discover: 1, read: 1, study: 1, explore: 1 };
    if (!allowed[id]) id = 'discover';
    document.documentElement.setAttribute('data-workspace-mode', id);
    var _idx = 0;
    MODES.forEach(function (m, i) { if (m.id === id) _idx = i; });
    document.documentElement.style.setProperty('--nour-ws-index', String(_idx));
    qa('.nour-workspace-mode').forEach(function (b) {
      var on = b.getAttribute('data-workspace-mode') === id;
      b.classList.toggle('on', on);
      b.setAttribute('aria-selected', on ? 'true' : 'false');
    });
    if (!silent) { try { localStorage.setItem('nur_workspace_mode', id); } catch (e) {} }
  }

  function init() {
    var home = q('#nourProductHome');
    if (!home) { window.setTimeout(init, 60); return; }
    if (q('.nour-workspace-switcher', home)) return;
    buildSwitcher(home);
    buildPanels(home);
    var saved = null;
    try { saved = localStorage.getItem('nur_workspace_mode'); } catch (e) {}
    var initial = (saved && { discover: 1, read: 1, study: 1, explore: 1 }[saved]) ? saved : 'discover';
    setMode(initial, true);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () { window.setTimeout(init, 40); });
  } else {
    init();
  }
})();
