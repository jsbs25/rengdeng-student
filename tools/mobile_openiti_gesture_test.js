return await (async function(){
  var out=[],errors=[];
  function pause(ms){return new Promise(function(r){setTimeout(r,ms);});}
  function check(n,o,d){out.push({name:n,ok:!!o,detail:String(d||'')});}
  function fs(x,y){rdTouchStart({touches:[{clientX:x,clientY:y}]});}
  function fm(x,y){rdTouchMove({touches:[{clientX:x,clientY:y}],cancelable:true,preventDefault:function(){}});}
  function fe(x,y){rdTouchEnd({changedTouches:[{clientX:x,clientY:y}]});}
  window.addEventListener('error',function(e){errors.push(String(e.message||e.error||e));});
  try{
    nav('learn'); await pause(180); libTab('islamic'); await pause(1100);
    var original=document.querySelector('#catGrid .bk-original');
    check('阿拉伯原文书卡可见',!!original);
    if(original) original.click();
    await pause(3000);
    var reader=document.getElementById('mReader'),body=document.getElementById('mReaderBody'),paper=body&&body.querySelector('.rd-paper');
    check('OpenITI 留在软件内阅读',!!window.RD_OPENITI&&!!reader&&getComputedStyle(reader).display!=='none');
    check('OpenITI 正文已加载',!!body&&!!body.querySelector('.rd-page')&&!body.textContent.includes('正在载入'));
    check('OpenITI AI 面板已挂载',!!document.querySelector('.rd-page-analysis'));
    check('移动触摸样式已启用',!!paper&&getComputedStyle(paper).touchAction==='pan-y');
    var p0=window.RD_PAGE,max=Math.max(0,body.scrollHeight-body.clientHeight);
    body.scrollTop=Math.min(160,max); await pause(50);
    check('OpenITI 纵向滚动正常',max===0||body.scrollTop>0,'scroll='+body.scrollTop+' max='+max);
    fs(200,500);fm(210,270);fe(210,270);await pause(120);
    check('OpenITI 纵向滑动不翻页',window.RD_PAGE===p0,'page='+window.RD_PAGE);
    fs(315,420);fm(100,422);fe(100,422);await pause(700);
    var p1=window.RD_PAGE;
    check('OpenITI 左滑下一页',p1===Math.min(p0+1,(window.RD_OPENITI.total||1)-1),'from='+p0+' to='+p1);
    fs(90,420);fm(300,422);fe(300,422);await pause(700);
    check('OpenITI 右滑返回',window.RD_PAGE===p0,'page='+window.RD_PAGE);
    closeModal('mReader');await pause(150);
    check('退出后无残留阅读状态',!document.body.classList.contains('reading')&&!document.querySelector('.modal.show'));
  }catch(e){errors.push(String(e&&e.stack||e));}
  check('无 JavaScript 错误',errors.length===0,errors.join('\n'));
  return JSON.stringify({viewport:[innerWidth,innerHeight],passed:out.filter(function(x){return x.ok;}).length,total:out.length,results:out,errors:errors});
})();
