return await (async function(){
  var out=[], errors=[];
  function pause(ms){return new Promise(function(r){setTimeout(r,ms);});}
  function check(name,ok,detail){out.push({name:name,ok:!!ok,detail:detail||''});}
  function visible(el){if(!el)return false;var r=el.getBoundingClientRect(),c=getComputedStyle(el);return r.width>0&&r.height>0&&c.display!=='none'&&c.visibility!=='hidden';}
  try{
    await pause(900);
    var study=document.querySelector('[data-primary-route="study"]');
    check('学习一级入口存在',!!study);
    if(study){study.click(); await pause(220);}
    var modal=document.getElementById('mLearn'), intro=modal&&modal.querySelector('.study-workspace-intro');
    check('学习入口打开真实工作台',!!modal&&visible(modal)&&modal.classList.contains('show'));
    check('工作台标题正确',!!modal&&/学习工作台/.test(modal.querySelector('.m-head')?.textContent||''));
    check('工作台概览可见',!!intro&&visible(intro));
    check('真实进度指标存在',!!modal&&!!modal.querySelector('#studyWorkspaceLearned')&&!!modal.querySelector('#studyWorkspaceStreak'));
    check('保留原句子分类',!!modal&&!!modal.querySelector('.cat-scroll')&&modal.querySelectorAll('.cat-scroll *').length>1);
    check('保留原句子列表与筛选',!!modal&&!!modal.querySelector('#sList')&&!!modal.querySelector('[data-flt="learned"]')&&!!modal.querySelector('[data-flt="fav"]')&&!!modal.querySelector('[data-flt="review"]'));
    check('四个真实学习快捷入口存在',!!modal&&modal.querySelectorAll('.study-workspace-actions button').length===4);
    var action=modal&&modal.querySelector('.study-workspace-actions button');
    if(action){action.click(); await pause(180);}
    check('快捷入口可触发既有课程面板',!!document.querySelector('.modal.show')||!!document.querySelector('.page[style*="display"]'));
    if(modal&&typeof closeModal==='function') closeModal('mLearn');
    var html=document.documentElement, old=html.getAttribute('data-theme');
    if(study){study.click(); await pause(180);}
    intro=document.querySelector('#mLearn .study-workspace-intro');
    html.setAttribute('data-theme','dark'); await pause(60);
    var bg=intro&&getComputedStyle(intro).backgroundColor, color=intro&&getComputedStyle(intro).color;
    check('夜间工作台保持深色对比',!!intro&&bg&&bg!=='rgb(255, 255, 255)'&&color!=='rgb(29, 41, 34)');
    if(old)html.setAttribute('data-theme',old);else html.removeAttribute('data-theme');
    if(typeof closeModal==='function')closeModal('mLearn');
  }catch(e){errors.push(String(e&&e.stack||e));}
  var passed=out.filter(function(x){return x.ok;}).length;
  return JSON.stringify({passed:passed,total:out.length,results:out,errors:errors});
})();
