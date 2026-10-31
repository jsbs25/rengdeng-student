/* ============================================================================
   燃灯同学 · 阅读器控制层 (Reader Controls v1)
   字号 A−/A+ 与四种阅读背景，纯前端增强。
   - 复用现有 .rd-bar，不重写阅读/翻页/书签逻辑
   - 通过 CSS 变量与 data-reader-bg 驱动，浅色/深色都可回退
   ============================================================================ */
(function () {
  'use strict';
  var FS_KEY = 'nur_reader_fs';
  var BG_KEY = 'nur_reader_bg';
  var FS = [15, 18, 21, 24];
  var FS_DEF = 1;
  var BGS = ['paper', 'sepia', 'green', 'night'];
  var BGS_LABEL = { paper: '纸白', sepia: '米黄', green: '护眼绿', night: '夜间' };

  function q(s, r) { return (r || document).querySelector(s); }
  function qa(s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); }
  function get(k, d) { try { var v = localStorage.getItem(k); return v == null ? d : v; } catch (e) { return d; } }
  function set(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }

  function fsIndex() {
    var i = parseInt(get(FS_KEY, String(FS_DEF)), 10);
    if (isNaN(i) || i < 0 || i >= FS.length) i = FS_DEF;
    return i;
  }

  function applyFs() {
    var i = fsIndex();
    document.documentElement.style.setProperty('--nour-reader-fs', FS[i] + 'px');
    document.documentElement.setAttribute('data-reader-fs', String(i));
    var v = q('.nour-rc .nour-rc-fsval');
    if (v) v.textContent = String(FS[i]);
  }

  function stepFs(d) {
    var i = Math.max(0, Math.min(FS.length - 1, fsIndex() + d));
    set(FS_KEY, String(i));
    applyFs();
  }

  function applyBg() {
    var bg = get(BG_KEY, 'paper');
    if (BGS.indexOf(bg) < 0) bg = 'paper';
    document.documentElement.setAttribute('data-reader-bg', bg);
    document.body.setAttribute('data-reader-bg', bg);
    qa('.nour-rc .nour-rc-swatch').forEach(function (b) {
      b.classList.toggle('on', b.getAttribute('data-bg') === bg);
      b.setAttribute('aria-pressed', b.getAttribute('data-bg') === bg ? 'true' : 'false');
    });
  }

  function setBg(bg) { set(BG_KEY, bg); applyBg(); }

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
      BGS.map(function (b) {
        return '<button type="button" class="nour-rc-swatch" data-bg="' + b + '" aria-label="' + BGS_LABEL[b] + '" title="' + BGS_LABEL[b] + '"></button>';
      }).join('');
    qa('[data-a]', g).forEach(function (b) { b.addEventListener('click', function () { stepFs(parseInt(b.getAttribute('data-a'), 10)); }); });
    qa('[data-bg]', g).forEach(function (b) { b.addEventListener('click', function () { setBg(b.getAttribute('data-bg')); }); });
    return g;
  }

  function attach() {
    var bar = q('body.reading #mReader .rd-bar');
    if (!bar || q('.nour-rc', bar)) return;
    bar.appendChild(build());
    applyFs();
    applyBg();
  }

  function watch() {
    var root = q('#mReader');
    if (!root) return;
    new MutationObserver(function () { attach(); }).observe(root, { childList: true, subtree: true });
    attach();
  }

  function boot() { applyFs(); applyBg(); watch(); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
  setTimeout(boot, 1200);
})();
