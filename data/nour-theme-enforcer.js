/* ============================================================================
   燃灯同学 Rengdeng Student · 主题执行器 v3 (Theme Enforcer)
   ----------------------------------------------------------------------------
   遵循全局 Design System v2.0 色彩规范：
   浅色模式：主背景 #FFFFFF · 次背景 #F5F5F7 · 主文字 #1D1D1F · 次文字 #86868B · 分割线 #D2D2D7
   深色模式：主背景 #0B0C0E · 次背景 #141619 · 卡片表面 #1C1E22 · 主文字 #F5F5F7 · 次文字 #A1A1A6 · 分割线 #2C2E33
   品牌色：橄榄墨绿 (#1B4D3E / #3CA680) 与 哑光金 (#B08D40 / #D1B062)，仅用于主按钮、选中状态与少量强调。
   ============================================================================ */
(function () {
  'use strict';

  var L = {
    bg: '#FFFFFF',
    bgSecondary: '#F5F5F7',
    surface: '#FFFFFF',
    surface2: '#F5F5F7',
    elevated: 'rgba(255, 255, 255, 0.88)',
    ink: '#1D1D1F',
    ink2: '#86868B',
    ink3: '#AEAEB2',
    line: '#D2D2D7',
    lineSubtle: '#E8E8ED',
    brand: '#1B4D3E',
    brandSoft: 'rgba(27, 77, 62, 0.08)',
    gold: '#B08D40'
  };

  var D = {
    bg: '#0B0C0E',
    bgSecondary: '#141619',
    surface: '#1C1E22',
    surface2: '#141619',
    elevated: 'rgba(28, 30, 34, 0.88)',
    ink: '#F5F5F7',
    ink2: '#A1A1A6',
    ink3: '#6E6E73',
    line: '#2C2E33',
    lineSubtle: '#222428',
    brand: '#3CA680',
    brandSoft: 'rgba(60, 166, 128, 0.15)',
    gold: '#D1B062'
  };

  function set(el, prop, val) {
    if (el && el.style) el.style.setProperty(prop, val, 'important');
  }
  function setAll(sel, prop, val) {
    try {
      document.querySelectorAll(sel).forEach(function (el) { set(el, prop, val); });
    } catch (e) {}
  }

  function apply(P, isDark) {
    var root = document.documentElement;
    if (root) {
      root.style.setProperty('color-scheme', isDark ? 'dark' : 'light', 'important');
      set(root, 'background', P.bg);
    }
    set(document.body, 'background', P.bg);
    set(document.body, 'background-image', 'none');
    set(document.body, 'color', P.ink);

    // 顶层页面容器
    setAll('body > .page, #page-home, #mCat, #page-search, #page-me, #aiSec', 'background', P.bg);
    setAll('body > .page, #page-home, #mCat, #page-search, #page-me, #aiSec', 'color', P.ink);

    // 顶部品牌导航栏
    setAll('#page-home > .hdr', 'background', P.elevated);
    setAll('#page-home > .hdr', 'border-bottom-color', P.lineSubtle);
    setAll('.hdr .logo, #page-home > .hdr .logo', 'color', P.ink);
    setAll('.hdr .logo-sub, #page-home > .hdr .logo-sub', 'color', P.ink2);

    // 底部主导航栏
    setAll('.tabbar', 'background', P.elevated);
    setAll('.tabbar', 'border-color', P.line);
    setAll('.tabbar .tb', 'color', P.ink2);
    setAll('.tabbar .tb', 'background', 'transparent');
    setAll('.tabbar .tb .t-nm', 'color', P.ink2);
    setAll('.tabbar .tb.on, .tabbar .tb.nour-active', 'background', P.brandSoft);
    setAll('.tabbar .tb.on, .tabbar .tb.nour-active', 'color', P.brand);
    setAll('.tabbar .tb.on .t-nm, .tabbar .tb.nour-active .t-nm', 'color', P.brand);

    // 弹窗与专注工作区
    setAll('.m-head, .page .pg-h', 'background', P.elevated);
    setAll('.m-head, .page .pg-h', 'color', P.ink);
    setAll('.m-head, .page .pg-h', 'border-color', P.line);
    setAll('.m-body', 'background', P.bgSecondary);
    setAll('.m-body', 'color', P.ink);

    // 表单输入框（排除实心主按钮）
    setAll('input:not([type="checkbox"]):not([type="radio"]), textarea, select', 'background', P.surface);
    setAll('input:not([type="checkbox"]):not([type="radio"]), textarea, select', 'color', P.ink);
    setAll('input:not([type="checkbox"]):not([type="radio"]), textarea, select', 'border-color', P.line);

    // 图书馆与阅读器表面
    setAll('.bk-side, .bk-card, .bkcard, .s-card, .gcard, .profile-card', 'background', P.surface);
    setAll('.bk-side, .bk-card, .bkcard, .s-card, .gcard, .profile-card', 'border-color', P.lineSubtle);
    setAll('.bk-side, .bk-card, .bkcard, .s-card, .gcard, .profile-card', 'color', P.ink);
    setAll('.bk-cat', 'color', P.ink2);
    setAll('.bk-cat.on', 'background', P.brandSoft);
    setAll('.bk-cat.on', 'color', P.brand);
    setAll('.bk-title, .bkname, .bk-meta, .bk-meta b', 'color', P.ink);
    setAll('.bkcat', 'color', P.ink2);
    setAll('.lib-tabs .lt', 'background', P.surface2);
    setAll('.lib-tabs .lt', 'color', P.ink2);
    setAll('.lib-tabs .lt', 'border-color', P.line);
    setAll('.lib-tabs .lt.on', 'background', P.brand);
    setAll('.lib-tabs .lt.on', 'color', '#FFFFFF');
    setAll('.lib-tabs .lt.on', 'border-color', P.brand);

    // 阅读器纸面（若用户未手动切到羊皮纸/护眼色，则跟随全局浅/深色）
    setAll('.rd-paper, .rd-page', 'background', P.surface);
    setAll('.rd-paper, .rd-page', 'color', P.ink);
    setAll('.rd-paper, .rd-page', 'border-color', P.lineSubtle);
    setAll('.rd-bar, .rd-head, .rd-foot', 'color', P.ink2);
    setAll('.rd-bar, .rd-head', 'border-color', P.lineSubtle);
    setAll('.rd-bar', 'background', P.elevated);
  }

  function run() {
    var t = document.documentElement.getAttribute('data-theme');
    var isDark = (t === 'dark');
    apply(isDark ? D : L, isDark);
  }

  window.__NOUR_ENFORCE_THEME__ = run;
  run();

  try {
    new MutationObserver(run).observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['data-theme']
    });
  } catch (e) {}

  var _deb;
  try {
    new MutationObserver(function (muts) {
      var added = false;
      for (var i = 0; i < muts.length; i++) {
        if (muts[i].addedNodes && muts[i].addedNodes.length) {
          added = true;
          break;
        }
      }
      if (!added) return;
      clearTimeout(_deb);
      _deb = setTimeout(run, 90);
    }).observe(document.body, { childList: true, subtree: true });
  } catch (e) {}
})();
