/* ============================================================
   努尔老师 · 独立界面入口
   把首页的 #aiSec 搬进一个独立弹层；点侧栏「🤖 努尔老师」进入
   —— 只搬 DOM 节点，不动任何函数 ✓
   ============================================================ */
(function(){
  var MODAL_ID = 'mAI';
  var moved = false;

  /* ① 建独立界面容器（复用站点 .modal / .m-head / .m-body 体系）*/
  function ensureModal(){
    if(document.getElementById(MODAL_ID)) return document.getElementById(MODAL_ID);
    var m = document.createElement('div');
    m.className = 'modal';
    m.id = MODAL_ID;
    m.innerHTML = '<div class="m-head"><span>🤖</span><b>努尔老师 · 阿语 AI</b>'
                + '<button class="m-close" onclick="window.closeModal(\'' + MODAL_ID + '\')">✕</button></div>'
                + '<div class="m-body" id="mAIBody"></div>';
    document.body.appendChild(m);
    return m;
  }

  /* ② 把 #aiSec 搬进弹层（只搬一次）*/
  function moveAI(){
    var ai = document.getElementById('aiSec');
    var body = document.getElementById('mAIBody');
    if(!ai || !body) return false;
    if(ai.parentNode !== body){
      body.appendChild(ai);          // 搬节点：事件、状态、历史消息全部保留 ✓
      ai.style.display = '';
    }
    moved = true;
    return true;
  }

  /* ③ 打开独立界面 */
  function openAI(){
    ensureModal();
    moveAI();
    try{ if(typeof window.openModal === 'function'){ window.openModal(MODAL_ID); } else { document.getElementById(MODAL_ID).classList.add('show'); } }catch(e){}
    setTimeout(function(){
      var msgs = document.querySelector('#mAI .ps-ai-msgs');
      if(msgs) msgs.scrollTop = msgs.scrollHeight;
      var inp = document.querySelector('#mAI .ps-ai-input input');
      if(inp && window.innerWidth > 900) try{ inp.focus(); }catch(e){}
    }, 350);
  }
  window.openNurAI = openAI;

  /* ④ 在侧栏加入口（插到「句子库」后面）*/
  function addEntry(){
    var rail = document.querySelector('.hs-rail');
    if(!rail || rail.querySelector('[data-ai-entry]')) return;
    var btn = document.createElement('button');
    btn.setAttribute('data-ai-entry','1');
    btn.className = 'chip';
    btn.innerHTML = '<span class="chip-i">🤖</span>努尔老师';
    btn.style.cssText = 'width:100%;justify-content:flex-start;border:none;background:transparent;text-align:left;cursor:pointer';
    btn.onclick = function(){
      var all = rail.querySelectorAll('.chip');
      all.forEach(function(c){ c.classList.remove('on'); });
      btn.classList.add('on');
      openAI();
    };
    rail.appendChild(btn);
  }

  /* ⑤ 也加一个手机端悬浮入口（万一侧栏滚不到）*/
  function addFloat(){
    if(document.getElementById('nurFab')) return;
    var b = document.createElement('button');
    b.id = 'nurFab';
    b.type = 'button';
    b.title = '努尔老师';
    b.setAttribute('aria-label','打开努尔老师');
    b.innerHTML = '🤖';
    b.style.cssText = 'position:fixed;right:14px;bottom:calc(96px + env(safe-area-inset-bottom));z-index:3300;'
                    + 'width:52px;height:52px;border-radius:999px;border:1px solid rgba(26,26,26,.12);'
                    + 'background:rgba(253,251,247,.94);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);'
                    + 'font-size:22px;box-shadow:0 6px 22px rgba(26,26,26,.14);cursor:pointer;display:none;';
    b.onclick = openAI;
    document.body.appendChild(b);
    function sync(){ b.style.display = (window.innerWidth <= 900) ? 'flex' : 'none'; }
    sync();
    window.addEventListener('resize', function(){ setTimeout(sync, 150); });
  }

  /* ⑥ 启动 */
  function boot(){ ensureModal(); addEntry(); addFloat(); }
  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
  [1200, 2600, 5000, 9000].forEach(function(t){ setTimeout(boot, t); });

  /* ⑦ 打开的入口：任何带 openNurAI 的点击都生效 */
  document.addEventListener('click', function(e){
    var el = e.target && e.target.closest ? e.target.closest('[data-open-ai],[onclick*="openNurAI"]') : null;
    if(el){ e.preventDefault(); openAI(); }
  }, true);
})();
