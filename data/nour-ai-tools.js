/* ============================================================================
   燃灯同学 · AI 对话工具 (AI Tools v1)：清空对话 + 导出 Markdown 记录。
   纯前端增强，复用 #homeAI，不改 homeAISend 的请求/业务逻辑。
   ============================================================================ */
(function () {
  'use strict';
  function q(s, r) { return (r || document).querySelector(s); }

  function nourAIClear() {
    var box = document.getElementById('homeAI');
    if (!box) return;
    box.innerHTML = '<div class="ps-ai-msg bot">你好！我是你的阿拉伯语老师「努尔」，可以陪你练习对话、翻译、解释课文，或一起解决学习中的问题。</div>';
  }

  function nourAIExport() {
    var box = document.getElementById('homeAI');
    if (!box) return;
    var lines = [];
    Array.prototype.forEach.call(box.querySelectorAll('.ps-ai-msg'), function (m) {
      var who = m.classList.contains('user') ? '我' : '努尔老师';
      var txt = (m.getAttribute('data-full') || m.textContent || '').trim();
      if (txt) lines.push('## ' + who + '\n\n' + txt + '\n');
    });
    var md = '# 燃灯同学 · AI 对话记录\n\n' + (lines.join('\n') || '（暂无对话）');
    var blob = new Blob([md], { type: 'text/markdown;charset=utf-8' });
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = '燃灯同学-对话-' + new Date().toISOString().slice(0, 10) + '.md';
    document.body.appendChild(a);
    a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); if (a.parentNode) a.parentNode.removeChild(a); }, 300);
  }

  function build() {
    var sec = q('#aiSec');
    if (!sec || q('.nour-ai-tools', sec)) return;
    var bar = document.createElement('div');
    bar.className = 'nour-ai-tools';
    bar.setAttribute('role', 'toolbar');
    bar.setAttribute('aria-label', 'AI 对话工具');
    var clear = document.createElement('button');
    clear.type = 'button'; clear.className = 'nour-ai-tool'; clear.textContent = '清空对话';
    clear.addEventListener('click', nourAIClear);
    var exp = document.createElement('button');
    exp.type = 'button'; exp.className = 'nour-ai-tool'; exp.textContent = '导出对话';
    exp.addEventListener('click', nourAIExport);
    bar.appendChild(clear); bar.appendChild(exp);
    var msgs = q('#homeAI', sec);
    if (msgs && msgs.parentNode) msgs.parentNode.insertBefore(bar, msgs);
    else sec.appendChild(bar);
  }

  function boot() { build(); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
  setTimeout(boot, 1000);
})();
