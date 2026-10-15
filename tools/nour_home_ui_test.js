return await (async function(){
  var out=[],errors=[];
  function pause(ms){return new Promise(function(r){setTimeout(r,ms);});}
  function check(name,ok,detail){out.push({name:name,ok:!!ok,detail:String(detail||'')});}
  window.addEventListener('error',function(e){errors.push(String(e.message||e.error||e));});
  try{
    await pause(2600);
    document.body.classList.remove('locked');
    var lock=document.getElementById('mLock'); if(lock) lock.style.display='none';
    var home=document.getElementById('nourProductHome');
    check('首页工作台存在',!!home);
    check('今日一句来自现有句子数据',!!document.querySelector('.nour-daily-quote')&&document.querySelector('.nour-daily-quote-ar').textContent.trim()===document.getElementById('qAr').textContent.trim()&&document.querySelector('.nour-daily-quote-cn').textContent.trim()===document.getElementById('qCn').textContent.trim());
    check('阿语与中文方向隔离',document.querySelector('.nour-daily-quote-ar').getAttribute('dir')==='rtl'&&document.querySelector('.nour-daily-quote-cn').getAttribute('dir')==='ltr');
    var resources=performance.getEntriesByType('resource').map(function(x){return x.name;});
    var dailyRequests=resources.filter(function(x){return /\/api\/sentences\/daily(?:\?|$)/.test(x);});
    var fullRequests=resources.filter(function(x){return /\/api\/sentences(?:\?|$)/.test(x);});
    check('首页只请求有界今日一句',dailyRequests.length>=1&&fullRequests.length===0,{daily:dailyRequests,full:fullRequests});
    check('今日一句摘要响应小于10KB',dailyRequests.every(function(x){var e=performance.getEntriesByName(x)[0];return !e||!e.transferSize||e.transferSize<10000;}),dailyRequests);
    check('今日一句可进入真实句子库',!!document.querySelector('[data-open-sentences]')&&typeof window.showAllSentences==='function');
    check('学习进度读取既有记录',!!document.querySelector('.nour-home-progress')&&document.getElementById('nourHomeProgressValue').textContent.length>0&&document.getElementById('nourHomeProgressBar').style.width.length>0);
    check('目录统计不是误导性的可读数目',document.getElementById('nourStatBooks').textContent.trim()===document.getElementById('hsBooks').textContent.trim()&&document.getElementById('nourStatBooks').nextElementSibling.textContent.trim()==='目录典籍');
    var more=document.querySelector('.nour-more-tools');
    check('次级工具默认折叠',!!more&&!more.open);
    check('折叠区保留原有入口',!!more&&more.querySelector('[data-open-wordbook]')&&more.querySelector('[data-open-dict]')&&more.querySelector('[data-open-listen]'));
    check('旧首页内容仍在 DOM 中',!!document.getElementById('homeShelves')&&!!document.getElementById('quote')&&!!document.getElementById('studyProgress'));
    if(innerWidth<761){check('手机首页无横向溢出',document.documentElement.scrollWidth<=innerWidth+2);}
    else{check('桌面首页保持不等宽双区',getComputedStyle(document.querySelector('.nour-product-grid')).gridTemplateColumns.split(' ').length===2);}
  }catch(e){errors.push(String(e&&e.stack||e));}
  check('无 JavaScript 错误',errors.length===0,errors.join('\n'));
  return JSON.stringify({viewport:[innerWidth,innerHeight],passed:out.filter(function(x){return x.ok;}).length,total:out.length,results:out,errors:errors});
})();
