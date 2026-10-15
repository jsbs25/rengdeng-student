/* ============================================================
   V3 底部导航（试版）—— 4 项指向网站已有的真实功能
   不新增功能，只做入口
   ============================================================ */
(function(){
  var ITEMS = [
    ['⌂','首页', function(){ try{ closeAllModals&&closeAllModals(); var h=document.getElementById('page-home'); if(h) h.scrollIntoView({behavior:'auto'}); window.scrollTo(0,0); }catch(e){} }],
    ['▤','书库', function(){ try{ closeAllModals&&closeAllModals(); if(typeof hsBooks==='function') hsBooks(); }catch(e){} }],
    ['⌕','查词', function(){ try{ closeAllModals&&closeAllModals(); if(typeof openDict==='function') openDict(); }catch(e){} }],
    ['◉','诺尔老师', function(){ try{ if(typeof openNurAI==='function') openNurAI(); }catch(e){} }]
  ];
  function build(){
    if(document.getElementById('v3nav')) return;
    var n = document.createElement('div'); n.id='v3nav';
    n.innerHTML = ITEMS.map(function(it,i){
      return '<button data-v3="'+i+'"><span class="i">'+it[0]+'</span><span class="l">'+it[1]+'</span></button>';
    }).join('');
    document.body.appendChild(n);
    n.querySelectorAll('button').forEach(function(b){
      b.onclick = function(){
        n.querySelectorAll('button').forEach(function(x){ x.classList.remove('on'); });
        b.classList.add('on');
        var i = parseInt(b.getAttribute('data-v3'),10);
        ITEMS[i][2]();
      };
    });
    n.querySelector('[data-v3="0"]').classList.add('on');
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded', build); else build();
  [1200,3000].forEach(function(t){ setTimeout(build,t); });
})();
