/* 古兰经阅读进度 (Quran Progress v1)：读 nur_quran_read，顶部显示进度条。 */
(function () {
  'use strict';
  function readCount() { try { var r = JSON.parse(localStorage.getItem('nur_quran_read') || '{}'); return Object.keys(r).length; } catch (e) { return 0; } }
  function render() {
    var body = document.getElementById('mQuranBody');
    if (!body || body.querySelector('.nour-quran-progress')) return;
    var n = readCount();
    var pct = Math.min(100, Math.round(n / 114 * 100));
    var bar = document.createElement('div');
    bar.className = 'nour-quran-progress';
    bar.innerHTML = '<div class="nour-quran-progress-h"><span>阅读进度</span><span>' + n + ' / 114 章</span></div><div class="nour-quran-progress-track"><i style="width:' + pct + '%"></i></div>';
    if (body.firstChild) body.insertBefore(bar, body.firstChild); else body.appendChild(bar);
  }
  function boot() {
    render();
    var body = document.getElementById('mQuranBody');
    if (body) new MutationObserver(function () { if (!body.querySelector('.nour-quran-progress')) render(); }).observe(body, { childList: true });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
  setTimeout(boot, 1000);
})();
