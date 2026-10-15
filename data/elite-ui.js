/* Nour Elite UI — command palette, focus mode, progressive reveal and micro-interactions */
(function () {
  'use strict';
  if (window.__NOUR_ELITE_UI__) return;
  window.__NOUR_ELITE_UI__ = true;

  function q(sel, root) { return (root || document).querySelector(sel); }
  function qa(sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); }
  function safe(fn) { try { return fn(); } catch (e) { try { console.warn('[Nour Elite]', e); } catch (_) {} } }
  function call(name) { var args = Array.prototype.slice.call(arguments, 1); return safe(function () { if (typeof window[name] === 'function') return window[name].apply(window, args); }); }

  function mountScrollProgress() {
    if (q('#nourScrollProgress')) return;
    var bar = document.createElement('div'); bar.id = 'nourScrollProgress'; bar.setAttribute('aria-hidden', 'true'); document.body.appendChild(bar);
    function update() {
      var doc = document.documentElement, max = Math.max(1, doc.scrollHeight - window.innerHeight), pct = Math.max(0, Math.min(1, window.scrollY / max));
      bar.style.width = (pct * 100).toFixed(2) + '%';
    }
    window.addEventListener('scroll', update, { passive: true }); window.addEventListener('resize', update); update();
  }

  function mountAmbientRing() {
    var hero = q('#page-home>.tk-hero'); if (!hero || q('.nour-ambient-ring', hero)) return;
    var ring = document.createElement('div'); ring.className = 'nour-ambient-ring'; ring.setAttribute('aria-hidden', 'true'); hero.appendChild(ring);
  }

  function mountTopAction() {
    var hdr = q('#page-home>.hdr'); if (!hdr || q('#nourPaletteOpen')) return;
    var btn = document.createElement('button'); btn.id = 'nourPaletteOpen'; btn.className = 'nour-top-action'; btn.type = 'button'; btn.title = '打开 Nour 快捷指令'; btn.setAttribute('aria-label', '打开 Nour 快捷指令'); btn.textContent = '⌘';
    btn.addEventListener('click', openPalette); hdr.appendChild(btn);
  }

  function refreshMission() {
    var learned = q('#studyLearned'), streak = q('#studyStreak'), text = q('#nourMissionText');
    if (text) text.textContent = '今日已掌握 ' + ((learned && learned.textContent) || '0') + ' 个词 · 连续学习 ' + ((streak && streak.textContent) || '0') + ' 天';
  }
  function mountMission() {
    var home = q('#page-home'), progress = q('#studyProgress');
    if (!home || !progress || q('#nourMission')) return;
    var box = document.createElement('section'); box.id = 'nourMission'; box.className = 'nour-mission nour-reveal is-visible'; box.setAttribute('aria-label', '今日学习任务');
    box.innerHTML = '<div class="nour-mission-mark" aria-hidden="true">✦</div><div class="nour-mission-copy"><strong>今日点灯任务</strong><span id="nourMissionText">准备好开始今天的阿拉伯语学习了吗？</span></div><div class="nour-mission-actions"><button type="button" data-nour-action="challenge">闯一关</button><button type="button" data-nour-action="dialogue">学对话</button><button type="button" data-nour-action="voice">开始语音</button><button type="button" data-nour-action="library">逛书库</button></div>';
    progress.parentNode.insertBefore(box, progress); refreshMission();
    box.addEventListener('click', function (ev) { var b = ev.target.closest('[data-nour-action]'); if (!b) return; if (b.dataset.nourAction === 'voice') call('startNourVoice'); else if (b.dataset.nourAction === 'dialogue') call('showDialog'); else if (b.dataset.nourAction === 'challenge') call('showChallenge'); else call('nav', 'learn'); });
    window.setInterval(refreshMission, 2500);
  }

  var entries = [
    { key: 'voice', icon: '◉', title: '开始 Nour 快速语音', hint: '浏览器实时识别 · DeepSeek 流式回答', run: function () { call('startNourVoice'); } },
    { key: 'library', icon: '▤', title: '打开世界图书馆', hint: '阿拉伯书籍 · 全屏阅读', run: function () { call('nav', 'learn'); } },
    { key: 'dict', icon: 'ع', title: '查一个阿拉伯语单词', hint: '释义 · 词根 · 例句', run: function () { call('openDict'); } },
    { key: 'search', icon: '⌕', title: '全站搜索', hint: '句子 · 词汇 · 书籍 · 哲言', run: function () { call('openSearchAll'); } },
    { key: 'flash', icon: '◆', title: '开始闪卡复习', hint: '用间隔重复巩固词汇', run: function () { call('showFlashcard'); } },
    { key: 'quiz', icon: '?', title: '做一组小测验', hint: '随机题目 · 即时反馈', run: function () { call('showQuiz'); } },
    { key: 'challenge', icon: '⚡', title: '开始阿拉伯语闯关', hint: '词汇 · 语法 · 拼句 · XP 进度', run: function () { call('showChallenge'); } },
    { key: 'focus', icon: '◌', title: '进入专注模式', hint: '隐藏干扰，只留下今日学习舞台', run: function () { toggleFocus(true); } }
  ];
  var paletteIndex = 0;
  function renderPalette(filter) {
    var list = q('#nourPaletteList'); if (!list) return;
    var f = String(filter || '').trim().toLowerCase();
    var filtered = entries.filter(function (x) { return !f || (x.title + ' ' + x.hint + ' ' + x.key).toLowerCase().indexOf(f) >= 0; });
    paletteIndex = Math.max(0, Math.min(paletteIndex, Math.max(0, filtered.length - 1)));
    list.innerHTML = filtered.length ? filtered.map(function (x, i) { return '<button class="nour-palette-item ' + (i === paletteIndex ? 'is-active' : '') + '" type="button" data-palette-key="' + x.key + '"><i>' + x.icon + '</i><span><strong>' + x.title + '</strong><small>' + x.hint + '</small></span></button>'; }).join('') : '<div style="padding:22px;color:#89959b;text-align:center;font-size:12px">没有匹配的指令</div>';
    qa('[data-palette-key]', list).forEach(function (b) { b.addEventListener('click', function () { var e = entries.find(function (x) { return x.key === b.dataset.paletteKey; }); closePalette(); if (e) e.run(); }); });
  }
  function openPalette() {
    var modal = q('#nourPalette'); if (!modal) return;
    modal.classList.add('is-open'); modal.setAttribute('aria-hidden', 'false');
    var input = q('.nour-palette-input', modal); if (input) { input.value = ''; renderPalette(''); setTimeout(function () { input.focus(); }, 40); }
  }
  function closePalette() { var modal = q('#nourPalette'); if (modal) { modal.classList.remove('is-open'); modal.setAttribute('aria-hidden', 'true'); } }
  function mountPalette() {
    if (q('#nourPalette')) return;
    var modal = document.createElement('div'); modal.id = 'nourPalette'; modal.setAttribute('aria-hidden', 'true');
    modal.innerHTML = '<div class="nour-palette-card" role="dialog" aria-modal="true" aria-label="Nour 快捷指令"><div class="nour-palette-head"><b>Nour 快捷指令</b><span>把下一步交给我</span></div><input class="nour-palette-input" type="search" autocomplete="off" placeholder="搜索学习动作…（Esc 关闭）" aria-label="搜索快捷指令"><div id="nourPaletteList" class="nour-palette-list"></div><div class="nour-palette-foot">↑ ↓ 选择 · Enter 执行 · ⌘ K 打开</div></div>';
    document.body.appendChild(modal); renderPalette('');
    var input = q('.nour-palette-input', modal); if (input) input.addEventListener('input', function () { paletteIndex = 0; renderPalette(input.value); });
    modal.addEventListener('click', function (ev) { if (ev.target === modal) closePalette(); });
    document.addEventListener('keydown', function (ev) {
      if ((ev.metaKey || ev.ctrlKey) && ev.key.toLowerCase() === 'k') { ev.preventDefault(); openPalette(); return; }
      if (!modal.classList.contains('is-open')) return;
      if (ev.key === 'Escape') { ev.preventDefault(); closePalette(); }
      if (ev.key === 'ArrowDown' || ev.key === 'ArrowUp') { ev.preventDefault(); paletteIndex += ev.key === 'ArrowDown' ? 1 : -1; var items = qa('[data-palette-key]', modal); if (items.length) { paletteIndex = (paletteIndex + items.length) % items.length; items.forEach(function (b, i) { b.classList.toggle('is-active', i === paletteIndex); }); items[paletteIndex].scrollIntoView({block:'nearest'}); } }
      if (ev.key === 'Enter') { var active = q('.nour-palette-item.is-active', modal); if (active) active.click(); }
    });
  }

  function toggleFocus(force) {
    var on = typeof force === 'boolean' ? force : !document.body.classList.contains('nour-focus');
    document.body.classList.toggle('nour-focus', on);
    var btn = q('#nourFocusToggle'); if (btn) { btn.textContent = on ? '×' : '◌'; btn.title = on ? '退出专注模式' : '进入专注模式'; btn.setAttribute('aria-label', btn.title); }
    try { localStorage.setItem('nour_focus', on ? '1' : '0'); } catch (e) {}
  }
  function mountFocusToggle() {
    if (q('#nourFocusToggle')) return;
    var btn = document.createElement('button'); btn.id = 'nourFocusToggle'; btn.className = 'nour-focus-toggle'; btn.type = 'button'; btn.textContent = '◌'; btn.title = '进入专注模式'; btn.setAttribute('aria-label', '进入专注模式'); btn.addEventListener('click', function () { toggleFocus(); }); document.body.appendChild(btn);
    try { if (localStorage.getItem('nour_focus') === '1') toggleFocus(true); } catch (e) {}
  }
  function mountReveal() {
    var nodes = qa('#page-home>.vision-cards .vision-card, #page-home>#quote, #page-home>.study-progress, #homeShelves .bkcard, #page-home>.nour-mission');
    nodes.forEach(function (el) { el.classList.add('nour-reveal'); });
    if (!('IntersectionObserver' in window)) { nodes.forEach(function (el) { el.classList.add('is-visible'); }); return; }
    var io = new IntersectionObserver(function (entries) { entries.forEach(function (x) { if (x.isIntersecting) { x.target.classList.add('is-visible'); io.unobserve(x.target); } }); }, {threshold:.08, rootMargin:'0px 0px -30px'});
    nodes.forEach(function (el) { io.observe(el); });
  }
  function mountRipples() {
    document.addEventListener('pointerdown', function (ev) {
      var target = ev.target.closest('button,[role="button"],.bk-card,.vision-card,.chip');
      if (!target || target.closest('#nourPalette')) return;
      var rect = target.getBoundingClientRect(); target.classList.add('nour-ripple-host');
      var dot = document.createElement('span'); dot.className = 'nour-ripple'; dot.style.left = (ev.clientX - rect.left) + 'px'; dot.style.top = (ev.clientY - rect.top) + 'px'; target.appendChild(dot); setTimeout(function () { if (dot.parentNode) dot.parentNode.removeChild(dot); }, 700);
    }, {passive:true});
  }
  function mountAIInputMagic() {
    var compose = q('#aiSec .home-ai-compose'), send = q('#aiSec .home-ai-send'), mic = q('#aiSec .ps-mic');
    if (!compose || compose.dataset.magicMounted) return;
    compose.dataset.magicMounted = '1';
    function spot(ev) {
      var r = compose.getBoundingClientRect();
      compose.style.setProperty('--spot-x', ((ev.clientX - r.left) / Math.max(1, r.width) * 100).toFixed(1) + '%');
      compose.style.setProperty('--spot-y', ((ev.clientY - r.top) / Math.max(1, r.height) * 100).toFixed(1) + '%');
    }
    function resetSpot() { compose.style.setProperty('--spot-x', '50%'); compose.style.setProperty('--spot-y', '50%'); }
    compose.addEventListener('pointermove', spot, {passive:true});
    compose.addEventListener('pointerleave', resetSpot, {passive:true});
    [send, mic].forEach(function (button) {
      if (!button) return;
      button.addEventListener('pointermove', function (ev) {
        if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
        var r = button.getBoundingClientRect(), dx = (ev.clientX - (r.left + r.width / 2)) / Math.max(1, r.width), dy = (ev.clientY - (r.top + r.height / 2)) / Math.max(1, r.height);
        button.style.setProperty('--mag-x', (dx * 3.2).toFixed(2) + 'px'); button.style.setProperty('--mag-y', (dy * 3.2).toFixed(2) + 'px');
      }, {passive:true});
      button.addEventListener('pointerleave', function () { button.style.setProperty('--mag-x', '0px'); button.style.setProperty('--mag-y', '0px'); }, {passive:true});
      button.addEventListener('pointerdown', function () { button.classList.add('is-pressed'); setTimeout(function () { button.classList.remove('is-pressed'); }, 160); }, {passive:true});
    });
  }
  function mount() {
    mountScrollProgress(); mountAmbientRing(); mountTopAction(); mountMission(); mountPalette(); mountFocusToggle(); mountReveal(); mountRipples(); mountAIInputMagic();
    document.addEventListener('keydown', function (ev) { if (ev.key === 'Escape' && document.body.classList.contains('nour-focus')) toggleFocus(false); });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount); else setTimeout(mount, 0);
})();


/* Nour mobile natural AI — keyboard-safe chat behavior */
(function(){
  'use strict';
  if(window.__NOUR_MOBILE_NATURAL_AI__) return;
  window.__NOUR_MOBILE_NATURAL_AI__ = true;
  function q(s){return document.querySelector(s)}
  function mobile(){return window.innerWidth <= 700}
  function syncViewport(){
    var ai=q('#aiSec');
    if(!mobile()) return;
    var focus=q('#nourFocusToggle'), active=!!(ai && getComputedStyle(ai).display!=='none');
    if(focus) focus.style.display=active?'none':'';
    if(!active) return;
    var vv=window.visualViewport, h=vv && vv.height ? vv.height : window.innerHeight;
    ai.style.setProperty('--nour-ai-vh', Math.max(460, Math.round(h)) + 'px');
    var input=q('#homeAIIn'), msgs=q('#homeAI');
    if(input && document.activeElement===input && msgs){
      window.setTimeout(function(){try{msgs.scrollTop=msgs.scrollHeight}catch(e){}},80);
    }
  }
  function bind(){
    var input=q('#homeAIIn');
    if(input && !input.dataset.naturalBound){
      input.dataset.naturalBound='1';
      input.addEventListener('focus',syncViewport,{passive:true});
      input.addEventListener('input',function(){
        if(typeof window.homeAIInputState==='function') window.homeAIInputState(input);
        syncViewport();
      },{passive:true});
    }
    var msgs=q('#homeAI');
    if(msgs && !msgs.dataset.naturalScrollBound){
      msgs.dataset.naturalScrollBound='1';
      var mo=new MutationObserver(function(){if(document.activeElement===input || mobile()) window.setTimeout(function(){msgs.scrollTop=msgs.scrollHeight},40)});
      mo.observe(msgs,{childList:true,subtree:true,characterData:true});
    }
    syncViewport();
  }
  window.addEventListener('resize',syncViewport,{passive:true});
  window.addEventListener('orientationchange',function(){window.setTimeout(syncViewport,180)},{passive:true});
  if(window.visualViewport){window.visualViewport.addEventListener('resize',syncViewport,{passive:true});window.visualViewport.addEventListener('scroll',syncViewport,{passive:true})}
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',bind); else window.setTimeout(bind,0);
  window.setInterval(bind,700);
})();
