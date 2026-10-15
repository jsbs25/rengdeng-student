/* ============================================================
   合并「听力练习」到「句子库」
   —— 侧栏隐藏独立的听力入口，在句子库里加一个 🔊 听力 标签
   —— 只做 UI 层操作，不改任何原函数
   ============================================================ */
(function(){
  var TITLES = ['听力训练','听力练习','听力'];

  /* ① 隐藏侧栏里的「听力」项 */
  function hideListenNav(){
    var n = 0;
    document.querySelectorAll('.chip,.mi,[onclick],[class*=nav]').forEach(function(el){
      if(el.__mlHidden) return;
      var t = (el.textContent || '').trim();
      if(!t || t.length > 12) return;
      for(var i=0;i<TITLES.length;i++){
        if(t.indexOf(TITLES[i]) === 0 || t === TITLES[i]){
          el.style.display = 'none';
          el.__mlHidden = 1; n++;
          break;
        }
      }
    });
    return n;
  }

  /* ② 在句子库视图顶部插「句子库 | 听力」标签 */
  function addTabs(){
    var host = document.getElementById('sentView') || document.querySelector('[id*=sent]') ||
               (function(){
                 // 兜底：找包含"句子"标题的弹层主体
                 var m = document.querySelector('.modal.show .m-body');
                 return m;
               })();
    if(!host) return false;
    if(host.querySelector('#mlTabs')) return true;
    var bar = document.createElement('div');
    bar.id = 'mlTabs';
    bar.style.cssText = 'display:flex;gap:8px;margin:0 0 14px;padding:0 2px';
    bar.innerHTML =
        '<button id="mlTabSent" style="flex:0 0 auto;min-height:44px;padding:10px 18px;border-radius:4px;border:1px solid rgba(26,26,26,.14);background:#1a1a1a;color:#fdfbf7;font-weight:650;font-size:.88rem;cursor:pointer">💬 句子库</button>'
      + '<button id="mlTabListen" style="flex:0 0 auto;min-height:44px;padding:10px 18px;border-radius:4px;border:1px solid rgba(26,26,26,.14);background:transparent;color:#6d6d68;font-weight:650;font-size:.88rem;cursor:pointer">🎧 听力练习</button>';
    host.insertBefore(bar, host.firstChild);
    var bS = bar.querySelector('#mlTabSent'), bL = bar.querySelector('#mlTabListen');
    function on(el, off){
      el.style.background = '#1a1a1a'; el.style.color = '#fdfbf7';
      off.style.background = 'transparent'; off.style.color = '#6d6d68';
    }
    bS.onclick = function(){ on(bS, bL); try{ if(typeof window.hsSent==='function') window.hsSent(); }catch(e){} };
    bL.onclick = function(){ on(bL, bS); try{ if(typeof window.hsListen==='function') window.hsListen(); }catch(e){} };
    return true;
  }

  /* ③ 定时兜底（单页应用切视图时重新插） */
  var tries = 0;
  function tick(){
    tries++;
    hideListenNav();
    addTabs();
    if(tries < 60) setTimeout(tick, 800);
  }
  function boot(){ tick(); }
  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
  setTimeout(boot, 1500); setTimeout(boot, 4000);
  // 点侧栏后也刷新一次
  document.addEventListener('click', function(e){
    var el = e.target && e.target.closest ? e.target.closest('.chip,.mi,[onclick]') : null;
    if(el) setTimeout(function(){ hideListenNav(); addTabs(); }, 600);
  }, true);
})();
