/* NOUR reader context bridge: keeps the current book/page/selection available to AI. */
(function () {
  'use strict';
  if (window.__NOUR_READER_CONTEXT__) return;
  window.__NOUR_READER_CONTEXT__ = true;

  function q(sel, root) { return (root || document).querySelector(sel); }
  function esc(v) {
    return String(v == null ? '' : v).replace(/[&<>"']/g, function (c) {
      return ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]);
    });
  }
  function usable(text) {
    var v = String(text || '').trim();
    return v.length >= 6 && !/^(正在载入|尚未载入|原文载入失败|（本页没有可显示)/.test(v);
  }
  function cleanSelection(value) {
    return String(value == null ? '' : value).replace(/\s+/g, ' ').trim().slice(0, 180);
  }
  function sameReadingPosition(a, b) {
    if (!a || !b) return false;
    if (a.id && b.id && String(a.id) !== String(b.id)) return false;
    return String(a.title || '') === String(b.title || '') && Number(a.page || 0) === Number(b.page || 0);
  }
  function currentContext() {
    var pages = window.RD_PAGES || [];
    var page = Number(window.RD_PAGE || 0);
    var text = String(pages[page] || '').trim();
    if (!usable(text)) return null;
    var titleEl = document.getElementById('mReaderTitle');
    var title = String(titleEl && titleEl.textContent || '经典阅读').trim() || '经典阅读';
    var state = window.RD_OPENITI || null;
    var meta = window.RD_BOOK_META || null;
    var total = state && state.total ? Number(state.total) : pages.length;
    var id = String((state && state.id) || (meta && meta.id) || '');
    var previous = window.NOUR_AI_CONTEXT || null;
    var selected = sameReadingPosition(previous, {id:id, title:title, page:page + 1})
      ? cleanSelection(previous.selected || previous.selection)
      : '';
    var ctx = {
      id: id,
      title: title,
      page: page + 1,
      total: total || 1,
      text: text.slice(0, 3200),
      source: String((state && state.source) || (meta && meta.source) || ''),
      updatedAt: Date.now()
    };
    if (selected) {
      ctx.selected = selected;
      ctx.selection = selected;
    }
    return ctx;
  }
  function contextPrompt(ctx, question) {
    var selected = cleanSelection(ctx && (ctx.selected || ctx.selection));
    var prompt = '【当前阅读上下文】\n书名：' + ctx.title + '\n页码：第 ' + ctx.page + ' 页' +
      (ctx.total ? ' / ' + ctx.total : '') + '\n原文：\n' + ctx.text;
    if (selected) {
      prompt += '\n\n【用户选中的阿拉伯语词或短语】\n' + selected +
        '\n请优先解释这个选中内容的词根、词形、词性、基本义和当前语境义；无法确定的内容请明确标注并建议核验原典。';
    }
    return prompt + '\n\n【用户问题】\n' + question;
  }
  function renderContext() {
    var ai = document.getElementById('aiSec'); if (!ai) return;
    var ctx = window.NOUR_AI_CONTEXT || null, box = q('#nourReaderContext', ai);
    if (!box) {
      box = document.createElement('section');
      box.id = 'nourReaderContext';
      box.className = 'nour-reader-context';
      box.setAttribute('aria-live', 'polite');
      var note = q('.nour-ai-note', ai);
      if (note && note.parentNode) note.insertAdjacentElement('afterend', box);
      else ai.insertBefore(box, ai.firstChild);
    }
    if (!ctx) {
      box.hidden = false;
      box.classList.add('is-empty');
      box.innerHTML = '<div class="nour-reader-context__mark" aria-hidden="true">问</div>' +
        '<div class="nour-reader-context__copy"><strong>未连接正文语境</strong><span>普通问题仍可回答；涉及某本书或某一页时，请从书库打开正文，NOUR 才会引用当前页。</span></div>' +
        '<button type="button" class="nour-reader-context__open">打开书库</button>';
      var open = q('.nour-reader-context__open', box);
      if (open) open.onclick = function () {
        try {
          if (typeof nav === 'function') nav('learn');
          else if (typeof showCatalog === 'function') showCatalog();
        } catch (e) {}
      };
      return;
    }
    box.classList.remove('is-empty');
    var selected = cleanSelection(ctx.selected || ctx.selection);
    var selectionHtml = selected
      ? '<div class="nour-reader-context__selection"><span>选词</span><b dir="rtl" lang="ar">' + esc(selected) + '</b></div>'
      : '';
    box.hidden = false;
    box.innerHTML = '<div class="nour-reader-context__mark" aria-hidden="true">页</div>' +
      '<div class="nour-reader-context__copy"><strong>当前阅读语境已连接</strong><span>' +
      esc(ctx.title) + ' · 第 ' + esc(ctx.page) + ' 页' + (ctx.total ? ' / ' + esc(ctx.total) : '') +
      '</span></div>' + selectionHtml +
      '<button type="button" class="nour-reader-context__clear">清除</button>';
    var clear = q('.nour-reader-context__clear', box);
    if (clear) clear.onclick = function () {
      window.NOUR_AI_CONTEXT = null;
      renderContext();
    };
  }
  function setReaderSelection(value) {
    var selected = cleanSelection(value);
    if (!selected) return null;
    var ctx = currentContext() || window.NOUR_AI_CONTEXT || null;
    if (!ctx) return null;
    ctx.selected = selected;
    ctx.selection = selected;
    ctx.updatedAt = Date.now();
    window.NOUR_AI_CONTEXT = ctx;
    renderContext();
    try {
      window.dispatchEvent(new CustomEvent('nour:reader-selection', {detail:{word:selected, context:ctx}}));
    } catch (e) {}
    return ctx;
  }
  function sync() {
    var ctx = currentContext();
    if (ctx) window.NOUR_AI_CONTEXT = ctx;
    renderContext();
  }
  function installRenderBridge() {
    if (typeof window.renderRead !== 'function' || window.__NOUR_RENDER_CONTEXT_WRAPPED__) return;
    var original = window.renderRead;
    window.renderRead = function () {
      var result = original.apply(this, arguments);
      try { window.setTimeout(sync, 0); } catch (e) { sync(); }
      return result;
    };
    window.__NOUR_RENDER_CONTEXT_WRAPPED__ = true;
  }
  function installAIContextBridge() {
    if (typeof window.homeAISend !== 'function' || window.__NOUR_AI_CONTEXT_WRAPPED__) return;
    var originalSend = window.homeAISend;
    window.homeAISend = function () {
      var ctx = window.NOUR_AI_CONTEXT;
      if (!ctx || !usable(ctx.text)) return originalSend.apply(this, arguments);
      var originalFetch = window.fetch;
      var wrappedFetch = function (input, init) {
        try {
          var url = String(typeof input === 'string' ? input : (input && input.url) || '');
          if (url.indexOf('/api/chat/message') >= 0 && init && typeof init.body === 'string') {
            var body = JSON.parse(init.body);
            if (body && typeof body.message === 'string' && body.message.indexOf('【当前阅读上下文】') !== 0) {
              body.message = contextPrompt(ctx, body.message);
              init = Object.assign({}, init, {body: JSON.stringify(body)});
            }
          }
        } catch (e) {}
        return originalFetch.call(this, input, init);
      };
      window.fetch = wrappedFetch;
      try {
        var result = originalSend.apply(this, arguments);
        var restore = function () { if (window.fetch === wrappedFetch) window.fetch = originalFetch; };
        if (result && typeof result.finally === 'function') result.finally(restore);
        else window.setTimeout(restore, 0);
        return result;
      } catch (e) {
        if (window.fetch === wrappedFetch) window.fetch = originalFetch;
        throw e;
      }
    };
    window.__NOUR_AI_CONTEXT_WRAPPED__ = true;
  }
  function installSelectionBridge() {
    if (window.__NOUR_SELECTION_BRIDGE__) return;
    window.__NOUR_SELECTION_BRIDGE__ = true;
    document.addEventListener('selectionchange', function () {
      try {
        var reader = document.getElementById('mReader');
        var sel = window.getSelection && window.getSelection();
        if (!reader || !reader.classList.contains('show') || !document.body.classList.contains('reading') || !sel || !sel.rangeCount || !sel.anchorNode || !reader.contains(sel.anchorNode)) return;
        var selected = cleanSelection(sel.toString());
        if (selected && selected.length <= 180) setReaderSelection(selected);
      } catch (e) {}
    });
  }
  function mount() {
    window.NOUR_SET_READER_SELECTION = setReaderSelection;
    installRenderBridge();
    installAIContextBridge();
    installSelectionBridge();
    renderContext();
    if (window.RD_PAGES && window.RD_PAGES.length) sync();
  }
  window.NOUR_SYNC_READER_CONTEXT = sync;
  window.NOUR_SET_READER_SELECTION = setReaderSelection;
  window.addEventListener('nour:reader-context', sync);
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', function () { window.setTimeout(mount, 0); });
  else window.setTimeout(mount, 0);
  window.setInterval(function () {
    if (!window.__NOUR_RENDER_CONTEXT_WRAPPED__ || !window.__NOUR_AI_CONTEXT_WRAPPED__ || !window.__NOUR_SELECTION_BRIDGE__) mount();
  }, 1200);
})();
