/* ============================================================================
   燃灯同学 · 阅读器控制层 v2 (Reader Controls)
   只做「常驻快捷入口」：A−/A+ 与阅读背景，全部委托现有 rdFs()/rdTheme()。
   不复制状态、不覆盖字号、不与现有主题打架。
   ============================================================================ */
(function () {
  'use strict';
  var THEMES = ['paper', 'sepia', 'night'];
  var THEME_LABEL = { paper: '纸张', sepia: '暖白', night: '夜间' };

  function q(s, r) { return (r || document).querySelector(s); }
  function qa(s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); }
  function store(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function call(name) { var a = Array.prototype.slice.call(arguments, 1); try { if (typeof window[name] === 'function') return window[name].apply(window, a); } catch (e) {} }

  function readFs() {
    var v = parseInt(store('nur_rdfont') || '18', 10);
    if (isNaN(v) || v < 13) v = 18;
    return v;
  }
  function readTheme() {
    var v = store('nur_rdtheme') || 'paper';
    return THEMES.indexOf(v) >= 0 ? v : 'paper';
  }

  function sync(g) {
    var val = q('.nour-rc-fsval', g);
    if (val) val.textContent = String(readFs());
    qa('.nour-rc-swatch', g).forEach(function (b) {
      var on = b.getAttribute('data-bg') === readTheme();
      b.classList.toggle('on', on);
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
  }

  function build() {
    var g = document.createElement('div');
    g.className = 'nour-rc';
    g.setAttribute('role', 'toolbar');
    g.setAttribute('aria-label', '阅读字号与背景');
    g.innerHTML =
      '<button type="button" class="nour-rc-fs" data-a="-1" aria-label="缩小字号">A−</button>' +
      '<span class="nour-rc-fsval">18</span>' +
      '<button type="button" class="nour-rc-fs" data-a="1" aria-label="放大字号">A+</button>' +
      '<span class="nour-rc-sep" aria-hidden="true"></span>' +
      THEMES.map(function (b) {
        return '<button type="button" class="nour-rc-swatch" data-bg="' + b + '" aria-label="' + THEME_LABEL[b] + '背景" title="' + THEME_LABEL[b] + '"></button>';
      }).join('');
    qa('[data-a]', g).forEach(function (b) {
      b.addEventListener('click', function () { call('rdFs', parseInt(b.getAttribute('data-a'), 10)); sync(g); });
    });
    qa('.nour-rc-swatch', g).forEach(function (b) {
      b.addEventListener('click', function () { call('rdTheme', b.getAttribute('data-bg')); sync(g); });
    });
    sync(g);
    return g;
  }

  function attach() {
    var bar = q('body.reading #mReader .rd-bar');
    if (!bar || q('.nour-rc', bar)) return;
    bar.appendChild(build());
  }

  function watch() {
    var root = q('#mReader');
    if (!root) return;
    new MutationObserver(function () { attach(); }).observe(root, { childList: true, subtree: true });
    attach();
  }

  function boot() { watch(); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
  setTimeout(boot, 1200);
})();
