return await (async function(){
  var checks=[], errors=[], capturedGuide='', capturedRead=null, originalGuide=window.openIslamicGuide, originalRead=window.openReadById;
  function pause(ms){return new Promise(function(r){setTimeout(r,ms);});}
  function check(name,ok,detail){checks.push({name:name,ok:!!ok,detail:String(detail||'')});}
  window.addEventListener('error',function(e){errors.push(String(e.message||e.error||e));});
  try{
    await pause(700);
    nav('learn');
    await pause(1400);
    var room=document.getElementById('nourFiqhReadingRoom');
    check('四学派阅读室已挂载',!!room);
    check('四大学派横向卡已显示',!!room&&room.querySelectorAll('.nour-fiqh-school-card').length===4);
    check('哈乃斐入口可见',!!room&&/哈乃斐学派/.test(room.textContent||'')&&/مختصر القدوري/.test(room.textContent||''));
    check('哈乃斐目录计数来自 API',!!room&&/127/.test(room.textContent||''));
    check('站内原文与书目导读状态分开',!!room&&room.querySelector('.nour-fiqh-badge.is-read')&&room.querySelector('.nour-fiqh-badge.is-guide'));
    var tab=room&&room.querySelector('[data-fiqh-school="shafii"]'); if(tab) tab.click();
    await pause(180);
    check('学派切换更新当前入口',!!room&&/沙斐仪学派/.test(room.querySelector('.nour-fiqh-focus')&&room.querySelector('.nour-fiqh-focus').textContent||''));
    window.openIslamicGuide=function(id){capturedGuide=String(id||'');};
    window.openReadById=function(id,rt){capturedRead={id:String(id||''),rt:String(rt||'')};};
    var quduri=room&&room.querySelector('[data-fiqh-open="fiqh-quduri"]');
    if(quduri) quduri.click();
    check('古都里简编进入完整 Shamela 阅读器',!!capturedRead&&capturedRead.id==='8220'&&capturedRead.rt==='shamela',JSON.stringify(capturedRead));
    var hanafi=room&&room.querySelector('[data-fiqh-school="hanafi"]'); if(hanafi) hanafi.click();
    var ai=room&&room.querySelector('[data-fiqh-ai]'); if(ai) ai.click();
    await pause(220);
    var input=document.getElementById('homeAIIn');
    check('四学派比较可交给 NOUR AI',!!input&&/四大学派/.test(input.value||'')&&/哈乃斐/.test(input.value||''));
    check('无 JavaScript 错误',errors.length===0,errors.join('\n'));
  }catch(e){errors.push(String(e&&e.stack||e));}
  window.openIslamicGuide=originalGuide; window.openReadById=originalRead;
  return JSON.stringify({viewport:[innerWidth,innerHeight],passed:checks.filter(function(x){return x.ok;}).length,total:checks.length,results:checks,errors:errors});
})();
