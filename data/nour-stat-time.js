/* ============================================================================
   燃灯同学 · 首页「累计学习时间」统计 (Stat Time v1)
   读 nur_minutes，在第四屏统计里补上「学习时间」。
   ============================================================================ */
(function () {
  'use strict';
  function q(s) { return document.querySelector(s); }
  function mins() { try { var m = parseInt(localStorage.getItem('nur_minutes') || '0', 10); return isNaN(m) ? 0 : m; } catch (e) { return 0; } }
  function fmt(m) {
    if (m >= 60) { var h = Math.floor(m / 60), mm = m % 60; return mm ? (h + ' 时 ' + mm + ' 分') : (h + ' 小时'); }
    return m + ' 分钟';
  }
  function render() {
    var list = q('#nourProductHome .nour-stat-list');
    if (!list) return;
    var div = list.querySelector('.nour-stat-time');
    if (!div) {
      div = document.createElement('div');
      div.className = 'nour-stat nour-stat-time';
      div.innerHTML = '<b>0 分钟</b><span>累计学习时间</span>';
      list.appendChild(div);
    }
    var b = div.querySelector('b');
    if (b) b.textContent = fmt(mins());
  }
  function boot() { render(); setInterval(render, 5000); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
  setTimeout(boot, 1200);
})();
