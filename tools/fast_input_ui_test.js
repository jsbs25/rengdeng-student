return await (async function(){
  const out=[]; const pause=ms=>new Promise(r=>setTimeout(r,ms));
  const check=(name,ok,detail)=>out.push({name,ok:!!ok,detail:detail||''});
  await pause(1800);
  if(typeof nav==='function') nav('ai');
  await pause(220);
  const input=document.getElementById('homeAIIn'), fast=document.getElementById('homeAIFast'), send=document.getElementById('homeAISendBtn');
  check('textarea exists',!!input);
  check('fast toggle exists',!!fast);
  check('send button exists',!!send);
  check('input supports multiline',input && input.tagName==='TEXTAREA');
  if(input){input.value='第一行\n第二行\n第三行'; if(typeof homeAIResize==='function') homeAIResize(input); input.dispatchEvent(new Event('input',{bubbles:true}));}
  check('multiline grows',input && parseFloat(getComputedStyle(input).height)>=70,'height='+((input&&getComputedStyle(input).height)||''));
  const before=fast&&fast.textContent; if(fast) fast.click(); await pause(50);
  check('mode toggles',fast && fast.textContent!==before,fast&&fast.textContent);
  if(fast) fast.click();
  if(input){input.value=''; homeAIResize(input); input.focus();}
  check('compose within viewport',input && input.getBoundingClientRect().right<=window.innerWidth+1);
  check('send within viewport',send && send.getBoundingClientRect().right<=window.innerWidth+1);
  check('no startup error',!window.__NUR_ERR,window.__NUR_ERR||'');
  return JSON.stringify({passed:out.filter(x=>x.ok).length,total:out.length,results:out});
})();
