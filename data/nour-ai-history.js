/* ============================================================================
   燃灯同学 · AI 对话历史持久化 (nour-ai-history v1)
   把 #homeAI 内容保存到 localStorage，刷新后恢复；纯前端，不改请求逻辑。
   ============================================================================ */
(function () {
  'use strict';
  var KEY = 'nur_ai_history';

  function nourHistoryEl() { return document.getElementById('homeAI'); }

  function nourHistorySave() {
    try {
      var box = nourHistoryEl();
      if (box && box.children.length) localStorage.setItem(KEY, box.innerHTML);
    } catch (e) {}
  }

  function nourHistoryLoad() {
    try {
      var box = nourHistoryEl();
      if (!box) return;
      var saved = localStorage.getItem(KEY);
      if (saved && saved.indexOf('ps-ai-msg') !== -1) box.innerHTML = saved;
    } catch (e) {}
  }

  function nourHistoryWatch() {
    var box = nourHistoryEl();
    if (!box || box.getAttribute('data-nour-hist')) return;
    box.setAttribute('data-nour-hist', '1');
    var t = null;
    new MutationObserver(function () {
      if (t) clearTimeout(t);
      t = setTimeout(nourHistorySave, 400);
    }).observe(box, { childList: true, subtree: true, characterData: true });
  }

  function nourHistoryBoot() { nourHistoryLoad(); nourHistoryWatch(); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', nourHistoryBoot);
  else nourHistoryBoot();
  setTimeout(nourHistoryBoot, 800);
})();
