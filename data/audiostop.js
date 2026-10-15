/* 退出阅读页/切后台 → 停掉所有正在播放的音频（全局拦截）*/
(function(){
  var all = [];
  var OrigAudio = window.Audio;
  if(OrigAudio && !OrigAudio.__wrapped){
    function W(src){ var a = new OrigAudio(src); try{ all.push(a); a.addEventListener('ended', function(){ var i = all.indexOf(a); if(i>=0) all.splice(i,1); }); }catch(e){} return a; }
    W.prototype = OrigAudio.prototype;
    W.__wrapped = 1;
    try{ window.Audio = W; }catch(e){}
  }
  function stopAll(){
    try{
      for(var i = all.length - 1; i >= 0; i--){ try{ all[i].pause(); }catch(e){} }
      all = [];
    }catch(e){}
    // 兜底：把页面上所有 audio 标签也停掉
    try{ Array.prototype.forEach.call(document.querySelectorAll('audio'), function(a){ try{ a.pause(); }catch(e){} }); }catch(e){}
    // 停掉语音合成（如果用了 speech）
    try{ if(window.speechSynthesis) window.speechSynthesis.cancel(); }catch(e){}
  }
  window.__stopAllAudio = stopAll;

  // ① 退出阅读器（返回/关闭弹层）时停
  try{
    var cm = window.closeModal;
    if(typeof cm === 'function' && !cm.__as){
      var w2 = function(id){ if(id === 'mReader' || id === 'mTalk' || id === 'mH6') stopAll(); return cm.apply(this, arguments); };
      w2.__as = 1;
      window.closeModal = w2;
    }
  }catch(e){}

  // ② 浏览器后退 / 返回键（popstate & 页面隐藏）
  window.addEventListener('popstate', function(){
    setTimeout(function(){ if(!document.querySelector('#mReader.show')) stopAll(); }, 120);
  });
  document.addEventListener('visibilitychange', function(){ if(document.hidden) stopAll(); });
  window.addEventListener('pagehide', function(){ stopAll(); });
  window.addEventListener('blur', function(){ setTimeout(function(){ if(!document.querySelector('.modal.show')) stopAll(); }, 1500); });

  // ③ 定时兜底：阅读器关着却还有声音 → 停
  setInterval(function(){
    try{
      var inReader = !!document.querySelector('#mReader.show');
      if(!inReader && all.length){ stopAll(); }
    }catch(e){}
  }, 1500);
})();
