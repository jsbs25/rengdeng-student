/* ============================================================================
   燃灯同学 Rengdeng Student · 产品壳层与编辑式四屏首页挂载器 (Product Shell v2.0)
   ----------------------------------------------------------------------------
   严格保留全部现有业务函数 (nav / openModal / showQuran / openDict / homeAISend 等)
   与原有 DOM ID，在此基础上实现 Apple 官网级四屏编辑式首页与多端自适应导航。
   ============================================================================ */
(function () {
  'use strict';
  if (window.__NOUR_PRODUCT_SHELL__) return;
  window.__NOUR_PRODUCT_SHELL__ = true;

  function q(sel, root) { return (root || document).querySelector(sel); }
  function qa(sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); }
  function esc(v) {
    return String(v == null ? '' : v).replace(/[&<>"']/g, function (c) {
      return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c];
    });
  }
  function call(name) {
    var args = Array.prototype.slice.call(arguments, 1);
    try {
      if (typeof window[name] === 'function') return window[name].apply(window, args);
    } catch (e) {}
  }

  function toast(message) {
    var box = q('#nourShellToast');
    if (!box) {
      box = document.createElement('div');
      box.id = 'nourShellToast';
      box.className = 'nour-shell-toast';
      document.body.appendChild(box);
    }
    box.textContent = message;
    box.classList.add('is-visible');
    clearTimeout(window.__NOUR_SHELL_TOAST_TIMER__);
    window.__NOUR_SHELL_TOAST_TIMER__ = setTimeout(function () {
      box.classList.remove('is-visible');
    }, 2600);
  }

  function readFootprints() {
    try {
      var raw = localStorage.getItem('nur_read_footprints') || '[]';
      var list = JSON.parse(raw);
      return Array.isArray(list) ? list.slice(0, 4) : [];
    } catch (e) {
      return [];
    }
  }

  function value(id, fallback) {
    var el = document.getElementById(id);
    var txt = el && String(el.textContent || '').trim();
    return txt || (fallback !== undefined ? fallback : '—');
  }

  function styleValue(id, fallback) {
    var el = document.getElementById(id);
    if (!el) return fallback || '0%';
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
    sources.forEach(function (source) {
      observer.observe(source, { childList: true, characterData: true, subtree: true });
    });
  }

  function lineIcon(kind) {
    if (kind === 'book' || kind === 'read') return '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 4.5A2.5 2.5 0 0 1 7.5 2H20v18H7.5A2.5 2.5 0 0 0 5 22.5z"/><path d="M5 4.5v18M9 6h7M9 10h7M9 14h5"/></svg>';
    if (kind === 'dict') return '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 4.5A2.5 2.5 0 0 1 7.5 2H20v18H7.5A2.5 2.5 0 0 0 5 22.5z"/><path d="M5 4.5v18M9 7h7M9 11h5"/><path d="M15.5 14.5l2.3 5M13.7 17.8h4.2"/></svg>';
    if (kind === 'study') return '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 5.5A2.5 2.5 0 0 1 7.5 3H20v16H7.5A2.5 2.5 0 0 0 5 21.5z"/><path d="M5 5.5v16M9 7h7M9 11h7"/><path d="m9 15 1.7 1.7L14 13.5"/></svg>';
    if (kind === 'spark') return '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2l1.8 6.2L20 10l-6.2 1.8L12 18l-1.8-6.2L4 10l6.2-1.8z"/><path d="M19 17v5M16.5 19.5h5"/></svg>';
    if (kind === 'person') return '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="8" r="3.5"/><path d="M5 21a7 7 0 0 1 14 0"/></svg>';
    if (kind === 'theme') return '<svg viewBox="0 0 24 24" aria-hidden="true" width="15" height="15" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8Z"/></svg>';
    return '<svg viewBox="0 0 24 24" aria-hidden="true" width="15" height="15" fill="none" stroke="currentColor" stroke-width="1.7"><circle cx="10.8" cy="10.8" r="6.3"/><path d="m16 16 4.5 4.5"/></svg>';
  }

  function bindAction(button, fn) {
    if (!button) return;
    button.addEventListener('click', function (ev) {
      ev.preventDefault();
      fn();
    });
  }

  /* 路由与核心功能动作（复用全部已有业务函数） */
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
  function openStudyWorkspace() {
    call('detachModal', 'mLearn');
    call('openModal', 'mLearn');
    setTimeout(syncStudyWorkspace, 40);
  }
  function openQuran() {
    if (typeof window.showQuran === 'function') return call('showQuran');
    return call('openModal', 'mQuran');
  }
  function toggleThemeQuick() {
    var html = document.documentElement;
    var next = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    if (typeof window.applyTheme === 'function') {
      call('applyTheme', next);
    } else {
      html.setAttribute('data-theme', next);
      try { localStorage.setItem('nur_theme', next); } catch (e) {}
    }
    var btn = q('#rdTopThemeBtn');
    if (btn) btn.setAttribute('aria-label', next === 'dark' ? '切换为浅色模式' : '切换为深色模式');
  }

  function renderFootprints() {
    var holder = q('#nourContinueList');
    if (!holder) return;
    var list = readFootprints();
    if (!list.length) {
      holder.innerHTML =
        '<div class="nour-continue-item">' +
          '<span class="nour-continue-mark" aria-hidden="true">ق</span>' +
          '<div class="nour-continue-copy">' +
            '<strong>尚未开始书架阅读</strong>' +
            '<small>进入世界图书馆选择一部典籍，阅读进度将自动保存在此处</small>' +
          '</div>' +
          '<button type="button" class="nour-product-action" data-open-library>浏览书架</button>' +
        '</div>';
      qa('[data-open-library]', holder).forEach(function (b) { bindAction(b, openLibrary); });
      return;
    }
    holder.innerHTML = list.map(function (item) {
      var title = esc(item.title || '未命名书目');
      var meta = esc((item.kind || '馆藏阅读') + (item.time ? ' · ' + item.time : ''));
      return (
        '<div class="nour-continue-item">' +
          '<span class="nour-continue-mark" aria-hidden="true">ق</span>' +
          '<div class="nour-continue-copy">' +
            '<strong>' + title + '</strong>' +
            '<small>' + meta + '</small>' +
          '</div>' +
          '<button type="button" class="nour-product-action" data-open-library>继续阅读</button>' +
        '</div>'
      );
    }).join('');
    qa('[data-open-library]', holder).forEach(function (b) { bindAction(b, openLibrary); });
  }

  function upgradeTopHeader(header) {
    if (!header || header.dataset.rdHeaderUpgraded) return;
    header.dataset.rdHeaderUpgraded = '1';
    var logo = q('.logo', header);
    if (logo) {
      logo.innerHTML =
        '<span class="rd-top-brand">' +
          '<span class="rd-top-brand-mark" lang="ar" dir="rtl">ن</span>' +
          '<span class="rd-top-brand-name">燃灯同学</span>' +
          '<span class="rd-top-brand-ar" lang="ar" dir="rtl">حامل المصباح</span>' +
        '</span>';
    }
    var rightBar = q('div[style*="display:flex"]', header);
    if (rightBar && !q('#nourProductSearch', rightBar)) {
      var searchBtn = document.createElement('button');
      searchBtn.type = 'button';
      searchBtn.id = 'nourProductSearch';
      searchBtn.className = 'rd-top-btn nour-product-search';
      searchBtn.setAttribute('aria-label', '全局搜索');
      searchBtn.innerHTML = lineIcon('search') + '<span>搜索</span>';
      bindAction(searchBtn, openSearch);

      var themeBtn = document.createElement('button');
      themeBtn.type = 'button';
      themeBtn.id = 'rdTopThemeBtn';
      themeBtn.className = 'rd-top-btn';
      themeBtn.setAttribute('aria-label', '切换浅色或深色外观');
      themeBtn.innerHTML = lineIcon('theme') + '<span>外观</span>';
      bindAction(themeBtn, toggleThemeQuick);

      rightBar.insertBefore(themeBtn, rightBar.firstChild);
      rightBar.insertBefore(searchBtn, rightBar.firstChild);
    }
  }

  function mountHome() {
    var home = q('#page-home'), header = home && q('.hdr', home);
    if (!home || !header || q('#nourProductHome')) return;

    upgradeTopHeader(header);

    var section = document.createElement('section');
    section.id = 'nourProductHome';
    section.className = 'nour-product-home';
    section.setAttribute('aria-label', '燃灯同学 · 知识与 AI 教育平台');

    section.innerHTML =
      /* ==================== 第一屏：品牌与主视觉 (Hero) ==================== */
      '<section class="rd-hero-screen" aria-label="品牌首屏">' +
        '<div class="rd-section-wrap rd-hero-grid">' +
          '<div class="rd-hero-copy">' +
            '<div class="rd-hero-eyebrow">' +
              '<span>RENGDENG STUDENT</span>' +
              '<span>·</span>' +
              '<span class="rd-hero-eyebrow-ar" lang="ar" dir="rtl">حامل المصباح</span>' +
            '</div>' +
            '<h1 class="rd-hero-brand nour-product-title">燃灯同学</h1>' +
            '<p class="rd-hero-subtitle">让学习成为一种探索。</p>' +
            '<p class="rd-hero-intro nour-product-lede">在语言、经典与人工智能之间，<br>建立属于自己的知识世界。</p>' +
            '<div class="rd-hero-ctas">' +
              '<button type="button" class="rd-btn-primary nour-product-action primary" data-open-study>开始学习</button>' +
              '<button type="button" class="rd-btn-secondary nour-product-action" data-open-ai>探索 AI</button>' +
            '</div>' +
          '</div>' +
          '<aside class="rd-hero-specimen nour-daily-quote" aria-label="每日原典选句">' +
            '<div class="rd-specimen-top">' +
              '<span class="rd-specimen-badge">今日原句 · آية وحكمة</span>' +
              '<span>双语对照</span>' +
            '</div>' +
            '<div class="nour-daily-quote-body" style="padding:0;border:0;background:transparent;box-shadow:none;display:block">' +
              '<div class="rd-specimen-ar nour-daily-quote-ar" dir="rtl" lang="ar">' + esc(value('qAr', 'العِلْمُ كَنْزٌ لَا يَفْنَىٰ')) + '</div>' +
              '<p class="rd-specimen-cn nour-daily-quote-cn" dir="ltr" lang="zh-CN">' + esc(value('qCn', '知识是永不消逝的宝藏')) + '</p>' +
            '</div>' +
            '<div class="rd-specimen-foot">' +
              '<button type="button" class="rd-text-link" data-open-sentences>进入 34,000+ 句原典语料库 ›</button>' +
              '<button type="button" class="rd-text-link" data-open-dict>词根查词 ›</button>' +
            '</div>' +
          '</aside>' +
        '</div>' +
      '</section>' +

      /* ==================== 第二屏：继续学习 (Continue Learning) ==================== */
      '<section class="rd-continue-screen" aria-label="继续学习">' +
        '<div class="rd-section-wrap">' +
          '<header class="rd-screen-header">' +
            '<div>' +
              '<div class="rd-screen-kicker">Continue Learning</div>' +
              '<h2 class="rd-screen-title">继续学习</h2>' +
              '<p class="rd-screen-desc">衔接最近学习的课程、阅读中的书籍与 AI 伴读对话。</p>' +
            '</div>' +
          '</header>' +
          '<div class="rd-continue-layout">' +
            /* 左侧：最近课程 + 学习进度 + 最近 AI 对话 */
            '<div class="rd-continue-panel">' +
              '<div class="rd-continue-panel-head">' +
                '<h3>最近学习的课程与 AI 对话</h3>' +
                '<small>今日进度实时同步</small>' +
              '</div>' +
              '<div class="rd-continue-stack">' +
                '<div class="rd-continue-course-row">' +
                  '<button type="button" class="rd-mini-task" data-open-study>' +
                    '<span class="rd-mini-task-tag">最近课程 · 阿拉伯语</span>' +
                    '<strong>真实语境句子与语法课</strong>' +
                    '<span>23 个核心场景 · 原音朗读与逐词拆解 ›</span>' +
                  '</button>' +
                  '<button type="button" class="rd-mini-task" data-open-ai>' +
                    '<span class="rd-mini-task-tag">最近的 AI 对话 · 努尔老师</span>' +
                    '<strong>继续跨语言问答与伴读</strong>' +
                    '<span>阅读助手 · 阿语语法导师 · 研究核验 ›</span>' +
                  '</button>' +
                '</div>' +
                '<div class="nour-home-progress" style="margin:0;padding:16px;border-radius:14px;background:var(--ds-bg-secondary);border:1px solid var(--ds-line-subtle)">' +
                  '<div class="nour-home-progress-head">' +
                    '<span>今日学习目标完成度</span>' +
                    '<b id="nourHomeProgressValue">' + esc(styleValue('studyBar', '0%')) + '</b>' +
                  '</div>' +
                  '<div class="nour-home-progress-track">' +
                    '<i id="nourHomeProgressBar" style="width:' + esc(styleValue('studyBar', '0%')) + '"></i>' +
                  '</div>' +
                '</div>' +
              '</div>' +
            '</div>' +
            /* 右侧：最近阅读的书籍 */
            '<div class="rd-continue-panel">' +
              '<div class="rd-continue-panel-head">' +
                '<h3>最近阅读的书籍</h3>' +
                '<small>自动记录最近 4 本馆藏</small>' +
              '</div>' +
              '<div id="nourContinueList" class="nour-continue-list"></div>' +
            '</div>' +
          '</div>' +
        '</div>' +
      '</section>' +

      /* ==================== 第三屏：探索知识 (Explore Knowledge) ==================== */
      '<section class="rd-explore-screen" aria-label="探索知识">' +
        '<div class="rd-section-wrap">' +
          '<header class="rd-screen-header">' +
            '<div>' +
              '<div class="rd-screen-kicker">Explore Knowledge</div>' +
              '<h2 class="rd-screen-title">探索知识</h2>' +
              '<p class="rd-screen-desc">四大核心知识领域，构建从语言习得到经典研读的完整路径。</p>' +
            '</div>' +
          '</header>' +
          '<div class="rd-explore-bento nour-discovery">' +
            /* 1. 阿拉伯语学习（跨 7 列主舞台） */
            '<article class="rd-domain-panel rd-domain-arabic nour-discovery-block">' +
              '<div>' +
                '<div class="rd-domain-kicker">Arabic Learning · اللغة العربية</div>' +
                '<h3 class="rd-domain-title">阿拉伯语学习</h3>' +
                '<p class="rd-domain-copy">从 28 个字母发音、核心语法体系到 3.4 万句带音符真实语料与 8.5 万词频词汇表，配合 SRS 间隔复习闪卡，让每一步习得都有章可循。</p>' +
              '</div>' +
              '<div class="rd-domain-pills">' +
                '<button type="button" class="rd-domain-pill" data-open-study>句子训练</button>' +
                '<button type="button" class="rd-domain-pill" data-open-vocab>高频词汇</button>' +
                '<button type="button" class="rd-domain-pill" data-open-grammar>系统语法</button>' +
                '<button type="button" class="rd-domain-pill" data-open-flash>闪卡复习</button>' +
                '<button type="button" class="rd-domain-pill" data-open-listen>听力跟读</button>' +
              '</div>' +
              '<div class="rd-domain-footer">' +
                '<button type="button" class="rd-btn-primary" data-open-study>进入阿拉伯语学习</button>' +
                '<span class="rd-domain-ar-watermark" lang="ar" dir="rtl">البيان</span>' +
              '</div>' +
            '</article>' +

            /* 2. AI 智能助手（跨 5 列智能交互面板） */
            '<article class="rd-domain-panel rd-domain-ai nour-discovery-block">' +
              '<div>' +
                '<div class="rd-domain-kicker">Apple Intelligence Style · الذكاء الاصطناعي</div>' +
                '<h3 class="rd-domain-title">AI 智能助手</h3>' +
                '<p class="rd-domain-copy">努尔老师（NOUR AI）围绕你正在阅读的正文工作：实时提供阿语词根拆解、句法分析、跨学派文献核验与自然语音对话。</p>' +
              '</div>' +
              '<div class="rd-domain-pills">' +
                '<button type="button" class="rd-domain-pill" data-open-ai>阅读伴读</button>' +
                '<button type="button" class="rd-domain-pill" data-open-ai>中阿互译与语法</button>' +
                '<button type="button" class="rd-domain-pill" data-open-talk>语音口语陪练</button>' +
              '</div>' +
              '<div class="rd-domain-footer">' +
                '<button type="button" class="rd-btn-secondary" data-open-ai>打开 AI 对话 ›</button>' +
                '<span class="rd-domain-ar-watermark" lang="ar" dir="rtl">نور</span>' +
              '</div>' +
            '</article>' +

            /* 3. 古兰经（跨 5 列文化典藏区） */
            '<article class="rd-domain-panel rd-domain-quran nour-discovery-block">' +
              '<div>' +
                '<div class="rd-domain-kicker">Sacred Classics · القرآن الكريم</div>' +
                '<h3 class="rd-domain-title">古兰经</h3>' +
                '<p class="rd-domain-copy">完整收录 114 章 6,236 节阿拉伯语原文与中文权威译注，支持名家诵读音频同步播放与 AI 逐词词形分解。</p>' +
              '</div>' +
              '<div class="rd-domain-pills">' +
                '<button type="button" class="rd-domain-pill" data-open-quran>114 章全本</button>' +
                '<button type="button" class="rd-domain-pill" data-open-quran>诵读音频</button>' +
                '<button type="button" class="rd-domain-pill" data-open-hadith>哲言与圣训</button>' +
              '</div>' +
              '<div class="rd-domain-footer">' +
                '<button type="button" class="rd-btn-secondary" data-open-quran>进入古兰经选读 ›</button>' +
                '<span class="rd-domain-ar-watermark" lang="ar" dir="rtl">اقرأ</span>' +
              '</div>' +
            '</article>' +

            /* 4. 世界图书馆（跨 7 列馆藏长卷区） */
            '<article class="rd-domain-panel rd-domain-library nour-discovery-block">' +
              '<div>' +
                '<div class="rd-domain-kicker">World Library · المكتبة العالمية</div>' +
                '<h3 class="rd-domain-title">世界图书馆</h3>' +
                '<p class="rd-domain-copy">汇聚 23,000+ 部世界典籍、8,400+ 部历史文献、伊斯兰经典书目与中文传世古籍。内置 Apple Books 级双语阅读器，支持即点即查与段落 AI 导读。</p>' +
              '</div>' +
              '<div class="rd-domain-pills">' +
                '<button type="button" class="rd-domain-pill" data-open-library>馆藏书架</button>' +
                '<button type="button" class="rd-domain-pill" data-open-islamic-lib>伊斯兰经典馆</button>' +
                '<button type="button" class="rd-domain-pill" data-open-civ>世界文明图谱</button>' +
              '</div>' +
              '<div class="rd-domain-footer">' +
                '<button type="button" class="rd-btn-primary" data-open-library>进入世界图书馆</button>' +
                '<span class="rd-domain-ar-watermark" lang="ar" dir="rtl">المكتبة</span>' +
              '</div>' +
            '</article>' +
          '</div>' +
        '</div>' +
      '</section>' +

      /* ==================== 第四屏：个人学习统计 (Personal Learning Stats) ==================== */
      '<section class="rd-stats-screen" aria-label="个人学习统计">' +
        '<div class="rd-section-wrap">' +
          '<header class="rd-screen-header">' +
            '<div>' +
              '<div class="rd-screen-kicker">Personal Analytics</div>' +
              '<h2 class="rd-screen-title">个人学习统计</h2>' +
              '<p class="rd-screen-desc">安静记录每一次坚持、词汇积累与经典阅读进度。</p>' +
            '</div>' +
          '</header>' +
          '<div class="nour-stat-list">' +
            '<div class="nour-stat"><b id="nourStatStreak">—</b><span>连续学习天数</span></div>' +
            '<div class="nour-stat"><b id="nourStatLearned">—</b><span>单词记忆与掌握</span></div>' +
            '<div class="nour-stat"><b id="nourStatRead">—</b><span>最近阅读进度 (本)</span></div>' +
            '<div class="nour-stat"><b id="nourStatBooks">—</b><span>馆藏可读典籍</span></div>' +
          '</div>' +
          '<details class="nour-more-tools" style="margin-top:24px;background:var(--ds-surface);border:1px solid var(--ds-line-subtle);border-radius:16px">' +
            '<summary style="padding:16px 20px"><span><strong>全部学习工具索引</strong><small>词典、生词本、闯关测验、字母入门与音频资料库</small></span><i aria-hidden="true">＋</i></summary>' +
            '<div class="nour-tool-index" style="padding:0 20px">' +
              '<button type="button" data-open-dict><span><strong>阿拉伯语词典</strong><small>词根、近义词、反义词与双语例句</small></span><i>›</i></button>' +
              '<button type="button" data-open-wordbook><span><strong>我的生词本</strong><small>管理阅读与查词中收藏的词汇</small></span><i>›</i></button>' +
              '<button type="button" data-open-alphabet><span><strong>28 字母入门课</strong><small>标准发音、词头词中词尾写法与小测</small></span><i>›</i></button>' +
              '<button type="button" data-open-challenge><span><strong>闯关与随机测验</strong><small>拼句训练、词义辨析与复习巩固</small></span><i>›</i></button>' +
              '<button type="button" data-open-listen><span><strong>听力跟读与音频库</strong><small>原生阿语发音评测与无损音频资料</small></span><i>›</i></button>' +
            '</div>' +
          '</details>' +
        '</div>' +
      '</section>';

    header.insertAdjacentElement('afterend', section);
    observeDailyQuote(section);

    /* 绑定所有交互入口 */
    qa('[data-open-study]', section).forEach(function (b) { bindAction(b, openStudyWorkspace); });
    qa('[data-open-ai]', section).forEach(function (b) { bindAction(b, openAI); });
    qa('[data-open-library]', section).forEach(function (b) { bindAction(b, openLibrary); });
    qa('[data-open-quran]', section).forEach(function (b) { bindAction(b, openQuran); });
    qa('[data-open-search]', section).forEach(function (b) { bindAction(b, openSearch); });
    qa('[data-open-wordbook]', section).forEach(function (b) { bindAction(b, openWordbook); });
    qa('[data-open-dict]', section).forEach(function (b) { bindAction(b, function () { call('openDict'); }); });
    qa('[data-open-listen]', section).forEach(function (b) { bindAction(b, function () { call('showListen'); }); });
    qa('[data-open-sentences]', section).forEach(function (b) { bindAction(b, function () { call('showAllSentences'); }); });
    qa('[data-open-vocab]', section).forEach(function (b) { bindAction(b, function () { call('showVocab'); }); });
    qa('[data-open-grammar]', section).forEach(function (b) { bindAction(b, function () { call('showGrammar'); }); });
    qa('[data-open-flash]', section).forEach(function (b) { bindAction(b, function () { call('showFlashcard'); }); });
    qa('[data-open-alphabet]', section).forEach(function (b) { bindAction(b, function () { call('showAlphabet'); }); });
    qa('[data-open-challenge]', section).forEach(function (b) { bindAction(b, function () { call('showChallenge'); }); });
    qa('[data-open-talk]', section).forEach(function (b) { bindAction(b, function () { call('openModal', 'mTalk'); }); });
    qa('[data-open-hadith]', section).forEach(function (b) { bindAction(b, function () { call('showH6'); }); });
    qa('[data-open-islamic-lib]', section).forEach(function (b) { bindAction(b, function () { call('showIslamicLibrary'); }); });
    qa('[data-open-civ]', section).forEach(function (b) { bindAction(b, function () { call('openCiv'); }); });

    renderFootprints();
    syncStudyWorkspace();
    q('#nourStatLearned').textContent = value('studyLearned', '0');
    q('#nourStatStreak').textContent = value('studyStreak', '0');
    q('#nourStatBooks').textContent = value('hsReadable', '13,185');
    q('#nourStatRead').textContent = String(readFootprints().length);
  }

  function syncStudyWorkspace() {
    var learned = value('studyLearned', '0'), streak = value('studyStreak', '0');
    var a = q('#studyWorkspaceLearned'), b = q('#studyWorkspaceStreak');
    if (a) a.textContent = learned;
    if (b) b.textContent = streak;
  }

  function syncPrimaryActive(route) {
    var allowed = { home: 1, read: 1, dict: 1, study: 1, me: 1 };
    if (!allowed[route]) route = 'home';
    window.NOUR_PRIMARY_ROUTE = route;
    var bar = q('.tabbar.nour-primary-nav');
    if (!bar) return;
    qa('.tb', bar).forEach(function (item) {
      var active = item.getAttribute('data-primary-route') === route;
      item.classList.toggle('nour-active', active);
      item.classList.toggle('on', active);
      if (active) item.setAttribute('aria-current', 'page');
      else item.removeAttribute('aria-current');
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
    button.type = 'button';
    button.className = 'tb';
    button.setAttribute('data-tab', route);
    button.setAttribute('data-primary-route', route);
    button.setAttribute('aria-label', aria || label);
    button.innerHTML = '<span class="t-ic">' + lineIcon(icon) + '</span><span class="t-nm">' + label + '</span>';
    button.addEventListener('click', function () { openPrimaryRoute(route); });
    return button;
  }

  function mountNav() {
    var bar = q('.tabbar');
    if (!bar || bar.dataset.nourShellMounted) return;
    bar.dataset.nourShellMounted = '1';
    bar.classList.add('nour-primary-nav');
    var search = q('[data-tab="search"]', bar),
        wordbook = q('[data-tab="wordbook"]', bar),
        learn = q('[data-tab="learn"]', bar),
        home = q('[data-tab="home"]', bar),
        me = q('[data-tab="me"]', bar);
    if (search) search.hidden = true;
    if (wordbook) wordbook.hidden = true;
    if (home) {
      home.setAttribute('data-primary-route', 'home');
      home.setAttribute('aria-label', '首页');
      home.removeAttribute('onclick');
      home.addEventListener('click', function () { openPrimaryRoute('home'); });
    }
    if (learn) {
      var ln = q('.t-nm', learn);
      if (ln) ln.textContent = '阅读';
      learn.setAttribute('data-tab', 'read');
      learn.setAttribute('data-primary-route', 'read');
      learn.setAttribute('aria-label', '打开阅读');
      learn.removeAttribute('onclick');
      learn.addEventListener('click', function () { openPrimaryRoute('read'); });
    }
    if (me) {
      var mn = q('.t-nm', me);
      if (mn) mn.textContent = '我的';
      me.setAttribute('data-primary-route', 'me');
      me.setAttribute('aria-label', '打开我的');
      me.removeAttribute('onclick');
      me.addEventListener('click', function () { openPrimaryRoute('me'); });
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
        else syncPrimaryActive(window.NOUR_PRIMARY_ROUTE || 'home');
        return result;
      };
      window.__NOUR_PRIMARY_NAV_WRAPPED__ = true;
    }
    var current = window.NOUR_PRIMARY_ROUTE || (window.NUR_ACTIVE_TAB === 'learn' ? 'read' : window.NUR_ACTIVE_TAB) || 'home';
    syncPrimaryActive(current);
  }

  function mountAI() {
    var ai = q('#aiSec');
    if (!ai || ai.dataset.nourWorkspaceMounted) return;
    ai.dataset.nourWorkspaceMounted = '1';
    ai.classList.add('nour-ai-workspace');
    var intro = document.createElement('div');
    intro.className = 'nour-ai-intro';
    intro.innerHTML =
      '<div>' +
        '<div class="nour-ai-intro-kicker">RENGDENG AI · 智能教育与经典伴读</div>' +
        '<h1>努尔 AI 助手</h1>' +
        '<p>兼具高效对话与严谨语境感知。支持阿拉伯语与中文混排解析、词根语法拆解、篇章翻译与原典核验。</p>' +
      '</div>' +
      '<div class="nour-ai-modes">' +
        '<button type="button" class="nour-ai-mode is-active" data-ai-mode="reading">阅读伴读</button>' +
        '<button type="button" class="nour-ai-mode" data-ai-mode="arabic">阿语语法导师</button>' +
        '<button type="button" class="nour-ai-mode" data-ai-mode="research">文献研究核验</button>' +
      '</div>';
    var note = document.createElement('div');
    note.className = 'nour-ai-note';
    note.textContent = '提示：打开书籍或选中一段阿拉伯语后提问，AI 会自动携带当前章节、词根与上下文进行解答。';
    ai.insertBefore(intro, ai.firstChild);
    ai.insertBefore(note, ai.children[1] || null);
    qa('[data-ai-mode]', intro).forEach(function (button) {
      button.addEventListener('click', function () {
        qa('[data-ai-mode]', intro).forEach(function (b) { b.classList.toggle('is-active', b === button); });
        var input = q('#homeAIIn');
        var mode = button.getAttribute('data-ai-mode');
        if (input) {
          input.placeholder =
            mode === 'arabic'
              ? '输入阿拉伯语句子，分析词根、词形变化与句法结构…'
              : mode === 'research'
              ? '输入研究主题或术语，围绕馆藏原典进行核验…'
              : '写下你想探讨的阿拉伯语、经典或阅读问题…';
          setTimeout(function () { input.focus(); }, 40);
        }
      });
    });
  }

  function syncHomeStats() {
    var section = q('#nourProductHome');
    if (!section) return;
    var statBooks = q('#nourStatBooks', section), sourceBooks = q('#hsBooks');
    if (statBooks && sourceBooks) {
      var bVal = String(sourceBooks.textContent || '').trim();
      statBooks.textContent = (bVal && bVal !== '—') ? bVal : '23,835';
    }
    var statLearned = q('#nourStatLearned', section);
    if (statLearned) statLearned.textContent = value('studyLearned', '0');
    var statStreak = q('#nourStatStreak', section);
    if (statStreak) statStreak.textContent = value('studyStreak', '0');
    var statRead = q('#nourStatRead', section);
    if (statRead) statRead.textContent = String(readFootprints().length);

    var bar = q('#nourHomeProgressBar', section), valueEl = q('#nourHomeProgressValue', section);
    if (bar) {
      var width = styleValue('studyBar', '0%');
      bar.style.width = width;
      if (valueEl) valueEl.textContent = width;
    }
  }

  function observeHomeStats() {
    if (!window.MutationObserver) return;
    var targets = ['hsBooks', 'studyBar', 'studyLearned', 'studyStreak']
      .map(function (id) { return document.getElementById(id); })
      .filter(Boolean);
    if (!targets.length) return;
    var observer = new MutationObserver(function () { syncHomeStats(); });
    targets.forEach(function (target) {
      observer.observe(target, { childList: true, characterData: true, attributes: true, subtree: true });
    });
    window.setTimeout(function () { observer.disconnect(); }, 8000);
  }

  /* 全局快捷键支持：Cmd/Ctrl + K 呼出全站搜索 */
  function bindGlobalShortcuts() {
    if (window.__RD_SHORTCUTS_BOUND__) return;
    window.__RD_SHORTCUTS_BOUND__ = true;
    document.addEventListener('keydown', function (ev) {
      if ((ev.metaKey || ev.ctrlKey) && String(ev.key).toLowerCase() === 'k') {
        ev.preventDefault();
        openSearch();
      }
    });
  }

  function mount() {
    mountHome();
    mountNav();
    mountAI();
    bindGlobalShortcuts();
    syncHomeStats();
    observeHomeStats();
    window.setTimeout(renderFootprints, 900);
    window.setTimeout(syncHomeStats, 700);
    window.setTimeout(syncHomeStats, 1500);
    window.addEventListener('storage', function () {
      renderFootprints();
      syncHomeStats();
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount);
  else setTimeout(mount, 0);
})();
