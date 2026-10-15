return await (async function(){
  const out=[]; const pause=ms=>new Promise(r=>setTimeout(r,ms));
  const check=(name,ok,detail)=>out.push({name,ok:!!ok,detail:detail||''});
  await pause(1600); if(typeof nav==='function') nav('ai'); await pause(180);
  const input=document.getElementById('homeAIIn'), count=document.getElementById('homeAICount'), send=document.getElementById('homeAISendBtn'), compose=document.querySelector('.home-ai-compose'), mode=document.getElementById('homeAIFast');
  check('textarea exists',!!input); check('counter exists',!!count); check('send exists',!!send); check('mode exists',!!mode);
  if(input){input.value='测试输入框动效'; input.dispatchEvent(new Event('input',{bubbles:true}));}
  await pause(80);
  check('counter updates',count && /\d+\s*字/.test(count.textContent),count&&count.textContent);
  check('compose has text class',compose&&compose.classList.contains('has-text'));
  check('send ready class',send&&send.classList.contains('is-ready'));
  if(input){input.value=''; input.dispatchEvent(new Event('input',{bubbles:true}));}
  await pause(50);
  check('ready clears',send&&!send.classList.contains('is-ready'));
  check('input within viewport',input&&input.getBoundingClientRect().right<=innerWidth+1);
  check('no startup error',!window.__NUR_ERR,window.__NUR_ERR||'');
  return JSON.stringify({passed:out.filter(x=>x.ok).length,total:out.length,results:out});
})();
