return await (async function(){
  var out=[], errors=[];
  function check(name,ok,detail){out.push({name:name,ok:!!ok,detail:String(detail||'')});}
  function pause(ms){return new Promise(function(r){setTimeout(r,ms);});}
  window.addEventListener('error',function(e){errors.push(String(e.message||e.error||e));});
  try{
    if(typeof window.showIslamicLibrary==='function') window.showIslamicLibrary();
    await pause(950);
    var button=document.querySelector('.isl-quran-card button');
    check('伊斯兰来源古兰经按钮存在',!!button);
    if(button) button.click();
    await pause(700);
    check('古兰经目录弹窗打开',!!document.getElementById('mQuran') && getComputedStyle(document.getElementById('mQuran')).display!=='none');
    check('古兰经包含114章',String((document.getElementById('mQuranCount')||{}).textContent||'').indexOf('114')>=0,(document.getElementById('mQuranCount')||{}).textContent);
    var first=document.querySelector('#mQuranBody .s-item');
    check('首章可点击',!!first);
    if(first) first.click();
    await pause(900);
    check('首章进入软件内阅读器',!!window.RD_AUDIO && window.RD_AUDIO.kind==='quran' && getComputedStyle(document.getElementById('mReader')).display!=='none');
    check('首章 RTL 原文已显示',!!document.querySelector('#mReader .rd-page') && document.querySelector('#mReader .rd-page').textContent.indexOf('بِسْمِ')>=0);
    check('逐页 AI 面板已挂载',!!document.getElementById('rdPageAnalysis'));
  }catch(e){errors.push(String(e&&e.stack||e));}
  check('无 JavaScript 错误',errors.length===0,errors.join('\n'));
  return JSON.stringify(out);
})();
