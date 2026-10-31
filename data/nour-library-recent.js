/* 世界图书馆「最近阅读」书架 (Library Recent v1) */
(function () {
  'use strict';
  function q(s) { return document.querySelector(s); }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]; }); }
  function items() { try { var a = JSON.parse(localStorage.getItem('nur_read_footprints') || '[]'); return Array.isArray(a) ? a : []; } catch (e) { return []; } }
  function render() {
    var cat = q('#mCat'), body = q('#mCatBody');
    if (!cat || !body || cat.querySelector('.nour-recent')) return;
    var list = items();
    var sec = document.createElement('div');
    sec.className = 'nour-recent';
    var inner = '<div class="nour-recent-h"><span>最近阅读</span><span class="nour-recent-count">' + list.length + ' 项</span></div>';
    if (list.length) {
      inner += '<div class="nour-recent-list">' + list.slice(0, 6).map(function (x) {
        var mark = (x.kind === '书籍') ? '书' : '阅';
        return '<div class="nour-recent-item"><span class="nour-recent-mark">' + mark + '</span><span class="nour-recent-title">' + esc(x.title) + '</span><span class="nour-recent-time">' + esc(x.time || '') + '</span></div>';
      }).join('') + '</div>';
    } else {
      inner += '<div class="nour-recent-empty">还没有阅读记录，打开一本书后会自动出现在这里。</div>';
    }
    sec.innerHTML = inner;
    cat.insertBefore(sec, body);
  }
  function boot() { render(); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
  setTimeout(boot, 1000);
})();
