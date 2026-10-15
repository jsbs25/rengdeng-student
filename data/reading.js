/* ============================================================
   燃灯同学 · 阅读增强  reading.js
   只做两件"加法"：夜间模式 + 阅读进度条
   —— 不修改任何现有功能逻辑
   ============================================================ */
(function(){
  var NIGHT_KEY = 'nur_lib_night';

  /* ---------- ① 夜间模式 ---------- */
  function applyNight(on){
    try{ document.body.setAttribute('data-lib-night', on ? '1' : '0'); }catch(e){}
    var b = document.getElementById('libNightBtn');
    if(b) b.textContent = on ? '☀️' : '🌙';
    var m = document.querySelector('meta[name="theme-color"]');
    if(m) m.setAttribute('content', on ? '#171a18' : '#faf8f3');
  }
  function toggleNight(){
    var on = document.body.getAttribute('data-lib-night') === '1';
    try{ localStorage.setItem(NIGHT_KEY, on ? '0' : '1'); }catch(e){}
    applyNight(!on);
  }
  function initNight(){
    var saved = '0';
    try{ saved = localStorage.getItem(NIGHT_KEY) || '0'; }catch(e){}
    // 跟随系统（用户没手动设过时）
    try{
      if(!localStorage.getItem(NIGHT_KEY) && window.matchMedia &&
         window.matchMedia('(prefers-color-scheme: dark)').matches){ saved = '1'; }
    }catch(e){}
    applyNight(saved === '1');
    // 插按钮（只在阅读时显示，CSS 控制）
    if(!document.getElementById('libNightBtn')){
      var btn = document.createElement('button');
      btn.id = 'libNightBtn';
      btn.type = 'button';
      btn.title = '夜间阅读模式';
      btn.setAttribute('aria-label', '夜间阅读模式');
      btn.onclick = toggleNight;
      document.body.appendChild(btn);
    }
  }
  window.libToggleNight = toggleNight;

  /* ---------- ② 阅读进度条 ---------- */
  function updateProgress(){
    var bar = document.getElementById('libProgress');
    if(!bar) return;
    var doc = document.documentElement;
    var h = (doc.scrollHeight - doc.clientHeight);
    var p = h > 0 ? (doc.scrollTop / h) * 100 : 0;
    bar.style.width = Math.max(0, Math.min(100, p)) + '%';
    // 数字进度（若有容器就写进去）
    var t = document.getElementById('libProgressTxt');
    if(t) t.textContent = Math.round(p) + '%';
  }
  function initProgress(){
    if(document.getElementById('libProgress')) return;
    var bar = document.createElement('div');
    bar.id = 'libProgress';
    bar.setAttribute('aria-hidden', 'true');
    document.body.appendChild(bar);
    window.addEventListener('scroll', function(){ requestAnimationFrame(updateProgress); }, {passive:true});
    // 阅读器里的滚动容器也要监听
    document.addEventListener('scroll', function(e){
      var el = e.target;
      if(el && el.scrollHeight > el.clientHeight + 20){
        var p = (el.scrollTop / (el.scrollHeight - el.clientHeight)) * 100;
        var b = document.getElementById('libProgress');
        if(b) b.style.width = Math.max(0, Math.min(100, p)) + '%';
      }
    }, true);
    updateProgress();
  }

  /* ---------- ③ 阅读器打开/关闭时同步 UI ---------- */
  function hookReader(){
    try{
      var cm = window.closeModal, om = window.openModal;
      if(typeof om === 'function' && !om.__lib){
        var nw = function(id){ var r = om.apply(this, arguments);
          if(id === 'mReader'){ setTimeout(function(){ updateProgress(); }, 300); } return r; };
        nw.__lib = 1; window.openModal = nw;
      }
      if(typeof cm === 'function' && !cm.__lib){
        var nw2 = function(id){ var r = cm.apply(this, arguments);
          if(id === 'mReader'){ var b = document.getElementById('libProgress'); if(b) b.style.width = '0'; }
          return r; };
        nw2.__lib = 1; window.closeModal = nw2;
      }
    }catch(e){}
  }


  /* ---------- ⑤ 关键：把主题 CSS 插到 <head> 最末尾（后加载 = 一定覆盖站内样式）---------- */
  function injectTheme(){
    try{
      var list = ['data/eink.css?v=r1','data/library.css?v=r1','data/upgrade.css?v=r1'];
      list.forEach(function(href){
        if(document.querySelector('link[href^="'+href.split('?')[0]+'"]')) return;
        var l = document.createElement('link');
        l.rel = 'stylesheet'; l.href = href;
        document.head.appendChild(l);   // 追加到末尾 → 优先级最高
      });
    }catch(e){}
  }

  /* ---------- ④ 启动 ---------- */
  function boot(){
    injectTheme();
    initNight();
    initProgress();
    hookReader();
  }
  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
  setTimeout(boot, 1800);
  setTimeout(hookReader, 3200);
})();
