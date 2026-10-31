/* ============================================================================
   燃灯同学 · AI 回复 Markdown 渲染 (AI Markdown v1)
   为 #homeAI 的机器人回复提供 Markdown + 代码高亮 + 中阿混排。
   不改 homeAISend 的请求/业务逻辑，只在渲染层增强，可整体删除回滚。
   ============================================================================ */
(function () {
  'use strict';
  var DONE = 'data-nour-md';

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c];
    });
  }

  function md(src) {
    if (!src || typeof src !== 'string') return esc(src || '');
    var blocks = [];
    src = src.replace(/```([\w+#-]*)[ \t]*\n?([\s\S]*?)```/g, function (m, lang, code) {
      var i = blocks.length;
      var langAttr = lang ? ' data-lang="' + esc(lang) + '"' : '';
      blocks.push('<pre class="nour-code"' + langAttr + '><code>' + esc(code.replace(/\n$/, '')) + '</code></pre>');
      return '\u0000' + i + '\u0000';
    });
    var h = esc(src);
    h = h.replace(/`([^`\n]+)`/g, '<code class="nour-inline-code">$1</code>');
    h = h.replace(/\*\*([^*\n]+)\*\*/g, '<strong>$1</strong>');
    h = h.replace(/(^|[^*])\*([^*\n]+)\*(?!\*)/g, '$1<em>$2</em>');
    h = h.replace(/^###\s+(.+)$/gm, '<h4 class="nour-md-h">$1</h4>');
    h = h.replace(/^##\s+(.+)$/gm, '<h3 class="nour-md-h">$1</h3>');
    h = h.replace(/^#\s+(.+)$/gm, '<h2 class="nour-md-h">$1</h2>');
    h = h.replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
    h = h.replace(/^&gt;\s?(.+)$/gm, '<blockquote class="nour-md-quote">$1</blockquote>');
    h = h.replace(/^[-*+]\s+(.+)$/gm, '<li>$1</li>');
    h = h.replace(/^\d+\.\s+(.+)$/gm, '<li>$1</li>');
    h = h.replace(/(<li>[\s\S]*?<\/li>(?:\s*<li>[\s\S]*?<\/li>)*)/g, '<ul class="nour-md-list">$1</ul>');
    h = h.replace(/\n{2,}/g, '</p><p>');
    h = h.replace(/\n/g, '<br>');
    h = '<p>' + h + '</p>';
    h = h.replace(/\u0000(\d+)\u0000/g, function (m, i) { return blocks[+i] || ''; });
    return h;
  }

  function buttons() {
    return '<button class="ps-copy" onclick="copyMsg(this)">📋 复制</button><button class="ps-ai-speak" onclick="nourSpeakReply(this)" aria-label="朗读这条回复">🔊 朗读</button>';
  }

  function findBot(n) {
    if (!n || n.nodeType !== 1) return null;
    if (n.classList && n.classList.contains('ps-ai-msg') && n.classList.contains('bot')) return n;
    if (n.closest) return n.closest('.ps-ai-msg.bot');
    var p = n.parentElement;
    while (p) { if (p.classList && p.classList.contains('ps-ai-msg') && p.classList.contains('bot')) return p; p = p.parentElement; }
    return null;
  }

  function tryRender(el) {
    if (!el || el.getAttribute(DONE)) return;
    var raw = el.getAttribute('data-full');
    if (!raw) return;
    el.setAttribute(DONE, '1');
    el.innerHTML = md(raw) + buttons();
  }

  function watch() {
    var box = document.getElementById('homeAI');
    if (!box) return;
    new MutationObserver(function (muts) {
      muts.forEach(function (m) {
        Array.prototype.forEach.call(m.addedNodes || [], function (n) {
          var el = findBot(n);
          if (el) tryRender(el);
        });
      });
    }).observe(box, { childList: true, subtree: true });
  }

  function boot() {
    watch();
    var box = document.getElementById('homeAI');
    if (box) Array.prototype.forEach.call(box.querySelectorAll('.ps-ai-msg.bot'), tryRender);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
  setTimeout(boot, 1200);
})();
