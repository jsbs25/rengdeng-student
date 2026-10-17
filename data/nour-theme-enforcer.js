/* NOUR 主题执行器 v2：内联 !important 强制全站关键表面配色，覆盖所有历史 CSS 层级。 */
(function () {
  var L = { bg:'#f7f5ef', surface:'#ffffff', surface2:'#f1efe8', ink:'#1f1e1b', ink2:'#6b6a64', ink3:'#9b9a93', line:'#e7e4da', brand:'#0f5132', gold:'#a98935' };
  var D = { bg:'#171512', surface:'#211e1a', surface2:'#2a2621', ink:'#ece6d8', ink2:'#b5ae9f', ink3:'#7d7768', line:'#332e25', brand:'#3a9a68', gold:'#c8a74d' };

  function set(el, prop, val) { if (el) el.style.setProperty(prop, val, 'important'); }
  function setAll(sel, prop, val) { document.querySelectorAll(sel).forEach(function (el) { set(el, prop, val); }); }

  function apply(P) {
    // 页面底
    set(document.body, 'background', P.bg);
    set(document.body, 'background-image', 'none');
    set(document.body, 'color', P.ink);
    set(document.documentElement, 'background', P.bg);

    // 底部导航
    setAll('.tabbar', 'background', P.surface);
    setAll('.tabbar', 'border-color', P.line);
    setAll('.tabbar .tb', 'color', P.ink2);
    setAll('.tabbar .tb.on', 'background', P.surface2);
    setAll('.tabbar .tb.on', 'color', P.brand);
    setAll('.tabbar .tb.on .t-nm', 'color', P.brand);

    // 弹窗
    setAll('.m-head', 'background', P.surface);
    setAll('.m-head', 'color', P.ink);
    setAll('.m-head', 'border-color', P.line);
    setAll('.m-body', 'background', P.bg);
    setAll('.m-body', 'color', P.ink);

    // 输入
    setAll('input, textarea, select', 'background', P.surface);
    setAll('input, textarea, select', 'color', P.ink);
    setAll('input, textarea, select', 'border-color', P.line);

    // 顶部品牌
    setAll('.hdr .logo, #page-home>.hdr .logo', 'color', P.brand);
    setAll('.hdr .logo-sub, #page-home>.hdr .logo-sub', 'color', P.ink2);
    setAll('.hdr .zh', 'color', P.ink3);

    // 各类卡片表面
    setAll('.nour-continue-item, .nour-discovery-block, .nour-stat, .nour-tool-index, .nour-daily-quote-body, .nour-home-progress, .nour-more-tools', 'background', P.surface);
    setAll('.nour-continue-item, .nour-discovery-block, .nour-stat, .nour-tool-index, .nour-daily-quote-body, .nour-home-progress, .nour-more-tools', 'border-color', P.line);
    setAll('.quote-card, .hs-row, .sup-card, .gcard, .belt-card, .vision-card, .hero', 'background', P.surface);
    setAll('.quote-card, .hs-row, .sup-card, .gcard, .belt-card, .vision-card, .hero', 'border-color', P.line);

    // 图书馆
    setAll('.bk-side, .bk-card', 'background', P.surface);
    setAll('.bk-side, .bk-card', 'border-color', P.line);
    setAll('.bk-side, .bk-card', 'color', P.ink);
    setAll('.bk-cat', 'color', P.ink2);
    setAll('.bk-cat.on', 'background', P.surface2);
    setAll('.bk-cat.on', 'color', P.brand);
    setAll('.bk-title, .bk-meta, .bk-meta b', 'color', P.ink);
    setAll('.bk-q', 'background', P.surface);
    setAll('.bk-q', 'color', P.ink);
    setAll('.bk-q', 'border-color', P.line);
    setAll('.lib-tabs .lt', 'background', P.surface);
    setAll('.lib-tabs .lt', 'color', P.ink2);
    setAll('.lib-tabs .lt.on', 'background', P.brand);
    setAll('.lib-tabs .lt.on', 'color', '#fff');

    // 阅读器
    setAll('.rd-paper, .rd-page', 'background', P.surface);
    setAll('.rd-paper, .rd-page', 'color', P.ink);
    setAll('.rd-paper, .rd-page', 'border-color', P.line);
    setAll('.rd-bar, .rd-head, .rd-foot', 'color', P.ink2);
    setAll('.rd-bar, .rd-head', 'border-color', P.line);
    setAll('.rd-bar', 'background', P.surface);
  }

  function run() {
    var t = document.documentElement.getAttribute('data-theme');
    apply(t === 'dark' ? D : L);
  }

  run();
  // 主题切换时立即重应用
  try {
    new MutationObserver(run).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
  } catch (e) {}
  // DOM 变化（动态渲染的图书馆/阅读器）防抖后重应用；仅新增节点时触发，避免无效重绘
  var _deb;
  try {
    new MutationObserver(function (muts) {
      var added = false;
      for (var i = 0; i < muts.length; i++) { if (muts[i].addedNodes && muts[i].addedNodes.length) { added = true; break; } }
      if (!added) return;
      clearTimeout(_deb);
      _deb = setTimeout(run, 80);
    }).observe(document.body, { childList: true, subtree: true });
  } catch (e) {}
})();
