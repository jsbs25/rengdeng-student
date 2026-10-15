return await (async function(){
  var out=[],errors=[];
  function pause(ms){return new Promise(function(r){setTimeout(r,ms);});}
  function check(name,ok,detail){out.push({name:name,ok:!!ok,detail:String(detail||'')});}
  window.addEventListener('error',function(e){errors.push(String(e.message||e.error||e));});
  try{
    await pause(3600);
    var home=document.getElementById('page-home'), ai=document.getElementById('aiSec');
    check('首页存在且可见',!!home&&getComputedStyle(home).display!=='none');
    check('首页默认不强制展示 AI',!!ai&&getComputedStyle(ai).display==='none');
    check('本地查词与发音入口可见',!!document.querySelector('[data-open-dict]')&&getComputedStyle(document.querySelector('[data-open-dict]')).display!=='none');
    check('首页没有金色 AI 光球主入口',!document.querySelector('.nour-orb'));
    openDict(); await pause(180);
    var dict=document.getElementById('mDict'), input=document.getElementById('dictQ');
    check('词典全屏弹层打开',!!dict&&dict.classList.contains('show')&&!!input);
    input.value='كتاب'; dictSearch(); await pause(2600);
    var body=document.getElementById('dictBody'), text=body?body.textContent:'';
    check('查词结果在站内显示',!!body&&text.length>40);
    check('查词结果含阿拉伯例句',!!body&&/[\u0600-\u06ff]/.test(text));
    check('查词结果有中文或英文释义',!!body&&/(书|book|公开词典补充|暂未找到固定释义)/i.test(text));
    check('查词不触发 AI 占位',!!body&&!text.includes('🤖')&&!text.includes('努尔老师补充'));
    check('公开来源标记可见',!!body&&text.includes('Arabic Wiktionary')||!!body&&text.includes('本地固定词库'));
    var play=body&&body.querySelector('.dict-play,.dict-mini-play');
    check('阿语朗读按钮可见',!!play&&play.getBoundingClientRect().width>0);
    if(play){play.click();await pause(80);}
    closeModal('mDict'); await pause(150);
    var fake=document.createElement('span');fake.textContent='كتاب';document.body.appendChild(fake);
    rdWord({stopPropagation:function(){}},fake); await pause(2200);
    var wb=document.getElementById('rdWordBox');
    check('阅读器单词卡能打开',!!wb&&getComputedStyle(wb).display!=='none');
    check('阅读器单词卡不被底部导航遮挡',!!wb&&wb.getBoundingClientRect().bottom<=innerHeight+2);
    check('阅读器单词卡有释义/例句',!!wb&&/[\u0600-\u06ff]/.test(wb.textContent||''));
    var close=wb&&wb.querySelector('.rd-word-close');if(close)close.click();fake.remove();
    check('关闭单词卡无残留',!document.getElementById('rdWordBox'));
    check('流式 OpenITI UI 代码仍在页面',typeof rdOpenitiFetch==='function'&&!!document.getElementById('rdOpenitiProgress')===false);
  }catch(e){errors.push(String(e&&e.stack||e));}
  check('无 JavaScript 错误',errors.length===0,errors.join('\n'));
  return JSON.stringify({viewport:[innerWidth,innerHeight],build:window.__NUR_BUILD,passed:out.filter(function(x){return x.ok;}).length,total:out.length,results:out,errors:errors});
})();
