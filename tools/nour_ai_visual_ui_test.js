return await (async function(){
  var out=[], errors=[];
  function pause(ms){return new Promise(function(r){setTimeout(r,ms);});}
  function check(name,ok,detail){out.push({name:name,ok:!!ok,detail:String(detail||'')});}
  window.addEventListener('error',function(e){errors.push(String(e.message||e.error||e));});
  try{
    await pause(700); nav('ai'); await pause(250);
    var ai=document.getElementById('aiSec'), card=ai&&ai.querySelector('.ps-ai-card'), msgs=document.getElementById('homeAI'), input=document.getElementById('homeAIIn'), send=document.getElementById('homeAISendBtn'), modes=ai&&ai.querySelector('.nour-ai-modes'), chips=ai&&ai.querySelector('.ps-ai-chips');
    var cr=card&&card.getBoundingClientRect(), mr=msgs&&msgs.getBoundingClientRect(), ir=input&&input.getBoundingClientRect(), sr=send&&send.getBoundingClientRect();
    check('AI 工作区可见',!!ai&&getComputedStyle(ai).display!=='none');
    check('AI 视觉精修层已加载',!!document.getElementById('nour-ai-polish'));
    check('AI 标题与模式切换可见',!!ai&&!!ai.querySelector('.nour-ai-intro h1')&&!!modes);
    check('AI 卡片有清晰边界',!!card&&getComputedStyle(card).borderTopLeftRadius==='8px'&&getComputedStyle(card).overflow==='hidden');
    check(innerWidth>760?'桌面使用左右工作区':'手机使用单列工作区',innerWidth>760?!!card&&getComputedStyle(card).gridTemplateColumns.split(' ').length>=2:!!card&&getComputedStyle(card).gridTemplateColumns.trim().split(/\s+/).length===1);
    check('消息区可滚动且不被挤出',!!msgs&&mr.width>220&&mr.height>150&&getComputedStyle(msgs).overflowY==='auto');
    check('输入框可见且在视口内',!!input&&ir.width>160&&ir.bottom<=innerHeight+2,'input='+JSON.stringify({x:ir&&ir.x,y:ir&&ir.y,w:ir&&ir.width,h:ir&&ir.height}));
    check('发送按钮可见且可聚焦',!!send&&sr.width>=38&&sr.height>=38&&!send.disabled);
    check('快捷问题区可见',!!chips&&chips.getBoundingClientRect().height>40);
    input.focus(); check('输入框焦点可见',document.activeElement===input);
    input.value='测试上下文'; homeAIInputState(input); await pause(50);
    check('输入后发送按钮进入可用态',send.classList.contains('is-ready'));
    var active=modes&&modes.querySelector('[data-ai-mode="arabic"]'); if(active){active.click();await pause(30);}
    check('模式切换即时更新提示',!!input&&input.placeholder.indexOf('阿拉伯语')>=0);
    nav('home'); await pause(120); check('离开 AI 后无残留弹层',document.querySelectorAll('.modal.show').length===0);
  }catch(e){errors.push(String(e&&e.stack||e));}
  check('无 JavaScript 错误',errors.length===0,errors.join('\n'));
  return JSON.stringify({viewport:[innerWidth,innerHeight],passed:out.filter(function(x){return x.ok;}).length,total:out.length,results:out,errors:errors});
})();
