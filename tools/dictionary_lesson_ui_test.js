return await (async function(){
  var out=[], errors=[];
  function pause(ms){return new Promise(function(r){setTimeout(r,ms);});}
  function check(name,ok,detail){out.push({name:name,ok:!!ok,detail:detail||''});}
  function visible(el){if(!el)return false;var r=el.getBoundingClientRect(),c=getComputedStyle(el);return r.width>0&&r.height>0&&c.display!=='none'&&c.visibility!=='hidden';}
  try{
    await pause(1100);
    var resources=[];
    var originalFetch=window.fetch;
    window.fetch=function(url,opts){resources.push(String(url));return originalFetch.apply(this,arguments);};
    if(typeof window.openDict==='function') window.openDict();
    await pause(180);
    if(typeof window.hsDictInit==='function') window.hsDictInit();
    var q=document.getElementById('dictQ'), body=document.getElementById('dictBody');
    check('词典工作区存在',!!q&&!!body);
    if(q&&body){
      q.value='كتاب';
      if(typeof window.dictSearch==='function') window.dictSearch();
      await pause(950);
      var lessons=document.getElementById('dictLessons');
      var items=lessons?lessons.querySelectorAll('.dict-lesson-item'):[];
      check('课程关联层出现',!!lessons&&visible(lessons));
      check('真实课程命中',items.length>0&&/词法课|语法课/.test(lessons.textContent||''),{count:items.length,text:(lessons&&lessons.textContent||'').slice(0,240)});
      check('课程示例词保持 RTL',!!lessons&&!!lessons.querySelector('[dir="rtl"][lang="ar"]'));
      check('课程接口实际发出',resources.some(function(u){return u.indexOf('/api/dict/lesson?')>=0;}));
      var open=lessons&&lessons.querySelector('.dict-lesson-open');
      if(open){open.click();await pause(220);}
      var gram=document.getElementById('mGrammar');
      check('课程按钮打开真实课程面板',!!gram&&gram.classList.contains('show')&&/词法课|语法课/.test((gram.textContent||'')));
      if(gram&&typeof closeModal==='function') closeModal('mGrammar');
    }
    var html=document.documentElement, old=html.getAttribute('data-theme');
    html.setAttribute('data-theme','dark'); await pause(80);
    var lessonDark=document.getElementById('dictLessons');
    check('夜间课程层保持可读',!!lessonDark&&getComputedStyle(lessonDark).borderTopColor&&getComputedStyle(lessonDark.querySelector('.dict-lesson-open')||lessonDark).color!=='rgb(29, 29, 31)');
    if(old) html.setAttribute('data-theme',old); else html.removeAttribute('data-theme');
    window.fetch=originalFetch;
  }catch(e){errors.push(String(e&&e.stack||e));}
  var passed=out.filter(function(x){return x.ok;}).length;
  return JSON.stringify({passed:passed,total:out.length,results:out,errors:errors});
})();
