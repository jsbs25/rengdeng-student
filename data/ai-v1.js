/* ============================================================
   努尔老师 · 手机端「不再霸屏滚动」
   只做一件事：阻止页面自动滚动到 AI 区域
   ============================================================ */
(function(){
  var IS_M = function(){ return window.innerWidth <= 820; };
  var inAI = function(el){
    try{
      var p = el;
      while(p && p !== document.body){
        if(p.id === 'aiSec' || (p.className && String(p.className).indexOf('ps-ai') >= 0)) return true;
        p = p.parentNode;
      }
    }catch(e){}
    return false;
  };

  /* ① 屏蔽掉针对 AI 区域的 scrollIntoView（这是"一直滚动"的元凶）*/
  try{
    var _si = Element.prototype.scrollIntoView;
    if(_si && !_si.__aiFix){
      var wrap = function(){
        try{ if(IS_M() && inAI(this)) return; }catch(e){}
        return _si.apply(this, arguments);
      };
      wrap.__aiFix = 1;
      Element.prototype.scrollIntoView = wrap;
    }
  }catch(e){}

  /* ② 屏蔽针对 AI 区域的 scrollTo / 平滑滚动锚点 */
  try{
    var _st = window.scrollTo;
    if(_st && !_st.__aiFix){
      var wrap2 = function(a,b){
        try{
          if(IS_M()){
            var y = (typeof a === 'object' && a) ? a.top : b;
            var ai = document.getElementById('aiSec');
            if(ai && typeof y === 'number'){
              var top = ai.getBoundingClientRect().top + window.pageYOffset;
              if(Math.abs(y - top) < 60 && Math.abs(y - window.pageYOffset) > 300) return;
            }
          }
        }catch(e){}
        return _st.apply(window, arguments);
      };
      wrap2.__aiFix = 1;
      window.scrollTo = wrap2;
    }
  }catch(e){}

  /* ③ 每次 AI 内容变化后，把页面滚回它原来的位置 */
  var lockY = null;
  function watch(){
    if(!IS_M()) return;
    var host = document.getElementById('aiSec');
    if(!host) return;
    var msgs = host.querySelector('.ps-ai-msgs');
    if(!msgs || msgs.__aiFixW) return;
    msgs.__aiFixW = 1;
    var obs = new MutationObserver(function(){
      var y = window.pageYOffset;
      // 只让答案区自己滚，不动页面
      setTimeout(function(){ if(Math.abs(window.pageYOffset - y) > 120) window.scrollTo({top:y, behavior:'auto'}); }, 40);
    });
    obs.observe(msgs, {childList:true, subtree:true, characterData:true});
  }
  setInterval(watch, 1200);
  [800,2000,4000].forEach(function(t){ setTimeout(watch, t); });
})();
