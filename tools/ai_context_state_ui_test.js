return await (async function(){
  var out=[],errors=[];
  function p(ms){return new Promise(function(r){setTimeout(r,ms);});}
  function c(name,ok,detail){out.push({name:name,ok:!!ok,detail:detail||''});}
  function vis(el){if(!el)return false;var r=el.getBoundingClientRect(),s=getComputedStyle(el);return r.width>0&&r.height>0&&s.display!=='none'&&s.visibility!=='hidden';}
  try{
    await p(900);
    var aiBtn=typeof nav==='function';
    c('问燃灯入口存在',aiBtn);
    if(aiBtn){nav('ai');await p(240);}
    window.NOUR_AI_CONTEXT=null;
    if(typeof window.NOUR_SYNC_READER_CONTEXT==='function')window.NOUR_SYNC_READER_CONTEXT();
    await p(80);
    var box=document.getElementById('nourReaderContext');
    c('无正文语境状态可见',!!box&&vis(box)&&box.classList.contains('is-empty'));
    c('无正文状态明确说明边界',!!box&&/未连接正文语境/.test(box.textContent||'')&&/普通问题仍可回答/.test(box.textContent||''));
    c('无正文状态提供打开书库入口',!!box&&!!box.querySelector('.nour-reader-context__open'));
    window.NOUR_AI_CONTEXT={id:'shamela-8220',title:'مختصر القدوري',page:239,total:239,text:'كتاب الطهارة نص عربي للاختبار',source:'shamela',selected:'الاستحسان'};
    if(typeof window.NOUR_SYNC_READER_CONTEXT==='function')window.NOUR_SYNC_READER_CONTEXT();
    await p(80); box=document.getElementById('nourReaderContext');
    c('连接正文后状态切换',!!box&&vis(box)&&!box.classList.contains('is-empty'));
    c('显示真实书名和页码',!!box&&/مختصر القدوري/.test(box.textContent||'')&&/239/.test(box.textContent||''));
    var sel=box&&box.querySelector('.nour-reader-context__selection b');
    c('选词保持阿语 RTL',!!sel&&sel.getAttribute('dir')==='rtl'&&sel.getAttribute('lang')==='ar');
    var clear=box&&box.querySelector('.nour-reader-context__clear');
    if(clear){clear.click();await p(60);}
    c('清除后恢复无正文状态',!!box&&box.classList.contains('is-empty')&&/未连接正文语境/.test(box.textContent||''));
  }catch(e){errors.push(String(e&&e.stack||e));}
  var pass=out.filter(function(x){return x.ok;}).length;
  return JSON.stringify({passed:pass,total:out.length,results:out,errors:errors});
})();
