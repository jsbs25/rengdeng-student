return await (async function(){
  var out=[], errors=[];
  function pause(ms){return new Promise(function(r){setTimeout(r,ms);});}
  function check(name,ok,detail){out.push({name:name,ok:!!ok,detail:detail||''});}
  try{
    await pause(1100);
    check('词典建议函数已加载',typeof window.dictSuggest==='function'&&typeof window.hsDictInit==='function');
    check('版本化 views2 已加载',performance.getEntriesByType('resource').some(function(x){return /data\/views2\.js\?v=/.test(x.name);}));
    if(typeof window.openDict==='function') window.openDict();
    await pause(180);
    if(typeof window.hsDictInit==='function') window.hsDictInit();
    var q=document.getElementById('dictQ'), box=document.getElementById('dictSug'), body=document.getElementById('dictBody');
    check('词典输入框存在',!!q&&!!box&&!!body);
    if(q&&box){
      q.value='كت'; q.dispatchEvent(new Event('input',{bubbles:true}));
      await pause(420);
      var rows=box.querySelectorAll('.dict-sug-i');
      check('真实词头候选出现',rows.length>0&&rows.length<=8,{count:rows.length,text:box.textContent.slice(0,120)});
      check('候选阿语方向正确',!!rows[0]&&rows[0].querySelector('[dir="rtl"]')!==null);
      check('建议请求实际发出',performance.getEntriesByType('resource').some(function(x){return /\/api\/dict\/suggest\?/.test(x.name);}));
    }
    if(q&&body){
      q.value='كتاب';
      if(typeof window.dictSearch==='function') window.dictSearch();
      await pause(360);
      check('真实查词结果出现',!!body.querySelector('.dict-definition')||body.textContent.indexOf('例句')>=0,{text:body.textContent.slice(0,180)});
      check('例句阿语保持 RTL',!!body.querySelector('.dict-ex-ar[dir="rtl"]'));
      check('例句中文保持 LTR',!!body.querySelector('.dict-ex-cn')&&getComputedStyle(body.querySelector('.dict-ex-cn')).direction==='ltr');
    }
    var html=document.documentElement, old=html.getAttribute('data-theme');
    html.setAttribute('data-theme','dark'); await pause(70);
    var sugBg=box?getComputedStyle(box).backgroundColor:'';
    check('夜间建议面板可读',!!box&&sugBg&&sugBg!=='rgb(255, 255, 255)',{background:sugBg});
    if(old) html.setAttribute('data-theme',old); else html.removeAttribute('data-theme');
  }catch(e){errors.push(String(e&&e.stack||e));}
  var passed=out.filter(function(x){return x.ok;}).length;
  return JSON.stringify({passed:passed,total:out.length,results:out,errors:errors});
})();
