(function(){
  var out=[];
  function check(name,ok,detail){out.push({name:name,ok:!!ok,detail:String(detail||'')});}
  setTimeout(function(){
    check('realtime start function',typeof window.startNourVoice==='function');
    check('realtime state object',!!(window.NourRealtime&&window.NourRealtime.state));
    check('orb exists',!!document.querySelector('#page-home .nour-orb'));
    check('realtime HUD exists',!!document.getElementById('nourRealtimeHud'));
    check('realtime not connected without click',!(window.NourRealtime&&window.NourRealtime.state.active));
    nav('learn');
    setTimeout(function(){
      check('library page visible',getComputedStyle(document.getElementById('mCat')).display!=='none');
      check('Arabic library default',document.querySelector('#mCatBody .bk-title') && document.querySelector('#mCatBody .bk-title').textContent==='阿拉伯书库');
      check('Arabic cards rendered',!!document.querySelector('#mCatBody .bk-grid .bk-card'));
      check('no startup error',!window.__NUR_ERR,window.__NUR_ERR||'');
      document.title=JSON.stringify({passed:out.filter(function(x){return x.ok;}).length,total:out.length,results:out});
    },1200);
  },900);
})();
