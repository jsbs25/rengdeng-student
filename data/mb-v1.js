/* ============================================================
   移动端顶部导航栏（返回 + 居中标题）
   文件名带版本号：mb-v1.js（绕开 CDN 缓存）
   ============================================================ */
(function(){
  var VIEW_TITLES = {
    'page-home':'燃灯同学', 'sentView':'句子库', 'dictView':'查词典',
    'libView':'书库', 'grammarView':'语法', 'morphView':'词法',
    'talkView':'日常口语', 'listenView':'听力练习', 'beltView':'中阿要闻'
  };
  function isMobile(){ return window.innerWidth <= 820; }

  function titleNow(){
    try{
      // 优先：标题可见的主视图
      var ids = Object.keys(VIEW_TITLES);
      for(var i=0;i<ids.length;i++){
        var el = document.getElementById(ids[i]);
        if(el && el.offsetParent !== null && getComputedStyle(el).display !== 'none'){
          return VIEW_TITLES[ids[i]];
        }
      }
      // 弹层标题
      var mo = document.querySelector('.modal.show .m-head h3,.modal.show .m-head b,.modal.show .m-title');
      if(mo && mo.textContent.trim()) return mo.textContent.trim().slice(0,14);
      // 侧栏高亮项
      var on = document.querySelector('.chip.on,.mi.on');
      if(on && on.textContent.trim()) return on.textContent.trim().replace(/^[^\u4e00-\u9fa5A-Za-z]+/,'').slice(0,10);
      // 正文大标题
      var h = document.querySelector('#page-home h1,.tk-hero h1,.tk-t1');
      if(h && h.textContent.trim()) return h.textContent.trim().slice(0,14);
    }catch(e){}
    return '燃灯同学';
  }

  function buildBar(){
    if(!isMobile()){ var old=document.getElementById('mobBar'); if(old) old.style.display='none'; return; }
    var bar = document.getElementById('mobBar');
    if(!bar){
      bar = document.createElement('div');
      bar.id = 'mobBar';
      bar.innerHTML = '<button class="mb-back" aria-label="返回"><span style="font-size:1.15rem;line-height:1">‹</span> 返回</button>'
                    + '<div class="mb-title">燃灯同学</div>';
      document.body.appendChild(bar);
      bar.querySelector('.mb-back').addEventListener('click', function(){
        try{
          var open = document.querySelector('.modal.show');
          if(open){ if(typeof window.closeModal==='function'){ window.closeModal(open.id); } else { open.classList.remove('show'); } return; }
          if(history.length > 1){ history.back(); } else { location.href = 'z.html'; }
        }catch(e){ location.reload(); }
      });
    }
    bar.style.display = 'flex';
    var t = bar.querySelector('.mb-title');
    var nt = titleNow();
    if(t && t.textContent !== nt) t.textContent = nt;
  }

  function loop(){ buildBar(); }
  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', loop);
  else loop();
  [600,1500,3000,6000,10000].forEach(function(ms){ setTimeout(loop, ms); });
  window.addEventListener('resize', function(){ setTimeout(buildBar, 200); });
  document.addEventListener('click', function(e){
    var el = e.target && e.target.closest ? e.target.closest('.chip,.mi,[onclick],.m-close') : null;
    if(el) setTimeout(buildBar, 500);
  }, true);
})();
