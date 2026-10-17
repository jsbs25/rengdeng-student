/* NOUR 主题执行器：用内联 !important 强制关键表面配色，覆盖所有历史 CSS 层级。 */
(function () {
  var L = { bg:'#f7f5ef', surface:'#ffffff', surface2:'#f1efe8', ink:'#1f1e1b', ink2:'#6b6a64', ink3:'#9b9a93', line:'#e7e4da', brand:'#0f5132', gold:'#a98935' };
  var D = { bg:'#171512', surface:'#211e1a', surface2:'#2a2621', ink:'#ece6d8', ink2:'#b5ae9f', ink3:'#7d7768', line:'#332e25', brand:'#3a9a68', gold:'#c8a74d' };

  function set(el, prop, val) {
    if (el) el.style.setProperty(prop, val, 'important');
  }
  function setAll(sel, prop, val) {
    document.querySelectorAll(sel).forEach(function (el) { set(el, prop, val); });
  }

  function apply(P) {
    set(document.body, 'background', P.bg);
    set(document.body, 'background-image', 'none');
    set(document.body, 'color', P.ink);

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
  }

  function run() {
    var t = document.documentElement.getAttribute('data-theme');
    apply(t === 'dark' ? D : L);
  }

  run();
  try {
    new MutationObserver(run).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
  } catch (e) {}
})();
