/* NOUR product shell adapter. It reorganizes existing surfaces without replacing business logic. */
(function () {
  'use strict';
  if (window.__NOUR_PRODUCT_SHELL__) return;
  window.__NOUR_PRODUCT_SHELL__ = true;

  function q(sel, root) { return (root || document).querySelector(sel); }
  function qa(sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); }
  function esc(v) { return String(v == null ? '' : v).replace(/[&<>"']/g, function (c) { return ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'})[c]; }); }
  function call(name) { var args = Array.prototype.slice.call(arguments, 1); try { if (typeof window[name] === 'function') return window[name].apply(window, args); } catch (e) {} }
  function toast(message) {
    var box = q('#nourShellToast');
    if (!box) { box = document.createElement('div'); box.id = 'nourShellToast'; box.className = 'nour-shell-toast'; document.body.appendChild(box); }
    box.textContent = message; box.classList.add('is-visible');
    clearTimeout(window.__NOUR_SHELL_TOAST_TIMER__);
    window.__NOUR_SHELL_TOAST_TIMER__ = setTimeout(function () { box.classList.remove('is-visible'); }, 2600);
  }
  function readFootprints() {
    try {
      var raw = localStorage.getItem('nur_read_footprints') || '[]';
      var list = JSON.parse(raw);
      return Array.isArray(list) ? list.slice(0, 4) : [];
    } catch (e) { return []; }
  }
  function value(id) { var el = document.getElementById(id); return el && String(el.textContent || '').trim() || '—'; }
  function styleValue(id, fallback) {
    var el = document.getElementById(id); if (!el) return fallback || '0%';
    var m = String(el.getAttribute('style') || '').match(/width\s*:\s*([^;]+)/i);
    return m ? m[1].trim() : (fallback || '0%');
  }
  function syncDailyQuote(section) {
    var sourceAr = q('#qAr'), sourceCn = q('#qCn');
    var targetAr = q('.nour-daily-quote-ar', section), targetCn = q('.nour-daily-quote-cn', section);
    if (sourceAr && targetAr) targetAr.textContent = String(sourceAr.textContent || '').trim();
    if (sourceCn && targetCn) targetCn.textContent = String(sourceCn.textContent || '').trim();
  }
  function observeDailyQuote(section) {
    syncDailyQuote(section);
    if (!window.MutationObserver) return;
    var sources = [q('#qAr'), q('#qCn')].filter(Boolean);
    if (!sources.length) return;
    var observer = new MutationObserver(function () { syncDailyQuote(section); });
    sources.forEach(function (source) { observer.observe(source, {childList: true, characterData: true, subtree: true}); });
  }
  function lineIcon(kind) {
    if (kind === 'book' || kind === 'read') return '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 4.5A2.5 2.5 0 0 1 7.5 2H20v18H7.5A2.5 2.5 0 0 0 5 22.5z"/><path d="M5 4.5v18M9 6h7M9 10h7M9 14h5"/></svg>';
    if (kind === 'dict') return '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 4.5A2.5 2.5 0 0 1 7.5 2H20v18H7.5A2.5 2.5 0 0 0 5 22.5z"/><path d="M5 4.5v18M9 7h7M9 11h5"/><path d="M15.5 14.5l2.3 5M13.7 17.8h4.2"/></svg>';
    if (kind === 'study') return '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 5.5A2.5 2.5 0 0 1 7.5 3H20v16H7.5A2.5 2.5 0 0 0 5 21.5z"/><path d="M5 5.5v16M9 7h7M9 11h7"/><path d="m9 15 1.7 1.7L14 13.5"/></svg>';
    if (kind === 'spark') return '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2l1.8 6.2L20 10l-6.2 1.8L12 18l-1.8-6.2L4 10l6.2-1.8z"/><path d="M19 17v5M16.5 19.5h5"/></svg>';
    if (kind === 'person') return '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="8" r="3.5"/><path d="M5 21a7 7 0 0 1 14 0"/></svg>';
    return '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="10.8" cy="10.8" r="6.3"/><path d="m16 16 4.5 4.5"/></svg>';
  }
  function bindAction(button, fn) { if (!button) return; button.addEventListener('click', function (ev) { ev.preventDefault(); fn(); }); }

  function openSearch() {
    if (typeof window.openSearchAll === 'function') return window.openSearchAll();
    var input = q('#sQ');
    call('nav', 'search');
    if (input) setTimeout(function () { input.focus(); }, 120);
  }
  function openLibrary() { call('nav', 'learn'); }
  function openAI() { call('nav', 'ai'); }
  function openMe() { call('nav', 'me'); }
  function openWordbook() { call('showWordBook'); }

  function renderFootprints() {
    var holder = q('#nourContinueList'); if (!holder) return;
    var list = readFootprints();
    if (!list.length) {
      holder.innerHTML = '<div class="nour-product-empty">还没有阅读足迹。打开书库，选一本真实书目开始阅读；之后这里会保留最近四本。</div>';
      return;
    }
    holder.innerHTML = list.map(function (item) {
      var title = esc(item.title || '未命名书目');
      var meta = esc((item.kind || '阅读') + (item.time ? ' · ' + item.time : ''));
      return '<div class="nour-continue-item"><span class="nour-continue-mark" aria-hidden="true">ق</span><div class="nour-continue-copy"><strong>' + title + '</strong><small>' + meta + '</small></div><button type="button" class="nour-product-action" data-open-library>回到书库</button></div>';
    }).join('');
    qa('[data-open-library]', holder).forEach(function (b) { bindAction(b, openLibrary); });
  }

  function mountHome() {
    var home = q('#page-home'), header = home && q('.hdr', home);
    if (!home || !header || q('#nourProductHome')) return;
    var section = document.createElement('section');
    section.id = 'nourProductHome'; section.className = 'nour-product-home';
    section.setAttribute('aria-label', 'NOUR 私人阿拉伯语图书馆');
    section.innerHTML =
      '<div class="nour-product-head">' +
        '<div><div class="nour-product-kicker">NOUR · AI Arabic Library</div><h1 class="nour-product-title">我的阿拉伯语私人图书馆</h1><p class="nour-product-lede">从一段原文开始。书库负责保存上下文，阅读器负责呈现细节，NOUR AI 只在你需要时参与。</p></div>' +
        '<button type="button" class="nour-product-search" id="nourProductSearch">' + lineIcon('search') + '<span>搜索书目、词汇与原文</span><kbd>⌘ K</kbd></button>' +
      '</div>' +
      '<div class="nour-product-grid">' +
        '<div class="nour-product-column">' +
          '<section class="nour-product-section"><div class="nour-product-section-head"><h2>继续阅读</h2><small>最近打开的真实内容</small></div><div id="nourContinueList" class="nour-continue-list"></div></section>' +
          '<section class="nour-product-section"><div class="nour-product-section-head"><h2>AI 为你发现</h2><small>从现有书库开始</small></div><div class="nour-discovery"><div class="nour-discovery-block"><h3>围绕一本书继续</h3><p>打开书库后，NOUR AI 可以根据当前页解释词形、上下文、作者背景和相关段落。没有正文时不会编造书目。</p><div class="nour-discovery-actions"><button type="button" class="nour-product-action primary" data-open-ai>进入阅读助手</button><button type="button" class="nour-product-action" data-open-library>查看书库</button></div></div><div class="nour-discovery-block"><h3>建立阅读路径</h3><p>输入一个主题，先交给全局搜索查找现有资料，再由你决定阅读顺序。</p><div class="nour-discovery-actions"><button type="button" class="nour-product-action" data-open-search>搜索一个主题</button></div></div></div></section>' +
        '</div>' +
        '<aside class="nour-product-column" aria-label="阅读数据与学习工具">' +
          '<section class="nour-product-section"><div class="nour-product-section-head"><h2>我的阅读数据</h2><small>来自现有记录</small></div><div class="nour-stat-list"><div class="nour-stat"><b id="nourStatLearned">—</b><span>已掌握词汇</span></div><div class="nour-stat"><b id="nourStatStreak">—</b><span>连续学习天数</span></div><div class="nour-stat"><b id="nourStatBooks">—</b><span>可读书目</span></div><div class="nour-stat"><b id="nourStatRead">—</b><span>已留下足迹</span></div></div></section>' +
          '<section class="nour-product-section"><div class="nour-product-section-head"><h2>索引</h2><small>不再堆叠入口</small></div><div class="nour-tool-index"><button type="button" data-open-library><span><strong>书库</strong><small>典籍、古兰经、圣训、法学与开放原文</small></span><i>↗</i></button><button type="button" data-open-ai><span><strong>NOUR AI</strong><small>阅读助手、阿语导师、研究助手</small></span><i>↗</i></button><button type="button" data-open-wordbook><span><strong>生词本</strong><small>收藏词汇与阅读中的上下文</small></span><i>↗</i></button><button type="button" data-open-dict><span><strong>查词与发音</strong><small>本地释义、例句与设备阿语声音</small></span><i>↗</i></button><button type="button" data-open-listen><span><strong>音频与跟读</strong><small>设备朗读、资料库与练习</small></span><i>↗</i></button></div></section>' +
        '</aside>' +
      '</div>';
    header.insertAdjacentElement('afterend', section);

    /* Phase 2: promote existing daily content without duplicating or refetching it. */
    var continueList = q('#nourContinueList', section);
    if (continueList && continueList.parentNode && !q('.nour-daily-quote', section)) {
      var quote = document.createElement('section');
      quote.className = 'nour-product-section nour-daily-quote';
      quote.innerHTML = '<div class="nour-product-section-head"><h2>今日一句</h2><small>来自现有句子库</small></div>' +
        '<div class="nour-daily-quote-body"><div class="nour-daily-quote-ar" dir="rtl" lang="ar">' + esc(value('qAr')) + '</div><div class="nour-daily-quote-cn" dir="ltr" lang="zh-CN">' + esc(value('qCn')) + '</div><button type="button" class="nour-product-action" data-open-sentences>打开句子库</button></div>';
      continueList.parentNode.parentNode.insertAdjacentElement('afterend', quote);
      bindAction(q('[data-open-sentences]', quote), function () {
        if (typeof window.showAllSentences === 'function') window.showAllSentences(); else openLibrary();
      });
    }
    observeDailyQuote(section);

    var statList = q('.nour-stat-list', section);
    if (statList && !q('.nour-home-progress', section)) {
      var progress = document.createElement('div');
      progress.className = 'nour-home-progress';
      progress.innerHTML = '<div class="nour-home-progress-head"><span>今日学习进度</span><b id="nourHomeProgressValue">' + esc(styleValue('studyBar', '0%')) + '</b></div><div class="nour-home-progress-track"><i id="nourHomeProgressBar"></i></div>';
      statList.insertAdjacentElement('afterend', progress);
      q('#nourHomeProgressBar', progress).style.width = styleValue('studyBar', '0%');
    }
    var toolIndex = q('.nour-tool-index', section);
    if (toolIndex && toolIndex.parentNode && toolIndex.parentNode.tagName !== 'DETAILS') {
      var details = document.createElement('details'); details.className = 'nour-more-tools';
      var summary = document.createElement('summary');
      summary.innerHTML = '<span><strong>更多工具</strong><small>词典、生词本、音频与跟读</small></span><i aria-hidden="true">＋</i>';
      details.appendChild(summary);
      toolIndex.parentNode.insertBefore(details, toolIndex);
      details.appendChild(toolIndex);
    }
    var statBooks = q('#nourStatBooks', section);
    if (statBooks) {
      statBooks.textContent = value('hsBooks');
      if (statBooks.nextElementSibling) statBooks.nextElementSibling.textContent = '目录典籍';
    }
    var statRead = q('#nourStatRead', section);
    if (statRead && statRead.nextElementSibling) statRead.nextElementSibling.textContent = '最近足迹';

    bindAction(q('#nourProductSearch'), openSearch);
    qa('[data-open-ai]', section).forEach(function (b) { bindAction(b, openAI); });
    qa('[data-open-library]', section).forEach(function (b) { bindAction(b, openLibrary); });
    qa('[data-open-search]', section).forEach(function (b) { bindAction(b, openSearch); });
    qa('[data-open-wordbook]', section).forEach(function (b) { bindAction(b, openWordbook); });
    qa('[data-open-dict]', section).forEach(function (b) { bindAction(b, function () { call('openDict'); }); });
    qa('[data-open-listen]', section).forEach(function (b) { bindAction(b, function () { call('showListen'); }); });
    renderFootprints();
    syncStudyWorkspace();
    q('#nourStatLearned').textContent = value('studyLearned');
    q('#nourStatStreak').textContent = value('studyStreak');
    q('#nourStatBooks').textContent = value('hsReadable');
    q('#nourStatRead').textContent = String(readFootprints().length);
  }

  function syncStudyWorkspace() {
    var learned = value('studyLearned'), streak = value('studyStreak');
    var a = q('#studyWorkspaceLearned'), b = q('#studyWorkspaceStreak');
    if (a) a.textContent = learned; if (b) b.textContent = streak;
  }

  function syncPrimaryActive(route) {
    var allowed = {home:1, read:1, dict:1, study:1, me:1};
    if (!allowed[route]) route = 'home';
    window.NOUR_PRIMARY_ROUTE = route;
    var bar = q('.tabbar.nour-primary-nav');
    if (!bar) return;
    qa('.tb', bar).forEach(function (item) {
      var active = item.getAttribute('data-primary-route') === route;
      item.classList.toggle('nour-active', active);
      item.classList.toggle('on', active);
      if (active) item.setAttribute('aria-current', 'page'); else item.removeAttribute('aria-current');
    });
  }

  function openPrimaryRoute(route) {
    if (route === 'read') {
      syncPrimaryActive('read');
      return call('nav', 'learn');
    }
    if (route === 'dict') {
      syncPrimaryActive('dict');
      return call('openDict');
    }
    if (route === 'study') {
      syncPrimaryActive('study');
      call('detachModal', 'mLearn');
      var opened = call('openModal', 'mLearn');
      setTimeout(syncStudyWorkspace, 40);
      return opened;
    }
    if (route === 'me') {
      syncPrimaryActive('me');
      return call('nav', 'me');
    }
    syncPrimaryActive('home');
    return call('nav', 'home');
  }

  function makePrimaryButton(route, label, icon, aria) {
    var button = document.createElement('button');
    button.type = 'button'; button.className = 'tb';
    button.setAttribute('data-tab', route);
    button.setAttribute('data-primary-route', route);
    button.setAttribute('aria-label', aria || label);
    button.innerHTML = '<span class="t-ic">' + lineIcon(icon) + '</span><span class="t-nm">' + label + '</span>';
    button.addEventListener('click', function () { openPrimaryRoute(route); });
    return button;
  }

  function mountNav() {
    var bar = q('.tabbar'); if (!bar || bar.dataset.nourShellMounted) return;
    bar.dataset.nourShellMounted = '1'; bar.classList.add('nour-primary-nav');
    var search = q('[data-tab="search"]', bar), wordbook = q('[data-tab="wordbook"]', bar), learn = q('[data-tab="learn"]', bar), home = q('[data-tab="home"]', bar), me = q('[data-tab="me"]', bar);
    if (search) search.hidden = true;
    if (wordbook) wordbook.hidden = true;
    if (home) {
      home.setAttribute('data-primary-route', 'home'); home.setAttribute('aria-label', '首页');
      home.removeAttribute('onclick'); home.addEventListener('click', function () { openPrimaryRoute('home'); });
    }
    if (learn) {
      var ln = q('.t-nm', learn); if (ln) ln.textContent = '阅读';
      learn.setAttribute('data-tab', 'read'); learn.setAttribute('data-primary-route', 'read'); learn.setAttribute('aria-label', '打开阅读');
      learn.removeAttribute('onclick'); learn.addEventListener('click', function () { openPrimaryRoute('read'); });
    }
    if (me) {
      var mn = q('.t-nm', me); if (mn) mn.textContent = '我的';
      me.setAttribute('data-primary-route', 'me'); me.setAttribute('aria-label', '打开我的');
      me.removeAttribute('onclick'); me.addEventListener('click', function () { openPrimaryRoute('me'); });
    }
    var dict = q('[data-primary-route="dict"]', bar);
    if (!dict) dict = makePrimaryButton('dict', '词典', 'dict', '打开词典');
    var study = q('[data-primary-route="study"]', bar);
    if (!study) study = makePrimaryButton('study', '学习', 'study', '打开学习');
    if (learn && !dict.parentNode) bar.insertBefore(dict, learn.nextSibling);
    if (learn && !study.parentNode) bar.insertBefore(study, dict.nextSibling);
    if (!window.__NOUR_PRIMARY_NAV_WRAPPED__ && typeof window.nav === 'function') {
      var originalNav = window.nav;
      window.nav = function (tab) {
        var result = originalNav.apply(this, arguments);
        if (tab === 'learn') syncPrimaryActive('read');
        else if (tab === 'home') syncPrimaryActive('home');
        else if (tab === 'me') syncPrimaryActive('me');
        else if (tab !== 'ai' && tab !== 'search' && tab !== 'listen') syncPrimaryActive(window.NOUR_PRIMARY_ROUTE || 'home');
        else syncPrimaryActive(window.NOUR_PRIMARY_ROUTE || 'home');
        return result;
      };
      window.__NOUR_PRIMARY_NAV_WRAPPED__ = true;
    }
    var current = window.NOUR_PRIMARY_ROUTE || (window.NUR_ACTIVE_TAB === 'learn' ? 'read' : window.NUR_ACTIVE_TAB) || 'home';
    syncPrimaryActive(current);
  }


  function mountAI() {
    var ai = q('#aiSec'); if (!ai || ai.dataset.nourWorkspaceMounted) return;
    ai.dataset.nourWorkspaceMounted = '1'; ai.classList.add('nour-ai-workspace');
    var intro = document.createElement('div'); intro.className = 'nour-ai-intro';
    intro.innerHTML = '<div><div class="nour-ai-intro-kicker">NOUR AI · READING WORKSPACE</div><h1>让 AI 围绕正文工作</h1><p>你可以直接提问，也可以先在书库打开一页。AI 的回答会带着当前内容、语言和法学派视角，不把未经核验的总结当成原典。</p></div><div class="nour-ai-modes"><button type="button" class="nour-ai-mode is-active" data-ai-mode="reading">阅读助手</button><button type="button" class="nour-ai-mode" data-ai-mode="arabic">阿语导师</button><button type="button" class="nour-ai-mode" data-ai-mode="research">研究助手</button></div>';
    var note = document.createElement('div'); note.className = 'nour-ai-note'; note.textContent = '提示：打开书籍或选中一段阿拉伯语后，解释、词形、词根和相关书目会获得更完整的上下文。';
    ai.insertBefore(intro, ai.firstChild); ai.insertBefore(note, ai.children[1] || null);
    qa('[data-ai-mode]', intro).forEach(function (button) {
      button.addEventListener('click', function () {
        qa('[data-ai-mode]', intro).forEach(function (b) { b.classList.toggle('is-active', b === button); });
        var input = q('#homeAIIn');
        var mode = button.getAttribute('data-ai-mode');
        if (input) input.placeholder = mode === 'arabic' ? '输入阿拉伯语句子，问词形、语法或发音…' : mode === 'research' ? '输入一个研究问题，NOUR 会围绕现有资料回答…' : '输入你正在阅读的问题…';
        if (input) setTimeout(function () { input.focus(); }, 40);
      });
    });
  }

  function syncHomeStats() {
    var section = q('#nourProductHome'); if (!section) return;
    var statBooks = q('#nourStatBooks', section), sourceBooks = q('#hsBooks');
    if (statBooks && sourceBooks) {
      statBooks.textContent = String(sourceBooks.textContent || '').trim() || '—';
      if (statBooks.nextElementSibling) statBooks.nextElementSibling.textContent = '目录典籍';
    }
    var statRead = q('#nourStatRead', section);
    if (statRead) {
      statRead.textContent = String(readFootprints().length);
      if (statRead.nextElementSibling) statRead.nextElementSibling.textContent = '最近足迹';
    }
    var bar = q('#nourHomeProgressBar', section), valueEl = q('#nourHomeProgressValue', section);
    if (bar) { var width = styleValue('studyBar', '0%'); bar.style.width = width; if (valueEl) valueEl.textContent = width; }
  }

  function observeHomeStats() {
    if (!window.MutationObserver) return;
    var targets = ['hsBooks', 'studyBar', 'studyLearned', 'studyStreak'].map(function (id) { return document.getElementById(id); }).filter(Boolean);
    if (!targets.length) return;
    var observer = new MutationObserver(function () { syncHomeStats(); });
    targets.forEach(function (target) { observer.observe(target, { childList: true, characterData: true, attributes: true, subtree: true }); });
    window.setTimeout(function () { observer.disconnect(); }, 8000);
  }

  function mount() {
    mountHome(); mountNav(); mountAI();
    syncHomeStats(); observeHomeStats();
    window.setTimeout(renderFootprints, 900);
    window.setTimeout(syncHomeStats, 700);
    window.setTimeout(syncHomeStats, 1500);
    window.addEventListener('storage', function () { renderFootprints(); syncHomeStats(); });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount); else setTimeout(mount, 0);
})();
